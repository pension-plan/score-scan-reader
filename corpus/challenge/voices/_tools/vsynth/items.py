"""challenge/voices item definitions: own CC0 compositions on public-domain texts.

Every item: make() -> (score, layout, lilypond opts); edge-case tags; expected
conversion; three damage recipes (scan, scan-mild, scan-severe).
"""
from __future__ import annotations

from .dsl import assemble
from .model import compute_extenders, parse_lyric_text, set_verses, voice_events

PD_TEXT = 'public domain text'


def set_lyrics_range(sc, pid, vkey, verse, text, m_from, m_to, noext_last=True):
    """assign syllables to the attacks of one voice within measures [m_from, m_to) (0-based)."""
    part = sc.part(pid)
    slots = [ev for i, t, ev in voice_events(sc, part, vkey)
             if m_from <= i < m_to and ev.kind == 'note' and not ev.is_tie_continuation()]
    syls = parse_lyric_text(text)
    if len(syls) != len(slots):
        raise ValueError(f'{pid}:{vkey} m{m_from}-{m_to}: {len(syls)} syllables for {len(slots)} notes')
    for ev, ly in zip(slots, syls):
        if ly is not None:
            ev.lyrics[verse] = ly
    last = [ly for ly in syls if ly is not None]
    if last and noext_last:
        last[-1].noext = True
    compute_extenders(sc)


def closed_staff(sid, clef, voices, lyrics=(), name=None, short=None, timed=None):
    st = {'id': sid, 'clef': clef, 'voices': voices,
          'lyrics': [{'voice': v, 'verses': vs, 'place': pl} for v, vs, pl in lyrics]}
    if name:
        st['name'] = name
    if short:
        st['short'] = short
    if timed:
        st['timed_lyrics'] = timed
    return st


def satb(parts, time, key, pickup=None, time_symbol=None, names=None, clefs=None):
    """parts: dict pid -> dsl ; standard S A T B one-voice parts."""
    names = names or {'S': ('Soprano', 'S.'), 'A': ('Alto', 'A.'), 'T': ('Tenor', 'T.'), 'B': ('Bass', 'B.')}
    clefs = clefs or {'S': 'treble', 'A': 'treble', 'T': 'bass', 'B': 'bass'}
    spec = [{'id': pid, 'name': names[pid][0], 'abbr': names[pid][1], 'clefs': [clefs[pid]],
             'voices': [('1', 1, dsl)]} for pid, dsl in parts.items()]
    return assemble(spec, time=time, key=key, pickup=pickup, time_symbol=time_symbol)


def base_opts(title, poet=None, composer=None, subtitle=None, size=20, paper='a4', font='C059', extra_paper=(),
              extra_layout=(), meter=None, arranger=None):
    hdr = {'title': title}
    for k, v in (('poet', poet), ('composer', composer), ('subtitle', subtitle), ('meter', meter),
                 ('arranger', arranger)):
        if v:
            hdr[k] = v
    return {'header': hdr, 'staff_size': size, 'paper': paper, 'font': font,
            'paper_extra': list(extra_paper), 'layout_extra': list(extra_layout), 'auto_beam_off_vocal': True}


# =====================================================================================
# A  closed SATB: crossings, unisons (one head two stems / one head one stem / unequal
#    durations), resting alto, lyrics only under the treble staff, no part labels
# =====================================================================================

A_S = ("f'4 | a'2 bes'4 | c''2 a'4 | g'2 e'4 | f'2 c''4 | d''2 c''4 | bes'2 a'4 | g'2 c''4 | a'2 bes'4 | "
       "c''2 a'4 | f'2 g'4 | a'2 a'4 | bes'2 a'4 | g'2 g'4 | f'2.")
A_A = ("c'4 | f'2 f'4 | f'2 f'4 | d'2 g'4 | f'2 a'4 | bes'2 a'4 | g'2 a'4\\nostem | e'2 r4 | f'2 f'4 | "
       "f'2 f'4 | a'2 g'4 | f'2 f'4 | f'2 f'4 | g'4 f' e' | f'2.")
A_T = ("a4 | c'2 d'4 | c'2 d'4 | g2 g4 | a2 c'4 | bes2 c'4 | d'2 c'4 | c2 g4 | c'2 d'4 | c'2 d'4 | "
       "d'2 d'4 | c'2 f4 | d2 f4 | c'2 bes4 | a2.")
A_B = ("f4 | f2 bes,4 | a,2 d4 | bes,2 c4 | f2 f4 | bes,2 f4 | bes,2 f4 | c2 e4 | f2 bes,4 | a,2 d4 | "
       "d2 bes,4 | f2 d4 | f2 c4 | c2 c4 | f,2.")
A_V = [
    "O God, our help in a -- ges past, Our hope for years to come, "
    "Our shel -- ter from the storm -- y blast, And our e -- ter -- nal home.",
    "Un -- der the sha -- dow of thy throne Thy saints have dwelt se -- cure; "
    "Suf -- fi -- cient is thine arm a -- lone, And our de -- fence is sure.",
    "Be -- fore the hills in or -- der stood, Or earth re -- ceived her frame, "
    "From ev -- er -- last -- ing thou art God, To end -- less years the same.",
    "A thou -- sand a -- ges in thy sight Are like an eve -- ning gone; "
    "Short as the watch that ends the night Be -- fore the ris -- ing sun.",
]


def mk_A():
    def make():
        sc = satb({'S': A_S, 'A': A_A, 'T': A_T, 'B': A_B}, (3, 4), (-1, 'major'), pickup=1)
        set_verses(sc, 'S', '1', A_V, mode='attack')
        sc.title = 'O God, Our Help in Ages Past'
        sc.composer = 'Tune CROSSWAY (challenge corpus, CC0)'
        sc.lyricist = 'Isaac Watts (1719)'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
        lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
            closed_staff('upper', 'treble', [('S', '1'), ('A', '1')], [(('S', '1'), [1, 2, 3, 4], 'below')]),
            closed_staff('lower', 'bass', [('T', '1'), ('B', '1')])]}]}
        opts = base_opts('O God, Our Help in Ages Past', poet='Isaac Watts, 1719',
                         composer='CROSSWAY  C.M.', size=21, paper='letter', font='C059',
                         extra_paper=['indent = 0', 'top-margin = 16\\mm', 'ragged-last-bottom = ##t'])
        return sc, lay, opts
    return make


ITEM_A = dict(
    id='satb-closed-crossing-unisons', title='O God, Our Help in Ages Past (closed SATB: crossings and unisons)',
    make=mk_A(), pages=1,
    edge_cases=['satb_closed', 'shared_staff_two_voices', 'voice_crossing_alto_above_soprano',
                'voice_exchange_soprano_alto', 'voice_crossing_tenor_below_bass', 'unison_one_head_two_stems',
                'unison_one_head_one_stem', 'unison_unequal_durations_two_heads', 'unison_dotted_half_final',
                'one_voice_rests_other_sings', 'lyrics_only_under_treble_staff', 'multi_verse', 'pickup',
                'no_part_labels', 'three_four_time', 'key_signature_flat'],
    expected={
        'parts': ['Soprano', 'Alto', 'Tenor', 'Bass'],
        'must_not_split': False,
        'shared_staves': [['Soprano', 'Alto'], ['Tenor', 'Bass']],
        'notes': ('Closed score without any part labels: the converter must infer S/A from stem direction on the '
                  'treble staff (stem up = Soprano, stem down = Alto) and T/B on the bass staff, even where the '
                  'voices cross (m.3 beat 3 and m.10 the alto is ABOVE the soprano; m.12 the tenor is BELOW the '
                  'bass). Unisons: shared note heads with two stems (mm.4, 10, 14, and T+B in m.7) belong to BOTH '
                  'parts; in m.6 beat 3 the alto unison is drawn with one head and only the soprano\'s up-stem '
                  '(the alto still sings a\' there - the down-stem was omitted); in m.13 the soprano half note and '
                  'the alto quarter on the same pitch are two separate heads. Alto rests on m.7 beat 3. Both verses '
                  'are printed under the treble staff and are aligned to the soprano; truth carries them on the '
                  'Soprano part only (the other parts sing the same words but the score does not print them '
                  'for them). Pickup bar is measure 0.'),
    },
    truth_limitations=[
        'The one-head-one-stem unison (m.6 beat 3) is an engraving choice: truth has an ordinary a\' quarter in '
        'both Soprano and Alto; a converter cannot see the alto note directly and must infer it from the '
        'continuing alto line (no alto rest is printed).',
        'Lyrics are only on the Soprano part in truth (convention shared with corpus/synthetic).'],
    license='Text public domain (Isaac Watts, 1719); music and engraving CC0-1.0',
    source='self-authored (challenge corpus); text: Isaac Watts, "Our God, our help in ages past" (1719)',
    attribution=('O God, Our Help in Ages Past. Text: Isaac Watts (1719), public domain.\n'
                 'Tune CROSSWAY and SATB setting: composed for this challenge corpus (2026), dedicated to the '
                 'public domain (CC0 1.0).'),
    scans={
        'scan': dict(dpi=200, seed=7101, mode='rgb', format='jpeg', quality=40,
                     summary='yellowed RGB scan, foxing, bleed-through, pencil circles/breath marks, 2.3 deg skew',
                     ops=[{'op': 'paper', 'rgb': [237, 226, 196], 'ink': [40, 32, 28], 'texture': 6, 'fibers': 3,
                           'bleed': {'strength': 0.13, 'blur_mm': 0.3, 'shift_mm': 4}},
                          {'op': 'foxing', 'n': 70, 'size_mm': [0.3, 2.2]},
                          {'op': 'pencil', 'circles': 3, 'breaths': 3, 'ticks': 1, 'texts': ['breathe', 'alto!'],
                           'alpha': 0.55},
                          {'op': 'rotate', 'deg': 2.3, 'fill': [228, 228, 226]},
                          {'op': 'gradient', 'strength': 0.14, 'angle': 30},
                          {'op': 'blur', 'sigma': 0.8}, {'op': 'noise', 'sigma': 4, 'chroma': 1.5}]),
        'scan-mild': dict(dpi=300, seed=7102, mode='gray', format='jpeg', quality=60,
                          summary='clean office scan: 0.6 deg skew, light texture and noise',
                          ops=[{'op': 'paper', 'rgb': [245, 245, 243], 'texture': 3},
                               {'op': 'rotate', 'deg': -0.6, 'fill': 250},
                               {'op': 'blur', 'sigma': 0.5}, {'op': 'noise', 'sigma': 2.5}]),
        'scan-severe': dict(dpi=120, seed=7103, mode='bilevel', format='png',
                            binarize={'thr': 92, 'noise': 22, 'pre_blur': 0.6},
                            summary='thin binarized photocopy at 120 dpi, 6.5 deg skew, faded ink, salt-and-pepper',
                            ops=[{'op': 'ink_dropout', 'amount': 0.25},
                                 {'op': 'paper', 'rgb': [236, 236, 236], 'texture': 8},
                                 {'op': 'rotate', 'deg': -6.5, 'fill': 255, 'expand': True},
                                 {'op': 'blur', 'sigma': 0.9}, {'op': 'speckle', 'per_mpx': 160},
                                 {'op': 'saltpepper', 'amount': 0.0015}]),
    },
)


# =====================================================================================
# B  closed SATB, German, labels "Sopran/Alt" "Tenor/Bass", lyrics under BOTH staves;
#    lyric lines switch voice (alto / tenor echo while soprano and bass rest);
#    bass with its own rhythm (dotted) so lower syllables sit at other onsets
# =====================================================================================

B_S = ("b'4 b' a' g' | a'2 g'2 | d''4 d'' c'' b' | a'4 g' a'2 | b'4 c'' d'' b' | c''2 b'2 | d''4 c'' b' a' | "
       "g'4 fis' g'2 | r1 | r1 | d''4 b' c'' a' | a'2 g'2\\fermata")
B_A = ("g'4 g' fis' e' | fis'2 d'2 | b'4 b' g' g' | a'4 e' fis'2 | g'4 g' g' g' | fis'2 g'2 | g'4 g' g' fis' | "
       "d'4 d' d'2 | d'4\\p e' d' c' | b4 a b2 | g'4\\f g' g' fis' | fis'2 d'2\\fermata")
B_T = ("d'4 d' d' b | d'2 b2 | g4 d' e' d' | d'4 b d'2 | d'4 d' d' a | a2 d'2 | d'4 e' d' d' | b4 a b2 | "
       "b4\\p c' b a | g4 fis g2 | d'4\\f e' e' d' | c'2 b2\\fermata")
B_B = ("g,4 b, d e | d2 g,2 | g4. fis8 e4 g4 | fis4 e d2 | g4 c b, e | d2 g,2 | b,4 c d d | d4 d g,2 | r1 | r1 | "
       "b,4 e c d | d2 g,2\\fermata")
B_TXT = ("Nun dan -- ket al -- le Gott mit Her -- zen, Mund und Hän -- den, der gro -- ße Din -- ge tut, "
         "an uns und al -- len En -- den.")
B_ECHO = "an uns und al -- len En -- den."
B_END = "Nun dan -- ket al -- le Gott!"


def mk_B():
    def make():
        sc = satb({'S': B_S, 'A': B_A, 'T': B_T, 'B': B_B}, (4, 4), (1, 'major'), time_symbol='common',
                  names={'S': ('Sopran', 'S.'), 'A': ('Alt', 'A.'), 'T': ('Tenor', 'T.'), 'B': ('Bass', 'B.')})
        for pid in ('S', 'B'):
            set_lyrics_range(sc, pid, '1', 1, B_TXT, 0, 8)
            set_lyrics_range(sc, pid, '1', 1, B_END, 10, 12)
        for pid in ('A', 'T'):
            set_lyrics_range(sc, pid, '1', 1, B_ECHO, 8, 10)
        sc.title = 'Nun danket alle Gott'
        sc.composer = 'Satz: challenge corpus (CC0)'
        sc.lyricist = 'Martin Rinkart (1636)'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
        lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
            closed_staff('upper', 'treble', [('S', '1'), ('A', '1')], name=['Sopran', 'Alt'], short=['S.', 'A.'],
                         timed=[{'sources': [('S', '1'), ('A', '1')], 'verse': 1}]),
            closed_staff('lower', 'bass', [('T', '1'), ('B', '1')], name=['Tenor', 'Bass'], short=['T.', 'B.'],
                         timed=[{'sources': [('B', '1'), ('T', '1')], 'verse': 1}])]}]}
        opts = base_opts('Nun danket alle Gott', poet='Text: Martin Rinkart, 1636',
                         composer='Satz: Challenge-Korpus (CC0)', size=19, paper='a4', font='TeX Gyre Pagella',
                         extra_paper=['top-margin = 20\\mm', 'system-system-spacing.basic-distance = #18'])
        return sc, lay, opts
    return make


ITEM_B = dict(
    id='satb-closed-lyrics-both-staves-de',
    title='Nun danket alle Gott (closed SATB, German, lyrics under both staves, lyrics switch voice)',
    make=mk_B(), pages=1,
    edge_cases=['satb_closed', 'shared_staff_two_voices', 'lyrics_under_each_staff', 'lyrics_lower_staff_bass',
                'lyric_line_switches_voice', 'independent_bass_rhythm_lyrics_offset', 'one_voice_rests_other_sings',
                'whole_bar_rests_in_one_voice', 'part_labels_german_center_column', 'unison_one_head_two_stems',
                'german_umlauts', 'dynamics', 'fermata', 'common_time_symbol'],
    expected={
        'parts': ['Sopran', 'Alt', 'Tenor', 'Bass'],
        'must_not_split': False,
        'shared_staves': [['Sopran', 'Alt'], ['Tenor', 'Bass']],
        'notes': ('Closed score with German labels "Sopran/Alt" and "Tenor/Bass" (abbreviated "S./A.", "T./B." on '
                  'later systems). Split each staff by stem direction into four parts. There is one lyric line '
                  'under EACH staff: the upper line belongs to the Sopran, except mm.9-10 where the Sopran has '
                  'whole-bar rests and the same line carries the Alt echo "an uns und allen Enden"; the lower line '
                  'belongs to the Bass, except mm.9-10 where the Bass rests and the line belongs to the Tenor. '
                  'In m.3 the Bass sings a dotted rhythm, so its syllable "Her-" sits half a beat after the '
                  'Sopran\'s. A correct conversion attaches each syllable to the voice whose note it is printed '
                  'under (truth: Sopran mm.1-8,11-12; Alt mm.9-10; Bass mm.1-8,11-12; Tenor mm.9-10).'),
    },
    truth_limitations=[
        'The lyric lines are printed as single rows that change voice; truth attributes each syllable to the '
        'voice whose note head it is aligned with (verse number 1 for all).'],
    license='Text public domain (Martin Rinkart, 1636); music and engraving CC0-1.0',
    source='self-authored (challenge corpus); text: Martin Rinkart, "Nun danket alle Gott" (1636), stanza 1, lines 1-4',
    attribution=('Nun danket alle Gott. Text: Martin Rinkart (1636), public domain.\n'
                 'Melody and four-part setting: composed for this challenge corpus (2026), CC0 1.0 '
                 '(not the Crüger tune).'),
    scans={
        'scan': dict(dpi=200, seed=7201, mode='rgb', format='jpeg', quality=35,
                     summary='phone photo of a book page: keystone perspective, page curl + gutter shadow, '
                             'vignette, motion blur',
                     ops=[{'op': 'paper', 'rgb': [240, 236, 226], 'texture': 4},
                          {'op': 'curl', 'side': 'left', 'amp_mm': 5, 'width': 0.22, 'fill': [60, 55, 50],
                           'shade': 0.3},
                          {'op': 'gutter', 'side': 'left', 'width': 0.08, 'dark': 0.5},
                          {'op': 'perspective', 'margin': 0.05, 'bg': [92, 80, 66], 'keystone': 0.045,
                           'jitter': 0.015, 'shadow': 0.25},
                          {'op': 'vignette', 'strength': 0.32}, {'op': 'blotch', 'strength': 0.12},
                          {'op': 'motion_blur', 'len_mm': 0.35, 'deg': 25}, {'op': 'blur', 'sigma': 0.7},
                          {'op': 'noise', 'sigma': 5, 'chroma': 2.5}]),
        'scan-mild': dict(dpi=300, seed=7202, mode='rgb', format='jpeg', quality=60,
                          summary='careful phone photo: slight perspective, mild gradient',
                          ops=[{'op': 'paper', 'rgb': [244, 242, 236], 'texture': 2},
                               {'op': 'perspective', 'margin': 0.03, 'bg': [120, 110, 100], 'jitter': 0.008},
                               {'op': 'gradient', 'strength': 0.12, 'angle': 200},
                               {'op': 'blur', 'sigma': 0.5}, {'op': 'noise', 'sigma': 2.5}]),
        'scan-severe': dict(dpi=150, seed=7203, mode='rgb', format='jpeg', quality=18,
                            summary='low-light phone photo: strong keystone, deep curl, dark vignette, '
                                    'motion + focus blur, heavy noise, JPEG q18',
                            ops=[{'op': 'paper', 'rgb': [232, 226, 210], 'texture': 6},
                                 {'op': 'curl', 'side': 'right', 'amp_mm': 10, 'width': 0.3, 'fill': [40, 36, 32],
                                  'shade': 0.45},
                                 {'op': 'perspective', 'margin': 0.07, 'bg': [50, 44, 40], 'keystone': 0.09,
                                  'jitter': 0.03, 'shadow': 0.4},
                                 {'op': 'vignette', 'strength': 0.55}, {'op': 'blotch', 'strength': 0.2},
                                 {'op': 'motion_blur', 'len_mm': 0.9, 'deg': -15}, {'op': 'blur', 'sigma': 1.2},
                                 {'op': 'noise', 'sigma': 11, 'chroma': 5}]),
    },
)


# =====================================================================================
# C  SAB: three parts on two staves; the alto drops onto the bass staff for a bar
#    (\change Staff), labels "Soprano/Alto" + "Baritone"
# =====================================================================================

C_S = ("a'4 a' d'' a' | b'4 a' fis'2 | g'4 a' b' g' | a'4 fis'2. | a'4 b' cis'' d'' | b'4 a' g'2 | "
       "b'4 a' g' b' | cis''4 d''2.")
C_A = ("fis'4 fis' fis' e' | d'4 cis' d'2 | d'4 e' d' e' | @lower cis'4 a2. | @upper fis'4 g' e' d' | "
       "d'4 cis' e'2 | d'4 d' e' g' | a'4 fis'2.")
C_B = "d4 d b, cis | g4 a d2 | b,4 cis d cis | a,4 d2. | d4 g a b | g4 a e2 | g4 fis e d | a,4 d2."
C_V = [
    "All things bright and beau -- ti -- ful, All crea -- tures great and small, "
    "All things wise and won -- der -- ful, The Lord God made them all.",
    "Each lit -- tle flower that o -- pens, Each lit -- tle bird that sings, "
    "He made their glow -- ing col -- ours, He made their ti -- ny wings.",
]


def mk_C():
    def make():
        spec = [{'id': 'S', 'name': 'Soprano', 'abbr': 'S.', 'clefs': ['treble'], 'voices': [('1', 1, C_S)]},
                {'id': 'A', 'name': 'Alto', 'abbr': 'A.', 'clefs': ['treble'], 'voices': [('1', 1, C_A)]},
                {'id': 'Bar', 'name': 'Baritone', 'abbr': 'Bar.', 'clefs': ['bass'], 'voices': [('1', 1, C_B)]}]
        sc = assemble(spec, time=(4, 4), key=(2, 'major'))
        set_verses(sc, 'S', '1', C_V, mode='attack')
        sc.title = 'All Things Bright and Beautiful'
        sc.composer = 'Tune: challenge corpus (CC0)'
        sc.lyricist = 'Cecil Frances Alexander (1848)'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'S', 'last': 'Bar', 'symbol': 'bracket'}]
        lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
            closed_staff('upper', 'treble', [('S', '1'), ('A', '1')], [(('S', '1'), [1, 2], 'below')],
                         name=['Soprano', 'Alto'], short=['S.', 'A.']),
            closed_staff('lower', 'bass', [('Bar', '1')], name='Baritone', short='Bar.')]}],
            # m.4 (index 3): alto is on the bass staff -> soprano alone (\oneVoice) on the treble staff,
            # alto stems up / baritone stems down on the bass staff
            'role_override': {('S', '1', 3): 0, ('A', '1', 3): 1, ('Bar', '1', 3): 2}}
        opts = base_opts('All Things Bright and Beautiful', poet='Cecil Frances Alexander, 1848',
                         composer='for SAB choir', size=20, paper='letter', font='TeX Gyre Schola',
                         extra_paper=['top-margin = 18\\mm', 'indent = 22\\mm'])
        return sc, lay, opts
    return make


ITEM_C = dict(
    id='sab-cross-staff-alto', title='All Things Bright and Beautiful (SAB: 3 parts on 2 staves, cross-staff alto)',
    make=mk_C(), pages=1,
    edge_cases=['sab_three_parts_two_staves', 'shared_staff_two_voices', 'single_voice_lower_staff',
                'voice_moves_to_other_staff', 'cross_staff_alto_on_bass_staff', 'part_labels_full_then_abbrev',
                'lyrics_only_under_treble_staff', 'multi_verse', 'key_signature_sharps'],
    expected={
        'parts': ['Soprano', 'Alto', 'Baritone'],
        'must_not_split': False,
        'shared_staves': [['Soprano', 'Alto']],
        'notes': ('SAB closed score: Soprano (stems up) and Alto (stems down) share the treble staff; the Baritone '
                  'is alone on the bass staff (its stems point both ways and must NOT be split into two parts). '
                  'In m.4 the alto line moves down onto the bass staff (c#\' then a, stems up, above the '
                  'baritone\'s down-stem notes) while the soprano is alone on the treble staff: those two alto '
                  'notes belong to the Alto part, not to the Baritone and not to a new part. Expected output: '
                  'exactly 3 parts. Two verses under the treble staff, aligned to the Soprano (truth: Soprano '
                  'only).'),
    },
    truth_limitations=['Staff placement is not part of the truth (each vocal part is its own one-staff part); the '
                       'cross-staff notes are simply Alto notes in m.4.'],
    license='Text public domain (Cecil Frances Alexander, 1848); music and engraving CC0-1.0',
    source='self-authored (challenge corpus); text: C. F. Alexander, "All things bright and beautiful", '
           'Hymns for Little Children (1848), refrain + stanza 1',
    attribution=('All Things Bright and Beautiful. Text: Cecil Frances Alexander (1848), public domain.\n'
                 'Tune and SAB setting: composed for this challenge corpus (2026), CC0 1.0 (not the Monk or '
                 'Hullah tunes).'),
    scans={
        'scan': dict(dpi=300, seed=7301, mode='gray', format='jpeg', quality=45,
                     summary='office photocopy from a ring binder: 3 punch holes, staple, thick ink, right edge '
                             'cropped through the staff ends, 1.2 deg skew',
                     ops=[{'op': 'ink_weight', 'n': 1},
                          {'op': 'paper', 'rgb': [243, 243, 241], 'texture': 4},
                          {'op': 'punch_holes', 'n': 3, 'd_mm': 6.0, 'edge_mm': 10, 'spacing_mm': 80, 'bg': 30},
                          {'op': 'staple', 'x_mm': 8, 'y_mm': 12, 'len_mm': 12, 'deg': 35},
                          {'op': 'crop', 'cut_staff_right_mm': 2.5, 'top_mm': 3},
                          {'op': 'rotate', 'deg': 1.2, 'fill': 250},
                          {'op': 'blur', 'sigma': 0.7}, {'op': 'noise', 'sigma': 4},
                          {'op': 'speckle', 'per_mpx': 25}]),
        'scan-mild': dict(dpi=400, seed=7302, mode='gray', format='jpeg', quality=60,
                          summary='high-resolution (400 dpi) flatbed scan, 0.4 deg skew',
                          ops=[{'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                               {'op': 'rotate', 'deg': -0.4, 'fill': 252},
                               {'op': 'blur', 'sigma': 0.4}, {'op': 'noise', 'sigma': 2}]),
        'scan-severe': dict(dpi=150, seed=7303, mode='bilevel', format='png',
                            binarize={'thr': 200, 'noise': 18, 'pre_blur': 0.8},
                            summary='page fed upside down (180 deg) into a fax-like thick binarized copier at '
                                    '150 dpi, 3.5 deg skew, punch holes, dark scanner border',
                            ops=[{'op': 'ink_weight', 'n': 1},
                                 {'op': 'paper', 'rgb': [240, 240, 240], 'texture': 10},
                                 {'op': 'punch_holes', 'n': 2, 'd_mm': 6.5, 'edge_mm': 11, 'spacing_mm': 80,
                                  'bg': 15},
                                 {'op': 'rot90', 'k': 2},
                                 {'op': 'rotate', 'deg': 3.5, 'fill': 70, 'expand': True},
                                 {'op': 'blur', 'sigma': 1.0}, {'op': 'speckle', 'per_mpx': 120},
                                 {'op': 'saltpepper', 'amount': 0.002}]),
    },
)


# =====================================================================================
# D  open-score SATB (4 staves, tenor treble_8) where divisi appears mid-piece:
#    tenor splits into two voices on its staff (mm.7-8), soprano and bass divisi as
#    chords on one stem (m.18, mm.20-21).  Two pages.
# =====================================================================================

D_S = ("bes'2 c''2 | bes'2. aes'4 | g'2 f'2 | bes'4 bes' c'' d'' | ees''2 d''2 | c''4 bes' bes'2 | g'2 aes'2 | "
       "g'2 f'2 | bes'4 c'' d'' ees'' | f''2 ees''4 d'' | c''2 bes'4 aes' | g'1 | g'2\\p g'2 | aes'2 g'2 | "
       "f'4 g' aes'2 | g'1 | bes'4\\mf c'' d'' ees'' | <aes' ees''>2^\"div.\" <aes' c''>2 | bes'2^\"unis.\" bes'2 | "
       "<aes' c''>1^\"div.\" | <g' bes'>1\\fermata")
D_A = ("ees'2 ees'2 | ees'2. f'4 | ees'2 d'2 | ees'4 ees' aes' f' | ees'2 f'2 | aes'4 g' f'2 | ees'2 f'2 | "
       "ees'2 d'2 | ees'4 ees' d' g' | bes'2 ees'4 f' | aes'2 g'4 f' | ees'1 | ees'2\\p ees'2 | c'2 c'2 | "
       "f'4 ees' c'2 | b1 | g'4\\mf aes' f' ees' | ees'2 f'2 | g'2 aes'2 | ees'1 | ees'1\\fermata")
D_T1 = ("g2 aes2 | g2. bes4 | bes2 bes2 | g4 bes ees' bes | g2 bes2 | ees'4 ees' d'2 | c'2^\"div.\" c'2 | "
        "bes2 aes2 | bes4^\"unis.\" aes bes c' | bes2 g4 bes | ees'2 ees'4 d' | bes1 | c'2\\p g2 | f2 g2 | "
        "bes4 bes f2 | g1 | ees'4\\mf ees' bes g | c'2 c'2 | ees'2 d'2 | c'1 | g1\\fermata")
D_T2 = "s1 | s1 | s1 | s1 | s1 | s1 | ees2 aes2 | ees2 f2 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1 | s1"
D_B = ("ees2 aes,2 | ees2. d4 | ees2 bes2 | ees4 g aes bes, | c2 d2 | aes,4 bes, bes,2 | c2 aes,2 | bes,2 bes,2 | "
       "g,4 aes, d c | d2 c4 bes, | aes,2 bes,4 bes, | ees1 | c2\\p c2 | f2 ees2 | d4 ees f2 | g,1 | "
       "g,4\\mf c bes, c | aes,2 f2 | bes2 bes2 | <aes, aes>1^\"div.\" | <ees, ees>1\\fermata")
D_TXT = ("A -- ve ve -- rum cor -- pus, na -- tum de Ma -- ri -- a Vir -- gi -- ne, ve -- re pas -- sum, "
         "im -- mo -- la -- tum in cru -- ce pro ho -- mi -- ne, cu -- jus la -- tus per -- fo -- ra -- tum "
         "flu -- xit a -- qua et san -- gui -- ne. A -- men.")


def mk_D():
    def make():
        spec = [{'id': 'S', 'name': 'Soprano', 'abbr': 'S.', 'clefs': ['treble'], 'voices': [('1', 1, D_S)]},
                {'id': 'A', 'name': 'Alto', 'abbr': 'A.', 'clefs': ['treble'], 'voices': [('1', 1, D_A)]},
                {'id': 'T', 'name': 'Tenor', 'abbr': 'T.', 'clefs': ['treble_8'],
                 'voices': [('1', 1, D_T1), ('2', 1, D_T2)]},
                {'id': 'B', 'name': 'Bass', 'abbr': 'B.', 'clefs': ['bass'], 'voices': [('1', 1, D_B)]}]
        sc = assemble(spec, time=(4, 4), key=(-3, 'major'))
        for pid in ('S', 'A', 'T', 'B'):
            set_verses(sc, pid, '1', [D_TXT], mode='attack')
        sc.title = 'Ave verum corpus'
        sc.composer = 'challenge corpus (CC0)'
        sc.lyricist = 'Latin, 14th century'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
        staves = []
        for pid, clef, name, short in (('S', 'treble', 'Soprano', 'S.'), ('A', 'treble', 'Alto', 'A.'),
                                       ('T', 'treble_8', 'Tenor', 'T.'), ('B', 'bass', 'Bass', 'B.')):
            vs = [(pid, '1'), (pid, '2')] if pid == 'T' else [(pid, '1')]
            staves.append(closed_staff('st' + pid, clef, vs, [((pid, '1'), [1], 'below')], name=name, short=short))
        lay = {'groups': [{'type': 'ChoirStaff', 'staves': staves}]}
        opts = base_opts('Ave verum corpus', poet='Latin, 14th century', composer='for mixed choir (CC0)',
                         size=22, paper='a4', font='TeX Gyre Termes',
                         extra_paper=['top-margin = 15\\mm', 'system-system-spacing.basic-distance = #22',
                                      'ragged-last-bottom = ##t'],
                         extra_layout=['\\context { \\Staff \\consists "Merge_rests_engraver" }'])
        return sc, lay, opts
    return make


ITEM_D = dict(
    id='satb-open-divisi-midpiece', title='Ave verum corpus (open score; divisi appears mid-piece)',
    make=mk_D(), pages=2,
    edge_cases=['satb_open_score', 'divisi_mid_piece', 'divisi_two_voices_one_staff_same_part',
                'divisi_chords_one_stem', 'bass_octave_divisi_chord', 'chords_must_stay_chords',
                'div_unis_markings', 'tenor_treble_8vb_clef', 'lyrics_under_every_staff', 'latin_text',
                'part_labels_full_then_abbrev', 'multi_page', 'dynamics', 'fermata', 'accidental_natural'],
    expected={
        'parts': ['Soprano', 'Alto', 'Tenor', 'Bass'],
        'must_not_split': True,
        'shared_staves': [],
        'notes': ('Open score, one staff per part, every staff labelled (full names on page 1, then S./A./T./B.). '
                  'MUST NOT create extra parts for the divisi passages: in mm.7-8 the Tenor staff splits into two '
                  'voices ("div.", stems up/down, back to "unis." in m.9) - both voices belong to the Tenor part '
                  '(truth: Tenor voice 1 and voice 2); in m.18 and mm.20-21 the Soprano sings two-note chords on '
                  'one stem and in mm.20-21 the Bass sings octave chords: these stay chords inside Soprano/Bass. '
                  'Exactly 4 parts. The tenor clef is a treble clef with a small 8 below (sounds an octave lower '
                  'than written): truth pitches are sounding pitches (e.g. m.16 tenor B3 natural). Lyrics are '
                  'printed under every staff and belong to each part (the second tenor voice in mm.7-8 has none).'),
    },
    truth_limitations=['Divisi voice 2 of the Tenor exists only in mm.7-8; elsewhere it is an empty voice '
                       '(<forward> in truth).'],
    license='Text public domain (Ave verum corpus, 14th-century Latin hymn); music and engraving CC0-1.0',
    source='self-authored (challenge corpus); text: "Ave verum corpus" (14th c.), lines 1-6 + Amen',
    attribution=('Ave verum corpus. Latin text (14th century), public domain.\n'
                 'Music: composed for this challenge corpus (2026), CC0 1.0 (unrelated to the settings by Mozart, '
                 'Byrd, Elgar or others).'),
    scans={
        'scan': dict(dpi=300, seed=7401, mode='gray', format='jpeg', quality=50,
                     summary='2-page flatbed scan; page 2 placed sideways (rotated 90 deg) and photocopied at 96.5%; '
                             'bleed-through of the facing page',
                     ops=[{'op': 'paper', 'rgb': [242, 242, 238], 'texture': 4,
                           'bleed': {'strength': 0.09, 'blur_mm': 0.4, 'shift_mm': 2}},
                          {'op': 'scale', 's': 0.965, 'pages': [1], 'dx_mm': 3, 'dy_mm': -2},
                          {'op': 'rotate', 'deg': 0.9, 'fill': 250, 'pages': [0]},
                          {'op': 'rotate', 'deg': -1.6, 'fill': 250, 'pages': [1]},
                          {'op': 'rot90', 'k': 1, 'pages': [1]},
                          {'op': 'gradient', 'strength': 0.08},
                          {'op': 'blur', 'sigma': 0.6}, {'op': 'noise', 'sigma': 3.5}]),
        'scan-mild': dict(dpi=600, seed=7402, mode='gray', format='jpeg', quality=60,
                          summary='2-page clean high-resolution scan at 600 dpi, slight skews 0.3/-0.5 deg',
                          ops=[{'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                               {'op': 'rotate', 'deg': 0.3, 'fill': 252, 'pages': [0]},
                               {'op': 'rotate', 'deg': -0.5, 'fill': 252, 'pages': [1]},
                               {'op': 'blur', 'sigma': 0.45}, {'op': 'noise', 'sigma': 2}]),
        'scan-severe': dict(dpi=150, seed=7403, mode='rgb', format='jpeg', quality=28,
                            spread={'pairs': [[0, 1]], 'gap_mm': 0, 'gutter': 0.6, 'gutter_width': 0.06,
                                    'fill': 60},
                            summary='open book scanned as one 2-up double-page spread at 150 dpi: gutter shadow '
                                    'and curl, 3 deg skew, yellowed paper, JPEG q28',
                            ops=[{'op': 'paper', 'rgb': [236, 228, 205], 'texture': 7},
                                 {'op': 'wave', 'amp_mm': 2.0, 'period': 1.0, 'phase': 1.57, 'fill': [60, 55, 50]},
                                 {'op': 'rotate', 'deg': 3.0, 'fill': [55, 52, 48], 'expand': True},
                                 {'op': 'vignette', 'strength': 0.18},
                                 {'op': 'blur', 'sigma': 0.9}, {'op': 'noise', 'sigma': 5, 'chroma': 2}]),
    },
)


# =====================================================================================
# E  TTBB closed score: tenors on a treble clef with 8 below (sounds an octave lower),
#    "a 2" (tenors) and "unis." (basses) passages printed as ONE voice with one stem
#    while both parts sing; divided again afterwards
# =====================================================================================

E_T1 = ("d'4\\mf d' ees' f' | g'4 f' ees' d' | c'4 ees' d'2 | f'4\\f^\"a+2\" ees' d' c' | bes4 c' d' ees' | "
        "f'8 ees' d'4 c'2 | d'4\\p d' ees' f' | g'4 g' f' ees' | d'4 c' bes2 | f'2\\mf d'2 | ees'4 c' bes2 | "
        "f'2\\f^\"a+2\" d'2 | ees'4 c' d'2\\fermata")
E_T2 = ("bes4 bes c' bes | bes4 bes g bes | a4 a bes2 | f'4\\hide ees'\\hide d'\\hide c'\\hide | "
        "bes4\\hide c'\\hide d'\\hide ees'\\hide | f'8\\hide ees'\\hide d'4\\hide c'2\\hide | bes4 bes c' bes | "
        "bes4 bes a a | f4 f f2 | bes2 bes2 | c'4 a f2 | f'2\\hide d'2\\hide | ees'4\\hide c'\\hide bes2\\fermata")
E_B1 = ("f4 g g f | ees4 f c f | f4 f f2 | f4 g g c | d4 f f c | f4 f f2 | bes,4^\"unis.\" g, c d | "
        "ees4 e f f, | bes,4 a, bes,2 | d2 bes,2 | ees4 ees d2 | d2^\"unis.\" g2 | c4 f, f2\\fermata")
E_B2 = ("bes,4 g, c d | ees4 d c bes, | f,4 f, bes,2 | d4 c g, a, | g,4 a, bes, c | d4 bes, f,2 | "
        "bes,4\\hide g,\\hide c\\hide d\\hide | ees4\\hide e\\hide f\\hide f,\\hide | "
        "bes,4\\hide a,\\hide bes,2\\hide | d2 g,2 | c4 f, bes,2 | d2\\hide g2\\hide | c4\\hide f,\\hide bes,2\\fermata")
E_TXT = ("In -- te -- ger vi -- tae sce -- le -- ris -- que pu -- rus non e -- get Mau -- ris ia -- cu -- lis "
         "ne -- que ar -- cu nec ve -- ne -- na -- tis gra -- vi -- da sa -- git -- tis, Fus -- ce, pha -- re -- tra, "
         "Fus -- ce, pha -- re -- tra.")


def mk_E():
    def make():
        spec = [{'id': 'T1', 'name': 'Tenor I', 'abbr': 'T. I', 'clefs': ['treble_8'], 'voices': [('1', 1, E_T1)]},
                {'id': 'T2', 'name': 'Tenor II', 'abbr': 'T. II', 'clefs': ['treble_8'], 'voices': [('1', 1, E_T2)]},
                {'id': 'B1', 'name': 'Bass I', 'abbr': 'B. I', 'clefs': ['bass'], 'voices': [('1', 1, E_B1)]},
                {'id': 'B2', 'name': 'Bass II', 'abbr': 'B. II', 'clefs': ['bass'], 'voices': [('1', 1, E_B2)]}]
        sc = assemble(spec, time=(4, 4), key=(-2, 'major'))
        set_verses(sc, 'T1', '1', [E_TXT], mode='attack')
        sc.title = 'Integer vitae'
        sc.composer = 'challenge corpus (CC0)'
        sc.lyricist = 'Horace, Odes I.22'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'T1', 'last': 'B2', 'symbol': 'bracket'}]
        lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
            closed_staff('upper', 'treble_8', [('T1', '1'), ('T2', '1')], [(('T1', '1'), [1], 'below')],
                         name=['Tenor I', 'Tenor II'], short=['T. I', 'T. II']),
            closed_staff('lower', 'bass', [('B1', '1'), ('B2', '1')], name=['Bass I', 'Bass II'],
                         short=['B. I', 'B. II'])]}]}
        opts = base_opts('Integer vitae', poet='Horace, Carmina I.22', composer='for male choir TTBB (CC0)',
                         size=20, paper='a4', font='DejaVu Serif',
                         extra_paper=['top-margin = 18\\mm', 'indent = 20\\mm'])
        return sc, lay, opts
    return make


ITEM_E = dict(
    id='ttbb-treble8-a2-unis', title='Integer vitae (TTBB closed score, octave treble clef, a 2 / unis.)',
    make=mk_E(), pages=1,
    edge_cases=['ttbb_closed', 'treble_8vb_clef_octave', 'shared_staff_two_voices', 'a2_one_voice_both_parts',
                'unis_one_voice_both_parts', 'divided_again_after_a2', 'unison_one_head_two_stems',
                'part_labels_roman_numerals', 'lyrics_only_under_upper_staff', 'latin_text', 'eighth_notes',
                'dynamics', 'fermata'],
    expected={
        'parts': ['Tenor I', 'Tenor II', 'Bass I', 'Bass II'],
        'must_not_split': False,
        'shared_staves': [['Tenor I', 'Tenor II'], ['Bass I', 'Bass II']],
        'notes': ('TTBB closed score. The upper staff uses a treble clef with a small 8 below: tenor notes SOUND an '
                  'octave lower than a plain treble clef would suggest (truth pitches, e.g. first note D4 not D5). '
                  'Split by stem direction into Tenor I/II and Bass I/II. Where "a 2" (tenors, mm.4-6 and m.12 to '
                  'beat 2 of m.13) or "unis." (basses, mm.7-9 and m.12 to beat 2 of m.13) is printed, the staff '
                  'shows a single line with one stem direction; BOTH parts of that staff sing it, so the notes '
                  'must appear in both parts (e.g. Tenor II in m.5 = Bb3 C4 D4 Eb4). The final chord is divided '
                  'again (stems up/down). Lyrics: one line between the staves aligned to Tenor I (truth carries '
                  'them on Tenor I only).'),
    },
    truth_limitations=['In the a 2 / unis. bars the second part is not drawn at all: its notes in truth are exact '
                       'copies of the printed line (verified: every such note has an identical printed carrier on '
                       'the same staff).',
                       'Lyrics only on Tenor I in truth.'],
    license='Text public domain (Horace, Odes I.22, c. 23 BC); music and engraving CC0-1.0',
    source='self-authored (challenge corpus); text: Horace, Carmina I.22, stanza 1 (+ repeat of "Fusce, pharetra")',
    attribution=('Integer vitae. Text: Quintus Horatius Flaccus (Horace), Odes I.22, public domain.\n'
                 'Music: composed for this challenge corpus (2026), CC0 1.0 (not the F. F. Flemming setting).'),
    scans={
        'scan': dict(dpi=200, seed=7501, mode='bilevel', format='png',
                     binarize={'thr': 172, 'noise': 14, 'pre_blur': 0.7},
                     summary='thick binarized photocopy at 200 dpi with a coffee ring, 4 deg skew',
                     ops=[{'op': 'ink_weight', 'n': 1},
                          {'op': 'paper', 'rgb': [244, 244, 244], 'texture': 5},
                          {'op': 'coffee', 'x': 0.72, 'y': 0.42, 'r_mm': 38, 'strength': 0.55, 'partial': True},
                          {'op': 'rotate', 'deg': 4.0, 'fill': 255, 'expand': True},
                          {'op': 'blur', 'sigma': 0.8}, {'op': 'speckle', 'per_mpx': 60}]),
        'scan-mild': dict(dpi=300, seed=7502, mode='gray', format='jpeg', quality=55,
                          summary='flatbed scan, 0.5 deg skew, light coffee ring',
                          ops=[{'op': 'paper', 'rgb': [245, 244, 240], 'texture': 3},
                               {'op': 'coffee', 'x': 0.72, 'y': 0.42, 'r_mm': 38, 'strength': 0.25},
                               {'op': 'rotate', 'deg': 0.5, 'fill': 250},
                               {'op': 'blur', 'sigma': 0.5}, {'op': 'noise', 'sigma': 2.5}]),
        'scan-severe': dict(dpi=100, seed=7503, mode='gray', format='jpeg', quality=15,
                            summary='100 dpi, 9.5 deg skew, out of focus, JPEG q15 (the clef 8 is barely visible)',
                            ops=[{'op': 'paper', 'rgb': [238, 238, 236], 'texture': 6},
                                 {'op': 'rotate', 'deg': -9.5, 'fill': 225, 'expand': True},
                                 {'op': 'blur', 'sigma': 1.6}, {'op': 'noise', 'sigma': 7}]),
    },
)


# =====================================================================================
# F  SSAA on two TREBLE staves (S I/II, A I/II) + piano grand staff whose right hand has
#    two voices and chords: the choir staves must be split, the piano must NOT be split
# =====================================================================================

F_S1 = ("R2. | R2. | e''2\\mp cis''4 | b'2 a'4 | b'2 cis''4 | d''2 cis''4 | b'2 a'4 | gis'2 a'4 | b'2. | "
        "@raw:\\pageBreak e''2 cis''4 | b'2 a'4 | d''2 cis''4 | b'2 cis''4 | d''2 cis''4 | b'2 gis'4 | a'2.\\fermata")
F_S2 = ("R2. | R2. | cis''2 a'4 | gis'2 e'4 | gis'2 a'4 | a'2 a'4 | gis'2 fis'4 | e'2 fis'4 | gis'2. | "
        "a'2 gis'4 | gis'2 fis'4 | a'2 a'4 | gis'2 a'4 | fis'2 e'4 | e'2 e'4 | e'2.\\fermata")
F_A1 = ("R2. | R2. | a'2\\mp e'4 | e'2 cis'4 | e'2 e'4 | fis'2 e'4 | e'2 cis'4 | cis'2 cis'4 | e'2. | "
        "cis'2 e'4 | e'2 cis'4 | fis'2 e'4 | e'2 e'4 | d'2 e'4 | e'2 d'4 | cis'2.\\fermata")
F_A2 = ("R2. | R2. | e'2 a4 | e'2 a4 | e'2 cis'4 | a2 a4 | b2 cis'4 | cis'2 cis'4 | b2. | "
        "a2 cis'4 | e'2 a4 | a2 a4 | b2 a4 | a2 a4 | b2 b4 | a2.\\fermata")
F_RH1 = ("a'4\\p b' cis'' | b'2. | e''2 cis''4 | b'2 a'4 | b'2 cis''4 | d''2 cis''4 | b'2 a'4 | gis'2 a'4 | "
         "b'2. | e''2 cis''4 | b'2 a'4 | d''2 cis''4 | b'2 cis''4 | d''2 cis''4 | b'2 gis'4 | a'2.\\fermata")
F_RH2 = ("<cis' e'>2. | <d' gis'>2. | <a' cis''>2 <e' a'>4 | <e' gis'>2 <cis' e'>4 | <e' gis'>2 <e' a'>4 | "
         "<fis' a'>2 <e' a'>4 | <e' gis'>2 <cis' fis'>4 | <cis' e'>2 <cis' fis'>4 | <e' gis'>2. | "
         "<cis' a'>2 <e' gis'>4 | <e' gis'>2 <cis' fis'>4 | <fis' a'>2 <e' a'>4 | <e' gis'>2 <e' a'>4 | "
         "<d' fis'>2 <cis' e'>4 | <e' gis'>2 <d' e'>4 | <cis' e'>2.")
F_LH = ("a,4 <e a cis'> <e a cis'> | e,4 <e gis b> <d gis b> | a,4 <e a cis'> <e a cis'> | "
        "e,4 <e gis b> <e a cis'> | e,4 <e gis b> <cis e a> | d,4 <d fis a> <e a cis'> | "
        "e,4 <e gis b> <fis a cis'> | cis,4 <e gis cis'> <fis a cis'> | e,4 <e gis b> <e gis b> | "
        "a,4 <e a cis'> <e gis cis'> | e,4 <e gis b> <fis a cis'> | d,4 <d fis a> <e a cis'> | "
        "e,4 <e gis b> <e a cis'> | d,4 <d fis a> <e a cis'> | e,4 <e gis b> <d gis b> | <a,, a,>2.\\fermata")
F_V = [
    "Love came down at Christ -- mas, Love all love -- ly, Love Di -- vine; "
    "Love was born at Christ -- mas, Star and An -- gels gave the sign.",
    "Wor -- ship we the God -- head, Love In -- car -- nate, Love Di -- vine; "
    "Wor -- ship we our Je -- sus: But where -- with for sa -- cred sign?",
]


def mk_F():
    def make():
        spec = [{'id': 'S1', 'name': 'Soprano I', 'abbr': 'S. I', 'clefs': ['treble'], 'voices': [('1', 1, F_S1)]},
                {'id': 'S2', 'name': 'Soprano II', 'abbr': 'S. II', 'clefs': ['treble'], 'voices': [('1', 1, F_S2)]},
                {'id': 'A1', 'name': 'Alto I', 'abbr': 'A. I', 'clefs': ['treble'], 'voices': [('1', 1, F_A1)]},
                {'id': 'A2', 'name': 'Alto II', 'abbr': 'A. II', 'clefs': ['treble'], 'voices': [('1', 1, F_A2)]},
                {'id': 'P', 'name': 'Piano', 'abbr': 'Pno.', 'instrument': 'piano', 'staves': 2,
                 'clefs': ['treble', 'bass'], 'voices': [('1', 1, F_RH1), ('2', 1, F_RH2), ('5', 2, F_LH)]}]
        sc = assemble(spec, time=(3, 4), key=(3, 'major'))
        set_verses(sc, 'S1', '1', F_V, mode='attack')
        sc.title = 'Love Came Down at Christmas'
        sc.composer = 'challenge corpus (CC0)'
        sc.lyricist = 'Christina Rossetti (1885)'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'S1', 'last': 'A2', 'symbol': 'bracket'}]
        lay = {'groups': [
            {'type': 'ChoirStaff', 'staves': [
                closed_staff('upper', 'treble', [('S1', '1'), ('S2', '1')], [(('S1', '1'), [1, 2], 'below')],
                             name=['Soprano I', 'Soprano II'], short=['S. I', 'S. II']),
                closed_staff('middle', 'treble', [('A1', '1'), ('A2', '1')], name=['Alto I', 'Alto II'],
                             short=['A. I', 'A. II'])]},
            {'type': 'PianoStaff', 'name': 'Piano', 'short': 'Pno.', 'staves': [
                closed_staff('rh', 'treble', [('P', '1'), ('P', '2')]),
                closed_staff('lh', 'bass', [('P', '5')])]}]}
        opts = base_opts('Love Came Down at Christmas', poet='Christina Rossetti, 1885',
                         composer='for SSAA choir and piano (CC0)', size=21, paper='a4', font='P052',
                         extra_paper=['top-margin = 14\\mm', 'system-system-spacing.basic-distance = #20',
                                      'ragged-last-bottom = ##t', 'max-systems-per-page = #2'],
                         extra_layout=['\\context { \\Staff \\consists "Merge_rests_engraver" }'])
        return sc, lay, opts
    return make


ITEM_F = dict(
    id='ssaa-two-treble-staves-piano', title='Love Came Down at Christmas (SSAA on two treble staves + piano)',
    make=mk_F(), pages=2,
    edge_cases=['ssaa_closed', 'two_treble_choir_staves', 'shared_staff_two_voices', 'piano_grand_staff',
                'piano_rh_two_voices_must_not_split', 'piano_chords_must_stay_chords', 'choir_tacet_full_bar_rests',
                'merged_full_bar_rests', 'piano_doubles_choir', 'lyrics_only_under_top_choir_staff',
                'multi_verse', 'part_labels_roman_numerals', 'three_four_time', 'key_signature_sharps', 'multi_page'],
    expected={
        'parts': ['Soprano I', 'Soprano II', 'Alto I', 'Alto II', 'Piano'],
        'must_not_split': True,
        'shared_staves': [['Soprano I', 'Soprano II'], ['Alto I', 'Alto II']],
        'notes': ('Two choir staves, BOTH in treble clef (Soprano I/II, Alto I/II) - do not mistake the alto '
                  'staff for a second soprano part or for a piano right hand. Split each choir staff by stem '
                  'direction into two parts (4 choir parts). The piano grand staff (brace, "Piano") is ONE part '
                  'with two staves: its right hand has two voices (melody stems up, two-note chords stems down) '
                  'and the left hand plays bass + chords - none of this may be split into separate parts and the '
                  'chords stay chords. Choir is tacet in mm.1-2 (one merged whole-bar rest per choir staff '
                  'stands for both parts). Two verses under the upper choir staff, aligned to Soprano I.'),
    },
    truth_limitations=['Lyrics only on Soprano I in truth.',
                       'Full-bar rests in mm.1-2 are written as measure rests in every choir part even though each '
                       'choir staff prints only one (merged) rest.'],
    license='Text public domain (Christina Rossetti, 1885); music and engraving CC0-1.0',
    source='self-authored (challenge corpus); text: Christina Rossetti, "Love came down at Christmas" (1885), '
           'stanzas 1-2',
    attribution=('Love Came Down at Christmas. Text: Christina G. Rossetti (1885), public domain.\n'
                 'Music (SSAA and piano): composed for this challenge corpus (2026), CC0 1.0.'),
    scans={
        'scan': dict(dpi=600, seed=7601, mode='rgb', format='jpeg', quality=45,
                     summary='reproduction printed with a halftone screen (tinted paper), rendered at 600 dpi and '
                             'rescanned at 200 dpi -> moire; page 2 photocopied at 97%; 1.5 / -0.8 deg skew',
                     ops=[{'op': 'paper', 'rgb': [228, 222, 206], 'ink': [30, 28, 30], 'texture': 3},
                          {'op': 'halftone', 'lpi': 133, 'deg': 45, 'strength': 0.85, 'white': [252, 250, 245]},
                          {'op': 'resample', 'factor': 0.3333333333, 'filter': 'bilinear'},
                          {'op': 'scale', 's': 0.97, 'pages': [1], 'fill': [240, 236, 226]},
                          {'op': 'rotate', 'deg': 1.5, 'fill': [236, 236, 236], 'pages': [0]},
                          {'op': 'rotate', 'deg': -0.8, 'fill': [236, 236, 236], 'pages': [1]},
                          {'op': 'blur', 'sigma': 0.4}, {'op': 'noise', 'sigma': 3}]),
        'scan-mild': dict(dpi=300, seed=7602, mode='gray', format='jpeg', quality=60,
                          summary='clean 2-page scan, 0.4 / 0.2 deg skew',
                          ops=[{'op': 'paper', 'rgb': [246, 246, 244], 'texture': 2},
                               {'op': 'rotate', 'deg': 0.4, 'fill': 252, 'pages': [0]},
                               {'op': 'rotate', 'deg': 0.2, 'fill': 252, 'pages': [1]},
                               {'op': 'blur', 'sigma': 0.45}, {'op': 'noise', 'sigma': 2}]),
        'scan-severe': dict(dpi=110, seed=7603, mode='rgb', format='jpeg', quality=20,
                            summary='rehearsal copy at 110 dpi: heavy pencil (circled notes, part reminders, '
                                    'breath marks), red-pen circles, foxing, 7 / -5 deg skew, page 2 at 95%, '
                                    'motion blur, JPEG q20',
                            ops=[{'op': 'paper', 'rgb': [240, 234, 218], 'texture': 6},
                                 {'op': 'foxing', 'n': 40, 'size_mm': [0.4, 1.8]},
                                 {'op': 'pencil', 'circles': 6, 'breaths': 4, 'ticks': 2, 'arrows': 1,
                                  'texts': ['S1!', 'A2 here', 'breathe', 'watch'], 'alpha': 0.7,
                                  'width_mm': 0.4},
                                 {'op': 'pencil', 'circles': 3, 'color': [190, 40, 40], 'alpha': 0.8,
                                  'width_mm': 0.5},
                                 {'op': 'scale', 's': 0.95, 'pages': [1], 'fill': [240, 234, 218]},
                                 {'op': 'rotate', 'deg': 7.0, 'fill': [210, 210, 210], 'expand': True,
                                  'pages': [0]},
                                 {'op': 'rotate', 'deg': -5.0, 'fill': [210, 210, 210], 'expand': True,
                                  'pages': [1]},
                                 {'op': 'motion_blur', 'len_mm': 0.6, 'deg': 0},
                                 {'op': 'noise', 'sigma': 6, 'chroma': 3}]),
    },
)


# =====================================================================================
# G  closed SATB in cut time, labels "S A" / "T B"; soprano and alto in unison for a
#    whole phrase; tied note in one voice vs re-attack of the same pitch in the other;
#    bass solo with its own text under the bass staff; Amen with chords on the soprano
#    and bass stems (must stay chords)
# =====================================================================================

G_S = ("c''4\\f b' a' g' | a'4 b' c''2 | e''4 d'' c'' b' | a'4 b' g'2~ | g'2 r2 | R1 | c''4\\f b' a' g' | "
       "a'4 b' c''2 | <a' c''>1 | <g' c''>1\\fermata")
G_A = ("c''4 b' a' g' | a'4 b' c''2 | g'2 e'2 | a'4 g' e'2 | g'2 r2 | R1 | r4 g' f' e' | f'4 f' e'2 | f'1 | "
       "e'1\\fermata")
G_T = "e'4 b c' c' | f4 d' e'2 | c'2 c'2 | c'4 b c'2 | r1 | r1 | g2 a2~ | a4 g c'2 | c'1 | c'1\\fermata"
G_B = ("c4 g f e | f4 g c2 | c2 e2 | f4 g c2 | r4 g\\mf g c' | b4 a g f | e4\\f d c c | a4 d c2 | <f, f>1 | "
       "<c, c>1\\fermata")
G_TXT = ("Hark! the her -- ald an -- gels sing, Glo -- ry to the new -- born King; "
         "God and sin -- ners re -- con -- ciled. A -- men.")
G_BASS = "Peace on earth, and mer -- cy mild,"


def mk_G():
    def make():
        sc = satb({'S': G_S, 'A': G_A, 'T': G_T, 'B': G_B}, (2, 2), (0, 'major'), time_symbol='cut')
        set_verses(sc, 'S', '1', [G_TXT], mode='attack')
        set_lyrics_range(sc, 'B', '1', 1, G_BASS, 4, 6)
        sc.title = 'Hark! the Herald Angels Sing'
        sc.composer = 'challenge corpus (CC0)'
        sc.lyricist = 'Charles Wesley (1739), alt. George Whitefield (1753)'
        sc.rights = 'Text public domain; music CC0 1.0'
        sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
        lay = {'groups': [{'type': 'ChoirStaff', 'staves': [
            closed_staff('upper', 'treble', [('S', '1'), ('A', '1')], [(('S', '1'), [1], 'below')],
                         name=['S', 'A'], short=['S', 'A']),
            closed_staff('lower', 'bass', [('T', '1'), ('B', '1')], [(('B', '1'), [1], 'below')],
                         name=['T', 'B'], short=['T', 'B'])]}]}
        opts = base_opts('Hark! the Herald Angels Sing', poet='Charles Wesley, 1739',
                         composer='(new tune, CC0)', size=22, paper='letter', font='URW Bookman',
                         extra_paper=['top-margin = 20\\mm', 'indent = 8\\mm'],
                         extra_layout=['\\context { \\Staff \\consists "Merge_rests_engraver" }'])
        return sc, lay, opts
    return make


ITEM_G = dict(
    id='satb-closed-ties-solo-amen-chords', title='Hark! the Herald Angels Sing (closed SATB, S A / T B labels, '
                                                  'ties vs re-attacks, bass solo, chords on one stem)',
    make=mk_G(), pages=1,
    edge_cases=['satb_closed', 'part_labels_single_letters', 'unison_whole_phrase_two_stems',
                'tie_in_one_voice_reattack_in_other', 'one_voice_rests_other_sings', 'bass_solo_lower_staff_lyrics',
                'lyrics_lower_staff_only_for_solo', 'chords_on_soprano_stem_closed_score',
                'bass_octave_chord_on_stem', 'chords_must_stay_chords', 'merged_rests', 'cut_time_alla_breve',
                'dynamics', 'fermata'],
    expected={
        'parts': ['Soprano', 'Alto', 'Tenor', 'Bass'],
        'must_not_split': True,
        'shared_staves': [['Soprano', 'Alto'], ['Tenor', 'Bass']],
        'notes': ('Closed score labelled only "S A" and "T B". mm.1-2: soprano and alto sing the same notes (every '
                  'head carries an up- and a down-stem) - both parts get the full phrase. m.4-5: the soprano '
                  'g\' is TIED over the barline while the alto RE-ATTACKS g\' on m.5 beat 1 (same head position): '
                  'truth has a tie in Soprano and a new note in Alto; the same happens in mm.7-8 on the bass staff '
                  '(tenor a tied, bass re-attacks a). mm.5-6: upper voices and tenor rest while the bass sings '
                  'a solo whose words ("Peace on earth, and mercy mild") are printed under the bass staff and '
                  'belong to the Bass. m.7: alto enters after a quarter rest. Amen (mm.9-10): the soprano sings '
                  'two-note chords on its up-stem and the bass octaves on its down-stem - these must stay chords '
                  'inside Soprano/Bass (must_not_split refers to these chords), the alto and tenor single notes '
                  'are separate parts. Exactly 4 parts.'),
    },
    truth_limitations=['Upper lyric line on Soprano only in truth; lower line (bass solo) on Bass.',
                       'Rests merged by the engraver (one printed rest for two voices) are explicit rests in both '
                       'parts in truth.'],
    license='Text public domain (Charles Wesley, 1739; alt. G. Whitefield, 1753); music and engraving CC0-1.0',
    source='self-authored (challenge corpus); text: Wesley/Whitefield "Hark! the herald angels sing", stanza 1 '
           'lines 1-4',
    attribution=('Hark! the Herald Angels Sing. Text: Charles Wesley (1739), altered by George Whitefield (1753), '
                 'public domain.\nTune and SATB setting: composed for this challenge corpus (2026), CC0 1.0 '
                 '(not the Mendelssohn tune).'),
    scans={
        'scan': dict(dpi=150, seed=7701, mode='rgb', format='jpeg', quality=30,
                     summary='copy on light-blue paper scanned at 150 dpi with the lid open: dark top border, '
                             'strong lighting gradient, -1.8 deg skew, JPEG q30',
                     ops=[{'op': 'paper', 'rgb': [212, 225, 238], 'ink': [36, 40, 58], 'texture': 5, 'fibers': 2},
                          {'op': 'rotate', 'deg': -1.8, 'fill': [30, 30, 32]},
                          {'op': 'gradient', 'strength': 0.3, 'angle': 270},
                          {'op': 'vignette', 'strength': 0.15},
                          {'op': 'blur', 'sigma': 0.7}, {'op': 'noise', 'sigma': 4.5, 'chroma': 2}]),
        'scan-mild': dict(dpi=300, seed=7702, mode='gray', format='jpeg', quality=60,
                          summary='office scan, 0.7 deg skew',
                          ops=[{'op': 'paper', 'rgb': [245, 245, 243], 'texture': 2},
                               {'op': 'rotate', 'deg': 0.7, 'fill': 252},
                               {'op': 'blur', 'sigma': 0.45}, {'op': 'noise', 'sigma': 2}]),
        'scan-severe': dict(dpi=125, seed=7703, mode='bilevel', format='png',
                            binarize={'thr': 105, 'noise': 20, 'pre_blur': 0.7},
                            summary='thin binarized copy at 125 dpi, right edge cropped through the staff ends, '
                                    '10 deg skew, speckles',
                            ops=[{'op': 'paper', 'rgb': [238, 238, 238], 'texture': 9},
                                 {'op': 'crop', 'cut_staff_right_mm': 3.0, 'top_mm': 6},
                                 {'op': 'rotate', 'deg': 10.0, 'fill': 255, 'expand': True},
                                 {'op': 'blur', 'sigma': 0.8}, {'op': 'speckle', 'per_mpx': 140},
                                 {'op': 'saltpepper', 'amount': 0.0012}]),
    },
)

ITEMS = [ITEM_A, ITEM_B, ITEM_C, ITEM_D, ITEM_E, ITEM_F, ITEM_G]
