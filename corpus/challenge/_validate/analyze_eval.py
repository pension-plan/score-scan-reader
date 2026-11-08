#!/usr/bin/env python3
"""Break a `node mvp/tools/eval.mjs --set challenge` report down by category, scan variant,
damage type and edge case.

  python analyze_eval.py <eval.json> [--ocr <eval-with-ocr.json>] [--out analysis.json]

Damage types:
  * degradation/<piece>-<variant>: the controlled set (4 pieces x 21 damage types x 3 strengths)
  * damage families: every scan file of every category tagged by damage.py from its meta record
Edge cases:
  * feature recall: for each notational feature present in a truth file (tuplets, grace notes,
    C clefs, 8vb treble clef, double accidentals, 6-7 sharp/flat keys, octave shifts, multi-bar
    rests, time changes, closed-score splitting, grand staff kept whole, lyrics ...) does the
    produced MusicXML contain it at all, on any scan variant of that item?
    "fails completely" = never produced for any item / variant carrying it.
  * per edge-case tag: mean scores on the scan-mild files (least damage) of items carrying it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH = HERE.parent
sys.path.insert(0, str(HERE))
import damage  # noqa: E402

CATS = ['voices', 'rhythm', 'pitch', 'lyrics', 'layout', 'degradation']
KEYS = ['aggregate', 'pitch', 'duration', 'rests', 'lyrics', 'parts', 'xml_valid']


def mean(xs):
    xs = list(xs)
    return round(sum(xs) / len(xs), 4) if xs else None


def summ(rs):
    o = {'n': len(rs)}
    for k in KEYS:
        o[k] = mean(r.get(k) or 0 for r in rs)
    o['crashes'] = sum(1 for r in rs if r.get('crash'))
    o['no_output'] = sum(1 for r in rs if not (r.get('counts') or {}).get('pp'))
    return o


# ------------------------------------------------------------------ features of a MusicXML file
def features(path):
    f = Counter()
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return None
    parts = root.findall('part')
    f['parts'] = len(parts)
    for p in parts:
        st = max([int(x.text) for x in p.iter('staves') if (x.text or '').strip().isdigit()] or [1])
        if st >= 2:
            f['multi_staff_part'] += 1
        voices_per_staff = defaultdict(set)
        times = set()
        for m in p.findall('measure'):
            for n in m.iter('note'):
                stf = n.findtext('staff') or '1'
                voices_per_staff[stf].add(n.findtext('voice') or '1')
            for t in m.iter('time'):
                times.add((t.findtext('beats'), t.findtext('beat-type')))
        if any(len(v) >= 2 for v in voices_per_staff.values()):
            f['multi_voice_staff'] += 1
        if len(times) >= 2:
            f['time_changes'] += 1
    for n in root.iter('note'):
        if n.find('time-modification') is not None:
            f['tuplet_notes'] += 1
        if n.find('grace') is not None:
            f['grace_notes'] += 1
        if n.find('chord') is not None:
            f['chord_notes'] += 1
        if n.find('cue') is not None:
            f['cue_notes'] += 1
        if len(n.findall('dot')) >= 2:
            f['double_dotted'] += 1
        a = n.findtext('pitch/alter')
        if a and abs(float(a)) >= 2:
            f['double_accidentals'] += 1
        if any(t.get('type') == 'start' for t in n.findall('tie')):
            f['ties'] += 1
        ty = n.findtext('type')
        if ty in ('32nd', '64th', '128th'):
            f['short_values_32_64'] += 1
        r = n.find('rest')
        if r is not None:
            f['rests'] += 1
        for l in n.findall('lyric'):
            f['lyric_syllables'] += 1
            t = ''.join(x.text or '' for x in l.findall('text'))
            if re.search(r'[^\x00-\x7f]', t):
                f['lyric_non_ascii'] += 1
            f['lyric_line_' + (l.get('number') or '1')] = 1
        if n.find('notations/fermata') is not None:
            f['fermatas'] += 1
    for c in root.iter('clef'):
        sign, line = c.findtext('sign'), c.findtext('line')
        oc = c.findtext('clef-octave-change')
        if sign == 'C':
            f['c_clef'] += 1
        if sign == 'G' and oc == '-1':
            f['treble_8vb_clef'] += 1
    for k in root.iter('key'):
        fi = k.findtext('fifths')
        if fi and abs(int(fi)) >= 6:
            f['key_6_or_7_accidentals'] += 1
    keys = {k.findtext('fifths') for k in root.iter('key')}
    if len(keys) >= 2:
        f['key_changes'] = 1
    f['octave_shifts'] = sum(1 for _ in root.iter('octave-shift'))
    f['multi_bar_rests'] = sum(1 for _ in root.iter('multiple-rest'))
    f['repeats_endings'] = sum(1 for _ in root.iter('repeat')) + sum(1 for _ in root.iter('ending'))
    f['lyric_lines'] = sum(1 for k in f if k.startswith('lyric_line_'))
    return f


FEATURE_LABEL = {
    'tuplet_notes': 'tuplets (time-modification)',
    'grace_notes': 'grace notes',
    'chord_notes': 'chords',
    'cue_notes': 'cue-size notes',
    'double_dotted': 'double-dotted values',
    'double_accidentals': 'double sharps / double flats',
    'ties': 'ties',
    'short_values_32_64': '32nd/64th note values',
    'fermatas': 'fermatas',
    'c_clef': 'C clefs (alto/tenor)',
    'treble_8vb_clef': 'treble-8vb (tenor) clef',
    'key_6_or_7_accidentals': 'keys with 6-7 sharps/flats',
    'key_changes': 'key changes',
    'time_changes': 'time-signature changes',
    'octave_shifts': '8va/8vb octave shifts',
    'multi_bar_rests': 'multi-bar rests',
    'repeats_endings': 'repeats / volta endings',
    'multi_staff_part': 'grand staff kept as one part (2+ staves)',
    'multi_voice_staff': 'two voices on one staff',
    'lyric_syllables': 'lyrics (any)',
    'lyric_non_ascii': 'lyrics with non-ASCII letters (umlauts, accents)',
}


# ------------------------------------------------------------------ note-level edge-case recall
STEPS = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def norm_name(s):
    s = (s or '').lower()
    s = re.sub(r'\bii\b', '2', s)
    s = re.sub(r'\bi\b', '1', s)
    return re.sub(r'[^a-z0-9]', '', s)


def note_list(path):
    """-> [ (part_name, [note dict]) ]; note: m, on, dur, midi, step, alter, rest, feats(set)"""
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return []
    names = {sp.get('id'): (sp.findtext('part-name') or '') for sp in root.iter('score-part')}
    res = []
    for p in root.findall('part'):
        div = 1
        clef = {}
        key = None
        first_key = None
        key_changed = False
        time = None
        first_time = None
        time_changed = False
        ottava = {}
        notes = []
        for mi, m in enumerate(p.findall('measure')):
            pos = 0.0
            last = 0.0
            mrest_span = False
            for c in m:
                if c.tag == 'attributes':
                    d = c.findtext('divisions')
                    if d:
                        div = int(d)
                    for cl in c.findall('clef'):
                        clef[cl.get('number', '1')] = (cl.findtext('sign'), cl.findtext('line'), cl.findtext('clef-octave-change'))
                    k = c.findtext('key/fifths')
                    if k is not None:
                        if first_key is None:
                            first_key = k
                        elif k != first_key:
                            key_changed = True
                        key = int(k)
                    t = c.find('time')
                    if t is not None:
                        tt = (t.findtext('beats'), t.findtext('beat-type'))
                        if first_time is None:
                            first_time = tt
                        elif tt != first_time:
                            time_changed = True
                        time = tt
                    if c.find('measure-style/multiple-rest') is not None:
                        mrest_span = True
                elif c.tag == 'direction':
                    for o in c.iter('octave-shift'):
                        st = c.findtext('staff') or '1'
                        ottava[st] = o.get('type') in ('up', 'down')
                elif c.tag == 'backup':
                    pos -= int(c.findtext('duration') or 0) / div
                elif c.tag == 'forward':
                    pos += int(c.findtext('duration') or 0) / div
                elif c.tag == 'note':
                    grace = c.find('grace') is not None
                    chord = c.find('chord') is not None
                    dur = 0.0 if grace else int(c.findtext('duration') or 0) / div
                    on = last if chord else pos
                    if not chord and not grace:
                        last = pos
                        pos += dur
                    if c.find('cue') is not None:
                        continue
                    pt = c.find('pitch')
                    rest = c.find('rest') is not None or pt is None
                    midi = step = alter = None
                    if pt is not None:
                        step = pt.findtext('step')
                        alter = int(round(float(pt.findtext('alter') or 0)))
                        midi = (int(pt.findtext('octave')) + 1) * 12 + STEPS[step] + alter
                    st = c.findtext('staff') or '1'
                    f = set()
                    cl = clef.get(st) or clef.get('1')
                    if grace:
                        f.add('grace note')
                    if c.find('time-modification') is not None:
                        f.add('tuplet note')
                    nd = len(c.findall('dot'))
                    if nd >= 2:
                        f.add('double-dotted value')
                    if c.findtext('type') in ('32nd', '64th', '128th'):
                        f.add('32nd/64th value')
                    if not rest:
                        if abs(alter) >= 2:
                            f.add('double sharp/flat')
                        if cl and cl[0] == 'C':
                            f.add('note in C clef (alto/tenor)')
                        if cl and cl[0] == 'G' and cl[2] == '-1':
                            f.add('note in treble-8vb clef')
                        if ottava.get(st):
                            f.add('note under 8va/8vb')
                        if key is not None and abs(key) >= 6:
                            f.add('note in 6-7 sharp/flat key')
                        if key_changed:
                            f.add('note after a key change')
                        if midi >= 93 or midi <= 31:
                            f.add('extreme ledger-line note')
                        if chord or (c.getnext() if hasattr(c, 'getnext') else None) is not None:
                            pass
                    else:
                        if mrest_span:
                            f.add('rest inside multi-bar rest')
                        if c.find('rest').get('measure') == 'yes':
                            f.add('whole-bar rest')
                    if time_changed:
                        f.add('note after a time change')
                    if c.findall('lyric'):
                        f.add('note with lyric')
                    notes.append({'m': mi, 'on': round(on, 4), 'dur': round(dur, 4), 'midi': midi, 'step': step, 'alter': alter, 'rest': rest, 'grace': grace, 'feats': f})
        res.append((names.get(p.get('id'), p.get('id')), notes))
    return res


def map_parts(T, P):
    mp, used = [-1] * len(T), set()
    for i, (tn, _) in enumerate(T):
        for j, (pn, _) in enumerate(P):
            if j not in used and norm_name(tn) and norm_name(pn) == norm_name(tn):
                mp[i] = j
                used.add(j)
                break
    rest = [j for j in range(len(P)) if j not in used]
    for i in range(len(T)):
        if mp[i] < 0 and rest:
            mp[i] = rest.pop(0)
    return mp


def note_recall(truth_path, prod_path):
    """per feature: [truth notes, pitch found, spelling found, rhythm found] (measure +-1 window)"""
    T, P = note_list(truth_path), note_list(prod_path)
    mp = map_parts(T, P)
    acc = defaultdict(lambda: [0, 0, 0, 0])
    for i, (_, tn) in enumerate(T):
        pn = P[mp[i]][1] if mp[i] >= 0 else []
        by_m = defaultdict(list)
        for n in pn:
            by_m[n['m']].append(n)
        for n in tn:
            cand = by_m[n['m']] + by_m[n['m'] - 1] + by_m[n['m'] + 1]
            if n['grace']:
                hit_p = any(c['grace'] and c['midi'] == n['midi'] for c in cand)
                hit_s, hit_r = hit_p, hit_p
            elif n['rest']:
                hit_p = hit_s = any(c['rest'] for c in cand)
                hit_r = any(c['rest'] and abs(c['dur'] - n['dur']) < 0.01 for c in cand)
            else:
                same = [c for c in cand if not c['rest'] and c['midi'] == n['midi']]
                hit_p = bool(same)
                hit_s = any(c['step'] == n['step'] and c['alter'] == n['alter'] for c in same)
                hit_r = any(abs(c['dur'] - n['dur']) < 0.01 for c in same)
            for f in n['feats'] | {'all notes and rests' if not n['grace'] else 'grace note'}:
                a = acc[f]
                a[0] += 1
                a[1] += hit_p
                a[2] += hit_s
                a[3] += hit_r
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('eval_json')
    ap.add_argument('--ocr', help='same set evaluated with OCR on (used for lyric numbers)')
    ap.add_argument('--out')
    a = ap.parse_args()
    rep = json.loads(Path(a.eval_json).read_text())
    outdir = Path(rep['config']['outputs'])
    items = [r for r in rep['items'] if r.get('set') == 'challenge']
    ocr = {}
    ocr_dir = None
    if a.ocr:
        o = json.loads(Path(a.ocr).read_text())
        ocr = {r['id']: r for r in o['items']}
        ocr_dir = Path(o['config']['outputs'])
    metas = {}
    for c in CATS:
        for m in json.loads((CH / c / 'manifest.json').read_text()):
            metas[(c, m['id'])] = m
    vrep = json.loads((HERE / 'report.json').read_text()) if (HERE / 'report.json').exists() else {'items': []}
    pdfs = {(i['category'], i['id']): i['pdfs'] for i in vrep['items']}
    out = {'source': a.eval_json, 'ocr_source': a.ocr, 'config': rep['config']}

    out['by_category'] = {c: summ([r for r in items if r['category'] == c]) for c in CATS}
    out['by_variant'] = {v: summ([r for r in items if r['variant'] == v]) for v in ('scan', 'scan-mild', 'scan-severe')}
    out['all'] = summ(items)
    if ocr:
        oi = [ocr[r['id']] for r in items if r['id'] in ocr]
        out['ocr'] = {'all': summ(oi), 'by_category': {c: summ([r for r in oi if r['category'] == c]) for c in CATS}}

    # ---- damage: controlled degradation set
    deg = defaultdict(lambda: defaultdict(list))
    for r in items:
        if r['category'] != 'degradation':
            continue
        m = metas[('degradation', r['item'])]
        deg[m['variant']][r['variant']].append(r)
    out['degradation_by_damage'] = {
        dv: {'mean': summ(sum(levels.values(), [])), **{lv: summ(rs) for lv, rs in sorted(levels.items())}}
        for dv, levels in sorted(deg.items())}
    # ---- damage families over every category
    fam = defaultdict(list)
    for r in items:
        m = metas[(r['category'], r['item'])]
        rec = m['degradations'].get(r['variant'] + '.pdf')
        r['_damage'] = damage.tags(rec, m, r['variant'] + '.pdf', (pdfs.get((r['category'], r['item'])) or {}).get(r['variant'] + '.pdf'))
        for t in r['_damage']:
            fam[t].append(r)
    out['damage_families'] = {t: summ(rs) for t, rs in sorted(fam.items(), key=lambda kv: mean(x['aggregate'] for x in kv[1]))}

    # ---- worst
    def short(r, src=None):
        pd, c = r.get('parts_detail') or {}, r.get('counts') or {}
        return {'id': r['id'], 'aggregate': round(r['aggregate'], 4), 'pitch': round(r['pitch'], 4), 'duration': round(r['duration'], 4),
                'parts': round(r['parts'], 4), 'lyrics': round(r['lyrics'], 4), 'xml_valid': r['xml_valid'],
                'parts_T_P': f"{pd.get('truth', '-')}/{pd.get('ours', '-')}", 'notes_T_P': f"{c.get('tp', '-')}/{c.get('pp', '-')}",
                'first_warning': (r.get('warnings') or [''])[0][:140], 'damage': r.get('_damage')}
    src = [ocr.get(r['id'], r) for r in items] if ocr else items
    for r in src:
        r['_damage'] = next(x['_damage'] for x in items if x['id'] == r['id'])
    out['worst_files'] = [short(r) for r in sorted(src, key=lambda r: (r['aggregate'], r['pitch']))[:25]]
    per_item = defaultdict(list)
    for r in src:
        per_item[(r['category'], r['item'])].append(r)
    ranked = sorted(per_item.items(), key=lambda kv: mean(x['aggregate'] for x in kv[1]))
    out['worst_items'] = [{'id': f'{c}/{i}', 'mean_aggregate': mean(x['aggregate'] for x in rs), 'best_aggregate': round(max(x['aggregate'] for x in rs), 4),
                           'variants': {x['variant']: round(x['aggregate'], 4) for x in rs},
                           'mean_pitch': mean(x['pitch'] for x in rs), 'parts_T_P': [ (x.get('parts_detail') or {}).get('ours') for x in rs],
                           'edge_cases': metas[(c, i)]['edge_cases'][:12]} for (c, i), rs in ranked[:15]]
    out['crashes'] = [{'id': r['id'], 'error': r.get('error')} for r in items if r.get('crash')]
    out['no_output'] = [r['id'] for r in items if not (r.get('counts') or {}).get('pp')]
    out['xsd_invalid_outputs'] = [r['id'] for r in items if r.get('xml_valid') != 1]

    # ---- feature recall (edge cases); the 85 degradation items count as their 4 source pieces
    feat = defaultdict(lambda: {'items': 0, 'items_any_variant': 0, 'items_mild': 0, 'files': 0, 'files_with': 0, 'truth_count': 0, 'produced_count_best': 0, 'examples_missing': []})
    tcache = {}
    groups = defaultdict(list)
    for (c, i), rs in per_item.items():
        tcache[(c, i)] = features(CH / c / i / 'truth.musicxml')
        gk = f"degradation/{metas[(c, i)]['piece']} (x{sum(1 for x in metas if x[0] == c and metas[x].get('piece') == metas[(c, i)]['piece'])} damage types)" if c == 'degradation' else f'{c}/{i}'
        for r in rs:
            groups[gk].append((c, i, r))
    for gk, members in groups.items():
        c0, i0, _ = members[0]
        tf = tcache[(c0, i0)]
        pfs = []
        for c, i, r in members:
            d = ocr_dir if (ocr and r['id'] in ocr) else outdir
            pfs.append((r['variant'], features(d / f"challenge__{c}__{i}__{r['variant']}.musicxml") or Counter()))
        for k in FEATURE_LABEL:
            if not tf.get(k):
                continue
            if k == 'multi_staff_part' and not metas[(c0, i0)]['expected'].get('must_not_split'):
                continue
            e = feat[k]
            e['items'] += 1
            e['truth_count'] += tf[k]
            got = [v for _, v in pfs if v.get(k)]
            e['files'] += len(pfs)
            e['files_with'] += len(got)
            e['produced_count_best'] += max([v.get(k, 0) for _, v in pfs] or [0])
            if got:
                e['items_any_variant'] += 1
            else:
                e['examples_missing'].append(gk)
            if any(vv == 'scan-mild' and v.get(k) for vv, v in pfs):
                e['items_mild'] += 1
    # closed-score splitting / part counts
    split = {'items': 0, 'right_count_any': 0, 'right_count_mild': 0, 'failing': []}
    keep = {'items': 0, 'right_count_any': 0, 'right_count_mild': 0, 'failing': []}
    for (c, i), rs in per_item.items():
        m = metas[(c, i)]
        want = tcache[(c, i)]['parts']
        got = {r['variant']: (r.get('parts_detail') or {}).get('ours') for r in rs}
        for flag, box in ((bool(m['expected'].get('shared_staves')), split), (bool(m['expected'].get('must_not_split')), keep)):
            if not flag:
                continue
            box['items'] += 1
            if any(v == want for v in got.values()):
                box['right_count_any'] += 1
            else:
                box['failing'].append(f'{c}/{i} (truth {want} parts, produced {sorted(set(map(str, got.values())))})')
            if got.get('scan-mild') == want:
                box['right_count_mild'] += 1
    out['feature_recall'] = {FEATURE_LABEL[k]: {**v, 'examples_missing': v['examples_missing'][:8]} for k, v in sorted(feat.items(), key=lambda kv: kv[1]['items_any_variant'] / max(kv[1]['items'], 1))}
    out['part_count'] = {'shared_staves_split_to_expected_count': split, 'must_not_split_expected_count': keep}
    # note-level recall of edge-case notes (mild + all variants)
    nrec = {'scan-mild': defaultdict(lambda: [0, 0, 0, 0]), 'all': defaultdict(lambda: [0, 0, 0, 0])}
    nitems = defaultdict(set)
    for (c, i), rs in per_item.items():
        if c == 'degradation':
            continue  # 4 simple pieces repeated 21x; their edge cases are damage, not notation
        for r in rs:
            d = ocr_dir if (ocr and r['id'] in ocr) else outdir
            acc = note_recall(CH / c / i / 'truth.musicxml', d / f"challenge__{c}__{i}__{r['variant']}.musicxml")
            for f, v in acc.items():
                nitems[f].add(f'{c}/{i}')
                for key in (['scan-mild', 'all'] if r['variant'] == 'scan-mild' else ['all']):
                    for k in range(4):
                        nrec[key][f][k] += v[k]
    out['edge_note_recall'] = {}
    for f in sorted(nrec['all'], key=lambda f: nrec['scan-mild'][f][3] / max(nrec['scan-mild'][f][0], 1)):
        mv, av = nrec['scan-mild'][f], nrec['all'][f]
        out['edge_note_recall'][f] = {'items': len(nitems[f]), 'truth_notes_mild': mv[0],
                                      'pitch_found_mild': round(mv[1] / max(mv[0], 1), 3), 'spelling_found_mild': round(mv[2] / max(mv[0], 1), 3),
                                      'pitch_and_duration_found_mild': round(mv[3] / max(mv[0], 1), 3),
                                      'pitch_and_duration_found_all_variants': round(av[3] / max(av[0], 1), 3),
                                      'examples': sorted(nitems[f])[:4]}
    # complete failures: marker never emitted AND (no note-level check, or <15 % of those notes right on mild files)
    NOTE_OF = {'tuplets (time-modification)': 'tuplet note', 'grace notes': 'grace note', 'double-dotted values': 'double-dotted value',
               '32nd/64th note values': '32nd/64th value', 'double sharps / double flats': 'double sharp/flat',
               'C clefs (alto/tenor)': 'note in C clef (alto/tenor)', '8va/8vb octave shifts': 'note under 8va/8vb',
               'multi-bar rests': 'rest inside multi-bar rest', 'key changes': 'note after a key change',
               'time-signature changes': 'note after a time change'}
    UNSCORED = {'fermatas', 'repeats / volta endings', 'cue-size notes', 'grace notes'}
    allr = out['edge_note_recall'].get('all notes and rests', {}).get('pitch_and_duration_found_mild')
    fails, partial = [], []
    for k, v in out['feature_recall'].items():
        nk = NOTE_OF.get(k)
        nr = out['edge_note_recall'].get(nk) if nk else None
        rate = nr['pitch_and_duration_found_mild'] if nr else None
        ev = {'edge_case': k, 'items': v['items'], 'marker_emitted_items': v['items_any_variant'],
              'notes_right_mild': rate, 'notes_right_baseline_all_notes': allr, 'scored_by_eval': k not in UNSCORED,
              'examples': v['examples_missing'][:4]}
        if v['items_any_variant'] == 0 and (rate is None or rate < 0.15):
            fails.append(ev)
        elif v['items_any_variant'] == 0 or (rate is not None and rate < 0.15):
            partial.append(ev)
    for f, nr in out['edge_note_recall'].items():
        if f != 'all notes and rests' and nr['pitch_and_duration_found_mild'] < 0.15 and f not in NOTE_OF.values():
            fails.append({'edge_case': f, 'items': nr['items'], 'notes_right_mild': nr['pitch_and_duration_found_mild'],
                          'notes_right_baseline_all_notes': allr, 'scored_by_eval': True, 'examples': nr['examples']})
    out['fails_completely'] = fails
    out['marker_missing_or_mostly_wrong'] = partial
    # lyric text with OCR on mild files
    if ocr:
        lyr = []
        for (c, i), rs in per_item.items():
            if not tcache[(c, i)].get('lyric_syllables'):
                continue
            mild = next((x for x in rs if x['variant'] == 'scan-mild'), rs[0])
            lyr.append({'id': f'{c}/{i}', 'lyrics_text_mild': round(mild.get('lyrics_text', 0), 3), 'lyrics_best': round(max(x.get('lyrics_text', 0) for x in rs), 3)})
        out['lyrics_text_ocr'] = sorted(lyr, key=lambda x: x['lyrics_best'])
    # per edge-case tag on mild files
    tag = defaultdict(list)
    for (c, i), rs in per_item.items():
        mild = next((x for x in rs if x['variant'] == 'scan-mild'), None)
        if not mild:
            continue
        for t in metas[(c, i)]['edge_cases']:
            tag[t].append(mild)
    out['edge_case_tags_mild'] = {t: {'items': len(rs), 'aggregate': mean(x['aggregate'] for x in rs), 'pitch': mean(x['pitch'] for x in rs),
                                     'duration': mean(x['duration'] for x in rs), 'parts': mean(x['parts'] for x in rs),
                                     'max_aggregate': round(max(x['aggregate'] for x in rs), 4)}
                                  for t, rs in sorted(tag.items(), key=lambda kv: mean(x['aggregate'] for x in kv[1]))}
    for r in items + src:
        r.pop('_damage', None)
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False))
    # ---- print
    f3 = lambda x: '  -  ' if x is None else f'{x:.3f}'
    print('== by category (no OCR)' + ('  | aggregate with OCR' if ocr else ''))
    for c, s in out['by_category'].items():
        print(f"  {c:12s} n={s['n']:3d} agg={f3(s['aggregate'])} pitch={f3(s['pitch'])} dur={f3(s['duration'])} rests={f3(s['rests'])} lyr={f3(s['lyrics'])} parts={f3(s['parts'])} xml={f3(s['xml_valid'])} no_output={s['no_output']}"
              + (f"  | ocr agg={f3(out['ocr']['by_category'][c]['aggregate'])} lyr={f3(out['ocr']['by_category'][c]['lyrics'])}" if ocr else ''))
    print('== by variant')
    for c, s in out['by_variant'].items():
        print(f"  {c:12s} n={s['n']:3d} agg={f3(s['aggregate'])} pitch={f3(s['pitch'])} dur={f3(s['duration'])} parts={f3(s['parts'])} no_output={s['no_output']}")
    print('== degradation category by damage type (agg mild / scan / severe; pitch mean)')
    for dv, s in sorted(out['degradation_by_damage'].items(), key=lambda kv: kv[1]['mean']['aggregate']):
        g = lambda lv: f3((s.get(lv) or {}).get('aggregate'))
        print(f"  {dv:16s} mean={f3(s['mean']['aggregate'])} mild={g('scan-mild')} scan={g('scan')} severe={g('scan-severe')} pitch={f3(s['mean']['pitch'])} no_output={s['mean']['no_output']}/{s['mean']['n']}")
    print('== damage families, all categories')
    for t, s in out['damage_families'].items():
        print(f"  {t:18s} files={s['n']:3d} agg={f3(s['aggregate'])} pitch={f3(s['pitch'])} no_output={s['no_output']}")
    print('== worst items (mean over variants)')
    for w in out['worst_items'][:10]:
        print(f"  {w['mean_aggregate']:.3f} best={w['best_aggregate']:.3f} {w['id']} {w['variants']} parts={w['parts_T_P']}")
    print('== worst files')
    for w in out['worst_files'][:12]:
        print(f"  {w['aggregate']:.3f} {w['id']} parts {w['parts_T_P']} notes {w['notes_T_P']} {w['first_warning'][:70]}")
    print('== crashes', len(out['crashes']), ' no-output files', len(out['no_output']), ' XSD-invalid outputs', len(out['xsd_invalid_outputs']))
    print('== feature recall (items whose output contains the feature on any variant / items whose truth has it)')
    for k, v in out['feature_recall'].items():
        print(f"  {k:48s} {v['items_any_variant']:2d}/{v['items']:2d}  mild {v['items_mild']:2d}  files {v['files_with']}/{v['files']}  count truth={v['truth_count']} best_prod={v['produced_count_best']}  missing e.g. {v['examples_missing'][:3]}")
    print('== part counts', json.dumps(out['part_count'], indent=1))
    if ocr:
        print('== lyric text (OCR) lowest')
        for x in out['lyrics_text_ocr'][:12]:
            print('  ', x)
    print('== note-level edge-case recall (non-degradation items; same measure +-1; mild variant)')
    print(f"  {'feature':34s} items notes  pitch  spell  pitch+dur(mild)  pitch+dur(all)")
    for f, v in out['edge_note_recall'].items():
        print(f"  {f:34s} {v['items']:5d} {v['truth_notes_mild']:5d}  {v['pitch_found_mild']:.3f}  {v['spelling_found_mild']:.3f}  {v['pitch_and_duration_found_mild']:.3f}            {v['pitch_and_duration_found_all_variants']:.3f}")
    print('== fails completely (marker never emitted and <15% of its notes right on mild files):')
    for e in out['fails_completely']:
        print('  ', json.dumps(e, ensure_ascii=False))
    print('== marker never emitted but notes partly right, or notes mostly wrong:')
    for e in out['marker_missing_or_mostly_wrong']:
        print('  ', json.dumps(e, ensure_ascii=False))


if __name__ == '__main__':
    main()
