"""Build one rhythm-challenge item:
  truth.musicxml (model -> MusicXML 4.0, XSD-validated)
  engraving.ly   (model -> LilyPond, explicit beams / breaks)
  verification   (LilyPond event dump == model; MIDI attacks == truth; music21 re-parse
                  of truth == model; lyric syllables present in the vector PDF)
  clean.pdf      (undamaged 300 dpi raster of the engraving, image-only)
  scan*.pdf      (damaged image-only PDFs, see scan.py; params + seed in meta.json)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import traceback

from PIL import Image

from . import scan as S
from . import verify as V
from .lily import LilyWriter
from .model import check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voices_with_lyrics
from .mxl import write_musicxml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))   # corpus/challenge/rhythm
CLEAN_DPI = 300


def run(cmd, timeout=600):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def lyric_text_check(score, pdf):
    """fraction of truth syllables found in the vector PDF text (as corpus/synthetic does)"""
    rc, out, err = run(['pdftotext', '-layout', pdf, '-'])
    text = re.sub(r'\s+', ' ', out)
    flat = text.replace('-', '').replace(' ', '')
    syls = []
    for pid, vk, vs in voices_with_lyrics(score):
        for m in score.part(pid).measures:
            for ev in m.get(vk, []):
                for ly in ev.lyrics.values():
                    syls.append(ly.text)
    if not syls:
        return None
    found = sum(1 for s_ in syls if not re.sub(r'[\W_]+', '', s_) or re.sub(r'[\W_]+', '', s_) in flat or s_ in text)
    return round(found / len(syls), 4)


def image_only(pdf):
    rc, fonts, _ = run(['pdffonts', pdf])
    font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
    rc, imgl, _ = run(['pdfimages', '-list', pdf])
    n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
    rc, txt, _ = run(['pdftotext', pdf, '-'])
    rc, info, _ = run(['pdfinfo', pdf])
    pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    return {'image_only': not font_lines and n_imgs == pages and not txt.strip(), 'fonts': font_lines,
            'images': n_imgs, 'pages': pages, 'text_chars': len(txt.strip())}


def build_item(item: dict, keep_work=False):
    t0 = time.time()
    iid = item['id']
    outdir = os.path.join(ROOT, iid)
    workdir = os.path.join(ROOT, '_work', iid)
    shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        os.remove(os.path.join(outdir, f))
    log = {'id': iid}
    try:
        score, layout, opts = item['make']()
        sanitize_ties(score)
        fix_unbalanced_slurs(score)
        compute_extenders(score)
        check(score)
        truth = os.path.join(outdir, 'truth.musicxml')
        write_musicxml(score, truth)
        xsd = V.xsd_validate(truth)
        ly = os.path.join(workdir, 'engraving.ly')
        open(ly, 'w', encoding='utf-8').write(LilyWriter(score, layout, opts).document())
        rc, warns, err, pdf, mid, evp = V.lilypond(ly, workdir)
        if rc != 0:
            raise RuntimeError('lilypond failed: ' + err[-1500:])
        eng = V.compare_engraving(score, layout, evp)
        midi = V.compare_midi(score, mid)
        m21 = V.compare_music21(score, truth)
        lyr = lyric_text_check(score, pdf)
        rc_, info, _ = run(['pdfinfo', pdf])
        vec_pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
        want_pages = len(item.get('pages_expected', [])) or None
        bad_warn = [w for w in warns if not re.search(r'already have slur', w)]
        log['validation'] = {'xsd': xsd, 'engraving_vs_truth': eng, 'midi': midi, 'music21_truth_reparse': m21,
                             'lyric_text_found_in_engraving': lyr, 'lilypond_warnings': warns,
                             'vector_pages': vec_pages}
        problems = []
        if not xsd['ok']:
            problems.append('xsd')
        if not eng['ok']:
            problems.append('engraving dump != truth')
        if not midi['ok']:
            problems.append('midi != truth')
        if not m21['ok']:
            problems.append('music21 reparse != truth')
        if bad_warn:
            problems.append('lilypond warnings: ' + '; '.join(bad_warn[:5]))
        if lyr is not None and lyr < 1.0:
            problems.append(f'lyric text found {lyr}')
        if item.get('pages') and vec_pages != item['pages']:
            problems.append(f'pages {vec_pages} != {item["pages"]}')
        if problems:
            raise RuntimeError('verification failed: ' + ' | '.join(problems) + '\n' +
                               json.dumps(log['validation'], default=str)[:6000])
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        # clean raster
        pages = S.render_pages(pdf, CLEAN_DPI, workdir)
        S.save_pdf([Image.fromarray(p) for p in pages], CLEAN_DPI, os.path.join(outdir, 'clean.pdf'), fmt='png')
        files = {'clean.pdf': {'dpi': CLEAN_DPI, 'pages': len(pages), 'ops': [], 'note': 'undamaged raster render'}}
        files['clean.pdf'].update(image_only(os.path.join(outdir, 'clean.pdf')))
        # damaged variants
        degr = {}
        for fname, Vv in item['variants'].items():
            pg = S.render_pages(pdf, Vv['dpi'], workdir)
            imgs, out_dpi, oplog = S.apply_variant(pg, Vv)
            outp = os.path.join(outdir, fname)
            fmt = Vv.get('format', 'jpeg')
            S.save_pdf(imgs, out_dpi, outp, fmt='png' if fmt in ('png', 'png1') else 'jpeg',
                       quality=Vv.get('jpeg', 75), jpeg_passes=Vv.get('jpeg_passes', 1))
            io_ = image_only(outp)
            if not io_['image_only']:
                raise RuntimeError(f'{fname} is not image-only: {io_}')
            degr[fname] = {'seed': Vv['seed'], 'render_dpi': Vv['dpi'], 'dpi': out_dpi,
                           'color': Vv.get('color', 'gray'), 'format': fmt,
                           'jpeg_quality': Vv.get('jpeg') if fmt == 'jpeg' else None,
                           'jpeg_passes': Vv.get('jpeg_passes', 1) if fmt == 'jpeg' else None,
                           'ops': Vv['ops'], 'tags': S.describe(Vv), 'output_pages': io_['pages'],
                           'pixel_size': list(imgs[0].size), 'image_mode': imgs[0].mode,
                           'bytes': os.path.getsize(outp), 'image_only_check': io_, 'op_log': oplog}
        # metadata
        lyr_parts = [{'part': score.part(pid).name, 'voice': vk, 'verses': len(vs)}
                     for pid, vk, vs in voices_with_lyrics(score)]
        exp = dict(item['expected'])
        exp.setdefault('lyrics', lyr_parts)
        exp['measures'] = len(score.measures)
        exp['first_measure_number'] = score.measures[0].number
        main = degr['scan.pdf']
        meta = {
            'id': iid, 'category': 'rhythm', 'title': item['title'],
            'composer': score.composer, 'lyricist': score.lyricist,
            'edge_cases': item['edge_cases'],
            'expected': exp,
            'truth_limitations': item.get('truth_limitations', []),
            'degradations': degr,
            'dpi': main['dpi'],
            'license': item['license'],
            'source': item['source'],
            'pages': vec_pages,
            'files': {'truth': 'truth.musicxml', 'engraving': 'engraving.ly', 'clean': 'clean.pdf',
                      'scan': 'scan.pdf', 'scan_mild': 'scan-mild.pdf' if 'scan-mild.pdf' in degr else None,
                      'scan_severe': 'scan-severe.pdf' if 'scan-severe.pdf' in degr else None,
                      'attribution': 'ATTRIBUTION.txt'},
            'clean': files['clean.pdf'],
            'validation': {
                'truth_xsd_valid': xsd['ok'],
                'engraving_event_dump_matches_truth': eng['ok'],
                'engraving_events_compared': sum(v['n_expected'] for v in eng['voices'].values()),
                'lyric_events_compared': sum(v.get('n_expected', 0) for v in eng['lyrics'].values()),
                'time_signatures_compared': sum(v['n_expected'] for v in eng['timesig'].values()),
                'midi_attacks_match_truth': midi['ok'], 'midi_attacks': midi['expected_attacks'],
                'midi_grace_notes_excluded': midi['grace_notes'],
                'music21_reparse_matches_model': m21['ok'],
                'lyric_text_found_in_engraving': lyr,
                'lilypond_warnings': warns,
                'method': 'LilyPond event-dump engraver (rsynth/dump.ly) compared with the model the truth is '
                          'written from: every note/rest/multi-bar rest (onset, pitch, notated type, dots, '
                          'tuplet scale), grace offsets, ties, beam starts/stops, slurs, fermatas, lyric '
                          'syllables/hyphens/extenders, bar numbers/measure positions and time signatures; '
                          'plus MIDI attack multiset and a music21 re-parse of truth.musicxml.',
            },
            'generator': 'corpus/challenge/rhythm/_tools/run_all.py (rsynth/items.py, build.py, scan.py)',
        }
        with open(os.path.join(outdir, 'meta.json'), 'w') as f:
            json.dump(meta, f, indent=2, default=str, ensure_ascii=False)
        with open(os.path.join(outdir, 'ATTRIBUTION.txt'), 'w') as f:
            f.write(item['attribution'].strip() + '\n')
        log['ok'] = True
        log['meta'] = meta
    except Exception as e:
        log['ok'] = False
        log['error'] = repr(e)[:8000]
        log['trace'] = traceback.format_exc()[-4000:]
    log['seconds'] = round(time.time() - t0, 1)
    if not keep_work and log.get('ok'):
        shutil.rmtree(workdir, ignore_errors=True)
    return log
