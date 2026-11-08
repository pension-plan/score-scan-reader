"""Multi-page piano book "Forty Variations" (own composition, procedurally generated, CC0).

Page k (1-based) is variation k: one of 22 textures (chorale, Alberti bass, toccata, waltz,
barcarolle, triplets, octaves with ottava, two-voice duet, sarabande, 32nd-note etude, pastorale,
march, siciliano, 5/4, 7/8, tremolo, clef study, sextuplets, quintuplets, grace notes, arpeggios,
chorale with breath marks) in its own key (all 15 major and 15 minor key signatures are cycled)
and metre, with its own tempo / metronome mark, rehearsal number, dynamics, hairpins, slurs,
articulations and pedal marks.  Harmony: 4-bar phrases from a small progression table, including
secondary dominants (chromatic accidentals) and harmonic-minor dominants; courtesy accidentals
are added where an altered note returns to the key signature in the next bar.
A document of N pages = variations 1..N (page 1 has the title and one system less).
"""
from __future__ import annotations

import random
from fractions import Fraction as F

from cov.dsl import parse_voice
from cov.lily import pitch_ly
from cov.model import STEP_PC, STEPS, midi

from .common import CC0_NOTE, PAPER, add_mark, assemble, finish_measures, mk_part, set_time

MAJ = [0, 2, 4, 5, 7, 9, 11]
MIN = [0, 2, 3, 5, 7, 8, 10]
KEYS = [  # (fifths, mode, tonic step, tonic alter)
    (0, 'major', 'C', 0), (1, 'major', 'G', 0), (-3, 'minor', 'C', 0), (2, 'major', 'D', 0),
    (-1, 'major', 'F', 0), (3, 'major', 'A', 0), (-2, 'minor', 'G', 0), (-4, 'major', 'A', -1),
    (4, 'major', 'E', 0), (0, 'minor', 'A', 0), (-2, 'major', 'B', -1), (5, 'major', 'B', 0),
    (1, 'minor', 'E', 0), (-5, 'major', 'D', -1), (6, 'major', 'F', 1), (-1, 'minor', 'D', 0),
    (-3, 'major', 'E', -1), (2, 'minor', 'B', 0), (-6, 'major', 'G', -1), (7, 'major', 'C', 1),
    (-4, 'minor', 'F', 0), (3, 'minor', 'F', 1), (-7, 'major', 'C', -1), (4, 'minor', 'C', 1),
    (-5, 'minor', 'B', -1), (5, 'minor', 'G', 1), (-6, 'minor', 'E', -1), (6, 'minor', 'D', 1),
    (-7, 'minor', 'A', -1), (7, 'minor', 'A', 1),
]
# phrase progressions: degree (0 = I) or ('V/', degree) secondary dominant
PROGS = [[0, 5, 1, 4], [0, 3, 4, 0], [5, 3, 0, 4], [0, ('V/', 4), 4, 0], [0, 2, 3, 4], [1, 4, 0, 0],
         [0, ('V/', 1), 1, 4], [3, 4, 5, ('V/', 4)], [0, 4, 5, 3], [('V/', 3), 3, 4, 0]]


# --------------------------------------------------------------------------- harmony helpers

CTX = {'v': 1}


def second_pass():
    return CTX['v'] > len(TEXTURES)


def spell(step, pc):
    alter = (pc - STEP_PC[step] + 6) % 12 - 6
    return (step, alter)


class Key:
    def __init__(self, fifths, mode, tstep, talt):
        self.fifths, self.mode = fifths, mode
        self.tpc = (STEP_PC[tstep] + talt) % 12
        iv = MAJ if mode == 'major' else MIN
        i0 = STEPS.index(tstep)
        self.scale = [spell(STEPS[(i0 + i) % 7], (self.tpc + iv[i]) % 12) for i in range(7)]

    def chord(self, deg, seventh=False):
        """chord tones [(step, alter)] root first"""
        if isinstance(deg, tuple):          # secondary dominant V7 of degree deg[1]
            tgt = self.scale[deg[1] % 7]
            ri = (STEPS.index(tgt[0]) + 4) % 7
            rpc = (STEP_PC[tgt[0]] + tgt[1] + 7) % 12
            return [spell(STEPS[(ri + 2 * k) % 7], (rpc + iv) % 12) for k, iv in enumerate((0, 4, 7, 10))]
        tones = [self.scale[(deg + 2 * k) % 7] for k in range(4 if seventh else 3)]
        if self.mode == 'minor' and deg in (4, 6):      # harmonic minor: raised leading tone
            lead = self.scale[6]
            tones = [(s, a + 1) if (s, a) == lead else (s, a) for s, a in tones]
        return tones


def place(sa, lo):
    """lowest pitch with this (step, alter) whose midi >= lo"""
    s, a = sa
    for o in range(0, 9):
        p = (s, a, o)
        if midi(p) >= lo:
            return p
    raise ValueError(sa)


def stack(tones, lo, n):
    """n ascending chord tones starting at/above lo cycling through tones"""
    out = []
    cur = lo
    k = 0
    while len(out) < n:
        p = place(tones[k % len(tones)], cur)
        out.append(p)
        cur = midi(p) + 1
        k += 1
    return out


def upper_neighbour(k, p):
    """the next scale step above pitch p (diatonic in key k)"""
    letters = [x[0] for x in k.scale]
    j = (letters.index(p[0]) + 1) % 7
    return place(k.scale[j], midi(p) + 1)


def L(p):
    return pitch_ly(p)


def C(ps):
    return '<' + ' '.join(pitch_ly(p) for p in ps) + '>' if len(ps) > 1 else pitch_ly(ps[0])


# --------------------------------------------------------------------------- textures
# each: (name, time, symbol, tempo text, unit, bpm, dots, fn(key, chord, nxt, pos, ph, rng) -> (rh1, rh2, lh))
# pos = bar position inside the 4-bar phrase (0..3), ph = phrase index on the page

def t_chorale(k, ch, nx, pos, ph, rng):
    rh = stack(ch[:3], 67, 3)
    bass = place(ch[0], 36)
    if pos == 3:
        return f"{C(rh)}1\\fermata", None, f"<{L(bass)} {L((bass[0], bass[1], bass[2] + 1))}>1\\fermata"
    rh2 = stack(ch[:3], 69, 3)
    return (f"{C(rh)}4-- {C(rh2)}4 {C(rh)}2", None,
            f"<{L(bass)} {L((bass[0], bass[1], bass[2] + 1))}>2 {L(place(ch[2], 43))}2")


def t_alberti(k, ch, nx, pos, ph, rng):
    r, t, f = place(ch[0], 43), place(ch[1], 50), place(ch[2], 46)
    lh = ' '.join([L(r) + '8', L(f), L(t), L(f)] * 2)
    m = stack(ch[:3], 67, 4)
    if pos == 3:
        return f"{L(m[0])}2 {L(m[1])}4-. r4", None, lh
    return f"{L(m[2])}4( {L(m[1])}8 {L(m[0])}8) {L(m[1])}4-. {L(m[3])}4-.", None, lh


def t_toccata(k, ch, nx, pos, ph, rng):
    up = stack(ch[:3], 67, 4)
    seq = up + up[::-1]
    rh = ' '.join(L(p) + ('16->' if j == 0 else '16') for j, p in enumerate(seq))
    lc = stack(ch[:3], 48, 2)
    lh = ' '.join([f"{C(lc)}8-." for _ in range(4)])
    return rh, None, lh


def t_valse(k, ch, nx, pos, ph, rng):
    b = place(ch[0], 38)
    lc = stack(ch[1:3], 53, 2)
    lh = f"{L(b)}4\\sustainOn {C(lc)}4-. {C(lc)}4-.\\sustainOff"
    m = stack(ch[:3], 69, 3)
    if pos == 3:
        return f"{L(m[0])}2.\\trill", None, lh
    if pos % 2 == 0:
        g = upper_neighbour(k, m[1])
        return f"\\gs {L(g)}8 {L(m[1])}2 {L(m[2])}4", None, lh
    return f"{L(m[2])}2 {L(m[0])}4", None, lh


def t_barcarolle(k, ch, nx, pos, ph, rng):
    b = place(ch[0], 36)
    up = stack(ch[:3], midi(b) + 7, 3)
    lh = f"{L(b)}8\\sustainOn {L(up[0])}8 {L(up[1])}8 {L(up[2])}8 {L(up[1])}8 {L(up[0])}8\\sustainOff"
    m = stack(ch[:3], 67, 3)
    hp = ['\\<', '', '\\>', ''][pos]
    end = '\\!' if pos in (1, 3) else ''
    if pos == 2:      # duplet: two eighths in the time of three
        return f"\\tup2/3 {L(m[1])}8{hp}( {L(m[2])}8) \\tupend {L(m[0])}4.", None, lh
    return f"{L(m[1])}4.{hp}( {L(m[2])}4 {L(m[0])}8{end})", None, lh


def t_triplets(k, ch, nx, pos, ph, rng):
    up = stack(ch[:3], 60, 6)
    grp = lambda a: '\\tup3/2 ' + ' '.join(L(p) + '8' for p in a) + ' \\tupend'
    hp = '\\<' if pos == 0 else ('\\>' if pos == 2 else '')
    end = '\\!' if pos in (1, 3) else ''
    rh = f"\\tup3/2 {L(up[0])}8{hp} {L(up[1])} {L(up[2])} \\tupend {grp(up[3:6])} {grp(up[5:2:-1])} " \
         f"\\tup3/2 {L(up[2])}8 {L(up[1])} {L(up[0])}{end} \\tupend"
    b = place(ch[0], 36)
    return rh, None, f"{L(b)}2 {L(place(ch[2], 43))}2"


def t_octaves(k, ch, nx, pos, ph, rng):
    hi = (pos <= 1 and ph % 2 == 0)
    up2 = second_pass()
    m = stack(ch[:3], (86 if up2 else 79) if hi else 67, 3)
    o = lambda p: f"<{L(p)} {L((p[0], p[1], p[2] + 1))}>"
    ott_on = (f'\\ottava={2 if up2 else 1} ') if pos == 0 and ph % 2 == 0 else ''
    ott_off = ' \\ottava=0' if pos == 1 and ph % 2 == 0 else ''
    rh = f"{ott_on}{o(m[0])}4-> {o(m[1])}4 {o(m[2])}4-^ {o(m[1])}4{ott_off}"
    b = place(ch[0], 28 if (pos <= 1 and ph % 2 == 1) else 36)
    lo = f"<{L(b)} {L((b[0], b[1], b[2] + 1))}>8"
    lott_on = '\\ottava=-1 ' if pos == 0 and ph % 2 == 1 else ''
    lott_off = ' \\ottava=0' if pos == 1 and ph % 2 == 1 else ''
    return rh, None, f"{lott_on}{lo} " + ' '.join([lo] * 7) + lott_off


def t_duet(k, ch, nx, pos, ph, rng):
    m = stack(ch[:3], 69, 3)
    inner = stack(ch[:3], 62, 4)
    v2 = ' '.join(L(p) + '8' for p in inner + inner[::-1])
    v1 = f"{L(m[1])}2( {L(m[0])}4 {L(m[2])}4)" if pos != 3 else f"{L(m[0])}1"
    if pos == 3 and ph % 2 == 1:
        return v1, v2, "r1"
    return v1, v2, f"{L(place(ch[0], 38))}4 {L(place(ch[2], 45))}4 {L(place(ch[1], 41))}4 {L(place(ch[2], 45))}4"


def t_sarabande(k, ch, nx, pos, ph, rng):
    m = stack(ch[:3], 67, 3)
    orn = '\\mordent' if pos % 2 == 0 else '\\turn'
    rh = f"{L(m[1])}2.{orn} {L(m[2])}4 {L(m[0])}2" if pos != 3 else f"{L(m[0])}1.\\fermata"
    lc = stack(ch[:3], 43, 3)
    lh = f"{C(lc)}2 {C(lc)}2 {C(lc)}2" if pos != 3 else f"{C(lc)}1.\\fermata"
    return rh, None, lh


def t_etude(k, ch, nx, pos, ph, rng):
    sc = k.scale
    start = sc.index(ch[0]) if ch[0] in sc else 0
    run_ = []
    lo = 67
    for j in range(8):
        p = place(sc[(start + j) % 7], lo)
        run_.append(p)
        lo = midi(p) + 1
    head = 'r32 ' + ' '.join(L(p) + '32' for p in run_[1:])
    if pos == 3:
        a, b_, c_ = place(ch[0], 72), place(ch[1], 72), place(ch[2], 72)
        rh = f"{head} r64 {L(a)}64 {L(b_)}32 {L(c_)}16 {L(a)}8 {L(place(ch[2], 69))}4-. {L(place(ch[0], 72))}4"
    else:
        rh = head + f" {L(run_[-1])}4-. {L(place(ch[2], 69))}4-. {L(place(ch[0], 72))}4"
    lc = stack(ch[:3], 48, 3)
    return rh, None, ' '.join([f"{C(lc)}4"] * 4)


def t_pastorale(k, ch, nx, pos, ph, rng):
    b = place(ch[0], 36)
    fifth = place(ch[2], midi(b) + 1)
    lh = ' '.join([f"<{L(b)} {L(fifth)}>4."] * 4)
    m = stack(ch[:3], 67, 3)
    grp = f"{L(m[1])}4 {L(m[0])}8"
    return f"{grp} {L(m[2])}8( {L(m[1])} {L(m[0])}) {grp} {L(m[0])}4.", None, lh


def t_march(k, ch, nx, pos, ph, rng):
    m = stack(ch[:3], 67, 3)
    b = place(ch[0], 36)
    lc = stack(ch[1:3], 53, 2)
    lh = f"{L(b)}4 {C(lc)}4-. {L(place(ch[2], 40))}4 {C(lc)}4-."
    if pos == 3:
        return f"{L(m[0])}2-> r2", None, lh
    return f"{L(m[0])}8.( {L(m[1])}16) {L(m[2])}4-. {L(m[1])}4-. {L(m[0])}4--", None, lh


def t_siciliano(k, ch, nx, pos, ph, rng):
    m = stack(ch[:3], 67, 3)
    lc = stack(ch[:3], 48, 3)
    lh = ' '.join([f"{C(lc)}4."] * 3)
    return f"{L(m[1])}4. {L(m[2])}8.( {L(m[1])}16 {L(m[0])}8) {L(m[0])}4.", None, lh


def t_five(k, ch, nx, pos, ph, rng):
    m = stack(ch[:3], 67, 3)
    b = place(ch[0], 36)
    lc = stack(ch[1:3], 52, 2)
    return (f"{L(m[0])}4 {L(m[1])}4 {L(m[2])}4 {L(m[1])}2", None, f"{L(b)}2. {C(lc)}2")


def t_five8(k, ch, nx, pos, ph, rng):
    up = stack(ch[:3], 69, 3)
    rh = f"{L(up[0])}8[ {L(up[1])}] {L(up[2])}8[ {L(up[1])} {L(up[0])}]"
    b = place(ch[0], 38)
    lc = stack(ch[1:3], 50, 2)
    return rh, None, f"{L(b)}4 {C(lc)}4."


def t_seven(k, ch, nx, pos, ph, rng):
    up = stack(ch[:3], 69, 4)
    rh = (f"{L(up[0])}8[ {L(up[1])}] {L(up[2])}8[ {L(up[1])}] {L(up[0])}8[ {L(up[2])} {L(up[3])}]")
    b = place(ch[0], 38)
    lc = stack(ch[1:3], 50, 2)
    return rh, None, f"{L(b)}4 {C(lc)}4 {L(place(ch[2], 45))}4."


def t_tremolo(k, ch, nx, pos, ph, rng):
    lc = stack(ch[:3], 69, 3)
    b = place(ch[0], 36)
    return (f"{C(lc)}2 {C(lc)}2", None, f"{L(b)}2:32 {L(place(ch[2], 43))}2:32")


def t_clefs(k, ch, nx, pos, ph, rng):
    if second_pass():
        return t_clefs2(k, ch, nx, pos, ph, rng)
    m = stack(ch[:3], 69, 3)
    rh = f"{L(m[0])}4 {L(m[1])}4 {L(m[2])}2"
    if pos == 1:      # LH moves up into the treble clef for this bar
        lc = stack(ch[:3], 60, 3)
        return rh, None, f"\\clef=treble {L(lc[0])}8 {L(lc[1])} {L(lc[2])} {L(lc[1])} {C(lc)}2"
    lc = stack(ch[:3], 41, 3)
    pre = '\\clef=bass ' if pos == 2 else ''
    return rh, None, f"{pre}{L(lc[0])}8 {L(lc[1])} {L(lc[2])} {L(lc[1])} {C(lc)}2"


def t_clefs2(k, ch, nx, pos, ph, rng):
    """right hand: treble -> soprano -> treble^8 -> treble; left hand: bass -> tenor -> alto -> bass"""
    rclef, rlo = [('treble', 69), ('soprano', 64), ('treble^8', 81), ('treble', 69)][pos]
    lclef, llo = [('bass', 41), ('tenor', 50), ('alto', 55), ('bass', 41)][pos]
    m = stack(ch[:3], rlo, 3)
    lc = stack(ch[:3], llo, 3)
    rpre = f'\\clef={rclef} ' if pos else ''
    lpre = f'\\clef={lclef} ' if pos else ''
    return (f"{rpre}{L(m[0])}4 {L(m[1])}4 {L(m[2])}2", None,
            f"{lpre}{L(lc[0])}8 {L(lc[1])} {L(lc[2])} {L(lc[1])} {C(lc)}2")


def t_sextuplets(k, ch, nx, pos, ph, rng):
    up = stack(ch[:3], 60, 6)
    if ph % 2 == 1:   # septuplets
        up7 = stack(ch[:3], 60, 7)
        sp = lambda a: '\\tup7/4 ' + ' '.join(L(p) + '16' for p in a) + ' \\tupend'
        rh = f"{sp(up7)} {L(up7[6])}4 {sp(up7[::-1])} {L(up7[0])}4"
    else:
        sx = lambda a: '\\tup6/4 ' + ' '.join(L(p) + '16' for p in a) + ' \\tupend'
        rh = f"{sx(up)} {L(up[5])}4 {sx(up[::-1])} {L(up[0])}4"
    lc = stack(ch[:3], 45, 2)
    return rh, None, ' '.join(L(p) + '8' for p in (lc * 4))


def t_quintuplets(k, ch, nx, pos, ph, rng):
    up = stack(ch[:3], 62, 5)
    rh = '\\tup5/4 ' + ' '.join(L(p) + '16' for p in up) + f" \\tupend {L(up[4])}8 {L(up[3])} {L(up[2])}2"
    lc = stack(ch[:3], 45, 3)
    return rh, None, f"{C(lc)}4 {C(lc)}4 {C(lc)}2"


def t_graces(k, ch, nx, pos, ph, rng):
    m = stack(ch[:3], 67, 4)
    gp = place(ch[1], midi(m[1]) + 1)
    rh = f"\\g {L(m[3])}16 \\g {L(gp)} {L(m[0])}8 {L(m[1])}8 \\gs {L(gp)}8 {L(m[2])}8 {L(m[1])}8"
    b = place(ch[0], 38)
    return rh, None, f"{L(b)}8 {L(place(ch[2], 45))}8 {L(place(ch[1], 41))}8 {L(place(ch[2], 45))}8"


def t_arpeggios(k, ch, nx, pos, ph, rng):
    rc = stack(ch[:3], 62, 4)
    lc = stack(ch[:3], 36, 3)
    fing = [1, 2, 3, 5]
    rcf = '<' + ' '.join(f"{L(p)}-{fing[j]}" for j, p in enumerate(rc)) + '>'
    lcf = '<' + ' '.join(f"{L(p)}-{[5, 3, 1][j]}" for j, p in enumerate(lc)) + '>'
    return (f"{rcf}2\\arpeggio {C(rc)}2\\arpeggio", None, f"{lcf}2\\arpeggio {C(lc)}2")


def t_breath(k, ch, nx, pos, ph, rng):
    m = stack(ch[:3], 69, 3)
    b = place(ch[0], 38)
    lc = stack(ch[1:3], 53, 2)
    br = '\\breathe' if pos in (1, 3) else ''
    return f"{L(m[1])}2 {L(m[0])}4{br}", None, f"{L(b)}4 {C(lc)}2"


def t_antico(k, ch, nx, pos, ph, rng):
    a, b_ = stack(ch[:3], 67, 3), stack(ch[:3], 69, 3)
    bass = place(ch[0], 36)
    if pos == 3:
        return f"{C(a)}\\breve\\fermata", None, f"{L(bass)}\\breve\\fermata"
    lh = 'r\\breve' if pos == 1 else (f"{L(bass)}\\breve" if pos == 0 else f"{L(bass)}1 {L(place(ch[2], 43))}1")
    return f"{C(a)}1 {C(b_)}1", None, lh


TEXTURES = [
    ('Chorale', (4, 4), 'common', 'Maestoso', 'quarter', 66, 0, t_chorale),
    ('Alberti', (4, 4), None, 'Allegretto', 'quarter', 108, 0, t_alberti),
    ('Toccata', (2, 4), None, 'Presto', 'quarter', 152, 0, t_toccata),
    ('Valse', (3, 4), None, 'Tempo di valse', 'quarter', 160, 0, t_valse),
    ('Barcarolle', (6, 8), None, 'Andante', 'quarter', 54, 1, t_barcarolle),
    ('Triplets', (4, 4), None, 'Moderato', 'quarter', 88, 0, t_triplets),
    ('Octaves', (4, 4), None, 'Con fuoco', 'quarter', 120, 0, t_octaves),
    ('Duet', (4, 4), None, 'Cantabile', 'quarter', 72, 0, t_duet),
    ('Sarabande', (3, 2), None, 'Grave', 'half', 48, 0, t_sarabande),
    ('Etude', (4, 4), None, 'Allegro', 'quarter', 116, 0, t_etude),
    ('Pastorale', (12, 8), None, 'Pastorale', 'quarter', 60, 1, t_pastorale),
    ('March', (2, 2), 'cut', 'Alla marcia', 'half', 60, 0, t_march),
    ('Siciliano', (9, 8), None, 'Siciliano', 'quarter', 50, 1, t_siciliano),
    ('Five', (5, 4), None, 'Inquieto', 'quarter', 132, 0, t_five),
    ('Seven', (7, 8), None, 'Danza', 'eighth', 220, 0, t_seven),
    ('Tremolo', (4, 4), None, 'Misterioso', 'quarter', 60, 0, t_tremolo),
    ('Clefs', (4, 4), None, 'Comodo', 'quarter', 96, 0, t_clefs),
    ('Sextuplets', (4, 4), None, 'Fluido', 'quarter', 69, 0, t_sextuplets),
    ('Quintuplets', (4, 4), None, 'Capriccioso', 'quarter', 76, 0, t_quintuplets),
    ('Graces', (2, 4), None, 'Scherzando', 'quarter', 100, 0, t_graces),
    ('Arpeggios', (4, 4), None, 'Largo', 'quarter', 50, 0, t_arpeggios),
    ('Breath', (3, 4), None, 'Semplice', 'quarter', 80, 0, t_breath),
    ('Antico', (4, 2), None, 'Stile antico', 'half', 72, 0, t_antico),
]
DYNS = ['p', 'mf', 'f', 'mp', 'pp', 'ff']
DS_PAGE = 3                 # variation with Segno / To Coda / D.S. al Coda / Coda
PAGE_SYSTEMS = 5            # systems per page (page 1: one less, for the title)
BARS_PER_SYSTEM = 4


def variation_plan(v):
    """variation number (1-based) -> (texture index, key index)"""
    return (v - 1) % len(TEXTURES), ((v - 1) * 7) % len(KEYS)


def build_voices(n_pages, seed=4242):
    rng = random.Random(seed)
    rh1, rh2, lh = [], [], []
    pages = []
    for v in range(1, n_pages + 1):
        ti, ki = variation_plan(v)
        name, time, sym, ttext, unit, bpm, dots, fn = TEXTURES[ti]
        CTX['v'] = v
        if v > len(TEXTURES) and name == 'March':
            sym = None                                   # numeric 2/2 instead of alla breve
        if v > len(TEXTURES) and name == 'Five':
            time, fn, unit, bpm = (5, 8), t_five8, 'eighth', 240
        fifths, mode, ts, ta = KEYS[ki]
        key = Key(fifths, mode, ts, ta)
        n_sys = PAGE_SYSTEMS - (1 if v == 1 else 0)
        n_bars = n_sys * BARS_PER_SYSTEM
        start = len(rh1)
        for b in range(n_bars):
            ph, pos = divmod(b, 4)
            prog = PROGS[(v * 3 + ph) % len(PROGS)]
            if ph == n_bars // 4 - 1:
                prog = [prog[0], prog[1], 4, 0] if not isinstance(prog[1], tuple) else [0, prog[1], 4, 0]
            deg = prog[pos]
            ch = key.chord(deg, seventh=isinstance(deg, tuple))
            nx = key.chord(prog[(pos + 1) % 4]) if pos < 3 else None
            r1, r2, l_ = fn(key, ch, nx, pos, ph, rng)
            if b == 0:
                r1 = _add_first(r1, f"\\{DYNS[v % len(DYNS)]}")
            rh1.append(r1)
            rh2.append(r2)
            lh.append(l_)
        pages.append(dict(variation=v, texture=name + (' II' if v > len(TEXTURES) else ''), time=time, symbol=sym, key=(fifths, mode),
                          tempo=(ttext, unit, bpm, dots), start=start, bars=n_bars, systems=n_sys))
    return rh1, rh2, lh, pages


def _add_first(s, suffix):
    """append a suffix (dynamic) to the first note/chord token of a DSL bar"""
    toks = s.split(' ')
    for j, t in enumerate(toks):
        if t and (t[0] in 'abcdefg<') and not (j > 0 and toks[j - 1] in ('\\g', '\\gs')):
            if t[0] == '<':
                j = next(x for x in range(j, len(toks)) if '>' in toks[x])
            toks[j] = toks[j] + suffix
            return ' '.join(toks)
    raise ValueError(s)


def make(n_pages, paper='A4'):
    rh1, rh2, lh, pages = build_voices(n_pages)
    # spacer bars for the second right-hand voice where it is unused (length from the bar's metre)
    from cov.dsl import mdur
    m1 = [parse_voice(x)[0] for x in rh1]
    ml = [parse_voice(x)[0] for x in lh]
    from cov.model import Event
    v2 = []
    for j, x in enumerate(rh2):
        if x:
            v2.append(parse_voice(x)[0])
        else:
            v2.append([Event('space', mdur(m1[j]))])
    piano = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ('treble', 'bass'), (('1', 1), ('2', 1), ('5', 2)))
    p0 = pages[0]
    sc = assemble(p0['time'], p0['key'], [(piano, {'1': m1, '2': v2, '5': ml})], time_symbol=p0['symbol'])
    prev = None
    for pg in pages:
        i = pg['start']
        if prev is not None:
            if pg['time'] != prev['time'] or pg['symbol'] != prev['symbol']:
                set_time(sc, i, pg['time'], pg['symbol'])
            if pg['key'] != prev['key']:
                sc.measures[i].key = pg['key']
            sc.measures[i - 1].right_bar = 'double'
            sc.measures[i].brk = 'page'
        for s in range(1, pg['systems']):
            sc.measures[i + s * BARS_PER_SYSTEM].brk = 'system'
        ttext, unit, bpm, dots = pg['tempo']
        add_mark(sc, i, 'rehearsal', text=str(pg['variation']))
        if pg['variation'] == DS_PAGE and pg['bars'] >= 20:
            add_mark(sc, i, 'segno')
            sc.measures[i + 11].end_marks.append(dict(kind='words', text='To Coda', style='italic',
                                                       sound={'tocoda': 'coda'}))
            sc.measures[i + 15].end_marks.append(dict(kind='words', text='D.S. al Coda', style='italic',
                                                       sound={'dalsegno': 'segno'}))
            sc.measures[i + 15].right_bar = 'double'
            add_mark(sc, i + 16, 'coda')
        add_mark(sc, i, 'tempo', text=f'Var. {pg["variation"]}  {ttext}', unit=unit, bpm=bpm, dots=dots)
        prev = pg
    sc.measures[-1].right_bar = 'final'
    _courtesy_pass(sc, piano)
    finish_measures(sc)
    title = 'Forty Variations' if n_pages > 1 else 'Variation'
    sc.title = title
    sc.composer = 'coverage corpus (CC0)'
    sc.rights = 'CC0 1.0'
    sc.credits = [{'page': 1, 'type': 'title', 'text': title},
                  {'page': 1, 'type': 'subtitle', 'text': f'for piano - {n_pages} page{"s" if n_pages > 1 else ""}'},
                  {'page': 1, 'type': 'composer', 'text': 'coverage corpus (CC0)'}]
    for k in range(2, n_pages + 1):
        sc.credits.append({'page': k, 'type': 'page number', 'text': str(k)})
    pname, wmm, hmm = PAPER[paper]
    staff = 18
    sc.page = {'name': paper, 'width_mm': wmm, 'height_mm': hmm, 'staff_size': staff}
    layout = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1'), ('P', '2')], 'part_staves': [('P', 1)]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')], 'part_staves': [('P', 2)]}]}]}
    opts = {'header': {'title': title, 'subtitle': sc.credits[1]['text'], 'composer': 'coverage corpus (CC0)'},
            'staff_size': staff, 'paper': pname,
            'paper_extra': ['top-margin = 10\\mm', 'bottom-margin = 10\\mm', 'left-margin = 14\\mm',
                            'right-margin = 14\\mm', 'ragged-last-bottom = ##f', 'print-page-number = ##t',
                            'print-first-page-number = ##f'],
            'layout_extra': []}
    textures = sorted({p['texture'] for p in pages})
    info = dict(
        layout='piano', layout_also=['two-voices-one-staff-instrument'] if 'Duet' in textures else [],
        parts=['Piano'], must_not_split=True,
        expected_notes=(f'One Piano part (grand staff) over {n_pages} page(s); every page is one variation '
                        'with its own key, metre, tempo + metronome mark and rehearsal number (1, 2, ...). '
                        'Pages are separated by double barlines + page breaks; systems hold 4 bars.'),
        truth_limitations=('Page numbers are printed (pages >= 2) and encoded only as <credit> page numbers. '
                           'Dynamics / hairpins / pedal marks are directions without placement attributes.'),
        title=f'Forty Variations for piano - {n_pages}-page document',
        license='CC0', source='own procedural composition for the coverage corpus (pieces/variations.py)',
        attribution='\n'.join([f'Forty Variations for piano (pages 1-{n_pages}): procedurally composed for the '
                               'coverage corpus - CC0 1.0.', '', CC0_NOTE]),
        pages_plan=[{k: v for k, v in p.items() if k != 'start'} | {'first_bar': p['start'] + 1} for p in pages],
    )
    return sc, layout, opts, info


def _dur_token(d):
    d = F(d)
    for tok, q in (('1.', F(6)), ('1', F(4)), ('2.', F(3)), ('2', F(2)), ('4.', F(3, 2)), ('4', F(1))):
        if d == q:
            return tok
    w = d / 4
    return f'1*{w.numerator}/{w.denominator}'


def _courtesy_pass(sc, part):
    """courtesy accidentals: after a bar in which a step/octave was altered away from the key signature,
    the first plain (key-signature) occurrence of that step/octave in the next bar gets a cautionary
    accidental (same staff)."""
    for i in range(1, len(sc.measures)):
        if sc.measures[i].key:
            continue
        fifths = sc.current_key(i)[0]
        from cov.acc import key_alters
        kalt = key_alters(fifths)
        for staff in (1, 2):
            altered = set()
            for v in part.voices:
                if v.staff != staff:
                    continue
                for ev in part.measures[i - 1].get(v.key, []):
                    if ev.kind == 'note':
                        for (s, a, o) in ev.pitches:
                            if a != kalt[s]:
                                altered.add((s, o))
            if not altered:
                continue
            done = set()
            for v in part.voices:
                if v.staff != staff:
                    continue
                for ev in part.measures[i].get(v.key, []):
                    if ev.kind != 'note':
                        continue
                    for p in ev.pitches:
                        s, a, o = p
                        if (s, o) in altered and (s, o) not in done:
                            done.add((s, o))
                            if a == kalt[s] and p not in ev.tie_stop:
                                ev.caut_acc.add(p)
