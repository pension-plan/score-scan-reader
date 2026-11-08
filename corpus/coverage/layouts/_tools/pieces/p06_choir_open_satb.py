"""choir-open-satb: four-part choir in open score (one staff per voice, lyrics under every staff),
imitative entries, tenor on a treble-8 clef."""
from csynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, breaks, header, mk_part, opts, scans

S = ("e''4\\mf cis''8 d'' e''4 a' | b'4( cis''8 d'' e''4) d'' | cis''4( b') a'2 | r4 e''\\f fis'' e''8 d'' | "
     "cis''4 b'8 a' gis'4 a' | fis'2(\\> gis'2) | a'1\\!\\fermata")
A = ("R1 | e'4\\mf e'8 fis' gis'4 a' | fis'4( gis'8 a' e'4) a' | gis'4( fis') e'2 | e'4\\f e'8 fis' e'4 e' | "
     "d'2(\\> e'2) | e'1\\!\\fermata")
T = ("R1 | R1 | a4\\mf a8 b cis'4 a | b4( cis'8 d' e'4) cis' | a4(\\f e') cis'2 | d'2(\\> b2) | cis'1\\!\\fermata")
B = ("R1 | R1 | R1 | e4\\mf e8 e a,4 cis | a4\\f gis8 fis( e4) a, | d2(\\> e2) | a,1\\!\\fermata")
TXT = {
    'S': "Glo -- ri -- a in ex -- cel -- _ _ _ sis De -- _ o, Glo -- ri -- a in ex -- cel -- sis De -- o. A -- _ men.",
    'A': "Glo -- ri -- a in ex -- cel -- _ _ _ sis De -- _ o, ex -- cel -- sis De -- o. A -- _ men.",
    'T': "Glo -- ri -- a in ex -- cel -- _ _ _ sis De -- _ o. A -- _ men.",
    'B': "Glo -- ri -- a in ex -- cel -- sis De -- _ o. A -- _ men.",
}


def make():
    parts = [mk_part('S', 'Soprano', 'S.', 'voice', 1, ['treble']), mk_part('A', 'Alto', 'A.', 'voice', 1, ['treble']),
             mk_part('T', 'Tenor', 'T.', 'voice', 1, ['treble_8']), mk_part('B', 'Bass', 'B.', 'voice', 1, ['bass'])]
    src = {'S': S, 'A': A, 'T': T, 'B': B}
    sc = assemble((4, 4), (3, 'major'), [(p, {'1': src[p.id]}) for p in parts])
    for pid, t in TXT.items():
        set_verses(sc, pid, '1', [t], mode='attack')
    add_mark(sc, 0, 'tempo', text='Allegro moderato', unit='half', bpm=60)
    sc.measures[0].time_symbol = None
    breaks(sc, systems=(4,))
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket'}]
    sc.marks_part = 'S'
    hdr = header(sc, 'Gloria', 'for mixed choir (SATB)', lyricist='Text: liturgical (public domain)')
    staves = []
    for pid, clef, nm in (('S', 'treble', 'Soprano'), ('A', 'treble', 'Alto'), ('T', 'treble_8', 'Tenor'),
                          ('B', 'bass', 'Bass')):
        staves.append({'id': pid.lower(), 'clef': clef, 'name': nm, 'short': nm[0] + '.', 'voices': [(pid, '1')],
                       'lyrics': [{'voice': (pid, '1'), 'verses': [1], 'place': 'below', 'stanza': False}]})
    lay = {'groups': [{'type': 'ChoirStaff', 'staves': staves}]}
    return sc, lay, opts(hdr, 19, extra_paper=['indent = 16\\mm', 'short-indent = 7\\mm',
                                                'system-system-spacing.basic-distance = #20'])


ITEM = dict(
    id='choir-open-satb-gloria',
    title='Gloria - SATB choir in open score with imitative entries',
    layout='choir-open-satb', make=make, pages=1, must_not_split=False,
    expected_notes=('FOUR parts, one staff each: Soprano, Alto, Tenor (treble clef with a small 8 below: sounds an '
                    'octave lower; truth pitches are sounding pitches), Bass. Voices enter one after another '
                    '(whole-bar rests before each entry). Every staff has its own lyric line (Latin) that belongs '
                    'to that part.'),
    truth_limitations=['The tenor clef is <clef><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change>; '
                       'its pitches are written at sounding pitch as usual for vocal tenor parts.'],
    layout_desc='A4 portrait, staff size 19, 2 systems (4 + 3 measures) on 4 bracketed staves, full then short names',
    scans=scans(6, 'T2', 'S1'),
    attribution='Gloria for SATB choir composed for the OMR coverage suite (2026) - CC0 1.0. Text: "Gloria in '
                'excelsis Deo" (Latin liturgy, public domain).\n\n' + CC0_NOTE,
)
