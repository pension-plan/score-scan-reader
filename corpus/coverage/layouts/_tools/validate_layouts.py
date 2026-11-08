#!/usr/bin/env python3
"""Independent validation of corpus/coverage/layouts/<id>/ items.

Reuses the challenge-corpus validator (chval.py = unmodified copy of corpus/challenge/_validate/validate.py):
  * every truth*.musicxml passes the MusicXML 4.0 XSD; music21 parses it
  * every PDF opens, renders, is image-only (no fonts, no text, >= 1 image per page)
  * engraving.ly re-rendered from scratch with LilyPond 2.24: MIDI attacks and lyric syllables == truth,
    clean.pdf pixel-compared with the fresh raster (ink overlap >= 0.97)
and adds coverage-suite checks:
  * meta.json keys {id, family, title, symbols, layout, expected{parts, must_not_split}, counts,
    degradations, dpi, pages, license}; layout tag from the taxonomy; symbols == keys of counts and
    canonical or x- prefixed; expected.parts == truth part names
  * counts re-computed from truth.musicxml with count_symbols.py == meta.counts
  * scan.pdf and scan-severe.pdf present with seed + params; page counts == meta.pages

usage: /Users/d.sloane/music/.venv/bin/python validate_layouts.py [--jobs N] [--out report.json]
"""
import argparse
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chval  # noqa: E402
from count_symbols import count_all  # noqa: E402

FAMILY_DIR = HERE.parent
chval.CH = FAMILY_DIR.parent           # corpus/coverage  (render_check uses CH / cat / id)
LAYOUTS = {'melody', 'melody-lyrics', 'piano', 'voice-piano', 'choir-closed-satb', 'choir-open-satb', 'choir-sab',
           'choir-ttbb', 'choir-ssaa', 'choir-piano', 'organ', 'string-quartet', 'orchestral', 'lead-sheet',
           'hymnal-stanzas', 'divisi', 'cross-staff', 'two-voices-one-staff-instrument', 'percussion-none'}
TAXONOMY = set('''note-breve note-whole note-half note-quarter note-8th note-16th note-32nd note-64th dot double-dot chord
beam flag stem-up stem-down ledger-above ledger-below grace grace-slash cue-note tremolo rest-breve rest-whole rest-half
rest-quarter rest-8th rest-16th rest-32nd rest-64th rest-dotted rest-whole-bar rest-multibar clef-treble clef-bass
clef-alto clef-tenor clef-soprano clef-treble-8vb clef-treble-8va clef-bass-8vb clef-change key-0 key-change acc-sharp
acc-flat acc-natural acc-double-sharp acc-double-flat acc-courtesy ottava-8va ottava-8vb ottava-15ma time-2-4 time-3-4
time-4-4 time-2-2 time-3-2 time-6-8 time-9-8 time-12-8 time-5-4 time-5-8 time-7-8 time-common time-cut time-change
pickup tuplet-3 tuplet-2 tuplet-5 tuplet-6 tuplet-7 tuplet-nested tie tie-across-system slur staccato staccatissimo
accent tenuto marcato fermata trill mordent turn arpeggio breath dyn-pp dyn-p dyn-mp dyn-mf dyn-f dyn-ff dyn-sfz
hairpin-cresc hairpin-dim pedal fingering text-expression tempo-mark metronome rehearsal-mark chord-symbol
barline-double barline-final repeat-start repeat-end volta-1 volta-2 segno coda dc ds fine system-break page-break
multi-page lyrics lyrics-multi-verse lyrics-melisma lyrics-extender lyrics-hyphen lyrics-elision lyrics-non-ascii
stanza-text'''.split()) | {f'key-s{i}' for i in range(1, 8)} | {f'key-f{i}' for i in range(1, 8)}


def meta_check(meta, iid, scans, truth_parts, truth_path):
    P, W = [], []
    for k in ('id', 'family', 'title', 'symbols', 'layout', 'expected', 'counts', 'degradations', 'dpi', 'pages',
              'license'):
        if k not in meta or meta[k] in (None, '', [], {}):
            P.append(f'missing/empty meta.{k}')
    if meta.get('id') != iid:
        P.append(f'meta.id {meta.get("id")!r} != folder {iid!r}')
    if meta.get('family') != 'layouts':
        P.append(f'meta.family {meta.get("family")!r} != layouts')
    if meta.get('layout') not in LAYOUTS:
        P.append(f'unknown layout tag {meta.get("layout")!r}')
    if meta.get('license') != 'CC0':
        P.append('license must be "CC0"')
    ex = meta.get('expected') or {}
    if not isinstance(ex.get('parts'), list) or not ex['parts']:
        P.append('expected.parts missing')
    elif truth_parts is not None and ex['parts'] != truth_parts:
        P.append(f'expected.parts {ex["parts"]} != truth {truth_parts}')
    if not isinstance(ex.get('must_not_split'), bool):
        P.append('expected.must_not_split not a bool')
    syms, counts = meta.get('symbols') or [], meta.get('counts') or {}
    if set(syms) != set(counts):
        P.append(f'symbols != keys(counts): {sorted(set(syms) ^ set(counts))}')
    bad = [s for s in syms if s not in TAXONOMY and not s.startswith('x-')]
    if bad:
        P.append(f'non-taxonomy symbol tags: {bad}')
    if any((not isinstance(v, int)) or v <= 0 for v in counts.values()):
        P.append('counts must be positive integers')
    recount = count_all(truth_path)
    if recount != counts:
        diff = {k: (counts.get(k), recount.get(k)) for k in set(counts) | set(recount) if counts.get(k) != recount.get(k)}
        P.append(f'meta.counts != recount of truth: {diff}')
    deg = meta.get('degradations') or {}
    for s in ('scan.pdf', 'scan-severe.pdf'):
        if s not in scans:
            P.append(f'missing {s}')
        rec = deg.get(s) or {}
        if 'seed' not in rec or not rec.get('params'):
            P.append(f'degradations[{s}] lacks seed/params')
    return P, W


def check(task):
    iid, scratch = task
    d = FAMILY_DIR / iid
    r = {'id': iid, 'problems': [], 'warnings': []}
    P = r['problems']
    for f in ('engraving.ly', 'truth.musicxml', 'clean.pdf', 'scan.pdf', 'scan-severe.pdf', 'meta.json',
              'ATTRIBUTION.txt'):
        if not (d / f).exists() or not (d / f).stat().st_size:
            P.append(f'missing {f}')
    scans = sorted(p.name for p in d.glob('scan*.pdf'))
    code, out, err = chval.sh(['xmllint', '--noout', '--nonet', '--schema', str(chval.XSD), str(d / 'truth.musicxml')], 120)
    r['xsd'] = code == 0
    if code != 0:
        P.append('truth fails XSD: ' + err[:300])
    truth = chval.truth_events(d / 'truth.musicxml')
    r['truth'] = {k: truth[k] for k in ('parts', 'n_notes', 'n_rests', 'measures')}
    code, out, err = chval.sh([sys.executable, '-c', 'import sys,music21;s=music21.converter.parse(sys.argv[1],'
                               'format="musicxml",forceSource=True);print(len(s.parts),len(list(s.recurse().notes)))',
                               str(d / 'truth.musicxml')], 600)
    r['music21'] = out.strip() if code == 0 else 'FAIL'
    if code != 0:
        P.append('music21 cannot parse truth')
    meta = json.loads((d / 'meta.json').read_text())
    p2, w2 = meta_check(meta, iid, scans, truth['parts'], d / 'truth.musicxml')
    P.extend(p2)
    r['warnings'].extend(w2)
    r['pdfs'] = {}
    for pdf in sorted(d.glob('*.pdf')):
        pr = chval.pdf_check(pdf, scratch)
        r['pdfs'][pdf.name] = {k: pr.get(k) for k in ('ok', 'pages', 'image_only', 'image_ppi', 'image_px')}
        if not pr['ok']:
            P.append(f'{pdf.name} not a valid image-only PDF: {pr}')
        if pr['pages'] != meta.get('pages'):
            P.append(f'{pdf.name} has {pr["pages"]} pages, meta.pages={meta.get("pages")}')
    rc = chval.render_check(('layouts', iid, scratch))
    r['render'] = {'midi': {k: rc.get('midi', {}).get(k) for k in ('truth_attacks', 'midi_attacks', 'missing', 'extra',
                                                                    'truth_syllables', 'midi_syllables', 'lyr_missing',
                                                                    'lyr_extra', 'notes_exact', 'lyrics_ok')},
                   'clean_min_overlap': rc.get('clean', {}).get('min_overlap'),
                   'lilypond_warnings': rc.get('lilypond_warnings')}
    if not rc.get('ok'):
        P.append(f'render check failed: {r["render"]} {rc.get("error", "")}')
    elif not rc['midi']['notes_exact']:
        P.append('MIDI attacks not exact')
    r['ok'] = not P
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=24)
    ap.add_argument('--out', default=str(FAMILY_DIR / '_logs' / 'validation-report.json'))
    ap.add_argument('--scratch', default=os.environ.get('VALIDATE_SCRATCH', str(FAMILY_DIR / '_work' / '_validate')))
    a = ap.parse_args()
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    ids = sorted(p.name for p in FAMILY_DIR.iterdir() if p.is_dir() and not p.name.startswith('_'))
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        res = list(ex.map(check, [(i, a.scratch) for i in ids]))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    rep = {'items': len(res), 'ok': sum(r['ok'] for r in res), 'results': res}
    Path(a.out).write_text(json.dumps(rep, indent=1, default=str))
    for r in res:
        print(('OK  ' if r['ok'] else 'ERR ') + r['id'], '' if r['ok'] else r['problems'][:3])
    print(f"{rep['ok']}/{rep['items']} ok -> {a.out}")


if __name__ == '__main__':
    main()
