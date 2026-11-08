"""divisi (choir variant): open-score SATB where the Soprano divides into two voices on its staff and the
Bass sings octave chords; every staff keeps one part."""
import copy

from csynth.model import Event, set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, first_note, header, mk_part, opts, satb, scans
from csynth.dsl import parse_voice

SOP = ("c''4 c'' d'' e'' | d''4 c'' b'2 | a'4 b' c'' d'' | e''4 d'' c''2 | "
       "e''4 e'' f'' g'' | e''4 d'' c''2 | a'4 c'' b' a' | g'4 b' c''2\\fermata")
CHORDS = ['C', 'Am', 'G', 'C', 'G', 'C', 'G', 'F', 'G', 'Am', 'G', 'C', 'G', 'C',
          'C', 'Am', 'F', 'C', 'Am', 'G', 'C', 'F', 'Am', 'G', 'Dm', 'C/G', 'G7', 'C']
S2 = "s1 | s1 | s1 | s1 | c''4 c'' c'' c'' | c''4 b' g'2 | s1 | s1"
TEXT = ("Lift your voi -- ces, sing and play, wel -- come in the bright new day; "
        "let the hills and val -- leys ring, all the world be -- gin to sing.")


def make():
    v = satb(SOP, CHORDS, 0)
    s2 = parse_voice(S2)
    # bass divisi: octave chords in mm.7-8
    for mi in (6, 7):
        for ev in v['B'][mi]:
            if ev.kind == 'note':
                st, al, o = ev.pitches[0]
                ev.pitches = [(st, al, o - 1), (st, al, o)] if o >= 3 else [(st, al, o), (st, al, o + 1)]
                ev.tie_start = set()
                ev.tie_stop = set()
    parts = [mk_part('S', 'Soprano', 'S.', 'voice', 1, ['treble'], [('1', 1), ('2', 1)]),
             mk_part('A', 'Alto', 'A.', 'voice', 1, ['treble']),
             mk_part('T', 'Tenor', 'T.', 'voice', 1, ['treble_8']),
             mk_part('B', 'Bass', 'B.', 'voice', 1, ['bass'])]
    sc = assemble((4, 4), (0, 'major'), [(parts[0], {'1': v['S'], '2': s2}), (parts[1], {'1': v['A']}),
                                         (parts[2], {'1': v['T']}), (parts[3], {'1': v['B']})])
    for pid in ('S', 'A', 'T', 'B'):
        set_verses(sc, pid, '1', [TEXT], mode='attack')
        first_note(sc, pid, '1', 0).dynamics.append('mf')
    first_note(sc, 'S', '1', 4).words.append(('div.', 'above', 'italic'))
    first_note(sc, 'S', '1', 6).words.append(('unis.', 'above', 'italic'))
    first_note(sc, 'B', '1', 6).words.append(('div.', 'above', 'italic'))
    first_note(sc, 'S', '1', 4).dynamics.append('f')
    add_mark(sc, 0, 'tempo', text='Brightly', unit='quarter', bpm=108)
    breaks(sc, systems=(4,))
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.marks_part = 'S'
    hdr = header(sc, 'Bright New Day', 'for mixed choir with divisi', lyricist='Words: coverage suite (2026)')
    staves = []
    for pid, clef, nm, sh, vs in (('S', 'treble', 'Soprano', 'S.', [('S', '1'), ('S', '2')]),
                                  ('A', 'treble', 'Alto', 'A.', [('A', '1')]),
                                  ('T', 'treble_8', 'Tenor', 'T.', [('T', '1')]),
                                  ('B', 'bass', 'Bass', 'B.', [('B', '1')])):
        staves.append({'id': pid.lower(), 'clef': clef, 'name': nm, 'short': sh, 'voices': vs,
                       'lyrics': [{'voice': (pid, '1'), 'verses': [1], 'place': 'below', 'stanza': False}]})
    lay = {'groups': [{'type': 'ChoirStaff', 'staves': staves}]}
    return sc, lay, opts(hdr, 18, extra_paper=['indent = 16\\mm', 'short-indent = 8\\mm',
                                                'system-system-spacing.basic-distance = #20'])


ITEM = dict(
    id='divisi-choir-bright-new-day',
    title='Bright New Day - open SATB with soprano divisi (two voices) and bass octave divisi (chords)',
    layout='divisi', make=make, pages=1, must_not_split=True,
    expected_notes=('FOUR parts, one per staff: Soprano, Alto, Tenor (treble-8 clef, sounding pitches), Bass. In '
                    'mm.5-6 the Soprano staff is "div.": two voices (stems up/down) that both belong to the Soprano '
                    'part (truth: voice 1 and 2; only voice 1 carries the lyrics) - back to "unis." in m.7. In mm.7-8 '
                    'the Bass sings octave chords ("div."), which stay chords in the Bass part. Every staff has its '
                    'own lyric line.'),
    truth_limitations=['Soprano voice 2 exists only in mm.5-6 (elsewhere <forward>); it carries no lyrics.'],
    layout_desc='A4 portrait, staff size 18, 2 systems of 4 measures on 4 bracketed staves',
    scans=scans(17, 'T4', 'S1'),
    attribution='Bright New Day - tune, harmonisation (corpus voice-leading solver), divisi and words composed for '
                'the OMR coverage suite (2026) - CC0 1.0.\n\n' + CC0_NOTE,
)
