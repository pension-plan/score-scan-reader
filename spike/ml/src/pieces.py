"""Test pieces for the ML OMR spike (all public domain: tunes/texts pre-1830).

Each voice is a list of note tokens "<Pitch><Oct>:<dur>[.][(|)]" or "r:<dur>",
e.g. "F#4:4", "B4:8(" (slur start), "G4:8)" (slur end), "D5:2." (dotted half).
Lyrics are LilyPond-style syllable strings ("A -- maz -- ing __ grace").
Melisma notes (inside a slur, after the first) take no syllable.
"""

# Amazing Grace (NEW BRITAIN, 1829) - text John Newton 1779.  3/4, pickup.
AMAZING_MELODY = (
    "D4:4 | G4:2 B4:8( G4:8) | B4:2 A4:4 | G4:2 E4:4 | D4:2 D4:4 | G4:2 B4:8( G4:8) | B4:2 A4:4 | "
    "D5:2 B4:4 | D5:2 B4:8( G4:8) | B4:2 A4:4 | G4:2 E4:4 | D4:2 D4:4 | G4:2 B4:8( G4:8) | B4:2 A4:4 | G4:2."
)
AMAZING_V1 = ("A -- maz -- ing __ grace how sweet the sound That saved a __ wretch like me "
              "I once was __ lost but now am found Was blind but __ now I see")
AMAZING_V2 = ("'Twas grace that __ taught my heart to fear And grace my __ fears re -- lieved "
              "How pre -- cious __ did that grace ap -- pear The hour I __ first be -- lieved")

# Old Hundredth (Genevan Psalter 1551), simple 4-part setting written for this spike.
OLD100_S = ("G4:2 G4:4 F#4:4 | E4:4 D4:4 G4:4 A4:4 | B4:1 | B4:2 B4:4 B4:4 | A4:4 G4:4 C5:4 B4:4 | A4:1 | "
            "G4:2 A4:4 B4:4 | A4:4 G4:4 E4:4 F#4:4 | G4:1 | D5:2 B4:4 G4:4 | A4:4 C5:4 B4:4 A4:4 | G4:1")
OLD100_A = ("D4:2 E4:4 D4:4 | C4:4 B3:4 D4:4 D4:4 | D4:1 | G4:2 G4:4 G4:4 | F#4:4 G4:4 G4:4 G4:4 | F#4:1 | "
            "D4:2 F#4:4 G4:4 | F#4:4 D4:4 C4:4 D4:4 | D4:1 | G4:2 G4:4 E4:4 | E4:4 E4:4 D4:4 D4:4 | D4:1")
OLD100_T = ("B3:2 B3:4 A3:4 | G3:4 G3:4 G3:4 F#3:4 | G3:1 | D4:2 D4:4 D4:4 | D4:4 D4:4 E4:4 D4:4 | D4:1 | "
            "B3:2 D4:4 D4:4 | D4:4 B3:4 G3:4 A3:4 | B3:1 | B3:2 D4:4 B3:4 | C4:4 A3:4 G3:4 F#3:4 | G3:1")
OLD100_B = ("G3:2 E3:4 D3:4 | C3:4 G2:4 B2:4 D3:4 | G2:1 | G3:2 E3:4 D3:4 | D3:4 B2:4 C3:4 G2:4 | D3:1 | "
            "G3:2 D3:4 G2:4 | D3:4 G3:4 C3:4 D3:4 | G2:1 | G3:2 G3:4 E3:4 | A2:4 A2:4 B2:4 D3:4 | G2:1")
OLD100_V1 = ("All peo -- ple that on earth do dwell Sing to the Lord with cheer -- ful voice "
             "Him serve with fear His praise forth tell Come ye be -- fore Him and re -- joice")
OLD100_V2 = ("The Lord ye know is God in -- deed With -- out our aid He did us make "
             "We are His folk He doth us feed And for His sheep He doth us take")

PIECES = {
    # single staff, melody + 2 verses, melismas/extenders, pickup, 3/4
    "melody_lyrics": {
        "title": "Amazing Grace", "key": "g \\major", "fifths": 1, "time": (3, 4), "partial": 4,
        "staves": [{"clef": "treble", "voices": [("melody", AMAZING_MELODY, None)]}],
        "lyrics": [("melody", AMAZING_V1, 0), ("melody", AMAZING_V2, 0)],
    },
    # closed score hymn: S+A on treble (voiceOne/voiceTwo), T+B on bass; lyrics between staves
    "satb_closed": {
        "title": "Old Hundredth", "key": "g \\major", "fifths": 1, "time": (4, 4), "partial": None,
        "staves": [
            {"clef": "treble", "voices": [("soprano", OLD100_S, "\\voiceOne"), ("alto", OLD100_A, "\\voiceTwo")]},
            {"clef": "bass", "voices": [("tenor", OLD100_T, "\\voiceOne"), ("bass", OLD100_B, "\\voiceTwo")]},
        ],
        "lyrics": [("soprano", OLD100_V1, 0), ("soprano", OLD100_V2, 0)],
        # in a hymnal the between-staves text is sung by all four voices
        "lyrics_apply_to": ["soprano", "alto", "tenor", "bass"],
    },
    # open score: one voice per staff (what satb-line-omr is trained for)
    "satb_open": {
        "title": "Old Hundredth (open score)", "key": "g \\major", "fifths": 1, "time": (4, 4), "partial": None,
        "staves": [
            {"clef": "treble", "voices": [("soprano", OLD100_S, None)]},
            {"clef": "treble", "voices": [("alto", OLD100_A, None)]},
            {"clef": "treble_8", "voices": [("tenor", OLD100_T, None)]},
            {"clef": "bass", "voices": [("bass", OLD100_B, None)]},
        ],
        "lyrics": [("soprano", OLD100_V1, 0), ("alto", OLD100_V1, 1), ("tenor", OLD100_V1, 2), ("bass", OLD100_V1, 3)],
    },
}
