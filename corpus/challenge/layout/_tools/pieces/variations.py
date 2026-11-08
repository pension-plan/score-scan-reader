"""L1: Theme and eight variations on 'Ah! vous dirai-je, maman' (PD French melody, 1761) for piano,
12 pages: running headers + page numbers, a heading/tempo text per variation, plain repeats and
1st/2nd endings, key change (minore/maggiore), time change 2/4 -> 6/8, triplets, pedal marks.
Textures are generated from a per-beat harmonic plan (CC0)."""
from __future__ import annotations

from .common import CC0_NOTE, add_mark, assemble, from_midi_spelled, lyp, mk_part, set_time
from lsynth.harmonize import chord_tones
from lsynth.model import STEP_PC

MAJ = [0, 2, 4, 5, 7, 9, 11]
MIN = [0, 2, 3, 5, 7, 8, 10]
NAT = {0: ('C', 0), 2: ('D', 0), 4: ('E', 0), 5: ('F', 0), 7: ('G', 0), 9: ('A', 0), 11: ('B', 0)}
FLAT = {**NAT, 3: ('E', -1), 8: ('A', -1), 10: ('B', -1), 1: ('D', -1), 6: ('F', 1)}

MEL_MAJ_A = [[72, 72], [79, 79], [81, 81], [79, None], [77, 77], [76, 76], [74, 74], [72, None]]
MEL_MAJ_B = [[79, 79], [77, 77], [76, 76], [74, None], [79, 79], [77, 77], [76, 76], [74, None]]
MEL_MIN_A = [[72, 72], [79, 79], [80, 80], [79, None], [77, 77], [75, 75], [74, 74], [72, None]]
MEL_MIN_B = [[79, 79], [77, 77], [75, 75], [74, None], [79, 79], [77, 77], [75, 75], [74, None]]
CH_MAJ_A = [['C', 'C'], ['C', 'C'], ['F', 'F'], ['C', 'C'], ['G7', 'G7'], ['C', 'C'], ['Dm', 'G7'], ['C', 'C']]
CH_MAJ_B = [['C', 'C'], ['G7', 'G7'], ['C', 'C'], ['G', 'G'], ['C', 'C'], ['Dm', 'G7'], ['C', 'Am'], ['G', 'G7']]
CH_MIN_A = [['Cm', 'Cm'], ['Cm', 'Cm'], ['Fm', 'Fm'], ['Cm', 'Cm'], ['G7', 'G7'], ['Cm', 'Cm'], ['Ddim', 'G7'],
            ['Cm', 'Cm']]
CH_MIN_B = [['Cm', 'Cm'], ['G7', 'G7'], ['Cm', 'Cm'], ['G', 'G'], ['Cm', 'Cm'], ['Ddim', 'G7'], ['Cm', 'Ab'],
            ['G', 'G7']]
# 1st ending: C then G (leads back), 2nd ending: C held
E1_MEL, E1_CH = [72, 67], ['C', 'G7']
E2_MEL, E2_CH = [72, None], ['C', 'C']


def sp(m, minor, tones=None):
    if tones:
        for st, al in tones:
            if (STEP_PC[st] + al) % 12 == m % 12:
                return from_midi_spelled(m, tones)
    st, al = (FLAT if minor else NAT)[m % 12]
    return from_midi_spelled(m, [(st, al)])


def P(m, minor, sym=None):
    tones = chord_tones(sym)[0] if sym else None
    return lyp(sp(m, minor, tones))


def tones_midi(sym, lo, hi):
    tones, bass, q = chord_tones(sym)
    pcs = [(STEP_PC[s] + a) % 12 for s, a in tones]
    return [m for m in range(lo, hi + 1) if m % 12 in pcs], tones, bass


def ct_below(sym, m, k=1):
    cands, _, _ = tones_midi(sym, 30, m - 1)
    return cands[-k]


def scale_step(m, minor, d, sym=None):
    pcs = MIN if minor else MAJ
    if minor and sym and sym.startswith('G'):
        pcs = [0, 2, 3, 5, 7, 8, 11]
    x = m
    for _ in range(abs(d)):
        x += 1 if d > 0 else -1
        while x % 12 not in pcs:
            x += 1 if d > 0 else -1
    return x


def chord_close(sym, center, below=None):
    cands, tones, bass = tones_midi(sym, 36, 84)
    k = min(3, len(tones))
    best = None
    for i in range(len(cands) - k + 1):
        win = cands[i:i + k]
        if len({x % 12 for x in win}) != k:
            continue
        if below is not None and win[-1] >= below:
            continue
        s = abs(sum(win) / k - center)
        if best is None or s < best[0]:
            best = (s, win)
    return best[1], tones


def ch(ms, tones, dur):
    if len(ms) == 1:
        return lyp(from_midi_spelled(ms[0], tones)) + dur
    return '<' + ' '.join(lyp(from_midi_spelled(m, tones)) for m in ms) + '>' + dur


def bass(sym, lo=36, hi=47):
    tones, b, q = chord_tones(sym)
    for m in range(lo, hi + 1):
        if (STEP_PC[b[0]] + b[1]) % 12 == m % 12:
            return m, tones
    raise ValueError(sym)


# ------------------------------------------------------------------ textures (one 2/4 bar each)

def tex(v, mel, chs, minor, last=False):
    """v: texture id; mel: [m1, m2|None]; chs: [sym1, sym2] -> (rh, lh) dsl for one bar"""
    held = mel[1] is None
    m1 = mel[0]
    m2 = mel[0] if held else mel[1]
    t1 = chord_tones(chs[0])[0]
    t2 = chord_tones(chs[1])[0]
    if v == 'theme':
        rh = f'{P(m1, minor, chs[0])}2' if held else f'{P(m1, minor, chs[0])}4 {P(m2, minor, chs[1])}'
        if held:
            c, t = chord_close(chs[0], 52)
            lh = ch(c, t, '2')
        else:
            c1, ta = chord_close(chs[0], 52)
            c2, tb = chord_close(chs[1], 52)
            lh = ch(c1, ta, '4') + ' ' + ch(c2, tb, '4')
        return rh, lh
    if v == 'I':
        def fig(m, sym):
            return (f'{P(m, minor, sym)}16[ {P(scale_step(m, minor, 1, sym), minor)} {P(m, minor, sym)} '
                    f'{P(scale_step(m, minor, -1, sym), minor)}]')
        rh = fig(m1, chs[0]) + ' ' + (f'{P(m2, minor, chs[1])}4' if held else fig(m2, chs[1]))
        b, tb = bass(chs[0], 43, 54)
        c2, tc = chord_close(chs[1], 57, below=None)
        lh = ch([b], tb, '4') + ' ' + ch(c2[1:], tc, '4')
        return rh, lh
    if v == 'II':
        def top(m, sym, d):
            return ch([ct_below(sym, m), m], chord_tones(sym)[0], d)
        rh = top(m1, chs[0], '2') if held else top(m1, chs[0], '4') + ' ' + top(m2, chs[1], '4')

        def alb(sym):
            r, tt = bass(sym, 41, 52)
            cands, _, _ = tones_midi(sym, r, r + 12)
            fifth = [x for x in cands if (x - r) in (6, 7)]
            third = [x for x in cands if (x - r) in (3, 4)]
            f_ = fifth[0] if fifth else cands[-1]
            t_ = third[0] if third else cands[1]
            return (f'{lyp(from_midi_spelled(r, tt))}16[ {lyp(from_midi_spelled(f_, tt))} '
                    f'{lyp(from_midi_spelled(t_, tt))} {lyp(from_midi_spelled(f_, tt))}]')
        lh = alb(chs[0]) + ' ' + alb(chs[1])
        return rh, lh
    if v == 'III':
        def trip(m, sym):
            a = ct_below(sym, m, 1)
            b = ct_below(sym, m, 2)
            tt = chord_tones(sym)[0]
            return (f'\\tup3/2 {P(m, minor, sym)}8[ {lyp(from_midi_spelled(a, tt))} '
                    f'{lyp(from_midi_spelled(b, tt))}] \\tupend')
        rh = trip(m1, chs[0]) + ' ' + (f'{P(m2, minor, chs[1])}4' if held else trip(m2, chs[1]))
        b1, ta = bass(chs[0], 36, 47)
        b2, tb = bass(chs[1], 36, 47)
        lh = f'{lyp(from_midi_spelled(b1, ta))}4 {lyp(from_midi_spelled(b2 - 12 if b2 > 43 else b2, tb))}4'
        return rh, lh
    if v == 'IV':
        rh = (ch([m1 - 12, m1], t1, '2') if held else ch([m1 - 12, m1], t1, '4') + ' ' + ch([m2 - 12, m2], t2, '4'))

        def arp(sym):
            r, tt = bass(sym, 36, 47)
            cands, _, _ = tones_midi(sym, r + 1, r + 12)
            return (f'\\tup3/2 {lyp(from_midi_spelled(r, tt))}8[ {lyp(from_midi_spelled(cands[0], tt))} '
                    f'{lyp(from_midi_spelled(cands[1], tt))}] \\tupend')
        lh = arp(chs[0]) + ' ' + arp(chs[1])
        return rh, lh
    if v == 'V':
        def dot(m, sym):
            return f'{P(m, minor, sym)}8.[ {P(scale_step(m, minor, 1, sym), minor)}16]'
        rh = dot(m1, chs[0]) + ' ' + (f'{P(m2, minor, chs[1])}4' if held else dot(m2, chs[1]))

        def oom(sym):
            b, tb = bass(sym, 36, 47)
            c, tc = chord_close(sym, 55)
            return f'{lyp(from_midi_spelled(b, tb))}8[ ' + ch(c[1:], tc, '8') + ']'
        lh = oom(chs[0]) + ' ' + oom(chs[1])
        return rh, lh
    if v == 'VI':
        def blk(m, sym, d):
            c, tc = chord_close(sym, m - 5, below=m)
            return ch(c[-2:] + [m], tc, d)
        rh = blk(m1, chs[0], '2') if held else blk(m1, chs[0], '4') + ' ' + blk(m2, chs[1], '4')

        def run(sym):
            r, tt = bass(sym, 36, 45)
            seq = [r]
            for _ in range(3):
                seq.append(scale_step(seq[-1], minor, 1, sym))
            out = [lyp(sp(x, minor, tt)) for x in seq]
            return f'{out[0]}16[ {out[1]} {out[2]} {out[3]}]'
        lh = run(chs[0]) + ' ' + run(chs[1])
        return rh, lh
    if v == 'VII':
        def turn(m, sym):
            return f'{P(m, minor, sym)}8[ {P(scale_step(m, minor, 1, sym), minor)}16 {P(m, minor, sym)}]'
        rh = turn(m1, chs[0]) + ' ' + (f'{P(m2, minor, chs[1])}4' if held else turn(m2, chs[1]))

        def oom(sym):
            b, tb = bass(sym, 36, 47)
            c, tc = chord_close(sym, 55)
            return f'{lyp(from_midi_spelled(b, tb))}8[ ' + ch(c[1:], tc, '8') + ']'
        lh = oom(chs[0]) + ' ' + oom(chs[1])
        return rh, lh
    if v == 'VIII':   # 6/8
        def beat(m, sym):
            lo = ct_below(sym, m, 2)
            return f'{P(m, minor, sym)}4 {lyp(from_midi_spelled(lo, chord_tones(sym)[0]))}8'
        rh = beat(m1, chs[0]) + ' ' + (f'{P(m2, minor, chs[1])}4.' if held else beat(m2, chs[1]))

        def lb(sym):
            b, tb = bass(sym, 36, 47)
            c, tc = chord_close(sym, 55)
            return f'{lyp(from_midi_spelled(b, tb))}8[ ' + ch(c[1:], tc, '8') + ' ' + ch(c[1:], tc, '8') + ']'
        lh = lb(chs[0]) + ' ' + lb(chs[1])
        return rh, lh
    raise ValueError(v)


VARS = [
    # id, heading, tempo text, bpm, minor, voltas, dynamics(rh first), pedal
    ('theme', 'Thema', 'Andante', 76, False, False, '\\p', False),
    ('I', 'Var. I', 'Poco più mosso', None, False, False, '\\mf', False),
    ('II', 'Var. II', None, None, False, True, '\\p', False),
    ('III', 'Var. III', 'Leggiero', None, False, False, '\\mp', False),
    ('IV', 'Var. IV', 'Energico', None, False, True, '\\f', True),
    ('V', 'Var. V - Minore', 'Andante espressivo', 66, True, False, '\\p', False),
    ('VI', 'Var. VI - Maggiore', 'Allegretto', 96, False, True, '\\f', False),
    ('VII', 'Var. VII', 'Adagio cantabile', 50, False, False, '\\pp', True),
    ('VIII', 'Var. VIII - Finale', 'Allegro', 112, False, True, '\\f', False),
]

CODA_RH = ("<e' g' c''>4. <f' a' c''>4. | <d' f' b'>4. <e' g' c''>4. | <c'' e'' g''>4.^\"cresc.\" <c'' f'' a''>4. | "
           "<b' d'' g''>4. <b' d'' f''>4. | <c'' e'' g'' c'''>4.\\ff r4. | <f' a' c'' f''>4.^\"rit.\" <g' b' d'' g''>4. | "
           "<e' g' c'' e''>2. | <e' g' c'' e''>2.\\fermata")
CODA_LH = ("c8[ <e g> <e g>] f,8[ <f a> <f a>] | g,8[ <f g b> <f g b>] c8[ <e g> <e g>] | "
           "c8[ <e g> <e g>] f8[ <a c'> <a c'>] | g8[ <b d'> <b d'>] g,8[ <b, d f> <b, d f>] | "
           "<c, c>4. r4. | <f, f>4. <g, g>4. | <c, c>2. | <c, g, c>2.\\fermata")


def build():
    rh_bars, lh_bars, meta = [], [], []
    for (vid, head, tempo, bpm, minor, voltas, dyn, pedal) in VARS:
        A = MEL_MIN_A if minor else MEL_MAJ_A
        B = MEL_MIN_B if minor else MEL_MAJ_B
        CA = CH_MIN_A if minor else CH_MAJ_A
        CB = CH_MIN_B if minor else CH_MAJ_B
        e1c = ['Cm', 'G7'] if minor else E1_CH
        e2c = ['Cm', 'Cm'] if minor else E2_CH
        seq = []   # (mel, chords, tags)
        if voltas:
            for k in range(7):
                seq.append((A[k], CA[k], {'sec': 'A', 'k': k}))
            seq.append((E1_MEL, e1c, {'sec': 'A', 'end': 1}))
            seq.append((E2_MEL, e2c, {'sec': 'A', 'end': 2}))
            for k in range(8):
                seq.append((B[k], CB[k], {'sec': 'B', 'k': k}))
            for k in range(7):
                seq.append((A[k], CA[k], {'sec': 'A2', 'k': k}))
            seq.append((E1_MEL, e1c, {'sec': 'A2', 'end': 1}))
            seq.append((E2_MEL, e2c, {'sec': 'A2', 'end': 2, 'last': True}))
        else:
            for k in range(8):
                seq.append((A[k], CA[k], {'sec': 'A', 'k': k}))
            for k in range(8):
                seq.append((B[k], CB[k], {'sec': 'B', 'k': k}))
            for k in range(8):
                seq.append((A[k], CA[k], {'sec': 'A2', 'k': k, 'last': k == 7}))
        for j, (mel, chs, tag) in enumerate(seq):
            rh, lh = tex(vid, mel, chs, minor)
            if j == 0:
                rh = _add_suffix(rh, dyn)
            if pedal:
                lh = _add_suffix(lh, '\\sustainOn' if j == 0 else '\\sustainOff\\sustainOn')
                if tag.get('last'):
                    lh = _add_suffix_last(lh, '\\sustainOff')
            if vid == 'V' and tag.get('sec') == 'B' and tag.get('k') == 0:
                rh = _add_suffix(rh, '\\<')
            if vid == 'V' and tag.get('sec') == 'B' and tag.get('k') == 2:
                rh = _add_suffix(rh, '\\!')
            if vid in ('I', 'VI') and tag.get('sec') == 'B' and tag.get('k') == 4:
                lh = _add_suffix(lh, '_"cresc."')
            if vid == 'VII' and tag.get('last'):
                rh = _add_suffix_last(rh, '\\fermata')
                lh = _add_suffix_last(lh, '\\fermata')
            rh_bars.append(rh)
            lh_bars.append(lh)
            meta.append((vid, head, tempo, bpm, minor, voltas, j, tag))
    for r, l in zip(CODA_RH.split('|'), CODA_LH.split('|')):
        rh_bars.append(r.strip())
        lh_bars.append(l.strip())
        meta.append(('coda', None, None, None, False, False, None, {'sec': 'coda'}))
    return rh_bars, lh_bars, meta


def _toks(bar):
    import re
    return re.findall(r'(?<!\\)<[^<>]*>\S*|\S+', bar)


def _add_suffix(bar, suf):
    toks = _toks(bar)
    for i, t in enumerate(toks):
        if not t.startswith('\\'):
            # insert before beam/end markers is not needed: suffix order is free
            toks[i] = t + suf
            break
    return ' '.join(toks)


def _add_suffix_last(bar, suf):
    toks = _toks(bar)
    for i in range(len(toks) - 1, -1, -1):
        if not toks[i].startswith('\\'):
            toks[i] = toks[i] + suf
            break
    return ' '.join(toks)


TITLE = 'Variations on "Ah! vous dirai-je, maman"'
HEADER_ODD = 'Variations on "Ah! vous dirai-je, maman"'
HEADER_EVEN = 'Theme and eight variations for piano'
SYS_PER_PAGE = 5
FIRST_PAGE_SYS = 4


def make():
    rh_bars, lh_bars, meta = build()
    p = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((2, 4), (0, 'major'), [(p, {'1': ' | '.join(rh_bars), '5': ' | '.join(lh_bars)})])
    # structure: repeats, voltas, headings, keys, time, breaks
    nsys = 0
    sys_in_var = 0
    systems = []   # start indices
    prev_vid = None
    for i, (vid, head, tempo, bpm, minor, voltas, j, tag) in enumerate(meta):
        mi = sc.measures[i]
        if vid != prev_vid:
            if vid != 'coda':
                add_mark(sc, i, 'words', text=head, style='bold')
                if tempo:
                    add_mark(sc, i, 'tempo', text=tempo, unit='quarter' if vid != 'VIII' else 'quarter',
                             bpm=bpm, dots=1 if vid == 'VIII' else 0)
                if vid == 'V':
                    mi.key = (-3, 'minor')
                if vid == 'VI':
                    mi.key = (0, 'major')
                if vid == 'VIII':
                    set_time(sc, i, (6, 8))
            else:
                add_mark(sc, i, 'words', text='Coda', style='bold')
                add_mark(sc, i, 'tempo', text='Più allegro')
            systems.append(i)
            sys_in_var = 0
            prev_vid = vid
        elif vid != 'coda' and sys_in_var == 4:
            systems.append(i)
            sys_in_var = 0
        sys_in_var += 1
        if tag.get('sec') in ('A', 'B', 'A2') and tag.get('k', -1) == 0 and tag['sec'] in ('A', 'B'):
            mi.left_bar = 'repeat-start'
        if tag.get('end') == 1:
            mi.volta_start = '1'
            mi.volta_end = 'stop'
            mi.right_bar = 'repeat-end'
        if tag.get('end') == 2:
            mi.volta_start = '2'
            mi.volta_end = 'discontinue'
        if not voltas and tag.get('sec') == 'A' and tag.get('k') == 7:
            mi.right_bar = 'repeat-end'
        if not voltas and tag.get('last'):
            mi.right_bar = 'repeat-end'
        if voltas and tag.get('last') and vid == 'VIII':
            mi.right_bar = 'double'
    sc.measures[-1].right_bar = 'final'
    # page / system breaks
    for k, s in enumerate(systems):
        if k == 0:
            continue
        page_k = FIRST_PAGE_SYS if k == FIRST_PAGE_SYS else None
        if k == FIRST_PAGE_SYS or (k > FIRST_PAGE_SYS and (k - FIRST_PAGE_SYS) % SYS_PER_PAGE == 0):
            sc.measures[s].brk = 'page'
        else:
            sc.measures[s].brk = 'system'
    npages = 1 + -(-(len(systems) - FIRST_PAGE_SYS) // SYS_PER_PAGE)
    sc.title = TITLE
    sc.composer = 'Theme: French folk melody (1761); variations: layout-challenge corpus (CC0)'
    sc.rights = 'Dedicated to the public domain (CC0 1.0)'
    sc.credits = [{'page': 1, 'type': 'title', 'text': TITLE},
                  {'page': 1, 'type': 'subtitle', 'text': 'Theme and eight variations for piano'},
                  {'page': 1, 'type': 'composer', 'text': 'Theme: French folk melody (1761)'},
                  {'page': 1, 'type': 'arranger', 'text': 'Variations: layout-challenge corpus (2026)'},
                  {'page': 1, 'type': 'rights', 'text': 'Dedicated to the public domain (CC0 1.0) - page 1 of '
                                                        f'{npages}'}]
    for pg in range(2, npages + 1):
        sc.credits.append({'page': pg, 'type': 'header', 'text': HEADER_ODD if pg % 2 else HEADER_EVEN})
        sc.credits.append({'page': pg, 'type': 'page number', 'text': str(pg)})
    lay = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]}]}
    opts = {'header': {'title': TITLE, 'subtitle': 'Theme and eight variations for piano',
                       'composer': 'Theme: French folk melody (1761)',
                       'arranger': 'Variations: layout-challenge corpus (2026)',
                       'copyright': f'Dedicated to the public domain (CC0 1.0) - page 1 of {npages}'},
            'staff_size': 19, 'paper': 'a4', 'font': 'TeX Gyre Schola', 'forced_breaks': True,
            'paper_extra': [
                'left-margin = 24\\mm', 'indent = 12\\mm', 'ragged-last = ##f', 'ragged-bottom = ##f',
                'print-first-page-number = ##f',
                'oddHeaderMarkup = \\markup \\fill-line { \\null \\unless \\on-first-page \\italic '
                '"' + HEADER_ODD.replace('"', '\\"') + '" \\unless \\on-first-page \\bold '
                '\\fromproperty #\'page:page-number-string }',
                'evenHeaderMarkup = \\markup \\fill-line { \\unless \\on-first-page \\bold '
                '\\fromproperty #\'page:page-number-string \\unless \\on-first-page \\italic "'
                + HEADER_EVEN + '" \\null }',
                'oddFooterMarkup = \\markup \\fill-line { \\if \\on-first-page \\fromproperty #\'header:copyright }',
                'evenFooterMarkup = ##f',
                'system-system-spacing.basic-distance = #13',
            ],
            'layout_extra': []}
    return sc, lay, opts, npages


def make_item():
    def mk():
        sc, lay, opts, n = make()
        return sc, lay, opts
    return mk


ITEM = dict(
    id='variations-piano-12-pages',
    title='Variations on "Ah! vous dirai-je, maman" - 12-page piano score with headers, voltas, key/time changes',
    make=make_item(), pages=12,
    edge_cases=['multi_page_10plus', 'page_numbers', 'running_headers', 'title_block_text', 'copyright_footer',
                'tempo_text', 'section_heading_text', 'dynamics_text', 'repeats', 'volta_1st_2nd_endings',
                'key_change', 'time_change', 'triplets', 'pedal_marks', 'piano_grand_staff', 'must_not_split',
                'variation_starts_new_system', 'fermata', 'hairpin', 'cautionary_key_signature'],
    must_not_split=True,
    expected_notes=('One part: Piano with 2 staves, the grand staff must stay ONE part on every one of the 12 pages. '
                    'Measures are in notated order (repeats and 1st/2nd endings NOT unrolled): 232 measures. '
                    'Running headers, page numbers, the title block, "Var. ..." headings, tempo words, "cresc." and '
                    'the copyright footer are text, not notes or lyrics. Key changes to C minor (Var. V) and back '
                    '(Var. VI); time signature changes to 6/8 at Var. VIII. No lyrics.'),
    truth_limitations=('Beaming not encoded. Page headers/numbers are <credit> elements without coordinates. '
                       'Repeats/voltas are encoded in notated order (<repeat>, <ending>), not unrolled.'),
    layout_desc='A4 portrait, staff size 19, 4 systems on page 1 and 5 per following page, each variation starts a '
                'new system; headers on pages 2-12 alternate odd/even text with page numbers',
    license='Public domain melody; variations, engraving and scans CC0-1.0',
    source='self-authored (layout-challenge corpus); theme: French melody "Ah! vous dirai-je, maman" (1761)',
    attribution='\n'.join(['Theme: "Ah! vous dirai-je, maman", French folk melody first printed 1761 - public domain.',
                           'Variations generated for this corpus from a harmonic plan - CC0 1.0.', '', CC0_NOTE]),
)
