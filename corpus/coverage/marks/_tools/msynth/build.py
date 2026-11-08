"""Build one coverage/marks item:
  engraving.ly   model -> LilyPond (manual beams, explicit system breaks)
  verification   LilyPond event + grob dump == model, stems read back, MIDI attacks == truth,
                 music21 re-parse == model, xmllint XSD, symbol counts from the truth XML == model
  truth.musicxml model (+ engraved stem directions) -> MusicXML 4.0
  clean.pdf      undamaged 300 dpi raster (image-only)
  scan.pdf       typical office scan (200-300 dpi, slight skew, noise, JPEG)
  scan-severe.pdf heavy damage (params + seed in meta.json)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import traceback
from collections import Counter

from PIL import Image

from . import scan as S
from . import verify as V
from .count import __doc__ as COUNT_DOC
from .count import count_truth
from .lily import LilyWriter
from .model import DYNAMICS, staff_events
from .mxl import __doc__ as MXL_DOC
from .mxl import write_musicxml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))   # corpus/coverage/marks
CLEAN_DPI = 300
FAMILY = 'marks'
MARK_TAGS = {'staccato': 'staccato', 'staccatissimo': 'staccatissimo', 'accent': 'accent', 'tenuto': 'tenuto',
             'marcato': 'marcato', 'portato': 'x-portato', 'fermata': 'fermata', 'trill': 'trill',
             'mordent': 'mordent', 'prall': 'x-inverted-mordent', 'turn': 'turn', 'reverseturn': 'x-inverted-turn'}
DYN_STD = {'pp', 'p', 'mp', 'mf', 'f', 'ff', 'sfz'}


def run(cmd, timeout=600):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


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


def model_counts(score):
    """marks-family tags counted from the model (cross-check of the truth counter)"""
    c = Counter()
    for p, st in score.staves():
        for i, t, ev in staff_events(score, st):
            if ev.kind == 'clef':
                continue
            for typ, pl in ev.marks:
                c[MARK_TAGS[typ]] += 1
            c['breath'] += ev.breath
            c['arpeggio'] += ev.arpeggio and ev.kind == 'note'
            c['fingering'] += len(ev.fingering)
            c['slur'] += ev.slur_start
            c['tie'] += len(ev.tie_start)
            for d in ev.dynamics:
                c[f'dyn-{d}' if d in DYN_STD else f'x-dyn-{d}'] += 1
            for w in ev.wedges:
                if w in ('crescendo', 'diminuendo'):
                    c['hairpin-cresc' if w == 'crescendo' else 'hairpin-dim'] += 1
            for pd in ev.pedal:
                c['pedal' if pd == 'start' else 'x-pedal-release'] += 1
            c['text-expression'] += len(ev.words)
            if ev.tempo:
                c['tempo-mark'] += 1 if ev.tempo['text'] else 0
                c['metronome'] += 1 if ev.tempo['bpm'] else 0
        c['chord-symbol'] += len(p.chords) if st.number == 1 else 0
    c['rehearsal-mark'] = sum(1 for m in score.measures if m.mark)
    return {k: v for k, v in c.items() if v}


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
        score = item['make']()
        ly = os.path.join(workdir, 'engraving.ly')
        open(ly, 'w', encoding='utf-8').write(LilyWriter(score, item.get('lily', {})).document())
        rc, warns, err, pdf, mid, evp = V.lilypond(ly, workdir)
        if rc != 0:
            raise RuntimeError('lilypond failed: ' + err[-2500:])
        stems = V.read_engraved(score, evp)
        truth = os.path.join(outdir, 'truth.musicxml')
        score.rights = 'CC0 1.0 Universal (public domain dedication)'
        write_musicxml(score, truth)
        xsd = V.xsd_validate(truth)
        eng = V.compare_engraving(score, evp)
        midi = V.compare_midi(score, mid)
        m21 = V.compare_music21(score, truth)
        rc_, info, _ = run(['pdfinfo', pdf])
        vec_pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
        counts = count_truth(truth, vec_pages)
        mc = model_counts(score)
        cross = {k: (mc.get(k, 0), counts.get(k, 0)) for k in set(mc) | {t for t in counts if t in set(mc) or
                 t in MARK_TAGS.values() or t.startswith(('dyn-', 'x-dyn-', 'hairpin-'))}}
        cross_bad = {k: v for k, v in cross.items() if v[0] != v[1]}
        log['validation'] = {'xsd': xsd, 'stems': stems, 'engraving_vs_truth': eng, 'midi': midi,
                             'music21_truth_reparse': m21, 'lilypond_warnings': warns, 'vector_pages': vec_pages,
                             'counts_truth_vs_model': {'ok': not cross_bad, 'mismatch': cross_bad}}
        problems = []
        if not xsd['ok']:
            problems.append('xsd: ' + xsd['message'])
        if not stems['ok']:
            problems.append('stems')
        if not eng['ok']:
            problems.append('engraving dump != model')
        if not midi['ok']:
            problems.append('midi != truth')
        if not m21['ok']:
            problems.append('music21 reparse != truth')
        if warns:
            problems.append('lilypond warnings: ' + '; '.join(warns[:5]))
        if cross_bad:
            problems.append(f'truth counts != model counts {cross_bad}')
        if item.get('pages') and vec_pages != item['pages']:
            problems.append(f'pages {vec_pages} != {item["pages"]}')
        if problems:
            raise RuntimeError('verification failed: ' + ' | '.join(problems) + '\n' +
                               json.dumps(log['validation'], default=str)[:8000])
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        pages = S.render_pages(pdf, CLEAN_DPI, workdir)
        S.save_pdf([Image.fromarray(p) for p in pages], CLEAN_DPI, os.path.join(outdir, 'clean.pdf'), fmt='png')
        clean = {'dpi': CLEAN_DPI, 'pages': len(pages), 'ops': [], 'format': 'png',
                 'note': 'undamaged raster render of the engraving'}
        clean.update(image_only(os.path.join(outdir, 'clean.pdf')))
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
                           'ops': Vv['ops'], 'tags': S.describe(Vv), 'description': Vv.get('description', ''),
                           'output_pages': io_['pages'], 'pixel_size': list(imgs[0].size),
                           'image_mode': imgs[0].mode, 'bytes': os.path.getsize(outp), 'image_only_check': io_,
                           'op_log': oplog}
        symbols = sorted(counts)
        meta = {
            'id': iid, 'family': FAMILY, 'title': item['title'],
            'symbols': symbols,
            'focus_symbols': item['focus'],
            'layout': item['layout'],
            'expected': {'parts': [p.name for p in score.parts], 'must_not_split': item['must_not_split'],
                         'measures': len(score.measures), 'staves': sum(len(p.staves) for p in score.parts),
                         'notes': item['expected_notes']},
            'counts': counts,
            'degradations': degr,
            'clean': clean,
            'dpi': degr['scan.pdf']['dpi'],
            'pages': vec_pages,
            'license': 'CC0',
            'license_detail': 'CC0-1.0: music composed for this corpus; engraving, truth and scans dedicated to '
                              'the public domain',
            'composer': score.composer,
            'notes': item.get('notes', []) + TRUTH_NOTES,
            'counting_rules': COUNTING_RULES,
            'files': {'truth': 'truth.musicxml', 'engraving': 'engraving.ly', 'clean': 'clean.pdf',
                      'scan': 'scan.pdf', 'scan_severe': 'scan-severe.pdf', 'attribution': 'ATTRIBUTION.txt'},
            'validation': {
                'truth_xsd_valid': xsd['ok'],
                'music21_parses_and_matches': m21['ok'],
                'music21_marks_seen': m21['music21_marks_seen'],
                'engraving_event_dump_matches_truth': eng['ok'],
                'engraving_events_compared': sum(v['n_expected'] for v in eng['voices'].values())
                + eng['score']['n_expected'] + sum(v['n_expected'] for v in eng['chords'].values()),
                'printed_grob_census': {k: v['printed'] for k, v in eng['grobs']['counts'].items() if v['printed']},
                'printed_texts': eng['grobs']['printed_texts'],
                'accidentals_match': eng['accidentals']['ok'],
                'stems_read_from_engraving': stems['stems_read'],
                'mark_and_fingering_sides_read_from_engraving': stems['directions_read'],
                'midi_attacks_match_truth': midi['ok'], 'midi_attacks': midi['expected_attacks'],
                'truth_counts_match_model': not cross_bad,
                'lilypond_warnings': warns,
                'method': 'LilyPond 2.24 event/grob dump (_tools/msynth/dump.ly) compared with the model the truth '
                          'is written from: every note/rest (onset, pitch, type, dots), tie, beam, slur, '
                          'articulation/ornament/fermata (with forced direction), dynamic, hairpin start/stop, pedal '
                          'event, fingering (incl. inside chords), text script, arpeggio, breath mark, tempo and '
                          'rehearsal-mark event and chord-name pitch content; printed grob counts per kind; printed '
                          'accidentals; stem directions read from the engraving; MIDI attacks; music21 re-parse; '
                          'xmllint XSD; symbol counts recomputed from truth.musicxml == model.',
            },
            'generator': 'corpus/coverage/marks/_tools/run_all.py (msynth/items.py, build.py)',
        }
        with open(os.path.join(outdir, 'meta.json'), 'w') as f:
            json.dump(meta, f, indent=2, default=str, ensure_ascii=False)
        with open(os.path.join(outdir, 'ATTRIBUTION.txt'), 'w') as f:
            f.write(ATTRIBUTION.format(title=item['title'], id=iid).strip() + '\n')
        log['ok'] = True
        log['meta'] = meta
    except Exception as e:
        log['ok'] = False
        log['error'] = repr(e)[:12000]
        log['trace'] = traceback.format_exc()[-4000:]
    log['seconds'] = round(time.time() - t0, 1)
    if not keep_work and log.get('ok'):
        shutil.rmtree(workdir, ignore_errors=True)
    return log


def _rules(doc):
    out = []
    for line in doc.split('\n')[3:]:
        if not line.strip():
            continue
        if line.startswith('  ') and not line.startswith('   ') or not out:
            out.append(line.strip())
        else:
            out[-1] += ' ' + line.strip()
    return out


COUNTING_RULES = _rules(COUNT_DOC)

TRUTH_NOTES = [
    'Truth encoding: ' + ' '.join(MXL_DOC.split('\n', 2)[2].split()),
    'placement="above|below" of every articulation, ornament and fingering, fermata upright/inverted and '
    'marcato (strong-accent) type up/down are the sides LilyPond actually engraved (read back from the final '
    'grob directions), not a convention; MusicXML cannot express the exact offset or stacking order of '
    'several marks on one note, nor the horizontal position of a fingering inside a chord.',
    'Hairpin extents: LilyPond ends a hairpin at the note carrying \\! or the next dynamic; the truth puts '
    '<wedge type="stop"/> before that note, so a hairpin "to the barline" is encoded as ending on the next '
    'note.  Hairpins crossing a system break are one wedge in the truth.',
]

ATTRIBUTION = """
{title}
coverage/marks item {id}

Music composed for the OMR synthetic coverage corpus (2026) and dedicated to the public domain
under CC0 1.0 Universal (https://creativecommons.org/publicdomain/zero/1.0/).  Engraving
(LilyPond 2.24), truth.musicxml and all scan images are generated from the same source and are
likewise CC0.  No third-party material is included.
"""
