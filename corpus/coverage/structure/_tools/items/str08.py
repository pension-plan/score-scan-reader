"""str08: twelve-page piano score - Theme, seven variations and Coda (2/4, A major, 146 bars, 36 systems of
4 bars (5 where a section has 1st/2nd endings), 3 systems per page).

Every section repeats its halves (||: :||, the combined repeat sign falls on system breaks); Var. II and
Var. V have 1st/2nd endings; Var. IV is a minore (key change to A minor) and Var. V a maggiore (back to A
major); "To Coda" ends bar 8 of the Theme on page 1 and "D.C. al Coda" ends Var. VII on page 11; the
Coda sign starts the Coda.  All textures are generated from the theme's melody and harmony (CC0)."""
from __future__ import annotations

import re

from ssynth.harmonize import chord_tones
from ssynth.model import STEP_PC

from .common import CC0_NOTE, add_end_mark, add_mark, assemble, chord_ly, close_chord, from_midi_spelled, lyp, mk_part

THEME = [("cis''4 e''", 'A'), ("fis''4 d''", 'D'), ("e''4 cis''8 a'", 'A'), ("b'2", 'E'),
         ("cis''4 e''", 'A'), ("fis''4 a''", 'D'), ("gis''4 d''", 'E7'), ("a''2", 'A'),
         ("fis''4 cis''", 'F#m'), ("d''4 b'", 'Bm'), ("e''4 gis'", 'E'), ("a'2", 'A'),
         ("fis''4 a''", 'D'), ("e''4 cis''", 'A'), ("d''4 b'", 'E7'), ("a'2", 'A')]
FIRST_ENDING = {0: ("b'4 d''", 'E7'), 1: ("gis'4 b'", 'E7')}      # leads back to the start of the half
MAJ = {9: ('A', 0), 11: ('B', 0), 1: ('C', 1), 2: ('D', 0), 4: ('E', 0), 6: ('F', 1), 8: ('G', 1)}
MIN = {9: ('A', 0), 11: ('B', 0), 0: ('C', 0), 2: ('D', 0), 4: ('E', 0), 5: ('F', 0), 7: ('G', 0), 8: ('G', 1)}
TO_MINOR = {'A': 'Am', 'D': 'Dm', 'E': 'E', 'E7': 'E7', 'F#m': 'F', 'Bm': 'Dm'}
# (heading, texture, tempo, bpm, dynamic, voltas in half (None|0|1), minor, repeat second half)
SECTIONS = [
    ('Thema', 'theme', 'Andante', 69, 'p', None, False, True),
    ('Var. I', 'eighths', None, None, 'mf', None, False, True),
    ('Var. II', 'sixteenths', None, None, 'f', 0, False, True),
    ('Var. III', 'lh_melody', None, None, 'mp', None, False, True),
    ('Var. IV - Minore', 'chorale', 'Adagio', 50, 'p', None, True, True),
    ('Var. V - Maggiore', 'triplets', 'Tempo I', None, 'f', 1, False, True),
    ('Var. VI', 'dotted', None, None, 'mf', None, False, True),
    ('Var. VII', 'octaves', None, None, 'ff', None, False, False),
    ('Coda', 'coda', 'Più mosso', None, 'f', None, False, False),
]


def midi_of(tok):
    s = tok[0].upper()
    a = 1 if 'is' in tok else (-1 if 'es' in tok else 0)
    o = 3 + tok.count("'") - tok.count(',')
    return 12 * (o + 1) + STEP_PC[s] + a


def beats(dsl):
    """melody MIDI at beat 1 and beat 2 of a 2/4 bar"""
    toks = dsl.split()
    m1 = midi_of(toks[0].rstrip('248.'))
    if toks[0].endswith('2'):
        return m1, m1, True
    return m1, midi_of(toks[1].rstrip('248.')), False


def spell(m, sym, minor):
    t, b, q = chord_tones(sym)
    for st, al in t:
        if (STEP_PC[st] + al) % 12 == m % 12:
            return lyp(from_midi_spelled(m, t))
    st, al = (MIN if minor else MAJ)[m % 12]
    return lyp(from_midi_spelled(m, [(st, al)]))


def pcs(sym):
    t, b, q = chord_tones(sym)
    return {(STEP_PC[s] + a) % 12 for s, a in t}


def below(m, sym, k=1):
    c = [x for x in range(m - 12, m) if x % 12 in pcs(sym)]
    return c[-k]


def step(m, d, minor):
    sc = MIN if minor else MAJ
    x = m
    for _ in range(abs(d)):
        x += 1 if d > 0 else -1
        while x % 12 not in sc:
            x += 1 if d > 0 else -1
    return x


def bass(sym, lo=43, hi=54):
    t, b, q = chord_tones(sym)
    return next(m for m in range(lo, hi + 1) if m % 12 == (STEP_PC[b[0]] + b[1]) % 12)


def lh_chord(sym, center=56):
    return chord_ly(close_chord(sym, center))


def bar(tex, dsl, sym, minor, last):
    """(rh, lh) for one 2/4 bar"""
    m1, m2, held = beats(dsl)
    S = lambda m: spell(m, sym, minor)  # noqa: E731
    b = bass(sym)
    fifth = next(x for x in range(b + 6, b + 9) if x % 12 in pcs(sym))
    third = next(x for x in range(b + 3, b + 5) if x % 12 in pcs(sym))
    if tex == 'theme':
        return dsl, f'{S(b)}4 {lh_chord(sym)}4'
    if tex == 'eighths':
        if last:
            return f'{S(m1)}4 r4', f'{S(b)}4 r4'
        return (f'{S(m1)}8 {S(below(m1, sym))} {S(m2)} {S(below(m2, sym))}', f'{S(b)}4 {S(fifth)}4')
    if tex == 'sixteenths':
        if last:
            return f'{S(m1)}4 r4', f'{S(b)}8 {S(fifth)} {S(b)}4'
        r = []
        for m in (m1, m2):
            r += [S(m) + '16', S(step(m, 1, minor)), S(m), S(below(m, sym))]
        top = close_chord(sym, 56)
        return ' '.join(r), f'{S(b)}8 {lyp(top[-1])} {lyp(top[-2])} {lyp(top[-1])}'
    if tex == 'lh_melody':
        lo1 = m1 - 24 if m1 - 24 >= 40 else m1 - 12
        lo2 = m2 - 24 if m2 - 24 >= 40 else m2 - 12
        c = chord_ly(close_chord(sym, 67))
        if held or last:
            return f'r8 {c}8 r8 {c}8', f'{S(lo1)}2'
        return f'r8 {c}8 r8 {c}8', f'{S(lo1)}4 {S(lo2)}4'
    if tex == 'chorale':
        msym = TO_MINOR[sym]
        top1 = min((x for x in range(m1 - 4, m1 + 5) if x % 12 in pcs(msym)), key=lambda x: abs(x - m1))
        top2 = min((x for x in range(m2 - 4, m2 + 5) if x % 12 in pcs(msym)), key=lambda x: abs(x - m2))
        mb = bass(msym)

        def blk(top):
            ns = [top, below(top, msym), below(top, msym, 2)]
            return '<' + ' '.join(spell(x, msym, True) for x in sorted(ns)) + '>'
        if held or last:
            return f'{blk(top1)}2', f'{spell(mb, msym, True)}2'
        return f'{blk(top1)}4 {blk(top2)}4', f'{spell(mb, msym, True)}2'
    if tex == 'triplets':
        if last:
            return f'{S(m1)}4 r4', f'{S(b)}4 r4'
        r = []
        for m in (m1, m2):
            r.append(f'\\tup3/2 {S(m)}8 {S(below(m, sym))} {S(below(m, sym, 2))} \\tupend')
        return ' '.join(r), f'{S(b)}4 {S(fifth)}4'
    if tex == 'dotted':
        if last:
            return f'{S(m1)}4 r4', f'{S(b)}4 {lh_chord(sym)}4'
        return (f'{S(m1)}8. {S(step(m1, 1, minor))}16 {S(m2)}8. {S(below(m2, sym))}16',
                f'{S(b)}4 {lh_chord(sym)}4')
    if tex == 'octaves':
        lb = bass(sym, 36, 47)
        l5 = lb + 7 if (lb + 7) % 12 in pcs(sym) else lb + 6
        lh = f'{S(lb)}16 {S(l5)} {S(lb + 12)} {S(l5)} {S(lb)} {S(l5)} {S(lb + 12)} {S(l5)}'
        if held or last:
            return f'<{S(m1)} {S(m1 + 12)}>2', lh
        return f'<{S(m1)} {S(m1 + 12)}>4 <{S(m2)} {S(m2 + 12)}>4', lh
    raise ValueError(tex)


def coda_bars():
    """16 bars: theme B-half in eighths, then a cadential chorale in A major"""
    out = []
    for k in range(8, 16):
        dsl, sym = THEME[k]
        out.append(bar('eighths', dsl, sym, False, k == 15))
    cad = [('A', 76), ('D', 78), ('E7', 74), ('A', 73), ('F#m', 73), ('D', 74), ('E7', 71), ('A', 69)]
    for k, (sym, top) in enumerate(cad):
        t = min((x for x in range(top - 4, top + 5) if x % 12 in pcs(sym)), key=lambda x: abs(x - top))
        blk = '<' + ' '.join(spell(x, sym, False) for x in sorted([t, below(t, sym), below(t, sym, 2)])) + '>'
        b = bass(sym)
        if k == 7:
            out.append((f'{blk}2', f'<{spell(b - 12, sym, False)} {spell(b, sym, False)}>2'))
        else:
            out.append((f'{blk}4 {blk}4', f'{spell(b, sym, False)}4 {lh_chord(sym)}4'))
    return out


def build_bars():
    bars = []      # dicts: rh, lh, sec, half, role ('n' | 'first' | 'second'), last
    for si, (head, tex, tempo, bpm, dyn, volta_half, minor, rep2) in enumerate(SECTIONS):
        if tex == 'coda':
            for k, (rh, lh) in enumerate(coda_bars()):
                bars.append(dict(rh=rh, lh=lh, sec=si, half=k // 8, role='n', k=k))
            continue
        for half in (0, 1):
            ks = list(range(8 * half, 8 * half + 8))
            for k in ks:
                dsl, sym = THEME[k]
                last = k % 8 == 7
                if volta_half == half and last:
                    fdsl, fsym = FIRST_ENDING[half]
                    rh, lh = bar(tex, fdsl, fsym, minor, False)
                    bars.append(dict(rh=rh, lh=lh, sec=si, half=half, role='first', k=k))
                    rh, lh = bar(tex, dsl, sym, minor, True)
                    bars.append(dict(rh=rh, lh=lh, sec=si, half=half, role='second', k=k))
                else:
                    rh, lh = bar(tex, dsl, sym, minor, last)
                    bars.append(dict(rh=rh, lh=lh, sec=si, half=half, role='n', k=k))
    # dynamics on the first bar of each section
    seen = set()
    for b in bars:
        if b['sec'] not in seen:
            seen.add(b['sec'])
            d = '\\' + SECTIONS[b['sec']][4]
            # attach to the first note or chord (a dynamic on a rest is not heard by the Voice in LilyPond)
            mm = re.match(r"^((?:\\tup\S+\s+)?(?:r\d*\.*\s+)*(?:<[^>]*>|[a-g][a-z',]*)\d*\.*)", b['rh'])
            b['rh'] = mm.group(1) + d + b['rh'][mm.end():]
    return bars


def make():
    bars = build_bars()
    pn = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((2, 4), (3, 'major'), [(pn, {'1': ' | '.join(b['rh'] for b in bars),
                                              '5': ' | '.join(b['lh'] for b in bars)})])
    m = sc.measures
    n = len(bars)
    sys_starts = []
    for i, b in enumerate(bars):
        head, tex, tempo, bpm, dyn, volta_half, minor, rep2 = SECTIONS[b['sec']]
        first_of_sec = i == 0 or bars[i - 1]['sec'] != b['sec']
        first_of_half = first_of_sec or bars[i - 1]['half'] != b['half']
        last_of_half = i == n - 1 or bars[i + 1]['half'] != b['half'] or bars[i + 1]['sec'] != b['sec']
        if first_of_sec:
            add_mark(sc, i, 'words', text=head, style='bold') if tex != 'coda' else None
            if tex == 'coda':
                add_mark(sc, i, 'coda')
                add_mark(sc, i, 'words', text='Coda', style='bold')
            if tempo:
                add_mark(sc, i, 'tempo', text=tempo, **({'unit': 'quarter', 'bpm': bpm} if bpm else {}))
            if tex == 'chorale':
                m[i].key = (0, 'minor')
            if SECTIONS[b['sec'] - 1][6] if b['sec'] > 0 else False:
                m[i].key = (3, 'major')
        # repeats: every half except the Theme's first half starts with a start repeat;
        # Var. VII repeats only its first half, the Coda none
        repeated = tex != 'coda' and (b['half'] == 0 or rep2)
        if first_of_half and repeated and not (b['sec'] == 0 and b['half'] == 0):
            m[i].left_bar = 'repeat-start'
        if b['role'] == 'first':
            m[i].volta_start, m[i].volta_end, m[i].right_bar = '1', 'stop', 'repeat-end'
        elif b['role'] == 'second':
            m[i].volta_start, m[i].volta_end, m[i].right_bar = '2', 'discontinue', 'double'
        elif last_of_half and repeated:
            m[i].right_bar = 'repeat-end'
        # systems: two per section half, 4 bars each (a half with 1st/2nd endings has 5 in its second system)
        if first_of_half:
            sys_starts += [i, i + 4]
    sys_starts = sorted(set(sys_starts))
    assert len(sys_starts) == 36, len(sys_starts)
    for j, i in enumerate(sys_starts):
        if i == 0:
            continue
        m[i].brk = 'page' if j % 3 == 0 else 'system'
    # jumps
    add_end_mark(sc, 7, 'To Coda', style='italic', coda_sign=True, sound={'tocoda': 'coda'})
    v7_last = max(i for i, b in enumerate(bars) if SECTIONS[b['sec']][1] == 'octaves')
    m[v7_last].right_bar = 'double'
    add_end_mark(sc, v7_last, 'D.C. al Coda', style='bold-italic', sound={'dacapo': 'yes'})
    m[-1].right_bar = 'final'
    sc.title = 'Theme and Variations in A'
    sc.composer = 'Coverage corpus (2026)'
    sc.rights = 'CC0 1.0'
    sc.n_systems = len(sys_starts)
    lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]}]}
    opts = {'header': {'title': 'Theme and Variations in A', 'subtitle': 'for piano',
                       'composer': 'Coverage corpus (2026)', 'copyright': 'CC0 1.0'},
            'staff_size': 23, 'paper': 'a4', 'forced_breaks': True,
            'paper_extra': ['indent = 12\\mm', 'ragged-bottom = ##t', 'system-system-spacing.basic-distance = #22',
                            'oddHeaderMarkup = \\markup \\fill-line { "" \\unless \\on-first-page '
                            '\\italic "Theme and Variations in A" \\if \\should-print-page-number '
                            '\\fromproperty #\'page:page-number-string }',
                            'evenHeaderMarkup = \\markup \\fill-line { \\if \\should-print-page-number '
                            '\\fromproperty #\'page:page-number-string \\unless \\on-first-page '
                            '\\italic "Theme and Variations in A" "" }']}
    return sc, lay, opts


ITEM = dict(
    id='str08-variations-twelve-pages-piano',
    title='Theme and Variations in A - 12-page piano score: repeats in every section, endings, key changes, '
          'To Coda on page 1 and D.C. al Coda on page 11',
    make=make, pages=12, layout='piano', must_not_split=True,
    focus=['multi-page', 'page-break', 'system-break', 'repeat-start', 'repeat-end', 'volta-1', 'volta-2', 'dc',
           'coda', 'x-to-coda', 'barline-double', 'barline-final'],
    expect_counts={'multi-page': 12, 'page-break': 11, 'system-break': 24, 'repeat-start': 14, 'repeat-end': 15,
                   'volta-1': 2, 'volta-2': 2, 'dc': 1, 'coda': 2, 'x-to-coda': 1, 'barline-double': 3,
                   'barline-final': 1, 'key-change': 2},
    structure=('146 bars, 36 systems, 3 per page (page breaks before every 3rd system). Thema mm.1-16 (||: implied '
               ':|| ||: :||, "To Coda" + coda sign after m.8); Var. I mm.17-32; Var. II mm.33-49 (1st ending m.40, '
               '2nd ending m.41 + double bar); Var. III mm.50-65; Var. IV Minore mm.66-81 (A minor); Var. V Maggiore '
               'mm.82-98 (A major, 1st ending m.97, 2nd ending m.98); Var. VI mm.99-114; Var. VII mm.115-130 (only the '
               'first half repeated; double bar + "D.C. al Coda" after m.130); Coda sign + Coda mm.131-146, final bar. '
               'Every start+end repeat between sections falls on a system break and is split by the line break. '
               'Played form: Thema and Var. I-VII with repeats, then D.C.: mm.1-8, jump to the Coda (m.131).'),
    expected_notes=('One part (Piano), grand staff, must NOT be split. 2/4 throughout. Key A major (3 sharps); Var. IV '
                    'in A minor (0 sharps, key change with cancellation naturals), Var. V back to A major. Section '
                    'headings (Thema, Var. I ...) are bold text; tempo texts Andante (quarter = 69), Adagio (quarter = '
                    '50), Tempo I, Più mosso. Running header with title and page number on pages 2-12.'),
    notes=('Truth limitations: (1) running headers and page numbers are not encoded as <credit>s; (2) the courtesy '
           'key signature at the end of the system before Var. IV / Var. V and the cancellation naturals are implied '
           'by <key> (no <cancel> element is written); (3) whether repeats are taken after the D.C. is not encoded.'),
    attribution='\n'.join(['"Theme and Variations in A" for piano (theme and variations composed for this corpus, '
                           '2026) - CC0 1.0.', '', CC0_NOTE]),
    scans={
        'scan.pdf': {'seed': 48001, 'summary': '12 pages from a sheet feeder, 200 dpi grey, small random skew per '
                     'page, paper texture, noise, JPEG q70',
                     'params': dict(dpi=200, mode='gray', texture=3,
                                    rotate_pages={0: 0.4, 1: -0.6, 2: 0.9, 3: -0.3, 4: 0.7, 5: -1.0, 6: 0.5,
                                                  7: -0.2, 8: 0.8, 9: -0.7, 10: 0.3, 11: -0.5},
                                    blur=0.4, noise=4, jpeg=70)},
        'scan-severe.pdf': {'seed': 48002, 'summary': 'ring-binder photocopies at 150 dpi: punch holes, skew -4..5 '
                            'deg per page, page 6 upside down, pages 3 and 9 at a different scale, strong '
                            'bleed-through, binarised with speckles',
                            'params': dict(dpi=300, out_dpi=150, punch_holes={'n': 3, 'side': 'left', 'level': 25},
                                           rotate_pages={0: 2.0, 1: -3.0, 2: 4.5, 3: -1.5, 4: 3.5, 5: -4.0, 6: 2.8,
                                                         7: -2.2, 8: 5.0, 9: -3.6, 10: 1.8, 11: -2.7},
                                           page_rotate={5: 180}, scale_pages={2: 0.96, 8: 1.03}, bleed=0.12,
                                           ink_dropout=0.08, blur=0.7, noise=9, binarize=125, binarize_noise=18,
                                           speckle=80, format='png1')},
    },
)
