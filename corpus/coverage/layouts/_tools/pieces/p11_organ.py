"""organ: organ on three staves (two manuals joined by a brace + pedal staff), one part."""
import copy

from csynth.dsl import parse_voice
from csynth.harmonize import harmonize

from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

SOP = ("a'4 c'' b' a' | gis'4 a' b'2\\fermata | c''4 d'' e'' d''8 c'' | b'2 a'2\\fermata | "
       "e''4 d'' c'' b' | a'4 b' c''2\\fermata | b'4 a' a' gis' | a'1\\fermata")
CHORDS = ['Am', 'C', 'E', 'F', 'E', 'Am', 'E', 'Am', 'Dm', 'C', 'G', 'Am', 'E', 'Am',
          'C', 'G', 'Am', 'E', 'F', 'G', 'C', 'E', 'F', 'Dm', 'E', 'A']


def make():
    sop = parse_voice(SOP)
    alt, ten, bas = harmonize(sop, CHORDS, 9)
    org = mk_part('O', 'Organ', 'Org.', 'piano', 3, ['treble', 'bass', 'bass'],
                  [('1', 1), ('2', 1), ('5', 2), ('9', 3)])
    org.part_symbol = ('brace', 1, 2)
    sc = assemble((4, 4), (0, 'minor'), [(org, {'1': sop, '2': alt, '5': ten, '9': copy.deepcopy(bas)})])
    # registration texts (words) and dynamics
    s0 = [e for e in org.measures[0]['1'] if e.kind == 'note'][0]
    s0.words.append(("Man. I: Principal 8', Octave 4'", 'above', 'italic'))
    s0.dynamics.append('mf')
    t0 = [e for e in org.measures[0]['5'] if e.kind == 'note'][0]
    t0.words.append(("Man. II: Gedackt 8'", 'above', 'italic'))
    b0 = [e for e in org.measures[0]['9'] if e.kind == 'note'][0]
    b0.words.append(("Ped.: Subbass 16', Octave 8'", 'above', 'italic'))
    s4 = [e for e in org.measures[4]['1'] if e.kind == 'note'][0]
    s4.dynamics.append('f')
    add_mark(sc, 0, 'tempo', text='Andante maestoso', unit='quarter', bpm=63)
    breaks(sc, systems=(4,))
    hdr = header(sc, 'Chorale Prelude', 'for organ (manuals and pedal)')
    lay = {'groups': [
        {'type': 'PianoStaff', 'name': 'Organ', 'staves': [
            {'id': 'man1', 'clef': 'treble', 'voices': [('O', '1'), ('O', '2')]},
            {'id': 'man2', 'clef': 'bass', 'voices': [('O', '5')]}]},
        {'type': None, 'staves': [
            {'id': 'ped', 'clef': 'bass', 'name': 'Pedal', 'short': 'Ped.', 'voices': [('O', '9')]}]}]}
    return sc, lay, opts(hdr, 19, extra_paper=['indent = 18\\mm', 'short-indent = 10\\mm',
                                                'system-system-spacing.basic-distance = #20'])


ITEM = dict(
    id='organ-three-staves-chorale-prelude',
    title='Chorale Prelude - organ on three staves (manuals + pedal)',
    layout='organ', make=make, pages=1, must_not_split=True,
    expected_notes=('ONE part "Organ" with THREE staves: manual I (treble, two voices: soprano stems up, alto stems '
                    'down), manual II (bass clef) and pedal (bass clef). The brace joins only the two manual staves; '
                    'the pedal staff is outside the brace (labelled "Pedal") but belongs to the same Organ part - '
                    'must not be split into 2 or 3 parts, and the two manual-I voices are not choir parts. '
                    'Registration texts are words directions.'),
    truth_limitations=['Organ = one part with <staves>3</staves> and <part-symbol top-staff="1" bottom-staff="2">brace'
                       '</part-symbol>; voices 1+2 on staff 1, voice 5 on staff 2, voice 9 on staff 3.'],
    layout_desc='A4 portrait, staff size 19, 2 systems of 4 measures, braced manuals + separate pedal staff',
    scans=scans(11, 'T2', 'S4'),
    attribution='Chorale Prelude for organ - tune, harmonisation (corpus voice-leading solver) and layout composed '
                'for the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
