#!/usr/bin/env python3
"""Write corpus/coverage/manifest.json (every family merged) and corpus/coverage/README.md.

  /Users/d.sloane/music/.venv/bin/python corpus/coverage/_validate/build_index.py [--coverage docs/coverage.json]

Inputs: every <family>/<id>/meta.json (the authoritative per-item record; the family manifests have
different shapes), <family>/manifest.json (referenced), _validate/report.json (validate.py) and,
optionally, docs/coverage.json (tools/coverage.mjs) for the app-baseline section of the README.
Each merged manifest entry is a trimmed meta object plus:
  path            "<family>/<id>"
  scan_files      scan PDFs present
  eval_ids        ids used by `eval.mjs --set coverage` ("<family>/<id>/<variant>", clean + scans)
  pdf             pages and image resolution of every PDF (from validate.py)
  validation_coverage  result of _validate/validate.py for this item
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
COV = HERE.parent
ROOT = COV.parent.parent
sys.path.insert(0, str(HERE))
from validate import LAYOUTS, TAXONOMY, TAGS  # noqa: E402

FAMILY_DESC = {
    'notes': 'Note values breve-64th, dots and double dots, chords up to 6 notes, beams (groups, hooks, over rests), flags, stems, ledger lines to 5 above/below, grace notes (slashed, beamed, chords), cue notes, tremolos.',
    'rests': 'Every rest value breve-64th, dotted rests, whole-bar rests in simple and compound meters, multi-bar rests (H-bar and old-style symbols), rests in two-voice staves, piano and quartet, rests inside tuplets and beams.',
    'pitch': 'All 8 clefs and clef changes, all 15 major and 15 minor key signatures and key changes, every accidental incl. double sharps/flats and courtesy accidentals, 8va/8vb/15ma lines vs ledger lines.',
    'time': 'All simple, compound and irregular meters, C and cut time, meter changes, pickups, triplets to septuplets, duplets/quadruplets, nested tuplets, ties across barlines, systems and pages.',
    'marks': 'Articulations, ornaments, fermatas, breath marks, every dynamic and hairpin, pedal, arpeggios, fingering, tempo/metronome marks, text expressions, rehearsal marks, chord symbols.',
    'structure': 'Double and final barlines, repeats, 1st/2nd/3rd endings, segno/coda/D.S./D.C./Fine, system and page breaks, multi-page scores up to 12 pages.',
    'lyrics': 'Lyric elisions (two syllables on one note), non-ASCII lyrics in four languages (German, French, Spanish, Czech), numbered multi-verse lyrics, hyphens, extenders, melismas.',
    'layouts': 'One exemplar per score layout: melody, song, piano, voice+piano, five choir layouts, choir+piano, organ, quartet, orchestra, lead sheet, hymnal, divisi, cross-staff, two voices on one staff.',
    'percussion': 'Percussion layout (percussion-none): one-line snare staff and 5-line drum set (percussion clef, x noteheads, two voices) beside a pitched melody.',
    'perf': 'Speed/memory sets: one hymn page and one piano page at 100-600 dpi and on Letter/A4/A3, and a piano book of 1, 5, 10, 20 and 40 pages (identical pages across books).',
}
FOCUS_KEYS = ('focus_symbols', 'focus', 'target_symbols')


def load(p):
    return json.loads(Path(p).read_text())


def deg_summary(rec):
    if not isinstance(rec, dict):
        return ''
    for k in ('summary', 'description', 'recipe', 'preset', 'level'):
        if isinstance(rec.get(k), str) and rec[k].strip():
            return rec[k].strip()
    p = rec.get('params') or rec
    bits = []
    for k in ('dpi', 'rotate', 'jpeg', 'jpeg_quality'):
        if k in p:
            bits.append(f'{k}={p[k]}')
    return ', '.join(bits)


def deg_seed(rec):
    if isinstance(rec, dict):
        if rec.get('seed') not in (None, ''):
            return rec['seed']
        for v in rec.values():
            s = deg_seed(v)
            if s not in (None, ''):
                return s
    if isinstance(rec, list):
        for v in rec:
            s = deg_seed(v)
            if s not in (None, ''):
                return s
    return None


def notes_list(meta):
    n = meta.get('notes')
    if isinstance(n, str):
        n = [n]
    n = list(n or [])
    tl = meta.get('truth_limitations')
    if isinstance(tl, str):
        n.append(tl)
    elif isinstance(tl, list):
        n += tl
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--coverage', default=str(ROOT / 'docs' / 'coverage.json'))
    a = ap.parse_args()
    rep = load(HERE / 'report.json') if (HERE / 'report.json').exists() else {'items': []}
    vrep = {f'{i["family"]}/{i["id"]}': i for i in rep.get('items', [])}
    fams = sorted(d.name for d in COV.iterdir() if d.is_dir() and not d.name.startswith(('_', '.')))
    order = ['notes', 'rests', 'pitch', 'time', 'marks', 'structure', 'lyrics', 'layouts', 'percussion', 'perf']
    fams = [f for f in order if f in fams] + [f for f in fams if f not in order]
    entries = []
    for fam in fams:
        for d in sorted((COV / fam).iterdir()):
            if not d.is_dir() or d.name.startswith(('_', '.')) or not (d / 'meta.json').exists():
                continue
            m = load(d / 'meta.json')
            key = f'{fam}/{d.name}'
            v = vrep.get(key, {})
            scans = sorted(p.name for p in d.glob('scan*.pdf'))
            focus = next((m[k] for k in FOCUS_KEYS if isinstance(m.get(k), list) and m[k]), None)
            e = {
                'id': m.get('id'), 'family': fam, 'path': key, 'title': m.get('title'),
                'layout': m.get('layout'), 'layout_also': m.get('layout_also', []),
                'focus_symbols': focus, 'symbols': m.get('symbols'), 'counts': m.get('counts'),
                'expected': {k: (m.get('expected') or {}).get(k) for k in ('parts', 'must_not_split', 'shared_staves', 'notes')
                             if (m.get('expected') or {}).get(k) is not None},
                'pages': m.get('pages'), 'measures': m.get('measures') or (m.get('expected') or {}).get('measures'),
                'files': sorted(p.name for p in d.iterdir() if p.is_file()),
                'scan_files': scans,
                'eval_ids': [f'{key}/clean'] + [f'{key}/{s[:-4]}' for s in scans],
                'degradations': {s: {'seed': deg_seed((m.get('degradations') or {}).get(s)),
                                     'summary': deg_summary((m.get('degradations') or {}).get(s))} for s in scans},
                'pdf': {n: {'pages': p.get('pages'), 'image_ppi': p.get('image_ppi'), 'image_px': (p.get('image_px') or [None])[0]}
                        for n, p in (v.get('pdfs') or {}).items()},
                'notes': notes_list(m),
                'license': m.get('license'),
            }
            if m.get('perf'):
                e['perf'] = m['perf']
            if m.get('count_rules') or m.get('counting_rules') or m.get('count_conventions'):
                e['count_rules_in_meta'] = True
            e['validation_coverage'] = {'ok': not v.get('problems') if v else None, 'problems': v.get('problems', []),
                                        'warnings': v.get('warnings', []),
                                        'midi_exact': ((v.get('render') or {}).get('midi') or {}).get('notes_exact'),
                                        'clean_overlap': ((v.get('render') or {}).get('clean') or {}).get('min_overlap')}
            entries.append(e)
    # ------------------------------------------------ coverage tables
    tag_items, tag_occ = defaultdict(list), Counter()
    xtags = defaultdict(list)
    for e in entries:
        for t in e['symbols'] or []:
            (tag_items if t in TAGS else xtags)[t].append(e['path'])
        for t, n in (e['counts'] or {}).items():
            if isinstance(n, (int, float)):
                tag_occ[t] += n
    lay_items, lay_also = defaultdict(list), defaultdict(list)
    for e in entries:
        lay_items[e['layout']].append(e['path'])
        for l in e['layout_also'] or []:
            lay_also[l].append(e['path'])
    missing_tags = [t for t in TAGS if not tag_items[t]]
    missing_layouts = [l for l in LAYOUTS if not lay_items[l] and not lay_also[l]]
    fam_rows = []
    for fam in fams:
        es = [e for e in entries if e['family'] == fam]
        fm = COV / fam / 'manifest.json'
        fam_rows.append({'family': fam, 'items': len(es), 'scan_files': sum(len(e['scan_files']) for e in es),
                         'pdfs': sum(1 + len(e['scan_files']) for e in es),
                         'pages': sum(e['pages'] or 0 for e in es), 'ok': sum(1 for e in es if e['validation_coverage']['ok']),
                         'manifest': f'{fam}/manifest.json' if fm.exists() else None,
                         'tools': f'{fam}/_tools/' if (COV / fam / '_tools').exists() else None,
                         'description': FAMILY_DESC.get(fam, '')})
    man = {
        'suite': 'OMR synthetic coverage suite',
        'description': ('Every common notation symbol and score layout, each item with an exact MusicXML 4.0 truth '
                        'generated from the same model as its LilyPond 2.24 engraving, an undamaged raster (clean.pdf), '
                        'a typical scan (scan.pdf) and a heavily damaged scan (scan-severe.pdf). All CC0.'),
        'license': 'CC0',
        'n_items': len(entries), 'n_scan_files': sum(len(e['scan_files']) for e in entries),
        'n_pdfs': sum(1 + len(e['scan_files']) for e in entries),
        'n_validated_ok': sum(1 for e in entries if e['validation_coverage']['ok']),
        'families': fam_rows,
        'taxonomy': TAXONOMY, 'layouts': LAYOUTS,
        'symbol_coverage': {t: {'items': len(tag_items[t]), 'occurrences': tag_occ.get(t, 0), 'item_ids': tag_items[t]}
                            for t in TAGS},
        'x_tags': {t: {'items': len(v), 'occurrences': tag_occ.get(t, 0), 'item_ids': v} for t, v in sorted(xtags.items())},
        'layout_coverage': {l: {'items': lay_items[l], 'also': lay_also[l]} for l in LAYOUTS},
        'missing_tags': missing_tags, 'missing_layouts': missing_layouts,
        'validator': '_validate/validate.py (report: _validate/report.json)',
        'items': entries,
    }
    (COV / 'manifest.json').write_text(json.dumps(man, indent=1, ensure_ascii=False, default=str))
    # ------------------------------------------------ README
    covj = None
    if Path(a.coverage).exists():
        try:
            covj = load(a.coverage)
            if covj.get('inputs', {}).get('coverage_dir') not in (None, 'corpus/coverage'):
                covj = None
        except Exception:
            covj = None
    write_readme(man, entries, fam_rows, tag_items, tag_occ, xtags, lay_items, lay_also, rep, covj)
    print(json.dumps({k: man[k] for k in ('n_items', 'n_scan_files', 'n_pdfs', 'n_validated_ok', 'missing_tags', 'missing_layouts')}))


def md_esc(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


def write_readme(man, entries, fam_rows, tag_items, tag_occ, xtags, lay_items, lay_also, rep, covj):
    L = []
    w = L.append
    w('# Coverage suite: every common notation symbol and score layout, with exact truth')
    w('')
    w(f'{man["n_items"]} items in {len(fam_rows)} families, {man["n_pdfs"]} image-only PDFs ({man["n_items"]} clean '
      f'rasters + {man["n_scan_files"]} damaged scans). Each item is a short piece (mostly 4-16 bars; the `perf` and '
      '`structure` families add 2-40 page scores) written so that the target symbols are isolated, frequent and countable. '
      f'All {len(TAGS)} taxonomy symbol tags and all {len(LAYOUTS)} layout tags have at least one item'
      + ('' if not man['missing_tags'] and not man['missing_layouts'] else
         f' except {", ".join(man["missing_tags"] + man["missing_layouts"])}') + '. '
      'All music is composed for the suite (CC0) or public domain (Latin Gloria, Watts 1719, Blake 1794).')
    w('')
    w(f'Validation (`_validate/validate.py`, re-run from the published files): **{man["n_validated_ok"]}/{man["n_items"]} '
      'items pass**. See [Validation](#validation).')
    w('')
    w('## Files of an item')
    w('')
    w('`<family>/<id>/` holds:')
    w('')
    w('| file | content |')
    w('|---|---|')
    w('| `engraving.ly` | LilyPond 2.24 source |')
    w('| `truth.musicxml` | exact truth, MusicXML 4.0 partwise, XSD-valid (`mvp/work/schema/musicxml.xsd`), parses in music21 |')
    w('| `clean.pdf` | undamaged image-only raster of the engraving (300 dpi; the perf DPI set uses its own dpi) |')
    w('| `scan.pdf` | typical 200-300 dpi scan: slight skew, noise, paper tint, JPEG |')
    w('| `scan-severe.pdf` | heavy damage: binarised photocopies, phone photos, 100-150 dpi, stains, curl, spreads, rotation |')
    w('| `meta.json` | `id, family, title, symbols[], layout, expected{parts[], must_not_split}, counts{tag: n}, degradations{file: params + seed}, dpi, pages, license, notes[]` (truth limitations), plus family-specific detail (count rules, focus symbols, generator validation) |')
    w('| `ATTRIBUTION.txt` | sources and licence |')
    w('')
    w('`manifest.json` here merges all families: per item a trimmed meta object plus `path`, `scan_files`, `eval_ids` '
      '(ids used by `eval.mjs --set coverage`), `pdf` (pages and image resolution per file) and `validation_coverage`; at '
      'the top `symbol_coverage`, `layout_coverage`, `x_tags`, `missing_tags`, `missing_layouts`. Each family also keeps '
      'its own `<family>/manifest.json` and its generator in `<family>/_tools/`.')
    w('')
    w('## Families')
    w('')
    w('| family | items | PDFs | pages (clean) | focus | rebuild |')
    w('|---|---:|---:|---:|---|---|')
    for r in fam_rows:
        rb = f'`{r["tools"]}`' if r['tools'] else ''
        w(f'| {r["family"]} | {r["items"]} | {r["pdfs"]} | {r["pages"]} | {md_esc(r["description"])} | {rb} |')
    w(f'| **total** | **{man["n_items"]}** | **{man["n_pdfs"]}** | **{sum(r["pages"] for r in fam_rows)}** | | |')
    w('')
    w('Rebuild a family with `/Users/d.sloane/music/.venv/bin/python corpus/coverage/<family>/_tools/run_all.py` '
      '(`percussion`: `_tools/build.py`); each `_tools/README.txt` explains its generator and its own engraving checks. '
      'Then re-run `_validate/validate.py` and `_validate/build_index.py`.')
    w('')
    w('## Symbol coverage')
    w('')
    w('Items = items whose `meta.symbols` lists the tag; occurrences = sum of `meta.counts`. Counting conventions differ '
      'slightly between families (see [Counting conventions](#counting-conventions)), so occurrences are indicative; '
      '`tools/coverage.mjs` re-counts every tag from the truth with one tagger for the app scores.')
    w('')
    for fam, tags in TAXONOMY.items():
        w(f'### {fam}')
        w('')
        w('| tag | items | occurrences | example items |')
        w('|---|---:|---:|---|')
        for t in tags:
            ids = tag_items[t]
            # prefer items whose focus lists the tag
            foc = [e['path'] for e in entries if t in (e['focus_symbols'] or []) and e['path'] in ids]
            ex = (foc + [i for i in ids if i not in foc])[:3]
            occ = tag_occ.get(t, 0)
            w(f'| `{t}` | {len(ids) or "**0**"} | {occ:g} | {", ".join(f"`{x}`" for x in ex)} |')
        w('')
    thin = [t for t in TAGS if len(tag_items[t]) == 1]
    if man['missing_tags']:
        w('**Tags without an item:** ' + ', '.join(f'`{t}`' for t in man['missing_tags']))
    else:
        w(f'**Every one of the {len(TAGS)} taxonomy tags has at least one item.**')
    w('')
    if thin:
        w('Tags with exactly one item (accuracy for them rests on one piece): ' + ', '.join(
            f'`{t}` ({tag_items[t][0]}, {tag_occ.get(t, 0):g}x)' for t in thin) + '.')
        w('')
    w('Extra tags (`x-` prefix) used by the families for symbols outside the taxonomy:')
    w('')
    w(', '.join(f'`{t}` ({v and len(v)})' for t, v in sorted(xtags.items())
                if not t.startswith(('x-measures', 'x-noteheads', 'x-parts', 'x-staves'))) + '.')
    w('')
    w('## Layout coverage')
    w('')
    w('| layout | items (primary) | also tagged | examples |')
    w('|---|---:|---:|---|')
    for l in LAYOUTS:
        ex = (lay_items[l] + lay_also[l])[:3]
        w(f'| `{l}` | {len(lay_items[l]) or "**0**"} | {len(lay_also[l])} | {", ".join(f"`{x}`" for x in ex)} |')
    w('')
    if man['missing_layouts']:
        w('**Layouts without an item:** ' + ', '.join(man['missing_layouts']))
    else:
        w(f'**Every one of the {len(LAYOUTS)} layout tags has at least one item.** `expected.parts` and '
          '`expected.must_not_split` in each meta.json give the part structure a converter must produce '
          '(e.g. a piano grand staff or an organ is one part; closed SATB is four parts).')
    w('')
    w('## Items')
    w('')
    for r in fam_rows:
        fam = r['family']
        w(f'### {fam}')
        w('')
        w('| item | layout | expected parts (must_not_split) | pages | focus / main symbols | scan.pdf | scan-severe.pdf |')
        w('|---|---|---|---:|---|---|---|')
        for e in entries:
            if e['family'] != fam:
                continue
            foc = e['focus_symbols']
            if not foc:
                cs = {k: v for k, v in (e['counts'] or {}).items() if not k.startswith('x-') and k not in (
                    'stem-up', 'stem-down', 'barline-final', 'clef-treble', 'clef-bass', 'note-quarter', 'note-half',
                    'note-8th', 'key-0', 'time-4-4', 'system-break')}
                foc = [k for k, _ in sorted(cs.items(), key=lambda kv: -kv[1])[:8]]
            ex = e['expected']
            parts = ', '.join(ex.get('parts') or [])
            if len(parts) > 70:
                parts = parts[:67] + '...'
            d = e['degradations']
            w(f'| `{e["id"]}`<br>{md_esc(e["title"])} | {e["layout"]} | {md_esc(parts)} ({ex.get("must_not_split")}) | '
              f'{e["pages"]} | {", ".join(foc)} | {md_esc(d.get("scan.pdf", {}).get("summary", ""))[:160]} | '
              f'{md_esc(d.get("scan-severe.pdf", {}).get("summary", ""))[:160]} |')
        w('')
    w('## Validation')
    w('')
    by = rep.get('by_family', {})
    w('`_validate/validate.py` is an adapted copy of `corpus/challenge/_validate/validate.py` (same truth parser, MIDI '
      'comparison, PDF checks and pixel comparison). For every item it checks:')
    w('')
    w('- all seven files present; `truth.musicxml` passes the MusicXML 4.0 XSD (`xmllint`) and parses in music21;')
    w('- every PDF opens, renders, has no fonts, no text and at least one image per page (image-only);')
    w('- `meta.json`: id = folder, family = parent folder, title, `symbols[]` (taxonomy tags or `x-*`), `layout` (a '
      'layout tag), `expected.parts[]`, `expected.must_not_split` (bool), `counts` (a positive count for every taxonomy '
      'symbol listed), `degradations` with seed and parameters for `scan.pdf` and `scan-severe.pdf`, `dpi`, `pages` (= '
      'clean.pdf pages), CC0/public-domain licence; the generator\'s own verification record has no failed check;')
    w('- the harness tagger (`tools/coverage.mjs` `extract()`, via `_validate/tagcount.mjs`) finds every declared '
      'taxonomy tag in the truth (except `stanza-text`, which MusicXML cannot encode) and warns about tags it finds '
      'that meta does not declare;')
    w('- `engraving.ly` is re-rendered with LilyPond 2.24 in a scratch folder: every truth attack (onset, pitch; ties '
      'merged, grace notes separate, cue notes silent, unpitched notes at their `<midi-unpitched>` key) and every lyric '
      'syllable must match LilyPond\'s MIDI, and `clean.pdf` must match a fresh raster of the LilyPond PDF (ink overlap '
      '>= 0.97 both ways, page by page).')
    w('')
    w('Each family generator additionally checked its truth against LilyPond\'s own layout (grob/event dumps of note '
      'heads, stems, beams, flags, accidentals, rests, articulations, dynamics, lyrics, barlines, voltas, clefs, keys, '
      'times, system/page starts); see `<family>/_tools/README.txt` and `meta.validation`.')
    w('')
    if rep.get('items'):
        w(f'Result: **{rep.get("n_ok")}/{rep.get("n_items")} items pass**, {rep.get("n_renders")} LilyPond renders, '
          'every MIDI comparison exact. ' + ' '.join(f'{f} {v["ok"]}/{v["items"]};' for f, v in by.items()))
        w('')
        if rep.get('failed'):
            w('Failed items:')
            for f in rep['failed']:
                w(f'- `{f["id"]}`: ' + '; '.join(f['problems']))
            w('')
        warn = [x for x in rep.get('warnings', [])]
        if warn:
            w('Warnings (not failures):')
            w('')
            for x in warn:
                w(f'- `{x["id"]}`: ' + '; '.join(md_esc(s) for s in x['warnings']))
            w('')
        w('Most warnings are definitional: the harness tagger counts chords and tuplet markings on grace/cue notes and '
          'on two-note tremolos (encoded with `<time-modification>` 2:1), multi-bar rests as whole-bar rests too, and '
          '"To Coda" as a separate tag; two scan-severe files capture a 2-page score as one open-book spread on purpose.')
        w('')
    w('Re-run: `/Users/d.sloane/music/.venv/bin/python corpus/coverage/_validate/validate.py --jobs 48` (about 2 '
      'minutes; add `--no-render` for the static checks only, `--only family[/id],...` to select).')
    w('')
    w('## Counting conventions')
    w('')
    w('Counts in `meta.counts` are read back from `truth.musicxml` by each family generator; the rules are written in '
      'each meta.json (`count_rules` / `counting_rules` / `count_conventions`). Differences to keep in mind:')
    w('')
    w('- `note-*`, `dot`, `acc-*`, `ledger-*`, `tie`: per notehead in notes/pitch/time/marks/perf; per note event '
      '(a chord once) in layouts/lyrics/percussion (`layouts/_tools/count_symbols.py`). `chord`, `flag`, `stem-*`: per stem.')
    w('- Note-family tags count main notes only (not grace or cue notes) in the notes family.')
    w('- Clef/key/time/barline tags: one per MusicXML element and part (a quartet counts four) in most families; '
      'score-wide marks once per score position in structure and layouts.')
    w('- `stanza-text` has no MusicXML element; it is counted from the engraving (`printed_not_in_truth`).')
    w('- `tools/coverage.mjs` uses its own tagger on truth and app output alike, so its per-tag accuracies do not '
      'depend on these differences.')
    w('')
    w('## Truth limitations (summary; each meta.json `notes` has the item-specific list)')
    w('')
    w('- Courtesy clefs, keys and time signatures at system ends are printed but implied in MusicXML (not counted).')
    w('- Stanza numbers and whether an ottava reads "8va" or "8" cannot be encoded.')
    w('- Two-note tremolos: both notes carry the printed value with `<time-modification>` 2:1.')
    w('- Multi-bar rests: one measure rest per bar plus `<multiple-rest>`; old-style rest symbols are not encoded glyph by glyph.')
    w('- Rest heights use `<display-step>/<display-octave>` (MuseScore convention); placement of marks is only above/below.')
    w('- Unpitched percussion: `<unpitched>` display positions (treble positions; a one-line staff uses B4) and '
      '`<midi-unpitched>` instruments.')
    w('')
    w('## Evaluating the app')
    w('')
    w('```')
    w('cd /Users/d.sloane/music/mvp')
    w('node tools/eval.mjs --set coverage --jobs 48 --out work/eval-coverage-baseline.json            # accuracy (OCR on)')
    w('node tools/eval.mjs --set coverage --only perf --dpi native --jobs 8 --out work/eval-coverage-perf.json   # speed/memory')
    w('cd .. && node tools/coverage.mjs --eval mvp/work/eval-coverage-baseline.json --perf mvp/work/eval-coverage-perf.json')
    w('```')
    w('')
    w('`tools/coverage.mjs` writes `docs/COVERAGE.md` and `docs/coverage.json`: per tag occurrences, how often the app '
      'emits it, accuracy on clean/scan/scan-severe, status (supported >= 0.8, partial, unsupported < 0.2), confusion; '
      'per layout part structure scores; ms/page and peak memory by dpi, page size and page count.')
    w('')
    if covj:
        t = covj.get('totals', {})
        w(f'### Baseline ({covj.get("generated", "")[:10]}, source hash `{covj.get("inputs", {}).get("src_hash")}`)')
        w('')
        w(f'{t.get("items")} items / {t.get("variants")} PDFs: **{t.get("tags_supported")} tags supported, '
          f'{t.get("tags_partial")} partial, {t.get("tags_unsupported")} unsupported**, {t.get("tags_not_measured")} '
          f'not measurable from MusicXML, {t.get("tags_without_items")} without items. Full matrix: '
          '[docs/COVERAGE.md](../../docs/COVERAGE.md).')
        w('')
    (COV / 'README.md').write_text('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
