"""Build one coverage/rests item (copied from corpus/challenge/rhythm/_tools/rsynth/build.py and
adapted to the coverage meta format):
  engraving.ly   (model -> LilyPond, explicit beams / breaks / rest positions)
  LilyPond run   (with the event-dump engraver crest/dump.ly)
  stems          (engraved stem directions read back into the model -> <stem> in the truth)
  truth.musicxml (model -> MusicXML 4.0, XSD-validated)
  verification   (event dump == model; rest vertical positions == truth display-step/octave;
                  MIDI attacks == truth; music21 re-parse of truth == model)
  counts         (taxonomy tag counts parsed from truth.musicxml, cross-checked with the model)
  clean.pdf      (undamaged 300 dpi raster, image-only)
  scan.pdf, scan-severe.pdf (damaged image-only PDFs, see scan.py; params + seed in meta.json)
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
from .counts import count_truth, model_rest_counts
from .model import check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voices_with_lyrics
from .mxl import write_musicxml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))   # corpus/coverage/rests
FAMILY = 'rests'
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
    timing = {}
    try:
        score, layout, opts = item['make']()
        sanitize_ties(score)
        fix_unbalanced_slurs(score)
        compute_extenders(score)
        check(score)
        ly = os.path.join(workdir, 'engraving.ly')
        open(ly, 'w', encoding='utf-8').write(LilyWriter(score, layout, opts).document())
        t1 = time.time()
        rc, warns, err, pdf, mid, evp = V.lilypond(ly, workdir)
        timing['lilypond_s'] = round(time.time() - t1, 2)
        if rc != 0:
            raise RuntimeError('lilypond failed: ' + err[-1500:])
        stems = V.assign_stems(score, evp)
        auto_rests = V.assign_auto_rest_positions(score, evp)
        truth = os.path.join(outdir, 'truth.musicxml')
        write_musicxml(score, truth)
        xsd = V.xsd_validate(truth)
        eng = V.compare_engraving(score, layout, evp)
        restpos = V.check_rest_layout(score, evp)
        midi = V.compare_midi(score, mid)
        m21 = V.compare_music21(score, truth)
        lyr = lyric_text_check(score, pdf)
        rc_, info, _ = run(['pdfinfo', pdf])
        vec_pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
        bad_warn = [w for w in warns if not re.search(r'already have slur', w)]
        counts = count_truth(truth, vec_pages)
        mcounts = model_rest_counts(score)
        count_diff = {k: (v, counts.get(k, 0)) for k, v in mcounts.items() if counts.get(k, 0) != v}
        for k in ('rest-whole-bar', 'rest-multibar', 'x-rest-in-tuplet', 'x-rest-fermata'):
            if k in counts and k not in mcounts:
                count_diff[k] = (0, counts[k])
        log['validation'] = {'xsd': xsd, 'engraving_vs_truth': eng, 'rest_positions': restpos, 'stems': stems,
                             'rests_moved_by_layout': auto_rests,
                             'midi': midi, 'music21_truth_reparse': m21, 'lyric_text_found_in_engraving': lyr,
                             'lilypond_warnings': warns, 'vector_pages': vec_pages,
                             'model_vs_truth_rest_counts': {'ok': not count_diff, 'diff': count_diff}}
        problems = []
        if not xsd['ok']:
            problems.append('xsd')
        if not eng['ok']:
            problems.append('engraving dump != truth')
        if not restpos['ok']:
            problems.append('rest positions != truth')
        if not stems['ok']:
            problems.append('stem read-back incomplete')
        if not midi['ok']:
            problems.append('midi != truth')
        if not m21['ok']:
            problems.append('music21 reparse != truth')
        if count_diff:
            problems.append(f'rest counts model != truth {count_diff}')
        if bad_warn:
            problems.append('lilypond warnings: ' + '; '.join(bad_warn[:5]))
        if lyr is not None and lyr < 1.0:
            problems.append(f'lyric text found {lyr}')
        if item.get('pages') and vec_pages != item['pages']:
            problems.append(f'pages {vec_pages} != {item["pages"]}')
        for tag, n in item.get('min_counts', {}).items():
            if counts.get(tag, 0) < n:
                problems.append(f'count {tag} = {counts.get(tag, 0)} < required {n}')
        if problems:
            raise RuntimeError('verification failed: ' + ' | '.join(problems) + '\n' +
                               json.dumps(log['validation'], default=str)[:6000])
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        # clean raster
        t1 = time.time()
        pages = S.render_pages(pdf, CLEAN_DPI, workdir)
        S.save_pdf([Image.fromarray(p) for p in pages], CLEAN_DPI, os.path.join(outdir, 'clean.pdf'), fmt='png')
        clean = {'dpi': CLEAN_DPI, 'pages': len(pages), 'ops': [], 'note': 'undamaged raster render (PNG, gray)',
                 'pixel_size': [int(pages[0].shape[1]), int(pages[0].shape[0])],
                 'bytes': os.path.getsize(os.path.join(outdir, 'clean.pdf'))}
        clean.update(image_only(os.path.join(outdir, 'clean.pdf')))
        if not clean['image_only']:
            raise RuntimeError(f'clean.pdf is not image-only: {clean}')
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
                           'ops': Vv['ops'], 'tags': S.describe(Vv), 'severity': Vv.get('severity'),
                           'output_pages': io_['pages'], 'pixel_size': list(imgs[0].size),
                           'image_mode': imgs[0].mode, 'bytes': os.path.getsize(outp), 'image_only_check': io_,
                           'op_log': oplog}
        timing['raster_and_damage_s'] = round(time.time() - t1, 2)
        # metadata
        nmeas = len(score.measures)
        drawn = nmeas - sum(max(0, ev.multirest - 1) for p_ in score.parts[:1] for mm in p_.measures
                            for evs in mm.values() for ev in evs if ev.multirest)
        exp = {'parts': item['expected']['parts'], 'must_not_split': item['expected']['must_not_split']}
        for k, v in item['expected'].items():
            exp.setdefault(k, v)
        exp['measures'] = nmeas
        exp['bars_drawn'] = drawn
        exp['first_measure_number'] = score.measures[0].number
        exp['systems'] = 1 + sum(1 for m in score.measures if m.new_system or m.new_page)
        main = degr['scan.pdf']
        meta = {
            'id': iid, 'family': FAMILY, 'title': item['title'],
            'symbols': sorted(counts),
            'layout': item['layout'],
            'expected': exp,
            'counts': counts,
            'degradations': degr,
            'dpi': main['dpi'],
            'pages': vec_pages,
            'license': 'CC0',
            'license_detail': 'CC0-1.0: music composed for this corpus; engraving, truth and scans generated '
                              'by corpus/coverage/rests/_tools',
            'composer': score.composer,
            'focus': item['focus'],
            'notes': item.get('notes', []),
            'files': {'truth': 'truth.musicxml', 'engraving': 'engraving.ly', 'clean': 'clean.pdf',
                      'scan': 'scan.pdf', 'scan_severe': 'scan-severe.pdf', 'attribution': 'ATTRIBUTION.txt'},
            'clean': clean,
            'validation': {
                'truth_xsd_valid': xsd['ok'],
                'engraving_event_dump_matches_truth': eng['ok'],
                'engraving_events_compared': sum(v['n_expected'] for v in eng['voices'].values()),
                'time_signatures_compared': sum(v['n_expected'] for v in eng['timesig'].values()),
                'rest_positions_match_truth': restpos['ok'],
                'rests_position_checked': restpos['rests_checked'],
                'rests_with_explicit_display_position': restpos['explicit_positions'],
                'rests_with_display_position_read_from_layout': restpos['layout_positions'],
                'stems_read_from_engraving': stems['stems'],
                'midi_attacks_match_truth': midi['ok'], 'midi_attacks': midi['expected_attacks'],
                'music21_reparse_matches_model': m21['ok'],
                'rest_counts_model_equal_truth': not count_diff,
                'lilypond_warnings': warns,
                'method': 'LilyPond event-dump engraver (_tools/crest/dump.ly) compared with the model the truth '
                          'is written from: every note/rest/multi-bar rest (onset, pitch, notated type, dots, '
                          'tuplet scale), ties, beam starts/stops, slurs, articulations/fermatas, bar numbers, '
                          'measure positions and time signatures; post-layout read-back of every Rest / '
                          'MultiMeasureRest grob (staff-position and Y extent vs. the truth display-step/'
                          'display-octave) and of every Stem direction (written to <stem>); LilyPond MIDI attack '
                          'multiset; music21 re-parse of truth.musicxml; xmllint against the MusicXML 4.0 XSD; '
                          'counts parsed from truth.musicxml and cross-checked with the model for rest tags.',
            },
            'build_timing': timing,
            'generator': 'corpus/coverage/rests/_tools/run_all.py (crest/items.py, catalog.py, build.py, scan.py)',
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
