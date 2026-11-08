"""voice-piano: art-song layout - a vocal staff with lyrics above a braced piano grand staff."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

VOICE = ("R1 | r2 r4 bes'4\\mp | ees''2 r4 bes'4 | c''4 d'' ees'' f'' | g''2.( f''4) | "
         "ees''4 d''8 c'' bes'4 c'' | bes'2 r4 bes'4 | aes''4\\mf g'' f'' ees'' | f''4. ees''8 d''4 c'' | "
         "bes'4\\> c'' d'' ees'' | ees''1\\!\\fermata")
TEXT = ("Sleep now, the stars are keep -- ing watch _ the moon is on the sea; the "
        "wind has fold -- ed up its wings, and all is still for thee.")
RH = ("g'8(\\p bes' ees'' bes' g' bes' ees'' bes') | f'8( aes' d'' aes' f' aes' d'' aes') | "
      "<g' bes'>4 <g' bes'> <g' bes'> <g' bes'> | <aes' c''>4 <aes' c''> <g' bes'> <aes' c''> | "
      "<g' bes' ees''>2 <f' aes' d''>2 | <g' bes'>4 <aes' c''> <g' bes'> <aes' c''> | <f' aes' d''>2 <f' aes' d''>4 r4 | "
      "<aes' c'' ees''>2 <aes' c'' f''>2 | <aes' d'' f''>2 <aes' d''>2 | <g' bes' ees''>2\\< <aes' c'' ees''>2 | "
      "<g' bes' ees''>1\\!\\fermata")
LH = ("ees2\\sustainOn bes,2\\sustainOff | bes,2 d2 | ees2 g2 | aes,2 c2 | bes,2 bes,2 | ees2 aes,2 | "
      "bes,2 bes,4 r4 | aes,2 f,2 | bes,2 bes,,2 | ees2 aes,2 | ees,1\\fermata")


def make():
    v = mk_part('V', 'Voice', 'V.', 'voice', 1, ['treble'])
    pn = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((4, 4), (-3, 'major'), [(v, {'1': VOICE}), (pn, {'1': RH, '5': LH})])
    set_verses(sc, 'V', '1', [TEXT], mode='attack')
    add_mark(sc, 0, 'tempo', text='Andante tranquillo', unit='quarter', bpm=66)
    breaks(sc, systems=(4, 8))
    hdr = header(sc, 'Night Song', 'for voice and piano', lyricist='Words: coverage suite (2026)')
    lay = {'groups': [
        {'type': None, 'staves': [
            {'id': 'v', 'clef': 'treble', 'name': 'Voice', 'voices': [('V', '1')],
             'lyrics': [{'voice': ('V', '1'), 'verses': [1], 'place': 'below', 'stanza': False}]}]},
        {'type': 'PianoStaff', 'name': 'Piano', 'staves': [
            {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
            {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]}]}
    return sc, lay, opts(hdr, 19, extra_paper=['indent = 16\\mm', 'system-system-spacing.basic-distance = #18'])


ITEM = dict(
    id='voice-piano-night-song',
    title='Night Song - voice with lyrics above a piano grand staff',
    layout='voice-piano', make=make, pages=1, must_not_split=True,
    expected_notes=('TWO parts: "Voice" (one staff, lyrics) and "Piano" (ONE part, two staves joined by a brace; '
                    'must not be split). The voice is silent in m.1 (whole-bar rest) and enters on beat 4 of m.2. '
                    'The voice staff is not connected to the piano brace. Piano chords stay chords.'),
    truth_limitations=['Lyrics belong to the Voice part only.'],
    layout_desc='A4 portrait, staff size 19, 3 systems (4+4+3 measures) of voice staff + piano grand staff',
    scans=scans(4, 'T4', 'S4'),
    attribution='Night Song for voice and piano - music and words composed for the OMR coverage suite (2026) - '
                'CC0 1.0.\n\n' + CC0_NOTE,
)
