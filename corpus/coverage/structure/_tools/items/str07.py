"""str07: five-page orchestral score (flute, oboe, bassoon, 2 violins, viola, cello - all in C), 40 bars,
2 systems of 4 bars per page.

Intro mm.1-4 | [A] Segno m.5 ... m.16 "Fine" (final bar, end of page 2) | [B] ||: mm.17-23, 1st ending
mm.24-25 across the page turn 3|4 :||, 2nd ending mm.26-27 | [C] m.28, ||: mm.29-32 :|| (end of page 4) |
[D] mm.33-40 "D.S. al Fine" (double bar).  Wind players rest (whole-bar rests) in some sections."""
from __future__ import annotations

from ssynth.harmonize import chord_tones
from ssynth.model import STEP_PC

from .common import CC0_NOTE, add_end_mark, add_mark, assemble, from_midi_spelled, lyp, mk_part

MEL = [  # Violin I melody per bar (DSL, absolute pitch), with two chords per bar
    ("d''2 b'2", 'G G'), ("c''4 e'' d'' a'", 'C D'), ("b'4 d'' e'' b'", 'G Em'), ("c''2 c''4 c''", 'Am D7'),
    ("g''4 d'' b' d''", 'G G'), ("e''4 g'' e'' c''", 'C C'), ("d''4 fis'' a'' fis''", 'D D'), ("g''2 r2", 'G G'),
    ("e''4 g'' b'' g''", 'Em Em'), ("a''4 e'' fis'' d''", 'Am D7'), ("b'4 d'' e'' c''", 'G C'), ("a'1", 'D D'),
    ("d''8 c'' b' c'' d''4 g''", 'G G'), ("e''8 d'' c'' d'' e''4 a''", 'C Am'), ("fis''4 a'' c''' fis''", 'D7 D7'),
    ("g''1", 'G G'),
    ("b'4 e'' g'' e''", 'Em Em'), ("c''4 e'' a'' e''", 'Am Am'), ("dis''4 fis'' a'' fis''", 'B7 B7'),
    ("e''2 b'2", 'Em Em'), ("c''4 e'' g'' e''", 'C C'), ("a'4 c'' d'' fis'", 'Am D7'), ("g'4 b' e'' g''", 'G Em'),
    ("a''4 e'' dis'' b'", 'Am B7'), ("e''2. r4", 'Em Em'), ("c''4 e'' d'' c''", 'Am D7'), ("b'1", 'G G'),
    ("e''4 g'' c''' g''", 'C C'), ("g''4 d'' b' g'", 'G G'), ("c''4 e'' d'' fis''", 'C D'), ("g''4 e'' a'' e''", 'Em Am'),
    ("d''2 c''2", 'D7 D7'),
    ("g''4 b'' d''' b''", 'G G'), ("c'''4 g'' e'' c''", 'C C'), ("a''4 e'' d'' fis''", 'Am D'), ("d''2 g''2", 'G G'),
    ("e''4 b' c'' e''", 'Em C'), ("a'4 c'' fis'' a''", 'Am D7'), ("g''4 b'' a'' fis''", 'G D7'), ("g''1", 'G G'),
]
SECTIONS = {'intro': range(0, 4), 'A': range(4, 16), 'B': range(16, 27), 'C': range(27, 32), 'D': range(32, 40)}
FLUTE_PLAYS = {'A', 'D'}
OBOE_PLAYS = {'B', 'C', 'D'}
BASSOON_PLAYS = {'A', 'C', 'D'}


def section_of(i):
    return next(k for k, r in SECTIONS.items() if i in r)


def first_midi(dsl):
    from ssynth.dsl import parse_voice
    ev = [e for e in parse_voice(dsl)[0]]
    out = []
    t = 0
    for e in ev:
        out.append((t, e))
        t += e.dur
    return out


def tones(sym):
    t, b, q = chord_tones(sym)
    return t, [(STEP_PC[s] + a) % 12 for s, a in t], b


def pick(sym, lo, hi, target, avoid=()):
    t, pcs, _ = tones(sym)
    cands = [m for m in range(lo, hi + 1) if m % 12 in pcs and m not in avoid]
    m = min(cands, key=lambda x: (abs(x - target), x))
    return lyp(from_midi_spelled(m, t)), m


def melody_at(dsl, half):
    """MIDI of the melody note sounding at the start of half-bar `half` (None for a rest)"""
    t0 = 2 * half
    cur = None
    for t, e in first_midi(dsl):
        if t <= t0:
            cur = e
    if cur is None or cur.kind != 'note':
        return None
    s, a, o = cur.pitches[0]
    return 12 * (o + 1) + STEP_PC[s] + a


def parts():
    vc, va, v2 = [], [], []
    prev_va, prev_v2 = 57, 67
    for i, (dsl, ch) in enumerate(MEL):
        syms = ch.split()
        bar_vc, bar_va, bar_v2 = [], [], []
        for h, sym in enumerate(syms):
            t, pcs, b = tones(sym)
            root = next(m for m in range(40, 52) if m % 12 == (STEP_PC[b[0]] + b[1]) % 12)
            fifth = next((m for m in range(root + 5, root + 9) if m % 12 in pcs and (m - root) == 7), root)
            bar_vc.append(f'{lyp(from_midi_spelled(root, t))}4 {lyp(from_midi_spelled(fifth, t))}4')
            name, prev_va = pick(sym, 50, 67, prev_va)
            bar_va.append(name + '2')
            mel = melody_at(dsl, h) or prev_v2 + 3
            name, prev_v2 = pick(sym, 57, min(76, mel - 3), prev_v2, avoid=(prev_va,))
            bar_v2.append(name + '2')
        vc.append(' '.join(bar_vc))
        va.append(' '.join(bar_va))
        v2.append(' '.join(bar_v2))
    vn1 = [d for d, _ in MEL]
    fl = [d if section_of(i) in FLUTE_PLAYS else 'R1' for i, d in enumerate(vn1)]
    ob = [d if section_of(i) in OBOE_PLAYS else 'R1' for i, d in enumerate(vn1)]
    bn = [d if section_of(i) in BASSOON_PLAYS else 'R1' for i, d in enumerate(vc)]
    dyn = {0: '\\f', 16: '\\p', 27: '\\mf', 32: '\\f'}

    def with_dyn(bars, rest_ok=True):
        out = []
        for i, b in enumerate(bars):
            if i in dyn and not b.startswith('R'):
                tok = b.split(' ', 1)
                b = tok[0] + dyn[i] + (' ' + tok[1] if len(tok) > 1 else '')
            out.append(b)
        return ' | '.join(out)

    # wind entries get their own dynamic at the start of each playing section
    def entries(bars, plays):
        out = list(bars)
        for k, r in SECTIONS.items():
            if k in plays:
                i = r[0]
                d = dyn.get(i, {'A': '\\mf'}.get(k, '\\mf'))
                tok = out[i].split(' ', 1)
                out[i] = tok[0] + d + (' ' + tok[1] if len(tok) > 1 else '')
        return ' | '.join(out)

    return {'FL': entries(fl, FLUTE_PLAYS), 'OB': entries(ob, OBOE_PLAYS), 'BN': entries(bn, BASSOON_PLAYS),
            'V1': with_dyn(vn1), 'V2': with_dyn(v2), 'VA': with_dyn(va), 'VC': with_dyn(vc)}


SPECS = [('FL', 'Flute', 'Fl.', 'treble'), ('OB', 'Oboe', 'Ob.', 'treble'), ('BN', 'Bassoon', 'Bn.', 'bass'),
         ('V1', 'Violin I', 'Vl. I', 'treble'), ('V2', 'Violin II', 'Vl. II', 'treble'),
         ('VA', 'Viola', 'Va.', 'alto'), ('VC', 'Violoncello', 'Vc.', 'bass')]


def make():
    P = parts()
    pv = []
    for pid, name, abbr, clef in SPECS:
        pv.append((mk_part(pid, name, abbr, 'other', 1, [clef]), {'1': P[pid]}))
    sc = assemble((4, 4), (1, 'major'), pv, time_symbol='common')
    m = sc.measures
    add_mark(sc, 0, 'tempo', text='Allegro moderato', unit='quarter', bpm=112)
    add_mark(sc, 4, 'segno')
    add_mark(sc, 4, 'rehearsal', text='A')
    m[15].right_bar = 'final'
    add_end_mark(sc, 15, 'Fine', style='bold-italic', sound={'fine': 'yes'})
    add_mark(sc, 16, 'rehearsal', text='B')
    m[16].left_bar = 'repeat-start'
    m[23].volta_start, m[24].volta_end, m[24].right_bar = '1', 'stop', 'repeat-end'
    m[25].volta_start, m[26].volta_end, m[26].right_bar = '2', 'discontinue', 'double'
    add_mark(sc, 27, 'rehearsal', text='C')
    m[28].left_bar = 'repeat-start'
    m[31].right_bar = 'repeat-end'
    add_mark(sc, 32, 'rehearsal', text='D')
    m[39].right_bar = 'double'
    add_end_mark(sc, 39, 'D.S. al Fine', style='bold-italic', sound={'dalsegno': 'segno'})
    for i in range(4, 40, 4):
        m[i].brk = 'page' if i % 8 == 0 else 'system'
    sc.groups = [{'first': 'FL', 'last': 'BN', 'symbol': 'bracket'}, {'first': 'V1', 'last': 'VC', 'symbol': 'bracket'}]
    sc.title = 'Little Overture'
    sc.composer = 'Coverage corpus (2026)'
    sc.rights = 'CC0 1.0'
    groups = []
    for ids in (SPECS[:3], SPECS[3:]):
        groups.append({'type': 'StaffGroup', 'staves': [
            {'id': pid.lower(), 'clef': clef, 'name': name, 'short': abbr, 'voices': [(pid, '1')]}
            for pid, name, abbr, clef in ids]})
    lay = {'groups': groups}
    opts = {'header': {'title': 'Little Overture', 'subtitle': 'for small orchestra', 'composer': 'Coverage corpus (2026)',
                       'copyright': 'CC0 1.0'},
            'staff_size': 16, 'paper': 'a4', 'forced_breaks': True,
            'paper_extra': ['indent = 20\\mm', 'short-indent = 10\\mm', 'ragged-bottom = ##f',
                            'system-system-spacing.basic-distance = #16', 'top-margin = 12\\mm',
                            'bottom-margin = 12\\mm']}
    return sc, lay, opts


ITEM = dict(
    id='str07-orchestral-five-pages',
    title='Little Overture - rehearsal marks, Segno, Fine, D.S. al Fine, endings across a page turn (orchestra, 5 pages)',
    make=make, pages=5, layout='orchestral', must_not_split=False,
    focus=['multi-page', 'page-break', 'system-break', 'segno', 'fine', 'ds', 'volta-1', 'volta-2', 'repeat-start',
           'repeat-end', 'barline-final', 'barline-double', 'rehearsal-mark'],
    expect_counts={'multi-page': 5, 'page-break': 4, 'system-break': 5, 'segno': 1, 'fine': 1, 'ds': 1, 'volta-1': 1,
                   'volta-2': 1, 'repeat-start': 2, 'repeat-end': 2, 'barline-final': 1, 'barline-double': 2,
                   'rehearsal-mark': 4},
    structure=('5 pages x 2 systems x 4 bars (page breaks before mm.9, 17, 25, 33; system breaks before mm.5, 13, '
               '21, 29, 37). Intro mm.1-4; [A] + Segno m.5; "Fine" + final bar after m.16 (end of page 2); [B] start '
               'repeat m.17 (top of page 3, combined with the final bar of m.16 at the page turn); 1st ending mm.24-25 '
               'crossing the page turn 3|4 (end repeat after m.25); 2nd ending mm.26-27 (double bar); [C] m.28; '
               'repeat mm.29-32 (end of page 4); [D] mm.33-40, "D.S. al Fine" + double bar. Played form: 1-25, '
               '17-23, 26-32, 29-40, 5-16.'),
    expected_notes=('Seven parts, one staff each, all non-transposing: Flute, Oboe, Bassoon (bracket) and Violin I, '
                    'Violin II, Viola (alto clef), Violoncello (bracket). G major, common-time symbol. Winds are tacet '
                    'in some sections (whole-bar rests; no multi-bar rests). Directions (tempo, rehearsal, segno, '
                    'Fine, D.S.) are in the Flute part (top staff) of the truth.'),
    notes=('Truth limitations: the page numbers printed on pages 2-5 are not encoded; staff-group brackets are '
           '<part-group> elements. Score-wide marks (tempo, rehearsal marks, segno, Fine, D.S.) are stored once, in '
           'the top part; endings, repeats and bar styles are stored in every part.'),
    attribution='\n'.join(['"Little Overture" for small orchestra, composed for this corpus (2026) - CC0 1.0.', '',
                           CC0_NOTE]),
    scans={
        'scan.pdf': {'seed': 47001, 'summary': 'sheet-fed scan of 5 pages, 300 dpi grey, a different small skew per '
                     'page (-1.0..1.1 deg), light noise, JPEG q75',
                     'params': dict(dpi=300, mode='gray', texture=2,
                                    rotate_pages={0: 0.5, 1: -0.8, 2: 1.1, 3: -0.4, 4: -1.0},
                                    blur=0.35, noise=3, jpeg=75)},
        'scan-severe.pdf': {'seed': 47002, 'summary': 'worn photocopy set, 200 dpi binarised: per-page skew up to '
                            '6 deg, page 4 fed upside down, page 2 at 97 % scale, toner speckles, broken thin lines',
                            'params': dict(dpi=200, rotate_pages={0: 2.5, 1: -3.5, 2: 6.0, 3: -2.0, 4: 4.0},
                                           page_rotate={3: 180}, scale_pages={1: 0.97}, ink_dropout=0.1, blur=0.7,
                                           noise=9, binarize=125, binarize_noise=18, saltpepper=0.0015, speckle=120,
                                           format='png1')},
    },
)
