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

ITEMS = [ITEM_A, ITEM_B, ITEM_C]
