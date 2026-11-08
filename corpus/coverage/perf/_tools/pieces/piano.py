"""Dense one-page piano piece "Toccatina" (own composition, CC0): 18 bars on one page that use as
many piano symbols as possible (4 key / 4 time signatures, repeat + voltas, rehearsal marks,
tempo + metronome marks, grace notes (plain + slashed), trill, mordent, turn, arpeggios, fingering,
staccato / staccatissimo / accent / tenuto / marcato, fermatas, breath mark, tremolo, ottava 8va / 8vb,
clef changes, sharps / flats / naturals / double sharp / double flat / courtesy accidentals,
triplets / quintuplet / sextuplet, 16th / 32nd / 64th notes, double dots, ties across a system break,
two voices on the right-hand staff, pedal, dynamics pp..ff + sfz, hairpins, a whole-bar rest,
Fine + D.C. al Fine)."""
from __future__ import annotations

from cov.dsl import parse_voice

from .common import CC0_NOTE, PAPER, add_mark, assemble, finish_measures, mk_part, set_time

RH1 = [
    # A  (G major, C)  m1-m5
    "g''16-1\\f( a'' b'' c''' d'''8-.) d'''-. \\tup3/2 e'''8( d''' c''') \\tupend b''4->",
    "<b' d''>8.( cis''16 <a' c''>8. b'16) <g' b'>2",
    "\\gs fis''8 g''4\\trill a''8( b'') \\g c'''16 \\g d''' e'''4 d'''8 c'''",
    "b''4\\mordent a''8.\\turn g''16 g''2\\fermata",
    "b''4.. a''16 g''2",
    # B  (E-flat major, 3/4)  m6-m9 : two voices
    "g''2\\p^\"dolce\"( f''4)",
    "ees''4( d''8 c'' bes'4)",
    "f''4\\< g''8( aes'') bes''4~",
    "bes''2.\\mf\\!\\fermata",
    # C  (E major, 6/8)  m10-m13
    "\\ottava=1 e'''8-.\\ff fis'''-. gis'''-. a'''4.-^ \\ottava=0",
    "gis''8( fisis'' gis'') b''4.",
    "fis''?8 e'' d'' e''4 r8",
    "e''4.\\> r4.\\!",
    # D  (A-flat major, cut time)  m14-m18
    "\\tup6/4 aes16-1\\mp^\"leggiero\"( c' ees' aes' c'' ees'') \\tupend aes''4-! "
    "\\tup5/4 g''16( f'' ees'' des'' c'') \\tupend bes'4\\breathe",
    "c''8.\\sfz beses'32 aes' g'4-- f'8( ees'16 des') c'4",
    "\\tup3/2 bes'?4\\<( c'' des'') \\tupend ees''2-^\\!",
    "c'''64( des''' c''' bes'' aes''8.) r8 r16 ees''16 <c'' ees'' aes''>2\\pp\\arpeggio\\fermata",
    "R1",
]
RH2 = ["s1", "s1", "s1", "s1", "s1",
       "ees''8 bes' ees'' bes' d'' bes'",
       "aes'2 g'4",
       "d''2 d''4",
       "<ees'' g''>2.",
       "s2.", "s2.", "s2.", "s2.",
       "s1", "s1", "s1", "s1", "s1"]
LH = [
    "<g,-5 d-2 g-1>4 r8 d8-. g-. d-. <g, b,>4--",
    "g,8 d b, d g, d b, d",
    "c8 g e g d a fis a",
    "<g, d>2 g,,2\\fermata",
    "<d a>4 <d c'>4 <g, d b>2",
    "ees,4\\sustainOn <g bes> <g bes>",
    "aes,4\\sustainOff\\sustainOn <c' ees'> <c' ees'>",
    "bes,,4\\sustainOff\\sustainOn <aes d'> <aes d'>",
    "<ees, bes,>2.\\sustainOff\\sustainOn",
    "\\clef=treble e'8\\sustainOff gis' b' e''4.",
    "\\clef=bass e,8 b, e gis,4.",
    "a,8 e a b,4.",
    "<e, b, gis>2.",
    "\\ottava=-1 aes,,4 ees,,4 \\ottava=0 aes,2:32",
    "<aes, ees>4 <bes, des f>4 <c ees aes>4 <des f aes>4",
    "<ees, ees>2 r2",
    "aes,,2.\\sustainOn r4\\sustainOff",
    "<aes,, ees, aes,>1\\fermata",
]


def make(paper='A4'):
    rh1 = parse_voice(' | '.join(RH1))
    rh2 = parse_voice(' | '.join(RH2))
    lh = parse_voice(' | '.join(LH))
    piano = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ('treble', 'bass'), (('1', 1), ('2', 1), ('5', 2)))
    # rh2 is only present in bars 6-9: elsewhere its bars are spacers (no truth events)
    sc = assemble((4, 4), (1, 'major'), [(piano, {'1': rh1, '2': rh2, '5': lh})], time_symbol='common')
    set_time(sc, 5, (3, 4))
    set_time(sc, 9, (6, 8))
    set_time(sc, 13, (2, 2), 'cut')
    sc.measures[5].key = (-3, 'major')
    sc.measures[9].key = (4, 'major')
    sc.measures[13].key = (-4, 'major')
    sc.measures[0].left_bar = 'repeat-start'
    sc.measures[3].volta_start, sc.measures[3].volta_end, sc.measures[3].right_bar = '1', 'stop', 'repeat-end'
    sc.measures[4].volta_start, sc.measures[4].volta_end, sc.measures[4].right_bar = '2', 'discontinue', 'double'
    sc.measures[8].right_bar = 'double'
    sc.measures[12].right_bar = 'final'
    sc.measures[12].end_marks.append(dict(kind='words', text='Fine', style='bold', sound={'fine': 'yes'}))
    sc.measures[-1].right_bar = 'final'
    sc.measures[-1].end_marks.append(dict(kind='words', text='D.C. al Fine', style='italic', sound={'dacapo': 'yes'}))
    finish_measures(sc)
    add_mark(sc, 0, 'tempo', text='Allegro', unit='quarter', bpm=132)
    add_mark(sc, 0, 'rehearsal', text='A')
    add_mark(sc, 5, 'tempo', text='Andante', unit='quarter', bpm=76)
    add_mark(sc, 5, 'rehearsal', text='B')
    add_mark(sc, 9, 'tempo', text='Vivace', unit='quarter', dots=1, bpm=116)
    add_mark(sc, 9, 'rehearsal', text='C')
    add_mark(sc, 13, 'tempo', text='Tempo I', sound_tempo=132)
    add_mark(sc, 13, 'rehearsal', text='D')
    for i in (4, 8, 13, 15):
        sc.measures[i].brk = 'system'
    sc.title = 'Toccatina'
    sc.composer = 'coverage corpus (CC0)'
    sc.rights = 'CC0 1.0'
    sc.credits = [{'page': 1, 'type': 'title', 'text': 'Toccatina'},
                  {'page': 1, 'type': 'subtitle', 'text': 'symbol-dense piano page'},
                  {'page': 1, 'type': 'composer', 'text': 'coverage corpus (CC0)'}]
    pname, wmm, hmm = PAPER[paper]
    scale = {'A4': 1.0, 'Letter': 1.0, 'A3': 2 ** 0.5}[paper]
    staff = 19 * scale
    sc.page = {'name': paper, 'width_mm': wmm, 'height_mm': hmm, 'staff_size': staff}
    layout = {'groups': [{'type': 'PianoStaff', 'name': 'Piano', 'staves': [
        {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1'), ('P', '2')], 'part_staves': [('P', 1)]},
        {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')], 'part_staves': [('P', 2)]}]}]}
    mg = lambda v: f'{v * scale:.2f}\\mm'
    opts = {'header': {'title': 'Toccatina', 'subtitle': 'symbol-dense piano page',
                       'composer': 'coverage corpus (CC0)'},
            'staff_size': round(staff, 3), 'paper': pname,
            'paper_extra': [f'top-margin = {mg(12)}', f'bottom-margin = {mg(12)}', f'left-margin = {mg(14)}',
                            f'right-margin = {mg(14)}', 'ragged-last-bottom = ##f',
                            'system-system-spacing.basic-distance = #16'],
            'layout_extra': []}
    info = dict(
        layout='piano', layout_also=['two-voices-one-staff-instrument'],
        parts=['Piano'], must_not_split=True,
        expected_notes=('One Piano part on a grand staff (2 staves); bars 6-9 have two voices on the upper '
                        'staff (stems up / down) that stay in the Piano part. Sounding pitches under the '
                        '8va (bar 10) and 8vb (bar 14) brackets are an octave above / below the written '
                        'note heads. Bars 1-4 are repeated (1st ending bar 4, 2nd ending bar 5); "Fine" ends bar 13 and '
                        '"D.C. al Fine" ends bar 18 (encoded as words + <sound fine/dacapo>).'),
        truth_limitations=('Dynamics / hairpins / pedal marks are directions without placement attributes. '
                           'The truth has no <sound> playback for the repeat; voltas and repeat barlines are '
                           'encoded as printed.'),
        title='Toccatina - symbol-dense 1-page piano piece (18 bars, 4 keys, 4 metres)',
        license='CC0', source='own composition for the coverage corpus',
        attribution='\n'.join(['Toccatina (symbol-dense piano page): composed for the coverage corpus - CC0 1.0.',
                               '', CC0_NOTE]),
    )
    return sc, layout, opts, info
