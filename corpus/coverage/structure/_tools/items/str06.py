"""str06: two-page song (voice + piano): explicit system breaks at irregular places, a page break, a 1st
ending that crosses the page break, a 2nd ending, two stanzas, ties across system and page breaks.

Page 1: systems mm.1-2 | 3-5 | 6-7 | 8-9      Page 2: mm.10-12 | 13-14 | 15-16
"""
from __future__ import annotations

from ssynth.model import set_verses

from .common import CC0_NOTE, add_mark, assemble, mk_part

VOICE = ("R1 | R1 | es'4\\mf g' bes' g' | as'4 c'' bes' as' | g'2 f'2~ | f'2 r4 bes'4 | c''4 bes' as' f' | "
         "g'4( as') bes'2 | c''4 bes' g' es' | f'1 | c''4 d'' es'' g' | bes'1~ | bes'4 r4 es''4 d'' | "
         "c''4 bes' as' g' | f'4 g' as' f' | es'1")
RH = ("<g' bes' es''>2\\p <g' bes' es''>2 | <f' as' d''>2 <f' as' bes'>2 | <es' g' bes'>2 <es' g' bes'>2 | "
      "<es' as' c''>2 <es' as' c''>2 | <es' g' bes'>2 <d' f' bes'>2~ | <d' f' bes'>2 <d' f' as'>2 | "
      "<es' as' c''>2 <d' f' as'>2 | <es' g' bes'>1 | <es' g' c''>2 <d' f' bes'>2~ | <d' f' bes'>2 <d' f' as'>2 | "
      "<es' as' c''>2 <es' g' bes'>2 | <d' f' bes'>1~ | <d' f' bes'>4 r4 <g' bes' es''>4 <f' bes' d''>4 | "
      "<es' as' c''>2 <es' g' bes'>2 | <d' f' as'>2 <d' f' as'>2 | <es' g' bes'>1")
LH = ("es,2 es2 | bes,2 bes,2 | es,2 g,2 | as,2 c2 | es,2 bes,2 | bes,1 | as,2 bes,2 | es,1 | c2 bes,2 | "
      "bes,1 | as,2 es2 | bes,1~ | bes,4 r4 es4 bes,4 | as,2 es2 | bes,1 | es,1")
VERSE1 = ("Morn -- ing light is break -- ing o -- ver hill and field, ev -- ery val -- ley wakes _ to "
          "hear the bird -- song ring. " + ' '.join(['_'] * 16))
VERSE2 = ("Eve -- ning shad -- ows gath -- er gen -- tly o -- ver all, lamps are lit in ev -- _ ery "
          + ' '.join(['_'] * 5) + " win -- dow, home -- ward bound we go, rest -- ing till the "
          "morn -- ing light re -- turns.")


def make():
    vo = mk_part('V', 'Voice', 'V.', 'voice', 1, ['treble'])
    pn = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('5', 2)])
    sc = assemble((4, 4), (-3, 'major'), [(vo, {'1': VOICE}), (pn, {'1': RH, '5': LH})])
    set_verses(sc, 'V', '1', [VERSE1, VERSE2], mode='attack')
    m = sc.measures
    add_mark(sc, 0, 'tempo', text='Andante', unit='quarter', bpm=76)
    m[1].right_bar = 'double'                              # end of the introduction
    m[2].left_bar = 'repeat-start'                         # m.3, start of system 2
    m[8].volta_start = '1'                                 # 1st ending mm.9-10 across the page break
    m[9].volta_end = 'stop'
    m[9].right_bar = 'repeat-end'
    m[10].volta_start = '2'                                # 2nd ending mm.11-12
    m[11].volta_end = 'discontinue'
    m[15].right_bar = 'final'
    for n in (3, 6, 8, 13, 15):
        m[n - 1].brk = 'system'
    m[9].brk = 'page'                                      # m.10 starts page 2
    sc.title = 'Morning and Evening'
    sc.composer = 'Coverage corpus (2026)'
    sc.lyricist = 'Coverage corpus (2026)'
    sc.rights = 'CC0 1.0'
    lay = {'groups': [
        {'type': None, 'staves': [{'id': 'voice', 'clef': 'treble', 'name': 'Voice', 'voices': [('V', '1')],
                                   'lyrics': [{'voice': ('V', '1'), 'verses': [1, 2]}]}]},
        {'type': 'PianoStaff', 'name': 'Piano', 'staves': [
            {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1')]},
            {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]}]}
    opts = {'header': {'title': 'Morning and Evening', 'subtitle': 'song in two stanzas',
                       'poet': 'Words: coverage corpus (2026)', 'composer': 'Music: coverage corpus (2026)',
                       'copyright': 'CC0 1.0'},
            'staff_size': 18, 'paper': 'a4', 'forced_breaks': True,
            'paper_extra': ['indent = 14\\mm', 'ragged-bottom = ##t', 'ragged-last-bottom = ##t',
                            'system-system-spacing.basic-distance = #13', 'print-page-number = ##t',
                            'top-margin = 12\\mm', 'bottom-margin = 12\\mm']}
    return sc, lay, opts


ITEM = dict(
    id='str06-breaks-two-pages-song',
    title='Morning and Evening - explicit system/page breaks, 1st ending across a page turn (voice and piano, 2 pages)',
    make=make, pages=2, layout='voice-piano', must_not_split=True,
    focus=['system-break', 'page-break', 'multi-page', 'tie-across-system', 'volta-1', 'volta-2', 'repeat-start',
           'repeat-end'],
    expect_counts={'system-break': 5, 'page-break': 1, 'multi-page': 2, 'volta-1': 1, 'volta-2': 1,
                   'repeat-start': 1, 'repeat-end': 1, 'barline-double': 1, 'barline-final': 1},
    structure=('Page 1: systems mm.1-2 | 3-5 | 6-7 | 8-9; page 2: mm.10-12 | 13-14 | 15-16 (all breaks explicit: '
               '<print new-system="yes"/> at mm.3, 6, 8, 13, 15 and <print new-page="yes"/> at m.10). Piano '
               'introduction mm.1-2 (voice tacet, whole-bar rests; double bar), start repeat at m.3 (system start), '
               '1st ending mm.9-10 crossing the page turn (end repeat after m.10, mid-system on page 2), 2nd ending '
               'mm.11-12, final bar after m.16. Ties cross the system breaks 5|6 (voice + piano) and 12|13 (voice, '
               'both piano hands) and the page break 9|10 (piano right hand). Stanza 1 is sung in mm.3-10, stanza '
               '2 in mm.3-8 and 11-16. Played form: 1-10, 3-8, 11-16.'),
    expected_notes=('Two parts: Voice (with 2 lyric lines) and Piano (grand staff, ONE part, must NOT be split). '
                    'E-flat major, 4/4. Lyrics: line 1 under mm.3-10, line 2 under mm.3-8 and 11-16. A score that '
                    'ignores page/system breaks is still musically correct; <print> elements measure layout '
                    'recognition.'),
    notes=('Truth limitations: (1) the printed stanza numbers "1." and "2." are not encoded as text (they are implied '
           'by <lyric number="1|2">); (2) the page number printed on page 2 is not encoded as a <credit>. System and '
           'page breaks are encoded in every part (<print> in each part).'),
    attribution='\n'.join(['"Morning and Evening", words and music written for this corpus (2026) - CC0 1.0.', '',
                           CC0_NOTE]),
    scans={
        'scan.pdf': {'seed': 46001, 'summary': 'two-page flatbed scan, 300 dpi grey, pages skewed 0.7 and -0.9 deg, '
                     'light texture, faint bleed-through of the other page, JPEG q75',
                     'params': dict(dpi=300, mode='gray', texture=2, rotate_pages={0: 0.7, 1: -0.9}, bleed=0.05,
                                    blur=0.3, noise=3, jpeg=75)},
        'scan-severe.pdf': {'seed': 46002, 'summary': 'book-style capture: both pages as ONE 2-up image (double-page '
                            'spread) with gutter shadow and page curl, yellowed paper, -2.5 deg rotation, vignette, '
                            'motion blur, 150 dpi RGB, JPEG q25',
                            'params': dict(dpi=150, mode='rgb', paper_rgb=(236, 226, 198), texture=6,
                                           spread=[[0, 1]], gutter={'side': 'inner', 'width': 0.08, 'dark': 0.7},
                                           curl={'side': 'inner', 'amp': 40, 'width': 0.3}, rotate=-2.5,
                                           vignette=0.3, motion_blur={'len': 5, 'angle': 10}, noise=7, jpeg=25)},
    },
)
