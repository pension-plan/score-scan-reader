"""L7: 'A Red, Red Rose' - one page holding exactly ONE system (voice + piano), a text-heavy
title block (dedication, title, subtitle, poet, composer, tempo, copyright footer) and
stanzas 2-4 printed as a poem block below the music (must NOT become lyrics)."""
from __future__ import annotations

from .common import (CC0_NOTE, add_mark, assemble, bass_note, chord_ly, close_chord, mk_part)
from lsynth.model import set_verses

VOICE = ("c'4\\p | f'4 f' g' a' | c''4 bes' a'2 | g'4 f' g' a' | g'4 f'2 c'4 | "
         "f'4\\mf f' g' a' | d''4\\< c'' a'2\\! | bes'4^\"rit.\" a' g' f' | g'4 f'2\\fermata")
STANZA1 = ("O my Luve's like a red, red rose, That's new -- ly sprung in June; "
           "O my Luve's like the mel -- o -- die That's sweet -- ly play'd in tune.")
STANZAS = [
    ("2.", ["As fair art thou, my bonnie lass,", "So deep in luve am I;", "And I will luve thee still, my dear,",
            "Till a' the seas gang dry."]),
    ("3.", ["Till a' the seas gang dry, my dear,", "And the rocks melt wi' the sun:",
            "I will luve thee still, my dear,", "While the sands o' life shall run."]),
    ("4.", ["And fare thee weel, my only luve!", "And fare thee weel awhile!", "And I will come again, my luve,",
            "Tho' it were ten thousand mile."]),
]
# chord per beat (pickup = 1 beat, last bar = 3 beats)
CHORDS = [['C'], ['F', 'F', 'C', 'F'], ['F', 'Bb', 'F', 'F'], ['C', 'Dm', 'C', 'F'], ['C', 'F', 'F', 'C'],
          ['F', 'F', 'C', 'F'], ['Bb', 'F', 'Dm', 'Dm'], ['Gm', 'F', 'C', 'Bb'], ['C7', 'F', 'F']]


def piano():
    rh, lh = [], []
    for bi, beats in enumerate(CHORDS):
        if bi == 0:
            rh.append('r4')
            lh.append('r4')
            continue
        r, l = [], []
        k = 0
        while k < len(beats):
            sym = beats[k]
            # half note when the chord is held over two beats on a half-bar boundary
            if k % 2 == 0 and k + 1 < len(beats) and beats[k + 1] == sym:
                r.append(chord_ly(close_chord(sym, 62, 3)) + '2')
                k += 2
            else:
                r.append(chord_ly(close_chord(sym, 62, 3)) + '4')
                k += 1
        # LH: bass per half bar (dotted half in the 3-beat last bar)
        if len(beats) == 4:
            l.append(chord_ly([bass_note(beats[0], 36, 47)]) + '2')
            l.append(chord_ly([bass_note(beats[2], 36, 47)]) + '2')
        else:
            l.append(chord_ly([bass_note(beats[0], 36, 47)]) + '4')
            l.append(chord_ly([bass_note(beats[1], 36, 47)]) + '2')
        if bi == 1:
            r[0] += '\\p'
        if bi == len(CHORDS) - 1:
            r[-1] += '\\fermata'
            l[-1] += '\\fermata'
        rh.append(' '.join(r))
        lh.append(' '.join(l))
    return ' | '.join(rh), ' | '.join(lh)


def make():
    rh, lh = piano()
    v = mk_part('V', 'Voice', 'V.', 'voice', 1, ['treble'])
    p = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((4, 4), (-1, 'major'), [(v, {'1': VOICE}), (p, {'1': rh, '5': lh})])
    sc.measures[-1].right_bar = 'final'
    set_verses(sc, 'V', '1', [STANZA1], mode='attack')
    sc.title = 'A Red, Red Rose'
    sc.composer = 'Layout-challenge corpus (melody and accompaniment, CC0)'
    sc.lyricist = 'Robert Burns (1794)'
    sc.rights = 'Text public domain; music and engraving dedicated to the public domain (CC0 1.0)'
    add_mark(sc, 0, 'tempo', text='Andante con espressione', unit='quarter', bpm=66)
    sc.credits = [
        {'page': 1, 'type': 'dedication', 'text': 'for the Tuesday evening singers'},
        {'page': 1, 'type': 'title', 'text': 'A Red, Red Rose'},
        {'page': 1, 'type': 'subtitle', 'text': 'Song for medium voice and piano'},
        {'page': 1, 'type': 'lyricist', 'text': 'Words: Robert Burns (1794)'},
        {'page': 1, 'type': 'composer', 'text': 'Music: layout-challenge corpus (2026)'},
        {'page': 1, 'type': 'text', 'text': 'Stanzas 2-4 printed as a poem below the music'},
        {'page': 1, 'type': 'rights', 'text': 'Dedicated to the public domain (CC0 1.0). Text: R. Burns, 1794.'},
    ]
    lay = {'groups': [
        {'type': None, 'staves': [{'id': 'voice', 'clef': 'treble', 'name': 'Voice', 'voices': [('V', '1')],
                                   'lyrics': [{'voice': ('V', '1'), 'verses': [1], 'place': 'below',
                                               'stanza': True, 'labels': {1: '1.'}}]}]},
        {'type': 'PianoStaff', 'name': 'Piano', 'staves': [
            {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
            {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]},
    ]}
    stz = []
    for lab, lines in STANZAS:
        col = ' '.join('"' + l.replace('"', '\\"') + '"' for l in lines)
        stz.append(f'\\line {{ \\bold "{lab}" \\hspace #1 \\column {{ {col} }} }}')
    after = ['\\markup { \\vspace #3 }',
             '\\markup { \\fill-line { \\hspace #2 \\column { ' + stz[0] + ' \\vspace #1.2 ' + stz[1] +
             ' } \\hspace #3 \\column { ' + stz[2] + ' } \\hspace #2 } }']
    opts = {'header': {'dedication': '\\markup \\italic "for the Tuesday evening singers"',
                       'title': 'A Red, Red Rose', 'subtitle': 'Song for medium voice and piano',
                       'poet': 'Words: Robert Burns (1794)', 'composer': 'Music: layout-challenge corpus (2026)',
                       'copyright': 'Dedicated to the public domain (CC0 1.0). Text: R. Burns, 1794.'},
            'staff_size': 14, 'paper': 'a4', 'font': 'TeX Gyre Schola', 'forced_breaks': True,
            'auto_beam_off_vocal': True,
            'paper_extra': ['indent = 11\\mm', 'top-margin = 22\\mm', 'left-margin = 11\\mm',
                            'right-margin = 10\\mm', 'markup-system-spacing.basic-distance = #22',
                            'ragged-bottom = ##t'],
            'layout_extra': ['\\context { \\Lyrics \\override LyricText.font-size = #-0.4 }'],
            'after_markup': after}
    return sc, lay, opts


ITEM = dict(
    id='song-one-system-poem-block',
    title='A Red, Red Rose - a page with only one system, poem stanzas as a text block',
    make=make, pages=1,
    edge_cases=['single_system_page', 'title_block_text', 'dedication_text', 'tempo_text', 'dynamics_text',
                'copyright_footer', 'extra_stanzas_as_text_block_not_lyrics', 'pickup', 'lyrics', 'voice_piano',
                'piano_grand_staff', 'must_not_split', 'stanza_number_label', 'fermata', 'hairpin'],
    must_not_split=True,
    expected_notes=('Two parts: Voice (1 staff, lyrics stanza 1 only) and Piano (ONE part, 2 staves). The page has a '
                    'single system. Stanzas 2-4 are printed as a poem block below the music and must NOT be attached '
                    'to notes as lyrics; title/dedication/poet/composer/tempo/copyright text must not become notes or '
                    'lyrics. The stanza label "1." is not a syllable.'),
    truth_limitations=('Beaming is not encoded (no <beam>). Header/footer text is recorded as <credit> elements '
                       '(no positions). The poem block (stanzas 2-4) is recorded only in meta, not in the truth.'),
    layout_desc='A4 portrait, staff size 17, one system: Voice + Piano grand staff, 9 measures incl. pickup',
    license='Text public domain (Burns 1794); melody, accompaniment and engraving CC0-1.0',
    source='self-authored (layout-challenge corpus); text Robert Burns, "A Red, Red Rose" (1794)',
    attribution='\n'.join(['"A Red, Red Rose": text by Robert Burns (1794) - public domain.',
                           'Melody and piano accompaniment composed for this corpus - CC0 1.0.', '', CC0_NOTE]),
)
