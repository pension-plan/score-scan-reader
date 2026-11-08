#!/usr/bin/env python3
"""Write corpus/challenge/manifest.json (all category manifests merged) and corpus/challenge/README.md.

  python build_index.py [--analysis mvp/work/eval-challenge-baseline.analysis.json]

Inputs: <category>/manifest.json (arrays of meta objects), _validate/report.json (validate.py),
optionally the eval analysis (analyze_eval.py) for the baseline section.
Each merged entry is the item's meta object plus:
  path            "<category>/<id>"
  scan_files      scan PDFs present (scan.pdf, scan-mild.pdf, scan-severe.pdf)
  eval_ids        ids used by `eval.mjs --set challenge` ("<category>/<id>/<variant>")
  damage_families heuristic damage-family tags per scan file (damage.py)
  validation_challenge  result of _validate/validate.py for this item
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH = HERE.parent
ROOT = CH.parent.parent
sys.path.insert(0, str(HERE))
import damage  # noqa: E402

CATS = ['voices', 'rhythm', 'pitch', 'lyrics', 'layout', 'degradation']
CAT_DESC = {
    'voices': 'Voice separation: closed SATB/SAB/TTBB/SSAA scores with two voices per staff that must become separate parts, crossings, unisons, "a 2"/"unis.", divisi, cross-staff voices, choir + piano (piano must stay one part).',
    'rhythm': 'Rhythm and duration: tuplets of every kind, ties across barlines/systems/pages, double dots, meter changes and irregular meters, multi-bar rests, every rest value, grace notes, fermatas, dense 32nd/64th runs.',
    'pitch': 'Pitch spelling: 7-sharp/7-flat keys and key changes, clef changes (alto/tenor/treble/bass, mid-bar), accidental carry/cancel rules, double sharps/flats, ledger-line extremes, 8va/8vb, enharmonic respelling, chromatic closed-score SATB.',
    'lyrics': 'Lyrics: long melismas and extenders, 6 stacked stanzas, refrains, translations in italics, four independent lyric lines in closed SATB, text-block stanzas that must not be underlaid, elisions, multilingual text with diacritics.',
    'layout': 'Page layout: 12-page piano score, closed choir + piano with hidden staves, 3-staff organ in landscape, cross-staff beams, cue notes and small staves, bracket vs brace, one-system page under a text-heavy title block.',
    'degradation': 'Controlled damage sweep: 4 simple pieces x 21 damage types (22 for the 2-page piece) x 3 strengths; isolates the effect of each kind of scan damage.',
}
DEG_DESC = {
    'clean': 'control: lossless raster (scan) / normal good scan (mild); no severe file',
    'skew': 'scanner-bed rotation 2 / 6.5 / 10 deg (2-page piece: pages skewed in opposite directions)',
    'rot90': 'page sideways (90 deg); 2-page severe turns its pages in opposite directions',
    'rot180': 'page upside down; 2-page piece: only page 2 upside down (mixed orientation)',
    'phone': 'phone photo: perspective/keystone, hand shadow, vignette, warm cast, motion blur; colour 250/200 dpi',
    'book': 'book scan: gutter shadow, page curl up to 13 mm, wave, dark open-lid border',
    'yellowed': 'aged paper colour scan: fibres, edge darkening, brown faded ink, up to 150 foxing spots',
    'bleed': 'mirrored reverse page (a different piece) showing through at 8 / 20 / 38 %',
    'stain-pencil': 'coffee rings, pencil circles, handwritten words, fingerings, breath marks, arrows; severe adds highlighter + ballpoint',
    'holes-staple': '2 / 3 / 4 punch holes, staple, folded corner; severe holes bite into staff starts',
    'crop': 'tight crop, then header cropped and staff ends cut (never a note, clef or lyric)',
    'halftone': 'halftone screens 150 / 110 / 85 lpi with moire (music rescaled to 0.97 / 0.93)',
    'jpeg': 'JPEG quality 60, 30 (saved twice), 15 (saved twice)',
    'photocopy-thin': '1-bit thresholds 115 / 85 / 70: staff lines break up',
    'photocopy-thick': '1-bit thresholds 170 / 195 / 210 + ink spread: hollow heads fill in, toner specks, black borders',
    'lowdpi': '150 / 100 / 100 dpi + blur + JPEG 45',
    'highdpi': '400 / 600 / 600 dpi with paper grain and dust',
    'blur': 'focus blur + motion blur up to 14 px',
    'noise': 'Gaussian sigma 10 / 25 / 45 + 0.2-3 % salt-and-pepper',
    'spread': 'two pages on one landscape image (single-page pieces get a text-only facing page)',
    'scale': '2-page piece only: pages copied at different sizes (97 / 94 / 88 % against 104 %)',
    'combo': 'everything combined, up to 150 dpi, -7 deg, JPEG 25',
}
REBUILD = {
    'voices': 'corpus/challenge/voices/_tools/run_all.py',
    'rhythm': 'corpus/challenge/rhythm/_tools/run_all.py',
    'pitch': 'corpus/challenge/pitch/_tools/run_all.py',
    'lyrics': 'corpus/challenge/lyrics/_tools/run_all.py   (re-check: lyrics/_tools/verify.py)',
    'layout': 'corpus/challenge/layout/_tools/run_all.py',
    'degradation': 'corpus/challenge/degradation/_tools/run.py',
}


def esc(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--analysis', default=str(ROOT / 'mvp' / 'work' / 'eval-challenge-baseline.analysis.json'))
    a = ap.parse_args()
    vrep = json.loads((HERE / 'report.json').read_text())
    vitems = {(i['category'], i['id']): i for i in vrep['items']}
    merged = []
    for c in CATS:
        for m in json.loads((CH / c / 'manifest.json').read_text()):
            v = vitems.get((c, m['id']), {})
            scans = sorted(v.get('scans') or [k for k in m['degradations'] if k.startswith('scan')], key=lambda f: ({'scan.pdf': 0, 'scan-mild.pdf': 1, 'scan-severe.pdf': 2}.get(f, 9), f))
            e = dict(m)
            e['path'] = f'{c}/{m["id"]}'
            e['scan_files'] = scans
            e['eval_ids'] = [f'{c}/{m["id"]}/{s[:-4]}' for s in scans]
            e['damage_families'] = {s: damage.tags(m['degradations'].get(s), m, s, (v.get('pdfs') or {}).get(s)) for s in scans}
            r = v.get('render') or {}
            e['validation_challenge'] = {
                'ok': not v.get('problems'), 'problems': v.get('problems', []), 'warnings': v.get('warnings', []),
                'xsd': v.get('xsd'), 'image_only': {k: p.get('image_only') for k, p in (v.get('pdfs') or {}).items()},
                'midi_vs_truth': (r.get('midi') or {}).get('notes_ok', r.get('ok')) if r else None,
                'lyrics_vs_truth': (r.get('midi') or {}).get('lyrics_ok', r.get('ok')) if r else None,
                'clean_pdf_matches_render': (r.get('clean') or {}).get('ok', r.get('ok')) if r else None,
                'checked_by': 'corpus/challenge/_validate/validate.py',
            }
            merged.append(e)
    (CH / 'manifest.json').write_text(json.dumps(merged, indent=1, ensure_ascii=False))

    an = None
    if a.analysis and Path(a.analysis).exists():
        an = json.loads(Path(a.analysis).read_text())
    L = []
    w = L.append
    nscan = sum(len(e['scan_files']) for e in merged)
    w('# Challenge corpus: synthetic scanned sheet music with exact truth\n')
    w(f'{len(merged)} items in {len(CATS)} categories, {nscan} damaged scan PDFs. Every item is a LilyPond engraving with an exact '
      'MusicXML 4.0 truth, an undamaged raster (`clean.pdf`) and one to three image-only "scans" with recorded, seeded damage. '
      'The set stresses the converter (scanned PDF to MusicXML 4.0, lyrics kept, two voices on one staff split into parts, '
      'piano grand staves never split) on the edge cases listed per item below.\n')
    w('## Layout of an item\n')
    w('`<category>/<id>/` holds:\n')
    w('| file | content |\n|---|---|')
    w('| `engraving.ly` | LilyPond 2.24 source of the page(s) |')
    w('| `truth.musicxml` | exact truth, MusicXML 4.0 partwise, XSD-valid (`mvp/work/schema/musicxml.xsd`) |')
    w('| `clean.pdf` | undamaged image-only raster of the engraving (mostly 300 dpi) |')
    w('| `scan.pdf` | damaged image-only PDF (the main test file) |')
    w('| `scan-mild.pdf`, `scan-severe.pdf` | same page(s) with lighter / heavier damage (all items except the 4 `degradation/*-clean` controls, which have `scan-mild.pdf` only) |')
    w('| `meta.json` | `id, category, title, edge_cases[], expected{parts[], must_not_split, shared_staves[[..]], notes}, degradations{<file>: params + seed}, dpi, license`, plus truth limitations and generator validation details |')
    w('| `ATTRIBUTION.txt` | sources and licences |')
    w('')
    w('`lyrics/lyr06-amazing-grace-textblock` also has `truth-underlaid.musicxml` (stanzas 4-6 of the text block underlaid as lyric lines 4-6; see its meta).\n')
    w('`manifest.json` here is the array of all meta objects (the six `<category>/manifest.json` merged), each with `path`, `scan_files`, '
      '`eval_ids`, `damage_families` (normalised damage tags per scan file) and `validation_challenge` added.\n')

    w('## Categories\n')
    w('| category | items | scan files | focus |\n|---|---:|---:|---|')
    for c in CATS:
        es = [e for e in merged if e['path'].startswith(c + '/')]
        w(f'| {c} | {len(es)} | {sum(len(e["scan_files"]) for e in es)} | {CAT_DESC[c]} |')
    w('')

    fam = Counter(t for e in merged for s in e['scan_files'] for t in e['damage_families'][s])
    w('## Damage coverage\n')
    w('Each scan file records its damage steps, parameters and seed in `meta.json` (`degradations`). '
      'The six generators log damage in different shapes; `_validate/damage.py` maps them onto common families '
      '(heuristic, used for reporting only). Files per family:\n')
    w(', '.join(f'{k} {v}' for k, v in fam.most_common()) + '\n')
    ppi = Counter()
    for v in vrep['items']:
        for f, p in v['pdfs'].items():
            if f.startswith('scan'):
                for x in p.get('image_ppi') or []:
                    ppi[x] += 1
    w('Scan image resolutions (files per dpi): ' + ', '.join(f'{k}: {v}' for k, v in sorted(ppi.items())) + '. '
      'Skew ranges from 0.3 to 10 degrees; 90- and 180-degree pages, mixed page orientation, page-scale mismatch, 2-up spreads, '
      'JPEG quality 15-60 and binarised photocopies occur in every category.\n')

    for c in CATS:
        es = [e for e in merged if e['path'].startswith(c + '/')]
        w(f'## Items: {c}\n')
        if c == 'degradation':
            pieces = {}
            for e in es:
                pieces.setdefault(e['piece'], e)
            w('Four pieces; every item of a piece shares its `engraving.ly` and `truth.musicxml` byte for byte '
              '(only the damage differs). Item id = `<piece>-<damage type>`.\n')
            w('| piece | title | expected parts | must_not_split | edge cases (music) |\n|---|---|---|---|---|')
            for p, e in pieces.items():
                dmg = set()
                for x in es:
                    if x['piece'] == p and x['variant'] != 'clean':
                        dmg |= set(x['edge_cases']) - set(next(y for y in es if y['piece'] == p and y['variant'] == 'clean')['edge_cases'])
                music = [t for t in e['edge_cases'] if t not in dmg and t not in ('control_clean',)]
                w(f'| `{p}` | {esc(e["title"].rsplit(" - ", 1)[0])} | {", ".join(e["expected"]["parts"])} | {e["expected"]["must_not_split"]} | {esc(", ".join(music))} |')
            w('')
            w('| damage type | items | mild / scan / severe |\n|---|---:|---|')
            for dv in sorted({e['variant'] for e in es}, key=lambda x: list(DEG_DESC).index(x) if x in DEG_DESC else 99):
                n = sum(1 for e in es if e['variant'] == dv)
                w(f'| `{dv}` | {n} | {esc(DEG_DESC.get(dv, ""))} |')
            w('')
            continue
        w('| item | expected parts (must_not_split) | edge cases | scan | scan-mild | scan-severe |\n|---|---|---|---|---|---|')
        for e in es:
            d = e['degradations']
            cells = [esc(damage.describe(d.get(s), e, s))[:260] if s in e['scan_files'] else '-' for s in ('scan.pdf', 'scan-mild.pdf', 'scan-severe.pdf')]
            w(f'| `{e["id"]}`<br>{esc(e["title"])} | {esc(", ".join(e["expected"]["parts"]))} ({e["expected"]["must_not_split"]}) | '
              f'{esc(", ".join(e["edge_cases"]))} | {cells[0]} | {cells[1]} | {cells[2]} |')
        w('')

    w('## Truth conventions and limitations\n')
    w('Per-item limitations are in each `meta.json` (`truth_limitations` / `expected.notes`). Common to the set:\n')
    for s in [
        'Pitches are sounding pitches (8va/8vb and treble-8vb clefs resolved), with MusicXML octave-shift / clef-octave-change markers where printed.',
        'Lyrics printed once under a shared choir staff are attached to the voice they align with (usually Soprano or Tenor), following the corpus/synthetic convention.',
        'Beams, system/page breaks, positions and font sizes are not part of the truth. Repeats, voltas, D.S./D.C. are in notated order (not unrolled).',
        'In "a 2" / "unis." passages the second part is not drawn; its truth notes are verified copies of the printed line.',
        'Grace notes have no duration; cue notes are marked `<cue/>` (the eval harness skips both).',
        'Pencil marks, stains, holes, staples, bleed-through ghosts and handwritten words are damage, never music or lyrics. Crops never remove a note, clef or lyric.',
        'Stanzas printed as a text block below the music are not lyrics in the truth (lyr06 stores them as credits; the Burns poem in layout/song-one-system-poem-block is not encoded).',
    ]:
        w(f'- {s}')
    w('')

    nok = sum(1 for e in merged if e['validation_challenge']['ok'])
    w('## Validation\n')
    w(f'`_validate/validate.py` (independent of the generators) re-checked all {len(merged)} items: **{nok}/{len(merged)} pass, none dropped**. Per item:\n')
    for s in [
        'every `truth*.musicxml` validates against `mvp/work/schema/musicxml.xsd` (xmllint) and parses with music21;',
        'every PDF opens (pdfinfo) and renders (pdftoppm), has no fonts (pdffonts), no extractable text (pdftotext) and at least one image per page (pdfimages);',
        '`meta.json` has id (= folder), category (= parent folder), title, edge_cases, expected{parts, must_not_split, shared_staves, notes}, a degradations record with seed for every scan file, dpi and license; `expected.parts` equals the truth part names;',
        '`engraving.ly` is re-rendered with LilyPond 2.24.3 in a scratch folder: every truth attack (onset, pitch; ties merged) matches LilyPond\'s MIDI (grace notes and a leading-grace clock offset allowed for; a second `\\score` placed at its best offset), and every truth lyric syllable matches a MIDI lyric event (onset, text);',
        '`clean.pdf` is compared page by page with a fresh raster of that render at the same dpi (ink masks, 2 px tolerance): every page matches (overlap 1.000);',
        'the eval harness scores every truth against itself as 1.0 on pitch, duration, rests, lyrics and parts (`node _validate/selfscore.mjs`).',
    ]:
        w(f'- {s}')
    w('')
    w('Notes from the run: `voices/ttbb-treble8-a2-unis` has 31 truth attacks without their own MIDI note (the "a 2"/"unis." passages are printed once for two parts, by design); '
      'LilyPond warnings remain in `lyrics/lyr06` (page-count forced to 1), `layout/nocturne-cross-staff-pedal-ds-coda` (cross-staff beam slopes, one `\\voiceXx` hint) and `layout/trio-minuet-bracket-vs-brace-dc` (page 1 compressed); '
      'the rendered pages still match `clean.pdf` and the truth. `layout/organ-chorale-3-staves-landscape` takes its notes from the music21 corpus encoding of BWV 252 '
      '(Greentree, "used by permission"); the composition is public domain, but re-encode from a public-domain edition if strict provenance of the encoding matters.\n')
    w('Full report: `_validate/report.json`.\n')

    w('## Rebuild and re-check\n')
    w('```sh\ncd /Users/d.sloane/music')
    for c in CATS:
        w(f'.venv/bin/python {REBUILD[c]}')
    w('# independent validation of everything (about 30 s):')
    w('.venv/bin/python corpus/challenge/_validate/validate.py --jobs 96 --scratch /tmp/challenge-validate')
    w('# merged manifest + this README:')
    w('.venv/bin/python corpus/challenge/_validate/build_index.py')
    w('```\n')
    w('Each generator only writes inside its own category folder. Rebuilding is deterministic (fixed seeds).\n')

    w('## Evaluation\n')
    w('```sh\ncd /Users/d.sloane/music/mvp')
    w('node tools/eval.mjs --set challenge --jobs 48 --no-ocr --out work/eval-challenge-baseline.json')
    w('node tools/eval.mjs --set challenge --only lyrics --jobs 48 --out work/eval-challenge-baseline-lyrics-ocr.json')
    w('node tools/eval.mjs --set challenge --only voices/satb-closed-crossing-unisons/scan-mild --out /tmp/x.json   # one file')
    w('../.venv/bin/python ../corpus/challenge/_validate/analyze_eval.py work/eval-challenge-baseline.json --ocr work/eval-challenge-baseline-ocr.json --out work/eval-challenge-baseline.analysis.json')
    w('```\n')
    w('`--set challenge` scores every scan variant separately (id `<category>/<id>/<variant>`, variant = scan | scan-mild | scan-severe) against the folder\'s `truth.musicxml`; '
      '`--only` accepts ids or prefixes (`lyrics`, `voices/sab-cross-staff-alto`). Without `--set` the harness runs the unchanged synthetic + real benchmark.\n')
    if an:
        cfg = an.get('config', {})
        w(f'### Baseline ({str(cfg.get("src_hash"))}, dpi {cfg.get("dpi")}; aggregate = 0.3 pitch + 0.2 duration + 0.2 parts + 0.2 lyrics + 0.1 xml)\n')
        w('| category | files | aggregate (no OCR) | aggregate (OCR) | pitch | duration | parts | lyrics (OCR) | no output |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|')
        for c in CATS:
            s = an['by_category'][c]
            o = (an.get('ocr') or {}).get('by_category', {}).get(c, {})
            w(f'| {c} | {s["n"]} | {s["aggregate"]:.3f} | {o.get("aggregate", float("nan")):.3f} | {s["pitch"]:.3f} | {s["duration"]:.3f} | {s["parts"]:.3f} | {o.get("lyrics", float("nan")):.3f} | {s["no_output"]} |')
        s, o = an['all'], (an.get('ocr') or {}).get('all', {})
        w(f'| **all** | {s["n"]} | {s["aggregate"]:.3f} | {o.get("aggregate", float("nan")):.3f} | {s["pitch"]:.3f} | {s["duration"]:.3f} | {s["parts"]:.3f} | {o.get("lyrics", float("nan")):.3f} | {s["no_output"]} |')
        w('')
        w('By strength: ' + ', '.join(f'{k} {v["aggregate"]:.3f} (pitch {v["pitch"]:.3f}, {v["no_output"]} empty)' for k, v in an['by_variant'].items()) + ' (no OCR).\n')
        w('Controlled damage sweep (degradation category, mean aggregate over 4 pieces; mild / scan / severe):\n')
        w('| damage | mean | mild | scan | severe | pitch | empty outputs |\n|---|---:|---:|---:|---:|---:|---:|')
        f3 = lambda x: '-' if x is None else f'{x:.3f}'
        for dv, s in sorted(an['degradation_by_damage'].items(), key=lambda kv: kv[1]['mean']['aggregate']):
            g = lambda lv: f3((s.get(lv) or {}).get('aggregate'))
            w(f'| {dv} | {s["mean"]["aggregate"]:.3f} | {g("scan-mild")} | {g("scan")} | {g("scan-severe")} | {s["mean"]["pitch"]:.3f} | {s["mean"]["no_output"]}/{s["mean"]["n"]} |')
        w('')
        fc = an.get('fails_completely', [])
        w('Edge cases that fail completely at baseline (the produced MusicXML never contains the feature on any item or variant whose truth has it, '
          'and under 15 % of the affected notes come out with the right pitch and duration on the mild scans; all notes: '
          f'{(fc[0].get("notes_right_baseline_all_notes") if fc else 0) or 0:.0%}):\n')
        w('| edge case | items (degradation pieces counted once) | notes right (mild) | scored by eval | examples |\n|---|---:|---:|---|---|')
        for e in fc:
            nr = e.get('notes_right_mild')
            w(f'| {e["edge_case"]} | {e["items"]} | {"-" if nr is None else f"{nr:.1%}"} | {"yes" if e.get("scored_by_eval") else "no"} | {", ".join(e.get("examples", [])[:3])} |')
        w('')
        pm = an.get('marker_missing_or_mostly_wrong', [])
        if pm:
            w('Never emitted as notation but notes partly right: ' + '; '.join(
                f'{e["edge_case"]} ({e["items"]} items, {(e.get("notes_right_mild") or 0):.0%} of notes right)' for e in pm) + '.\n')
        w('Details: `mvp/work/eval-challenge-baseline.analysis.json` (`feature_recall`, `edge_note_recall`, `edge_case_tags_mild`, `worst_items`, `damage_families`).\n')

    w('## Licences\n')
    w('All music is either public domain (traditional tunes, hymn tunes, Bach BWV 252, the "Ah! vous dirai-je, maman" theme, Amazing Grace / NEW BRITAIN, Old Hundredth) '
      'or composed for this corpus and dedicated to the public domain (CC0-1.0). All texts are public domain (Watts, Rinkart, C. F. Alexander, Ave verum corpus, Horace, Rossetti, Wesley, '
      'Claudius, Neale, Daniel James, Newton, Liguori, Ingemann, Willis, Baath-Holmberg, Burns, Lyte, Baring-Gould, Newman, Latin liturgy). '
      'Engravings, truth files, rasters and damaged scans are CC0-1.0. Each item\'s `meta.json` (`license`) and `ATTRIBUTION.txt` give the exact sources.\n')
    lic = Counter(e['license'] for e in merged)
    w('<details><summary>Licence strings in meta.json</summary>\n')
    for k, v in lic.most_common():
        w(f'- ({v}) {esc(k)}')
    w('\n</details>\n')
    (CH / 'README.md').write_text('\n'.join(L))
    print(f'wrote {CH / "manifest.json"} ({len(merged)} entries) and {CH / "README.md"}')


if __name__ == '__main__':
    main()
