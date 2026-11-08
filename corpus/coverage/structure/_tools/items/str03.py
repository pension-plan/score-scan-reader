"""str03: 1st / 2nd (/ 3rd) endings in a string quartet (16 bars, 4/4, D major, 4 systems).

Section A: mm.1-3, 1st ending m.4 (:|), 2nd ending m.5 (||).
Section B: |: mm.6-8, 1st ending mm.9-10 crossing the system break 9|10 (:|), 2nd ending mm.11-12 (||).
Section C: |: m.13, 1st ending m.14 (:|), 2nd ending m.15 (:|), 3rd ending m.16 (final bar).
Violin I melody; the other three parts are a 4-part chorale setting (ssynth/harmonize.py)."""
from __future__ import annotations

from ssynth.dsl import parse_voice
from ssynth.harmonize import harmonize
from ssynth.model import Part, Score, VoiceDef, MeasureInfo, renumber
from fractions import Fraction as F

from .common import CC0_NOTE

SOP = ("a'4 d'' fis'' e'' | d''4 b' cis'' d'' | e''4 fis'' g'' e'' | fis''2 e''2 | d''1 | "
       "fis''4 g'' a'' fis'' | g''4 fis'' e'' d'' | cis''4 d'' e'' a' | b'4 cis'' d'' b' | e''2 cis''2 | "
       "b'4 cis'' d'' g'' | fis''2 d''2 | "
       "a''4 g'' fis'' e'' | d''2 e''2 | fis''2 e''2 | d''1")
CHORDS = ('D D D A  G G A D  A D G A  D A  D  '
          'D Em D Bm  G D A Bm  A D A D  G A D G  A A  '
          'G A D Em  D D  '
          'D Em D A  D A  Bm A  D').split()


def make():
    sop = parse_voice(SOP)
    alto, ten, bass = harmonize(sop, CHORDS, 2)
    nm = len(sop)
    sc = Score()
    for i in range(nm):
        mi = MeasureInfo(number=i + 1, dur=F(4), nominal=F(4))
        if i == 0:
            mi.time, mi.key = (4, 4), (2, 'major')
        sc.measures.append(mi)
    specs = [('V1', 'Violin I', 'Vl. I', 'treble', sop), ('V2', 'Violin II', 'Vl. II', 'treble', alto),
             ('VA', 'Viola', 'Va.', 'alto', ten), ('VC', 'Violoncello', 'Vc.', 'bass', bass)]
    for pid, name, abbr, clef, ms in specs:
        p = Part(id=pid, name=name, abbr=abbr, instrument='other', clefs=[clef])
        p.voices = [VoiceDef('1', 1)]
        p.measures = [{'1': m} for m in ms]
        sc.parts.append(p)
    renumber(sc)
    m = sc.measures

    def volta(first, last, num, end):
        m[first - 1].volta_start = num
        m[last - 1].volta_end = end

    volta(4, 4, '1', 'stop')
    m[3].right_bar = 'repeat-end'
    volta(5, 5, '2', 'discontinue')
    m[4].right_bar = 'double'
    m[5].left_bar = 'repeat-start'
    volta(9, 10, '1', 'stop')
    m[9].right_bar = 'repeat-end'
    volta(11, 12, '2', 'discontinue')
    m[11].right_bar = 'double'
    m[12].left_bar = 'repeat-start'
    volta(14, 14, '1', 'stop')
    m[13].right_bar = 'repeat-end'
    volta(15, 15, '2', 'stop')
    m[14].right_bar = 'repeat-end'
    volta(16, 16, '3', 'stop')                     # LilyPond hooks a bracket that ends at a final bar
    m[15].right_bar = 'final'
    for n in (6, 10, 13):
        m[n - 1].brk = 'system'
    sc.groups = [{'first': 'V1', 'last': 'VC', 'symbol': 'bracket'}]
    sc.title = 'Three Endings'
    sc.composer = 'Coverage corpus (2026)'
    sc.rights = 'CC0 1.0'
    staves = []
    for pid, name, abbr, clef, _ in specs:
        staves.append({'id': pid.lower(), 'clef': clef, 'name': name, 'short': abbr, 'voices': [(pid, '1')]})
    lay = {'groups': [{'type': 'StaffGroup', 'staves': staves}]}
    opts = {'header': {'title': 'Three Endings', 'subtitle': 'for string quartet',
                       'composer': 'Coverage corpus (2026)', 'copyright': 'CC0 1.0'},
            'staff_size': 18, 'paper': 'a4', 'forced_breaks': True,
            'paper_extra': ['indent = 22\\mm', 'short-indent = 10\\mm', 'ragged-bottom = ##t',
                            'system-system-spacing.basic-distance = #16']}
    return sc, lay, opts


ITEM = dict(
    id='str03-voltas-string-quartet',
    title='Three Endings - 1st, 2nd and 3rd endings incl. a 2-bar ending across a system break (string quartet)',
    make=make, pages=1, layout='string-quartet', must_not_split=False,
    focus=['volta-1', 'volta-2', 'x-volta-3', 'repeat-start', 'repeat-end', 'barline-double', 'barline-final'],
    expect_counts={'volta-1': 3, 'volta-2': 3, 'x-volta-3': 1, 'repeat-start': 2, 'repeat-end': 4,
                   'barline-double': 2, 'barline-final': 1, 'system-break': 3},
    structure=('A: mm.1-3, 1st ending m.4 (closed bracket, end repeat), 2nd ending m.5 (open bracket, double bar). '
               'B: start repeat m.6 (system start), mm.6-8, 1st ending mm.9-10 (two bars, bracket broken across the '
               'system break after m.9, end repeat after m.10), 2nd ending mm.11-12 (open, double bar). C: start '
               'repeat m.13 (system start, after the double bar that ends system 3), 1st ending m.14 (end repeat), 2nd ending m.15 (end repeat), 3rd ending m.16 (closed bracket, final '
               'bar). Played form: 1-4,1-3,5, 6-10,6-8,11-12, 13-14,13,15,13,16.'),
    expected_notes=('Four parts: Violin I, Violin II (treble), Viola (alto clef), Violoncello (bass clef), joined by a '
                    'bracket - four separate parts. D major, 4/4. Endings: <ending number="1|2|3" type="start"> on the '
                    'left barline of the first ending bar and type="stop" (bracket with end hook, before an end '
                    'repeat) or type="discontinue" (open end) on the right barline of the last ending bar, in every '
                    'part. Volta brackets are printed once, above the top staff.'),
    notes=('No truth limitations. Endings and repeats are repeated in all four parts of the truth (MusicXML requires '
           'it); counts give each ending / repeat once. "x-volta-3" is a third ending ("3.").'),
    attribution='\n'.join(['"Three Endings" for string quartet, composed for this corpus (2026) - CC0 1.0.', '',
                           CC0_NOTE]),
    scans={
        'scan.pdf': {'seed': 43001, 'summary': 'flatbed scan, 300 dpi, cream paper (RGB), 1.0 deg skew, '
                     'slight blur and noise, JPEG q70',
                     'params': dict(dpi=300, mode='rgb', paper_rgb=(243, 236, 214), texture=3, rotate=1.0,
                                    blur=0.4, noise=3, jpeg=70)},
        'scan-severe.pdf': {'seed': 43002, 'summary': 'dark, thickened binarised photocopy at 200 dpi, -5 deg skew, '
                            'heavy blur and noise, salt & pepper, staple, two punch holes in the left margin',
                            'params': dict(dpi=200, ink_weight=1, rotate=-5.0,
                                           punch_holes={'n': 2, 'side': 'left', 'level': 10}, staple={'corner': 'tl'},
                                           blur=1.0, noise=12, binarize=190, binarize_noise=20, saltpepper=0.002,
                                           format='png1')},
    },
)
