"""Coverage suite, pitch family: items, focus tags, layout tags, expectations, truth notes, damage recipes."""
from .items import (mk_acc_chords, mk_acc_melody, mk_clef_piano, mk_clefs_all, mk_keys_major_flats,
                    mk_keys_major_sharps, mk_keys_minor_flats, mk_keys_minor_sharps, mk_organ_keys,
                    mk_ottava_melody, mk_ottava_piano, mk_quartet)

ATT = ('"{title}" - composed for the OMR coverage suite, pitch family (2026), engraved with GNU LilyPond 2.24.\n'
       'No third-party material.')

COMMON_NOTES = [
    'Courtesy clefs / key signatures / time signatures printed at the end of a system before a change are not '
    'separate MusicXML elements (they are implied by the change in the next measure) and are not counted.',
    'Clefs and key signatures reprinted at every system start are implied in MusicXML and not counted; counts '
    'cover the initial statement of every staff and every change.',
    'Stem directions and beams in the truth are copied from the instrumented LilyPond render and cross-checked '
    '(stems, flags, beam groups); they describe this engraving.',
    'System breaks are explicit in the engraving and encoded as <print new-system="yes"/>.',
]
NOTE_MODE = ('<mode> (major/minor) is encoded but is not printed: a key signature looks the same for the major key '
             'and its relative minor, so evaluators should compare <fifths> and treat mode as unobservable.')
NOTE_OCTCLEF = ('Octave clefs are encoded with <clef-octave-change> (treble-8vb: G2 -1, treble-8va: G2 +1, '
                'bass-8vb: F4 -1); <pitch> is always the sounding pitch, so a note on the same staff position '
                'differs by one octave from the plain clef.')
NOTE_OTTAVA = ('Pitches under an octave bracket are sounding pitches (MusicXML convention): <octave-shift '
               'type="down" size="8"> = 8va, type="up" size="8" = 8vb, type="down" size="15" = 15ma; the stop is '
               'placed directly after the last note under the bracket.  The bracket text style ({style}) cannot be '
               'encoded in MusicXML; it is recorded in meta.engraving.ottava_style.')
NOTE_CANCEL = ('Cancellation naturals printed before a new key signature are encoded only as <cancel>old '
               'fifths</cancel> inside the new <key> (MusicXML has no per-glyph encoding); LilyPond prints one '
               'natural for every alteration of the old key that the new key changes.')
NOTE_EXTRANAT = ('A single sharp/flat after a double sharp/flat on the same line in the same bar is printed by '
                 'LilyPond 2.24 with an extra natural; encoded as <accidental>natural-sharp</accidental> / '
                 '<accidental>natural-flat</accidental> (tags x-acc-natural-sharp / x-acc-natural-flat).')
NOTE_COURTESY = ('Courtesy accidentals: parenthesised ones are <accidental cautionary="yes" parentheses="yes">, '
                 'unparenthesised reminders are <accidental cautionary="yes">; both count as acc-courtesy and '
                 'under their glyph tag.')


def typical(seed, dpi, deg, sigma=3, jpeg=65, blur=0.4, paper=(245, 244, 240), gray=True, summary=''):
    ops = [{'op': 'paper', 'rgb': list(paper), 'texture': 2},
           {'op': 'rotate', 'deg': deg},
           {'op': 'blur', 'radius_px300': blur},
           {'op': 'noise', 'sigma': sigma}]
    if gray:
        ops.append({'op': 'gray'})
    return dict(dpi=dpi, seed=seed, jpeg=jpeg, level='typical',
                summary=summary or (f'typical office scan: {dpi} dpi {"grey" if gray else "RGB"}, {deg:+.1f} deg '
                                    f'skew, light paper texture, slight blur, noise sigma {sigma}, JPEG q{jpeg}'),
                ops=ops)


ITEMS = [
    # ------------------------------------------------------------------ 1
    dict(
        id='pitch-cov-clefs-all', title='Eight Clefs', make=mk_clefs_all(), layout='melody',
        focus=['clef-treble', 'clef-bass', 'clef-alto', 'clef-tenor', 'clef-soprano', 'clef-treble-8vb',
               'clef-treble-8va', 'clef-bass-8vb', 'clef-change', 'ledger-above', 'ledger-below'],
        expected_notes=(
            'One part (Melody), one staff, 16 bars of 4/4 in C major, 4 systems.  Each 2-bar segment uses one '
            'clef: treble (bars 1-2), bass (3-4), alto (5-6), tenor (7-8), soprano (9-10), treble-8vb (11-12), '
            'treble-8va (13-14), bass-8vb (15-16).  Two staff-position patterns alternate, so the same note-head '
            'positions recur under different clefs: every pitch is wrong if a clef is misread.  Clef changes at '
            'bars 3, 7, 11, 15 are mid-system (small clefs before the barline); those at bars 5, 9, 13 fall on a '
            'system start and are preceded by a courtesy clef at the end of the previous system.  The small "8" '
            'above/below the G and F clefs changes the octave of every following pitch.'),
        truth_notes=COMMON_NOTES + [NOTE_OCTCLEF],
        layout_desc='single staff, 4 systems x 4 bars, explicit system breaks',
        damage={
            'scan.pdf': typical(31001, 300, 0.7, sigma=3, jpeg=70),
            'scan-severe.pdf': dict(
                dpi=150, seed=31002, jpeg=20, level='severe',
                summary='old yellowed copy at 150 dpi: strong bleed-through, foxing, 6.5 deg skew, gradient + '
                        'vignette, focus blur 1.4 px@300dpi, noise, JPEG q20 (RGB) - the small octave 8 of the '
                        'clefs is barely legible',
                ops=[{'op': 'paper', 'rgb': [226, 210, 176], 'ink_rgb': [46, 38, 32], 'texture': 8, 'fibers': 4,
                      'bleed': 0.18},
                     {'op': 'foxing', 'n': 70, 'strength': 0.45},
                     {'op': 'rotate', 'deg': 6.5, 'fill': [244, 244, 240], 'expand': True},
                     {'op': 'lighting', 'gradient': 0.22, 'vignette': 0.2, 'angle': 210},
                     {'op': 'blur', 'radius_px300': 1.4},
                     {'op': 'noise', 'sigma': 7, 'chroma': 2}]),
        }),
    # ------------------------------------------------------------------ 2
    dict(
        id='pitch-cov-clef-changes-piano', title='Changing Hands', make=mk_clef_piano(), layout='piano',
        must_not_split=True,
        focus=['clef-treble', 'clef-bass', 'clef-change', 'key-f1', 'ledger-below', 'ledger-above'],
        expected_notes=(
            'One part (Piano) with 2 staves (must not be split), 12 bars of 3/4 in F major, 4 systems x 3 bars.  '
            'Ten clef changes: right hand to bass mid-bar (bar 5 beat 2), back to treble at a system start (bar 7, '
            'courtesy clef at the end of system 2), to bass at a system start (bar 10) and back to treble mid-bar '
            '(bar 11 beat 2); left hand to treble mid-bar (bar 2 beat 3), back to bass at a system start (bar 4), '
            'two changes in bar 8 (treble on beat 1, bass on beat 3), treble on beat 2 of bar 11 and bass at bar '
            '12.  Both staves may use the same clef at once (bars 5-6 both bass; bar 8 beats 1-2 and bar 11 '
            'beats 2-3 both treble).  Each <clef> must carry the right staff number.'),
        truth_notes=COMMON_NOTES,
        layout_desc='grand staff (PianoStaff), 4 systems x 3 bars, explicit system breaks',
        damage={
            'scan.pdf': typical(32001, 250, -0.9, sigma=3, jpeg=65),
            'scan-severe.pdf': dict(
                dpi=150, seed=32002, format='png', level='severe',
                summary='thin light binarised photocopy at 150 dpi: -3 deg skew, low threshold (108) with noise -> '
                        'broken staff lines and thin stems, salt-and-pepper, 1-bit PNG',
                ops=[{'op': 'ink', 'weight': -1},
                     {'op': 'paper', 'rgb': [244, 244, 242], 'texture': 2},
                     {'op': 'rotate', 'deg': -3.0, 'expand': True},
                     {'op': 'noise', 'saltpepper': 0.003},
                     {'op': 'binarize', 'threshold': 108, 'noise': 18, 'pre_blur_px300': 0.6}]),
        }),
    # ------------------------------------------------------------------ 3
    dict(
        id='pitch-cov-clefs-quartet', title='Quartet in Changing Clefs', make=mk_quartet(), layout='string-quartet',
        focus=['clef-treble', 'clef-alto', 'clef-tenor', 'clef-bass', 'clef-change', 'key-s2'],
        expected_notes=(
            'Four parts (Violin I, Violin II, Viola, Violoncello), one staff each, 8 bars of 4/4 in D major, '
            '2 systems.  The viola reads alto clef, changes to treble on beat 3 of bar 3 and back to alto at the '
            'system start of bar 5 (courtesy clef at the end of system 1).  The cello changes bass -> tenor (bar 2) '
            '-> treble (bar 3 beat 2) -> tenor (bar 4 beat 3) -> bass (bar 6) -> tenor (bar 7 beat 3) -> bass '
            '(bar 8).  The D-major key signature (F#, C#) is drawn at different heights in alto and tenor clef; it '
            'must still give F# and C# in every octave.'),
        truth_notes=COMMON_NOTES,
        layout_desc='StaffGroup of four single staves, 2 systems x 4 bars',
        damage={
            'scan.pdf': typical(33001, 300, 0.5, sigma=2, jpeg=70, gray=False, paper=(246, 243, 236)),
            'scan-severe.pdf': dict(
                dpi=150, seed=33002, jpeg=25, level='severe',
                summary='phone photo at 150 dpi: perspective keystone on a dark desk, uneven light + vignette + warm '
                        'cast, motion blur (3 px@300dpi), sensor noise, JPEG q25 (RGB)',
                ops=[{'op': 'paper', 'rgb': [240, 238, 232], 'texture': 4},
                     {'op': 'lighting', 'gradient': 0.18, 'blotch': 0.2, 'vignette': 0.3, 'warm': 0.06, 'angle': 120},
                     {'op': 'phone', 'margin': 0.06, 'bg': [62, 58, 54], 'jitter': 0.04},
                     {'op': 'blur', 'motion_px300': 3, 'angle': 20},
                     {'op': 'noise', 'sigma': 6, 'chroma': 2}]),
        }),
    # ------------------------------------------------------------------ 4
    dict(
        id='pitch-cov-keys-major-sharps', title='Sharps Ascending', make=mk_keys_major_sharps(), layout='melody',
        focus=['key-0', 'key-s1', 'key-s2', 'key-s3', 'key-s4', 'key-s5', 'key-s6', 'key-s7', 'key-change',
               'barline-double'],
        expected_notes=(
            'One part (Violin), treble clef, 16 bars of 4/4, 4 systems.  Eight major keys, 2 bars each: C (bars '
            '1-2), G (3-4), D (5-6), A (7-8), E (9-10), B (11-12), F# (13-14), C# (15-16).  The music has no '
            'accidentals at all: every altered pitch comes from the key signature (e.g. bar 16 needs E#, B# in '
            'C# major).  Key changes at bars 5, 9, 13 fall on system starts (courtesy key signature at the end of '
            'the previous system); bars 5 and 11 change key without a double barline.  Adding sharps prints no '
            'cancellation naturals.  ' + NOTE_MODE),
        truth_notes=COMMON_NOTES + [NOTE_MODE],
        layout_desc='single treble staff, 4 systems x 4 bars',
        damage={
            'scan.pdf': typical(34001, 200, -1.2, sigma=4, jpeg=60),
            'scan-severe.pdf': dict(
                dpi=120, seed=34002, jpeg=18, level='severe',
                summary='120 dpi grey copy: coffee ring over the key signatures, 9 deg skew, gradient, focus blur '
                        '1.6 px@300dpi, noise, JPEG q18',
                ops=[{'op': 'paper', 'rgb': [238, 232, 220], 'texture': 5},
                     {'op': 'stain', 'cx': 0.16, 'cy': 0.42, 'r': 0.12, 'strength': 0.5, 'rgb': [150, 100, 55]},
                     {'op': 'rotate', 'deg': 9.0, 'fill': [245, 245, 242], 'expand': True},
                     {'op': 'lighting', 'gradient': 0.2, 'angle': 60},
                     {'op': 'blur', 'radius_px300': 1.6},
                     {'op': 'noise', 'sigma': 6},
                     {'op': 'gray'}]),
        }),
    # ------------------------------------------------------------------ 5
    dict(
        id='pitch-cov-keys-major-flats', title='Flats Descending', make=mk_keys_major_flats(), layout='piano',
        must_not_split=True,
        focus=['key-f1', 'key-f2', 'key-f3', 'key-f4', 'key-f5', 'key-f6', 'key-f7', 'key-change', 'chord'],
        expected_notes=(
            'One part (Piano) with 2 staves (must not be split), 14 bars of 4/4, 4 systems (4+4+4+2 bars).  Seven '
            'major keys with flats, 2 bars each: F (bars 1-2), Bb (3-4), Eb (5-6), Ab (7-8), Db (9-10), Gb '
            '(11-12), Cb (13-14); key signatures on both staves (treble and bass positions differ).  Right hand: '
            'tonic arpeggio, then V and I chords (3 notes each); left hand: tonic/dominant half notes.  No '
            'accidentals are printed: Cb major needs Cb, Fb in every octave (e.g. the left-hand Cb2/Gb2).  ' +
            NOTE_MODE),
        truth_notes=COMMON_NOTES + [NOTE_MODE],
        layout_desc='grand staff, 4 systems (4+4+4+2 bars)',
        damage={
            'scan.pdf': typical(35001, 300, 1.0, sigma=3, jpeg=65),
            'scan-severe.pdf': dict(
                dpi=200, seed=35002, format='png', level='severe',
                summary='thick binarised photocopy at 200 dpi: ink spread (+2 px) fills the flat glyphs, 4 deg skew, '
                        'toner speckles, threshold 170 -> 1-bit PNG',
                ops=[{'op': 'ink', 'weight': 2},
                     {'op': 'paper', 'rgb': [245, 244, 240], 'texture': 2},
                     {'op': 'rotate', 'deg': 4.0, 'expand': True},
                     {'op': 'noise', 'speckle': 220},
                     {'op': 'binarize', 'threshold': 170, 'noise': 16, 'pre_blur_px300': 0.8}]),
        }),
    # ------------------------------------------------------------------ 6
    dict(
        id='pitch-cov-keys-minor-sharps', title='Minor Keys with Sharps', make=mk_keys_minor_sharps(),
        layout='melody',
        focus=['key-0', 'key-s1', 'key-s2', 'key-s3', 'key-s4', 'key-s5', 'key-s6', 'key-s7', 'x-key-minor',
               'key-change', 'acc-sharp', 'acc-double-sharp', 'clef-bass'],
        expected_notes=(
            'One part (Violoncello), bass clef, 16 bars of 3/4, 4 systems.  Eight harmonic-minor keys, 2 bars '
            'each: A minor (bars 1-2), E (3-4), B (5-6), F# (7-8), C# (9-10), G# (11-12), D# (13-14), A# minor '
            '(15-16).  The raised leading note in bar 2 of each segment is a printed accidental: G#, D#, A#, E#, '
            'B# (sharps) and F##, C##, G## (double sharps in G#, D#, A# minor).  Key signatures are read in bass '
            'clef.  ' + NOTE_MODE),
        truth_notes=COMMON_NOTES + [NOTE_MODE],
        layout_desc='single bass staff, 4 systems x 4 bars',
        damage={
            'scan.pdf': typical(36001, 250, 0.4, sigma=3, jpeg=70),
            'scan-severe.pdf': dict(
                dpi=150, seed=36002, jpeg=28, level='severe',
                summary='page fed upside down at 150 dpi: rotated 180 deg + 2 deg skew, grey, gradient, blur, '
                        'noise, JPEG q28',
                ops=[{'op': 'paper', 'rgb': [244, 243, 240], 'texture': 3},
                     {'op': 'rotate', 'deg': 2.0, 'expand': True},
                     {'op': 'lighting', 'gradient': 0.15, 'angle': 90},
                     {'op': 'rot90', 'k': 2},
                     {'op': 'blur', 'radius_px300': 1.0},
                     {'op': 'noise', 'sigma': 6},
                     {'op': 'gray'}]),
        }),
    # ------------------------------------------------------------------ 7
    dict(
        id='pitch-cov-keys-minor-flats', title='Minor Keys with Flats', make=mk_keys_minor_flats(),
        layout='melody',
        focus=['key-f1', 'key-f2', 'key-f3', 'key-f4', 'key-f5', 'key-f6', 'key-f7', 'x-key-minor', 'key-change',
               'acc-natural', 'acc-sharp', 'clef-alto'],
        expected_notes=(
            'One part (Viola), alto clef, 14 bars of 6/8, 4 systems (4+4+4+2).  Seven harmonic-minor keys, 2 bars '
            'each: D minor (bars 1-2), G (3-4), C (5-6), F (7-8), Bb (9-10), Eb (11-12), Ab minor (13-14).  The '
            'raised leading note is printed as a sharp (C# in D minor, F# in G minor) or a natural (B, E, A, D, G '
            'natural).  Key signatures are drawn in alto-clef positions.  ' + NOTE_MODE),
        truth_notes=COMMON_NOTES + [NOTE_MODE],
        layout_desc='single alto staff, 4 systems (4+4+4+2 bars)',
        damage={
            'scan.pdf': typical(37001, 200, -0.6, sigma=3, jpeg=60, gray=False, paper=(243, 238, 226)),
            'scan-severe.pdf': dict(
                dpi=200, seed=37002, jpeg=25, level='severe',
                summary='halftone-screened reproduction (100 lpi, 45 deg) rescanned -> moire, bluish recycled paper, '
                        'page cropped 1.5 mm into the staff starts (cuts into clef + key signature), 4 deg skew, '
                        'JPEG q25',
                ops=[{'op': 'paper', 'rgb': [226, 231, 236], 'texture': 4, 'ink_rgb': [35, 38, 45]},
                     {'op': 'crop', 'left_into_mm': 1.5},
                     {'op': 'halftone', 'lpi': 100, 'angle': 45, 'oversample': 2},
                     {'op': 'rotate', 'deg': 4.0, 'expand': True, 'fill': [236, 236, 236]},
                     {'op': 'noise', 'sigma': 5}]),
        }),
    # ------------------------------------------------------------------ 8
    dict(
        id='pitch-cov-key-changes-organ', title='Modulating Chorale', make=mk_organ_keys(), layout='organ',
        must_not_split=True,
        focus=['key-s4', 'key-f3', 'key-0', 'key-s3', 'key-s2', 'key-f1', 'key-s5', 'key-change', 'x-key-cancel',
               'x-key-minor', 'barline-double', 'chord'],
        expected_notes=(
            'One part (Organ) with 3 staves: manuals on a braced pair (treble + bass) and a pedal staff (bass), '
            '14 bars of 4/4, 4 systems.  Seven keys, 2 bars each, with cancellation naturals: E major (bars 1-2) '
            '-> Eb major (bar 3: 4 naturals + 3 flats) -> C major (bar 5, system start: 3 naturals) -> A major '
            '(bar 7: 3 sharps, no naturals) -> D major (bar 9, system start, no double bar: 1 natural on G + 2 '
            'sharps) -> D minor (bar 11: 2 naturals + 1 flat; leading note C# printed) -> B major (bar 13, system '
            'start: 1 natural + 5 sharps).  The cancellation naturals are not notes and not accidentals.  Every '
            'key change applies to all three staves.  A two-part encoding (manuals + pedal) is an acceptable '
            'alternative representation of the organ; the truth uses one 3-staff part.  ' + NOTE_MODE),
        truth_notes=COMMON_NOTES + [NOTE_CANCEL, NOTE_MODE],
        layout_desc='organ: PianoStaff (manuals) + separate pedal staff, 4 systems (4+4+4+2 bars)',
        damage={
            'scan.pdf': typical(38001, 300, -0.5, sigma=2, jpeg=70),
            'scan-severe.pdf': dict(
                dpi=150, seed=38002, jpeg=20, level='severe',
                summary='bound book photocopy at 150 dpi: strong left page curl with wavy warp, deep gutter shadow, '
                        'vertical camera shake (motion blur 4 px@300dpi), noise, JPEG q20 (RGB)',
                ops=[{'op': 'paper', 'rgb': [234, 222, 196], 'texture': 6},
                     {'op': 'curl', 'side': 'left', 'amp': 36, 'width': 0.33, 'wave': 8},
                     {'op': 'gutter', 'side': 'left', 'width': 0.09, 'dark': 0.65},
                     {'op': 'blur', 'motion_px300': 4, 'angle': 85},
                     {'op': 'noise', 'sigma': 7, 'chroma': 2}]),
        }),
    # ------------------------------------------------------------------ 9
    dict(
        id='pitch-cov-accidentals-melody', title='Accidental Etude', make=mk_acc_melody(), layout='melody',
        focus=['acc-sharp', 'acc-flat', 'acc-natural', 'acc-double-sharp', 'acc-double-flat', 'acc-courtesy',
               'x-acc-courtesy-paren', 'x-acc-natural-sharp', 'x-acc-natural-flat', 'key-s1'],
        expected_notes=(
            'One part (Flute), G major, 12 bars of 4/4, 3 systems.  Accidentals of every kind: sharps, flats, '
            'naturals (including naturals that cancel the key-signature F# in bar 11 and accidentals carried '
            'through the bar, e.g. E#5 then E5 natural in bar 2), double sharps (F##4, C##5, E##5), double flats '
            '(Bbb4, Gbb5, Ebb5), natural-sharp (F#4 after F##4, bar 5) and natural-flat (Bb4 after Bbb4, bar 6), '
            'octave-specific accidentals (bar 10: C5, C#6, C6 natural, C#5), and courtesy accidentals after a '
            'barline: parenthesised (bar 3 F#5, bar 9 D5 and G5, bar 12 F#4) and unparenthesised (bar 9 E5 '
            'natural, F#5).  A correct conversion spells every pitch exactly (alter -2..+2) and may mark the '
            'courtesy accidentals as cautionary.'),
        truth_notes=COMMON_NOTES + [NOTE_EXTRANAT, NOTE_COURTESY],
        layout_desc='single treble staff, 3 systems x 4 bars',
        damage={
            'scan.pdf': typical(39001, 300, 1.4, sigma=3, jpeg=65),
            'scan-severe.pdf': dict(
                dpi=100, seed=39002, jpeg=15, level='severe',
                summary='100 dpi grey: 5 deg skew, focus blur 1.2 px@300dpi, heavy noise, JPEG q15 - sharps, '
                        'naturals and double sharps become blobs of a few pixels',
                ops=[{'op': 'paper', 'rgb': [242, 242, 240], 'texture': 3},
                     {'op': 'rotate', 'deg': -5.0, 'expand': True},
                     {'op': 'blur', 'radius_px300': 1.2},
                     {'op': 'noise', 'sigma': 9},
                     {'op': 'gray'}]),
        }),
    # ------------------------------------------------------------------ 10
    dict(
        id='pitch-cov-accidentals-chords-piano', title='Chromatic Chords', make=mk_acc_chords(), layout='piano',
        must_not_split=True,
        focus=['chord', 'acc-sharp', 'acc-flat', 'acc-natural', 'acc-double-sharp', 'acc-double-flat',
               'acc-courtesy', 'x-acc-natural-sharp', 'key-f4'],
        expected_notes=(
            'One part (Piano) with 2 staves (must not be split), Ab major, 8 bars of 4/4, 2 systems.  Chromatic '
            'chords with up to three stacked accidentals in one chord (e.g. bar 2 E-major triad: E natural, G#, '
            'B natural; bar 5 B-major triad), double flats and double sharps inside chords (Bbb4, Fb5 in bar 4; '
            'F##5 in bar 6; Bbb5 in bar 7), a natural-sharp in a chord (bar 6 F#5 after F##5), octave doublings '
            'in the left hand that need one accidental per octave, accidentals carried within the bar inside '
            'chords (bar 3), parenthesised courtesy accidentals in a chord (bar 5: Bb4, F5) and an '
            'unparenthesised courtesy flat (bar 8 Eb5).  Chords must stay chords (one <chord/> group per stem).'),
        truth_notes=COMMON_NOTES + [NOTE_EXTRANAT, NOTE_COURTESY],
        layout_desc='grand staff, 2 systems x 4 bars',
        damage={
            'scan.pdf': typical(40001, 250, -0.8, sigma=3, jpeg=65, gray=False, paper=(246, 244, 238)),
            'scan-severe.pdf': dict(
                dpi=200, seed=40002, jpeg=30, level='severe',
                summary='rehearsal copy at 200 dpi: pencil circles around accidentals, pencil reminder accidentals '
                        'and fingerings (NOT in the truth), coffee ring, 2.5 deg skew, blur, JPEG q30 (RGB)',
                ops=[{'op': 'paper', 'rgb': [244, 240, 230], 'texture': 4},
                     {'op': 'pencil', 'circles': 6, 'reminders': 5, 'fingerings': 4, 'alpha': 0.75},
                     {'op': 'stain', 'cx': 0.78, 'cy': 0.30, 'r': 0.10, 'strength': 0.4, 'rgb': [150, 100, 55]},
                     {'op': 'rotate', 'deg': 2.5, 'expand': True, 'fill': [240, 240, 238]},
                     {'op': 'blur', 'radius_px300': 0.9},
                     {'op': 'noise', 'sigma': 5, 'chroma': 1.5}]),
        }),
    # ------------------------------------------------------------------ 11
    dict(
        id='pitch-cov-ottava-piano', title='Octave Signs', make=mk_ottava_piano(), layout='piano',
        must_not_split=True,
        focus=['ottava-8va', 'ottava-8vb', 'ottava-15ma', 'ledger-above', 'ledger-below'],
        expected_notes=(
            'One part (Piano) with 2 staves (must not be split), C major, 12 bars of 4/4, 3 systems.  Brackets '
            'labelled 8va / 15ma above the right hand and 8vb below the left hand: 8va from bar 2 to the middle '
            'of bar 3, 15ma from beat 2 of bar 4 across the system break into bar 5 (C8), 8va in bars 6-7, 8va '
            'from beat 2 of bar 9 to bar 10; 8vb in bar 3, from bar 5 to bar 6 (A0) and from bar 10 to the middle '
            'of bar 11.  Notes under a bracket sound one (two) octaves away from where they are drawn; the truth '
            'holds sounding pitches.  Outside the brackets many notes use 1-3 ledger lines.'),
        truth_notes=COMMON_NOTES + [NOTE_OTTAVA.format(style='"8va", "8vb", "15ma" ordinals')],
        layout_desc='grand staff, 3 systems x 4 bars, ordinal ottava texts',
        damage={
            'scan.pdf': typical(41001, 200, 0.9, sigma=4, jpeg=60),
            'scan-severe.pdf': dict(
                dpi=150, seed=41002, jpeg=30, level='severe',
                summary='page scanned sideways (rotated 90 deg) + 1.5 deg skew, two punch holes, 150 dpi grey, '
                        'gaussian + salt-and-pepper noise, JPEG q30',
                ops=[{'op': 'paper', 'rgb': [245, 244, 240], 'texture': 2},
                     {'op': 'holes', 'n': 2, 'side': 'left', 'd_mm': 6, 'offset_mm': 9, 'spacing_mm': 80,
                      'fill': [30, 30, 32]},
                     {'op': 'rotate', 'deg': 1.5},
                     {'op': 'rot90', 'k': 1},
                     {'op': 'noise', 'sigma': 9, 'saltpepper': 0.003},
                     {'op': 'gray'}]),
        }),
    # ------------------------------------------------------------------ 12
    dict(
        id='pitch-cov-ottava-ledger-melody', title='Ledger Lines and Octave Signs', make=mk_ottava_melody(),
        layout='melody',
        focus=['ottava-8va', 'ottava-8vb', 'ottava-15ma', 'ledger-above', 'ledger-below'],
        expected_notes=(
            'One part (Melody), treble clef, C major, 12 bars of 2/4, 3 systems.  The same passages are written '
            'twice: with ledger lines (bars 1-2 up to C7 with up to 5 ledger lines; bars 5-6 down to C3 with up to '
            '4 ledger lines below) and with an octave bracket (bars 3-4 under "8" above = 8va; bars 7-8 under "8" '
            'below = 8vb), so bars 1-2 = bars 3-4 and bars 5-6 = bars 7-8 in sounding pitch.  Bars 9-10 are under '
            '"15" (15ma) and sound up to C8.  This item uses LilyPond 2.24\'s default bracket text (plain "8" / '
            '"15"); the direction (above/below) distinguishes 8va from 8vb.'),
        truth_notes=COMMON_NOTES + [NOTE_OTTAVA.format(style='plain "8" / "15" numbers, LilyPond 2.24 default')],
        layout_desc='single treble staff, 3 systems x 4 bars, numeric ottava texts',
        damage={
            'scan.pdf': typical(42001, 250, -1.5, sigma=3, jpeg=60, gray=False, paper=(244, 241, 233)),
            'scan-severe.pdf': dict(
                dpi=150, seed=42002, jpeg=18, level='severe',
                summary='low-light phone photo at 150 dpi: strong keystone, dark vignette, focus blur 1.3 '
                        'px@300dpi, heavy sensor noise, JPEG q18 (RGB) - ledger lines merge',
                ops=[{'op': 'paper', 'rgb': [230, 226, 216], 'texture': 5},
                     {'op': 'lighting', 'gradient': 0.25, 'vignette': 0.45, 'warm': 0.08, 'angle': 300},
                     {'op': 'phone', 'margin': 0.05, 'bg': [40, 38, 36], 'jitter': 0.06},
                     {'op': 'blur', 'radius_px300': 1.3},
                     {'op': 'noise', 'sigma': 10, 'chroma': 3}]),
        }),
]

for _it in ITEMS:
    _it.setdefault('attribution', ATT.format(title=_it['title']))
    _it.setdefault('source', 'composed for this corpus (CC0)')
