"""L2: 'All Things Bright and Beautiful' - anthem for SATB choir in CLOSED score (S+A on one staff,
T+B on one staff, bracket) with piano accompaniment (brace, right hand partly in two voices), 4 pages.
Piano-only systems (introduction, interlude) hide the choir staves; the verse is repeated with 1st/2nd
endings and two stacked verses; Segno / To Coda / D.S. al Coda / Coda; page numbers.
Melody, harmonisation (voice-leading solver) and accompaniment: CC0.  Text: C. F. Alexander, 1848 (PD)."""
from __future__ import annotations

import copy
from fractions import Fraction as F

from .common import CC0_NOTE, REMOVE_EMPTY, add_end_mark, add_mark, assemble, from_midi_spelled, lyp, mk_part
from lsynth.dsl import parse_voice
from lsynth.harmonize import chord_tones, harmonize
from lsynth.model import Event, STEP_PC, VoiceDef, derive_lyrics, midi, set_verses

SOP = ("R1 | R1 | R1 | R1 | "
       "g'4 b' d'' d'' | e'' d'' b'2 | c''4 b' a' g' | a' d'2. | "
       "g'4 b' d'' g'' | e''4 c'' a'2 | d''4 c'' b' a' | g'4 g'2. | "
       "R1 | R1 | "
       "b'4 b' a' g' | fis' g' a'2 | g'4 a' b' c'' | d''4 d''2. | b'4 b' c'' d'' | e''4 d'' b'2 | "
       "c''4 a' fis' g' | a'4 g'2. | a'4 d''2. | "
       "d''4 c'' b' a' | g'2 g'2~ | g'1\\fermata | R1")
CHORDS = (['G', 'Em', 'G', 'Bm'] + ['C', 'G', 'Em'] + ['Am', 'G', 'D', 'Em'] + ['A7', 'D'] +
          ['G', 'G', 'Bm', 'Em'] + ['C', 'Am', 'D'] + ['G', 'D7', 'Em', 'D'] + ['C', 'G'] +
          ['Em', '-', 'D', 'Em'] + ['B7', 'Em', 'D'] + ['G', 'D', 'Em', 'C'] + ['G', 'D'] +
          ['Em', 'G', 'Am', 'G'] + ['C', 'G', 'Em'] + ['Am', 'D', 'D7', 'G'] + ['D', 'G'] + ['A7', 'D'] +
          ['G', 'Am', 'G', 'D'] + ['C', 'G', '~'])
REFRAIN = ("All things bright and beau -- ti -- ful, All crea -- tures great and small, "
           "All things wise and won -- der -- ful, The Lord God made them all.")
V1 = "Each lit -- tle flower that o -- pens, Each lit -- tle bird that sings, He made their glow -- ing col -- ours, He made their ti --"
V2 = "The pur -- ple -- head -- ed moun -- tain, The ri -- ver run -- ning by, The sun -- set and the mor -- ning, That bright -- ens up"
CODA = "The Lord God made them all."
INTRO, REF, INTER, VERSE, E1, E2, CODA_I = 0, 4, 12, 14, 21, 22, 23


def skips(n):
    return ' '.join(['_'] * n)


def make():
    sop_ms = parse_voice(SOP)
    a_ms, t_ms, b_ms = harmonize(sop_ms, CHORDS, 7)
    # chord symbol per soprano note event (for the piano figuration)
    sym_iter = iter(CHORDS)
    prev = None
    note_syms = []
    for mm in sop_ms:
        row = []
        for ev in mm:
            if ev.kind == 'note':
                s_ = next(sym_iter)
                if s_ in ('-', '~'):
                    s_ = prev
                prev = s_
                row.append(s_)
            else:
                row.append(None)
        note_syms.append(row)
    nm = len(sop_ms)
    # ---------------- piano from the SATB
    rh1, rh2, lh = [], [], []

    def dyad(a, s, d):
        ps = [s] if midi(a) == midi(s) else [a, s]
        return Event('note', d.dur, pitches=ps, dtype=d.dtype, dots=d.dots)

    def octave(b, d):
        lo = (b[0], b[1], b[2] - 1)
        ps = [lo, b] if midi(lo) >= 31 else [b]
        return Event('note', d.dur, pitches=ps, dtype=d.dtype, dots=d.dots)

    def fill(mm_idx_src):
        """refrain-style accompaniment for source measure index: RH [A,S] chords, LH bass octaves"""
        r, l = [], []
        for es, ea, eb in zip(sop_ms[mm_idx_src], a_ms[mm_idx_src], b_ms[mm_idx_src]):
            if es.kind != 'note':
                r.append(copy.deepcopy(es))
                l.append(copy.deepcopy(es))
                continue
            r.append(dyad(ea.pitches[0], es.pitches[0], es))
            l.append(octave(eb.pitches[0], es))
            r[-1].tie_start = {p for p in r[-1].pitches} if es.tie_start else set()
            l[-1].tie_start = {p for p in l[-1].pitches} if eb.tie_start else set()
        return r, l

    def lower_ct(sym, p):
        tones, _, _ = chord_tones(sym)
        pcs = [(STEP_PC[s] + a) % 12 for s, a in tones]
        m = midi(p) - 1
        while m % 12 not in pcs:
            m -= 1
        return from_midi_spelled(m, tones)

    for i in range(nm):
        if INTRO <= i < REF:                 # introduction = refrain bars 5-8 on the piano
            r, l = fill(REF + 4 + (i - INTRO))
            rh1.append(r), rh2.append([]), lh.append(l)
        elif INTER <= i < VERSE:             # interlude = refrain bars 7-8
            r, l = fill(REF + 6 + (i - INTER))
            rh1.append(r), rh2.append([]), lh.append(l)
        elif VERSE <= i <= E2:               # verse: melody + 8th figuration (2 voices) + bass
            v1, v2, l = [], [], []
            for k, (es, ea, eb) in enumerate(zip(sop_ms[i], a_ms[i], b_ms[i])):
                v1.append(copy.deepcopy(es))
                v1[-1].lyrics = {}
                n8 = int(es.dur / F(1, 2))
                lo = lower_ct(note_syms[i][k], ea.pitches[0])
                for j in range(n8):
                    p = ea.pitches[0] if j % 2 == 0 else lo
                    v2.append(Event('note', F(1, 2), pitches=[p], dtype='eighth'))
                l.append(Event('note', es.dur, pitches=[eb.pitches[0]], dtype=es.dtype, dots=es.dots))
            rh1.append(v1), rh2.append(v2), lh.append(l)
        elif i == nm - 1:                    # postlude bar
            rh1.append(parse_voice("<b' d'' g''>1\\fermata")[0]), rh2.append([])
            lh.append(parse_voice("<g,, g,>1\\fermata")[0])
        else:                                # refrain and coda: doubling chords
            r, l = fill(i)
            rh1.append(r), rh2.append([]), lh.append(l)
    # ---------------- assemble score
    from lsynth.model import MeasureInfo, Part, Score, renumber
    sc = Score()
    for i in range(nm):
        d = sum((e.dur for e in sop_ms[i]), F(0))
        sc.measures.append(MeasureInfo(number=i + 1, dur=d, nominal=F(4)))
    sc.measures[0].time, sc.measures[0].key = (4, 4), (1, 'major')
    parts = []
    for pid, name, abbr, clef, ms in (('S', 'Soprano', 'S.', 'treble', sop_ms), ('A', 'Alto', 'A.', 'treble', a_ms),
                                      ('T', 'Tenor', 'T.', 'bass', t_ms), ('B', 'Bass', 'B.', 'bass', b_ms)):
        p = mk_part(pid, name, abbr, 'voice', 1, [clef])
        p.measures = [{'1': m} for m in ms]
        parts.append(p)
    pno = mk_part('P', 'Piano', 'Pno.', 'piano', 2, ['treble', 'bass'], [('1', 1), ('2', 1), ('5', 2)])
    pno.measures = [{'1': rh1[i], '2': rh2[i], '5': lh[i]} for i in range(nm)]
    parts.append(pno)
    sc.parts = parts
    renumber(sc)
    # lyrics (verse 1: refrain, verse 1, coda; verse 2: verse 2 only)
    n_ref, n_v, n_e = 26, 24, 2
    v1_text = ' '.join([REFRAIN, V1, 'ny wings.', skips(2), CODA])
    v2_text = ' '.join([skips(n_ref), V2, skips(2), 'the sky.', skips(6)])
    set_verses(sc, 'S', '1', [v1_text, v2_text], mode='attack')
    derive_lyrics(sc, ('S', '1'), ('T', '1'))
    # dynamics / words
    def first_note(pid, vk, i):
        return [e for e in sc.part(pid).measures[i][vk] if e.kind == 'note'][0]
    first_note('P', '1', 0).dynamics.append('p')
    for pid in ('S', 'T'):
        first_note(pid, '1', REF).dynamics.append('mf')
        first_note(pid, '1', VERSE).dynamics.append('p')
        first_note(pid, '1', CODA_I).dynamics.append('f')
    first_note('P', '1', REF).dynamics.append('mf')
    first_note('P', '1', VERSE).dynamics.append('p')
    first_note('P', '1', VERSE).words.append(('legato', 'above', 'italic'))
    first_note('P', '1', INTER).words.append(('cresc.', 'below', 'italic'))
    first_note('S', '1', CODA_I + 1).words.append(('rit.', 'above', 'italic'))
    first_note('P', '1', CODA_I).dynamics.append('f')
    first_note('P', '1', nm - 1).dynamics.append('ff')
    # structure
    add_mark(sc, 0, 'tempo', text='Allegretto', unit='quarter', bpm=104)
    add_mark(sc, REF, 'segno')
    add_mark(sc, REF, 'rehearsal', text='A')
    add_end_mark(sc, REF + 5, 'To Coda', coda_sign=True, sound={'tocoda': 'coda'})
    add_mark(sc, VERSE, 'rehearsal', text='B')
    sc.measures[INTER - 1].right_bar = 'double'
    sc.measures[VERSE].left_bar = 'repeat-start'
    sc.measures[E1].volta_start, sc.measures[E1].volta_end, sc.measures[E1].right_bar = '1', 'stop', 'repeat-end'
    sc.measures[E2].volta_start, sc.measures[E2].volta_end, sc.measures[E2].right_bar = '2', 'discontinue', 'double'
    add_end_mark(sc, E2, 'D.S. al Coda', style='bold-italic', sound={'dalsegno': 'segno'})
    add_mark(sc, CODA_I, 'coda')
    sc.measures[-1].right_bar = 'final'
    for i, kind in ((4, 'system'), (8, 'page'), (12, 'system'), (14, 'page'), (17, 'system'), (20, 'page'),
                    (23, 'system')):
        sc.measures[i].brk = kind
    sc.groups = [{'first': 'S', 'last': 'B', 'symbol': 'bracket', 'name': 'Choir'}]
    sc.title = 'All Things Bright and Beautiful'
    sc.composer = 'Layout-challenge corpus (2026), CC0'
    sc.lyricist = 'Cecil Frances Alexander (1848)'
    sc.rights = 'Text public domain; music and engraving CC0 1.0'
    sc.credits = [{'page': 1, 'type': 'title', 'text': 'All Things Bright and Beautiful'},
                  {'page': 1, 'type': 'subtitle', 'text': 'Anthem for SATB choir and piano'},
                  {'page': 1, 'type': 'lyricist', 'text': 'Words: Cecil Frances Alexander (1848)'},
                  {'page': 1, 'type': 'composer', 'text': 'Music: layout-challenge corpus (2026)'},
                  {'page': 1, 'type': 'rights', 'text': 'Dedicated to the public domain (CC0 1.0)'}]
    for pg in (2, 3, 4):
        sc.credits.append({'page': pg, 'type': 'header', 'text': 'All Things Bright and Beautiful'})
        sc.credits.append({'page': pg, 'type': 'page number', 'text': str(pg)})
    choir_with = list(REMOVE_EMPTY)
    lay = {'groups': [
        {'type': 'ChoirStaff', 'staves': [
            {'id': 'sa', 'clef': 'treble', 'name': ['Soprano', 'Alto'], 'short': ['S.', 'A.'],
             'voices': [('S', '1'), ('A', '1')], 'with': choir_with,
             'lyrics': [{'voice': ('S', '1'), 'verses': [1, 2], 'place': 'below', 'stanza': False}]},
            {'id': 'tb', 'clef': 'bass', 'name': ['Tenor', 'Bass'], 'short': ['T.', 'B.'],
             'voices': [('T', '1'), ('B', '1')], 'with': choir_with,
             'lyrics': [{'voice': ('T', '1'), 'verses': [1, 2], 'place': 'below', 'stanza': False}]}]},
        {'type': 'PianoStaff', 'name': 'Piano', 'short': 'Pno.', 'staves': [
            {'id': 'rh', 'clef': 'treble', 'voices': [('P', '1'), ('P', '2')]},
            {'id': 'lh', 'clef': 'bass', 'voices': [('P', '5')]}]},
    ]}
    opts = {'header': {'title': 'All Things Bright and Beautiful', 'subtitle': 'Anthem for SATB choir and piano',
                       'poet': 'Words: Cecil Frances Alexander (1848)',
                       'composer': 'Music: layout-challenge corpus (2026)',
                       'copyright': 'Dedicated to the public domain (CC0 1.0)'},
            'staff_size': 20, 'paper': 'letter', 'font': 'TeX Gyre Schola', 'forced_breaks': True,
            'auto_beam_off_vocal': True,
            'paper_extra': [
                'indent = 20\\mm', 'short-indent = 9\\mm', 'ragged-bottom = ##t',
                'system-system-spacing.basic-distance = #20',
                'oddHeaderMarkup = \\markup \\fill-line { \\null \\unless \\on-first-page \\italic '
                '"All Things Bright and Beautiful" \\unless \\on-first-page \\fromproperty #\'page:page-number-string }',
                'evenHeaderMarkup = \\markup \\fill-line { \\unless \\on-first-page '
                '\\fromproperty #\'page:page-number-string \\unless \\on-first-page \\italic '
                '"All Things Bright and Beautiful" \\null }'],
            'layout_extra': []}
    return sc, lay, opts


ITEM = dict(
    id='anthem-satb-closed-piano-4-pages',
    title='All Things Bright and Beautiful - SATB closed score + piano, 4 pages, hidden choir staves, endings, D.S.',
    make=make, pages=4,
    edge_cases=['satb_closed_score', 'choir_plus_piano', 'bracket_vs_brace', 'piano_two_voices_on_rh_staff',
                'hidden_empty_staves', 'systems_with_different_staff_counts', 'multi_page_3_4', 'page_numbers',
                'running_headers', 'volta_1st_2nd_endings', 'stacked_verses_in_repeat', 'segno', 'to_coda',
                'ds_al_coda', 'coda', 'rehearsal_marks', 'tempo_text', 'dynamics_text', 'lyrics',
                'lyrics_on_both_choir_staves', 'must_not_split', 'ties', 'fermata'],
    must_not_split=True,
    shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
    expected_notes=('Five parts: Soprano, Alto, Tenor, Bass (closed score: S+A share the treble staff, T+B the bass '
                    'staff, bracketed; each shared staff MUST be split into two parts by stem direction) and Piano '
                    '(braced grand staff, ONE part, never split - its right hand has two voices in the verse, which '
                    'must stay inside the piano part). Systems 1 (introduction) and 4 (interlude) show only the piano: '
                    'the choir parts have invisible whole-measure rests there. The verse (mm. 15-23) is repeated: '
                    'verse 1 and verse 2 are stacked; m.22 = 1st ending (verse 1 "ny wings"), m.23 = 2nd ending '
                    '(verse 2 "the sky"). Segno m.5, To Coda after m.10, D.S. al Coda after m.23, Coda m.24 - notated '
                    'order, not unrolled. Lyrics are under both choir staves; truth attaches them to Soprano and '
                    'Tenor (Alto/Bass sing the same syllables on the same rhythm).'),
    truth_limitations=('Lyrics are encoded on Soprano (verses 1-2) and Tenor (copied by onset), not on Alto/Bass. '
                       'Choir rests in piano-only systems are print-object="no". Beaming not encoded.'),
    layout_desc='US letter, staff size 20, 8 systems on 4 pages (2 per page); piano-only systems at the start of '
                'page 1 and the end of page 2',
    license='Text public domain (C. F. Alexander 1848); music, arrangement and engraving CC0-1.0',
    source='self-authored (layout-challenge corpus); text "All Things Bright and Beautiful", Hymns for Little '
           'Children (1848)',
    attribution='\n'.join(['Text: Cecil Frances Alexander, "All Things Bright and Beautiful" (1848) - public domain.',
                           'Melody, SATB harmonisation (corpus voice-leading solver) and piano accompaniment composed '
                           'for this corpus - CC0 1.0.', '', CC0_NOTE]),
)
