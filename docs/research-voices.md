# Voice and part separation for scanned-score OMR: research notes

Scope: how to detect several voices or parts printed on one staff, mainly closed-score SATB hymns and chorales, and divisi, from page images. Covers when to split them into separate MusicXML `<part>`s, when to keep them as `<voice>`s in one part (piano grand staves, organ, local divisi), how lyrics follow the split, and how to handle uncertain cases. Written for an environment-agnostic JS OMR core that runs in the browser and in node.

Status: research and design input, compiled 2026-11-08. Sources are cited inline and listed in full in section 14. "Recommendation" marks this project's own engineering choices, as opposed to what a source says.

---

## 0. Summary

1. **On a printed staff, stem direction is the main evidence for voices.** It beats pitch. Engraving convention puts the upper voice stems up and the lower voice stems down on a shared staff, with voice-1 rests moved up and voice-2 rests moved down ([MuseScore handbook][ms-voices]). Every image-based system examined uses stems, beams and ties first and treats pitch proximity as secondary: Audiveris ([source][aud-src]), Jin & Raphael 2015 ([paper][jin15]) and BeadSolver 2026 ([paper][bead]). Symbolic (MIDI-style) voice-separation algorithms have no stems to work with, so in OMR they serve only as **fallbacks**, for stemless whole notes or broken detections.
2. **The difficult part is consistency, not the first guess.** In BeadSolver's piano test set, a greedy rule baseline that groups x-aligned columns and chains them forward gets only **55.1 % of measures with all voices matching** and **50.5 % fully correct measures**. Probability-guided search raises this to **92.4 % / 86.8 %** ([BeadSolver Table 7][bead]). On Rachmaninoff with corrected symbols, Jin & Raphael's graph optimisation (voice edges plus coincidence edges, hard bar-length constraints) interprets **355/371 = 95.7 %** of system measures correctly ([paper][jin15]). Closed-score hymns are far easier than piano music, but the same tool applies: **a hard constraint that each voice fills the bar exactly, plus repair search.**
3. **Closed-score SATB statistics (measured here)** over **368 four-part Bach chorales** in the music21 10.5.2 corpus ([script](#appendix-a-chorale-statistics-script)):
   - S/A unisons at **2.46 %** of onset slots, T/B unisons at **3.58 %**. Shared noteheads are common enough that they must be handled.
   - Voice crossings at only **0.24 %** (S/A) and **0.78 %** (T/B). Splitting by pitch order almost never contradicts the true voices, but stem direction should still decide.
   - At about **31 %** of slots only one voice of a pair has an onset (passing notes, suspensions, melismas). Lyric copying therefore has to align by time slot, not by note index.
   - Lyrics appear **only on the soprano part in 320/368** files, and never on A/T/B. Ground truth for lower-voice lyrics has to be derived.
4. **When to split:**
   - Split a staff group into one part per voice when it is classified as **vocal closed score**. The strongest cues are lyrics between or under the staves, vocal labels ("S A", "T B", "Soprano/Alto", "Women/Men"), every voice monophonic (at most 2 heads per stem), two stem directions present throughout, and SATB ranges.
   - **Never split a keyboard group.** Cues: "Piano/Pno./Organ" labels, chords of 3 or more notes per stem, pedal marks, cross-staff beams, and lyrics present only on a *different* staff.
   - Braces are weak evidence because hymnals often brace their SATB staves (an observation; see §5). Brackets point towards separate performers.
   - Make the decision **once per logical part for the whole piece**, never per measure. Unison passages written with single stems are copied into both voices.
   - When the evidence is ambiguous, keep one part with `<voice>`s. This loses nothing. Show a warning and offer a one-click split (§11).
5. **MusicXML output:**
   - Split vocal parts: one `<score-part>` per voice inside `<part-group type="start"><group-symbol>bracket</group-symbol><group-barline>yes</group-barline>`, each part monophonic in `<voice>1</voice>`, and lyrics **copied** to every voice that sings them.
   - Unsplit keyboard: one part with `<staves>2</staves>`, `<staff>` on every note, and `<backup>` between voices. Voice IDs 1–4 go on staff 1 and 5–8 on staff 2, the convention used by Audiveris ([`Voice.VoiceKind`][aud-voice]), Finale and MuseScore. Sibelius numbers voices per staff ([MuseScore forum][ms-voicenum]). `<voice>` is just a string with no defined semantics ([W3C][mx-voice]).
6. **Licensing:**
   - Audiveris and homr are **AGPL-3.0**. Take ideas only and do not port code.
   - music21 (BSD-3), partitura (Apache-2.0), piano_svsep, vocsep_ijcai2023, voice-splitting and MV2H (all MIT), oemer (MIT) and OSMD (BSD-3) are all compatible.
   - OpenScore Lieder and OpenScore String Quartets are **CC0**, which makes them good negative and positive test sets.

---

## 1. Terms

| Term | Meaning here |
|---|---|
| **Voice** | A monophonic (or homophonic-chord) sequence of events moving linearly in time. MusicXML: "A voice is a sequence of musical events (e.g. notes, chords, rests) that proceeds linearly in time" ([W3C `<voice>`][mx-voice]). |
| **Part** | One performer or section, in MusicXML a `<part>` with a `<score-part>` entry. It may have several staves (`<staves>`) and several voices. |
| **Staff group** | Staves joined by a brace or bracket and/or connected barlines within a system. |
| **Closed (close) score** | Two or more vocal parts sharing a staff. SATB on two staves, "as in hymnals" ([MuseScore 3 handbook][ms3-voices]). Merriam-Webster gives "close score" ([M-W][mw-close]). |
| **Open score** | One staff per part. |
| **Divisi** | One section temporarily divided (S1/S2, Vln I div.), often on one staff with two stem directions or as a chord on one stem. |
| **Slot** | A set of chords and rests on a system that share an onset time and are roughly x-aligned (Audiveris terminology, [SlotsRetriever][aud-src]). |
| **Logical part** | The same instrument followed across systems and pages, even when its physical staves differ per system (Audiveris "logical parts", [handbook][aud-logical]). |

---

## 2. Visual evidence for several voices on one staff

### 2.1 Stem direction (primary)

- Convention: "Two voices on the same staff are normally indicated using opposing stems". In MuseScore, voices 1 and 3 are stems up and voices 2 and 4 stems down ([MuseScore handbook][ms-voices]). For closed SATB, "use Voice 1 and Voice 2 only, for both upper and lower staves": soprano and tenor in voice 1, alto and bass in voice 2 ([MuseScore 3 handbook][ms3-voices]).
- Jin & Raphael's edge-plausibility rule 6: "Vertices connected by a voice edge usually have the same stem direction and tend to appear at similar staff height" ([ISMIR 2015][jin15]).
- In Audiveris' `VoiceDistance.Separated`, the cost of linking two chords into one voice is: opposite stems +6, different staff +20, voice "new in staff" +10, +4 per head chord (so rests are cheap "placeholders"), plus the pitch difference. A different part or a different assigned voice counts as incompatible (10000), and leaving a chord unlinked costs 60 ([`VoiceDistance.java`][aud-src]). These numbers come from AGPL code and are listed only for the cost *structure*. Re-derive the weights; do not copy them.
- Audiveris also has a "Merged" mode for lute-style staves whose middle line is physically shared. There, "chords with upward stem are considered as part of high voices, and chords with downward stem as part of low voices", and staff membership is "rather secondary" (same file).
- Stem direction **overrides pitch order**, which preserves real voice crossings. Crossings occur in 0.24–0.78 % of chorale slots (§0). Pitch order decides only for stemless notes (whole notes, breves) and for several heads on one stem.

### 2.2 Shared noteheads and unisons

- A head with **one stem on each side** serves both voices. Audiveris accepts the canonical layout ("stem down on the left side of the head and stem up on the right side") and splits the head logically into two halves, each linked to its own stem and joined by a mirror relation ([Audiveris shared head][aud-shared]). Mirrored heads go into the same slot ([SlotsRetriever][aud-src]).
- Unison heads can be shared only when they are the same type: both filled, or both open with stems. A half against a quarter, or a dotted against an undotted note, is printed offset side by side, usually with the lower voice moved to the right. Gould's *Behind Bars* covers this (pp. 50, 53, 307, quoted second-hand in [MuseScore forum 290420][ms-shared], [25454][ms-unison]). An OMR system will therefore see either one head with two stems, or two heads touching horizontally at the same staff position.
- Failure mode: when the two stems line up, the engine "may detect just one long stem, instead of two aligned ones" ([Audiveris limitations][aud-limits]). Check for a single stem that has heads at its middle, or a head at both ends.
- Hymnals often print S+A or T+B on **one stem as a 2-note chord** when the rhythms coincide, and print a single-stem note when both voices sing a unison (an observation from common hymnal engraving; see also LilyPond's part-combiner rules below). On a staff known to carry two voices, a single-stem chord with two heads therefore means *top head to the upper voice, bottom head to the lower voice*. A single-stem single head with no opposite-stem event in the same time span means *unison: copy to both voices*.
- LilyPond's `\partCombine` documents the inverse transform that engravers apply. Same pitch becomes one "a2" note. Same rhythm less than a ninth apart becomes a chord. Wider intervals or crossings become separate stems ([LilyPond automatic part combining][ly-pc]). This is a good **generative model of closed-score layouts** for synthetic test data, and the de-combining logic is its inverse.

### 2.3 Rests: displaced versus shared

- Rests of voice 1 are moved up at least one staff space and rests of voice 2 down at least one ([MuseScore handbook][ms-voices]).
- Gould, quoted on the MuseScore forum: "Separately stemmed parts share rests wherever possible" (p. 528), with vertical placement on pp. 36–37 ([MuseScore forum 34511][ms-rests]).
- Interpretation: a rest at least one space above the middle line belongs to the upper voice and one at least one space below belongs to the lower voice. A **centred rest** is **shared by both voices**, unless one voice already has events covering that time, in which case it belongs to the other voice. A centred whole-measure rest is shared.
- A rest *inside* a beamed group takes the beam's voice. Audiveris records this as a `BeamRestRelation` ("rests embraced between two beamed chords … inherit voice and time information", [`MeasureRhythm`][aud-src]).

### 2.4 Chord versus two voices

| Visual | Interpretation on a 2-voice (closed) staff | On a keyboard staff |
|---|---|---|
| N heads on one stem | Split: top head to upper voice, bottom head to lower voice. If N ≥ 3, the extra heads are divisi or an error: warn | One chord in one voice |
| Two stems in opposite directions at the same x | Two voices, by stem direction | Two voices |
| One head with stems both sides | Unison: both voices | Two voices sharing a head |
| One stemmed head, no opposite-stem event during its span | Unison: both voices (copy) | One voice |
| Two stemless heads in one slot | Pitch order: higher to upper voice | Chord, or two voices |

Symbolic research handles the same tension. Kilian & Hoos allow chords inside a voice and penalise "chords with a large pitch interval between the highest and the lowest note, as well as irregular chords containing notes with different onset times" ([ISMIR 2002][kilian]). Foscarin et al. cluster synchronous notes into chords with a learned chord-edge predictor before linking voices ([arXiv 2407.21030][svsep]). The chord-level model of Gray & Bunescu lets one note belong to several voices (convergence and divergence), which is exactly the unison case. On the Bach-chorale notes involved in such many-to-many links, an envelope baseline reaches only F = 56.7 against 87.2 for the chord-level model ([arXiv 2011.03028][chordlevel]).

### 2.5 Beams and ties within a voice

- All chords in one beam group belong to the same voice. Chords that are "within the same beam group, but not on the same stem, cannot belong to the same slot". Chords "that share a common stem belong to the same slot", and "similar abscissa is only an indication" ([Audiveris `SlotsRetriever`][aud-src]).
- Audiveris propagates voice and time through "tie and beam, plus the 'Next in Voice' manual relation" ([`MeasureRhythm`][aud-src]). Jin & Raphael rule 5: beamed notes are "usually connected by voice edges, while we penalize voices that exit a beamed group before it is completed" ([ISMIR 2015][jin15]).
- Use the majority stem direction of a beam group as its voice key. Treat a beam group whose stems point both ways (a cross-staff or kneed beam) as **keyboard evidence**. It is almost never vocal.

### 2.6 Rhythm as a global constraint

Jin & Raphael's hard constraints: the left barline is at onset 0 and the right barline at the meter. Onsets never decrease with x. Each vertex has a unique onset, so several paths into a vertex must agree. Coincident x implies the same onset ([ISMIR 2015][jin15]). Audiveris assigns voices slot by slot by mapping incoming "rookie" chords to active voices, using `VoiceDistance` and a NextInVoice blacklist. It assumes "all chords in a given narrow slot share the same time". When slot times disagree it "select[s] the smallest time value" and rejects the inconsistent mappings. Unmapped chords start new voices ([`MeasureRhythm.mapRookies`][aud-src]). Its handbook warns that the engine "tries to reconcile different heuristics" and that "the time and voice algorithms are tightly coupled". In release 5.11 "a chord can be assigned to exactly one voice", and sharing rests between voices is still "debated" ([Audiveris chords UI][aud-chords]).

Recommendation: solve voices and onsets together per staff and measure. Use a small beam or branch-and-bound search over the ambiguous decisions: shared or private rests, unison copy, divisi head placement, ambiguous dots. Score each candidate by summed link costs plus a hard penalty when any voice's durations do not fill the bar (or the pickup length).

### 2.7 Known image-side failure modes

- Aligned opposed stems merged into one stem ([Audiveris limitations][aud-limits]).
- Voices overlapping at nearly the same x, local partial voices, cross-staff voices, and tuplets coupled with rests merged across voices ([BeadSolver §1.3][bead]).
- Lyric hyphens and extenders mistaken for ledger lines or ties, and verse numbers mistaken for fingering. These are text-layer issues; see §7.

---

## 3. Closed-score SATB specifics

- Layout: S+A on a treble staff and T+B on a bass staff. S and T are stems up, A and B stems down ([MuseScore 3 handbook][ms3-voices]). Lyrics sit between the staves ([Finale hymns][finale-hymns]; LilyPond's SATB vocal-score template "regroups the four voices onto only two staves" with lyrics between them, [LilyPond SATB vocal score][ly-satb]).
- Variants to recognise:
  - **SAB**: S+A on the treble staff and one baritone voice on the bass staff.
  - **TTBB**: treble-8 clef with Tenor I/II, bass clef with Baritone/Bass.
  - **SSAA**: two treble staves.
  - **SATB with divisi**: three heads on a staff in places.
  - **Unison sections**: one voice per staff, or both staves in octaves.
- Measured phenomena in 368 Bach chorales (§0): unisons 2.5–3.6 % of slots, crossings below 0.8 %, rhythmic divergence about 31 %. Gray & Bunescu (2020), on the first 50 chorales, count 846 many-to-many (shared-note) pairs among 12,282 notes. Across their two datasets there are only 82 synchronous crossings among about 30,000 within-voice pairs ([arXiv 2011.03028][chordlevel]).
- A closed score usually keeps **two voices on every staff for the whole piece**, even where a passage is printed with single stems. Splitting therefore needs a fixed 4-part output with *unison copying*, not a per-measure voice count.

---

## 4. Divisi

- Choral and string practice puts two players or sub-sections on one staff with separate stems, often with "div." and "unis." labels. A return to a single line on its own implies unison ([Steinberg forum: divisi on same staff][st-div]). Gould is quoted as saying single-stem divisi belongs in scores, not parts (second-hand, same thread).
- Dorico allows condensing for vocal section players such as an SATB choir, unlike other section players ([Dorico condensing][dorico-cond]). Forum users report that choral condensing still handles lyrics poorly ([Steinberg forum][st-condense-lyrics]).
- LilyPond's `\partCombine` labels "Solo", "Solo II" and "a2", and for vocal scores it suggests turning those texts off ([LilyPond][ly-pc]).
- Recommendation:
  - Local divisi inside an otherwise single-voice staff: keep **one part** with voices 1 and 2 (or chords) and add a warning.
  - Promote divisi to separate parts only if (a) the label names two performers ("S1 S2", "Soprano I/II", "1.2", "I II", "div." across a whole section), or (b) two-voice texture covers at least 50 % of the measures in which that staff has notes, with each stream monophonic.

---

## 5. Piano grand staff versus vocal parts; brace versus bracket

- Convention: a **brace** joins the staves of one instrument (piano, harp, organ). A **bracket** groups different instruments or voices, such as choir parts or an instrument family ([Notation.com][brace-nc], [Dorico brackets/braces][dorico-brace]). Exceptions exist: Dorico uses sub-braces for identical instruments, and older editions sometimes bracketed piano staves ([MuseScore forum][ms-brace]).
- Hymnals often join their SA/TB staves with a **brace**, because the short score doubles as an organ part ([Finale hymns][finale-hymns]: "may be Soprano/Alto and Tenor/Bass and double as an organ part"). **A brace alone must not veto a split.** A bracket around two 2-voice staves is strong closed-choir evidence.
- Audiveris groups staves into physical parts by staff count ("one stave, or two staves (piano example), or even 3 staves (organ)"). Before release 5.6 it assigned MIDI programs by staff count, 1 → voice, 2 → piano, 3 → organ ([Audiveris logical parts][aud-logical]). That is exactly the heuristic that **mis-handles closed SATB**, which comes out as "piano". Our classifier must do better.

Discriminating features (weights are this project's recommendation; tune them on test data):

| Feature (per staff group, aggregated over all systems) | Weight |
|---|---|
| Vocal label tokens at system start (S, A, T, B, Soprano, Alto, Tenor, Bass, Sopran, Alt, Contralto, Basso, Cantus, Altus, Bassus, Women, Men, Choir, Chorus, Coro, Chor, SATB) | +3 |
| Lyric lines adjacent to the group (below staff 1, or between its staves) | +2.5 |
| Each staff: both stem directions co-occur in ≥ 30 % of measures | +1.5 per staff |
| ≥ 98 % of stems have ≤ 2 heads | +1 |
| Stream ranges fit SATB (S ≈ C4–A5, A ≈ F3–D5, T ≈ C3–G4, B ≈ E2–D4) | +1 |
| Treble-8 clef present | +0.5 |
| Bracket (rather than brace) | +0.5 |
| Keyboard label (Piano, Pno., Pf., Klavier, Organ, Org., Orgel, Manual, Ped., Harmonium, Harp, Accomp.) | −3 |
| Lyrics present in the system but only on a *different* staff (song or anthem accompaniment) | −2.5 |
| Pedal marks (Ped., ✱), arpeggio lines, fingering digits, cross-staff or kneed beams, 8va lines | −2 |
| ≥ 5 % of stems with ≥ 3 heads; octave doublings in the bottom stream | −1.5 |
| Brace, and no lyrics anywhere near | −0.5 |

Thresholds:
- **Score ≥ 3: vocal closed score, split.**
- **Score ≤ −1: keyboard, keep.**
- **In between: ambiguous.** Keep as voices, flag it, and offer a toggle (§11).

A typical hymn without labels scores about 2.5 + 3 + 1 + 1 − 0.5 = 7. A song accompaniment scores about −2.5 − 1.5 − 3 = −7.

---

## 6. Part naming from system-start labels

- Audiveris OCRs the whole sheet and assigns text roles, one of which is `PartName`, using heuristics. A recognised name is "compared, ignoring case, with logical name or logical abbreviation". Parts are collated across systems only when "physical configurations … match (number of staves, staff-line counts, …)" ([Audiveris logical parts][aud-logical], [text UI][aud-text]).
- Recommended procedure:
  1. **Find label regions.** Take text boxes to the left of the system's first barline that overlap a staff vertically or sit centred on a 2-staff brace or bracket. The first system usually has full names. Later systems have abbreviations ("S. A.", "T. B.") or nothing.
  2. **Normalise.** Lowercase, strip diacritics and punctuation, and split on whitespace, `/`, `&`, `,`, `+`, `.` and newlines. One label box can stack several names ("Soprano↵Alto").
  3. **Look up tokens in a lexicon** (multilingual):
     - soprano: s, sop, sopr, soprano/i/s, sopran, treble, cantus, superius, discantus
     - alto: a, alt, alto/i/s, contralto, altus
     - tenor: t, ten, tenor/e/i/s, ténor
     - baritone: bar, bari, baritone, baritono
     - bass: b, bs, bass, basso/i, basse(s), bassus
     - collectives: women/ladies/frauen/femmes → S+A; men/männer/hommes → T+B; satb/choir/chorus/coro/chor → group name
     - divisi markers: 1, 2, i, ii, div, divisi, unis, a2
     - keyboard tokens: as in §5
  4. **Map names to voices.** List the names in order. On a 2-voice staff the first name goes to the upper (stem-up) voice. On a 2-staff group with four names, assign (1, 2) to staff 1 and (3, 4) to staff 2. A collective ("Women") expands to two names.
  5. **Match later systems.** Match each name to logical parts by case-insensitive prefix (s → Soprano). Never let an abbreviation change the part count.
  6. **Fallback when unlabelled.** A vocal group with treble + bass staves gives S, A, T, B. Treble-8 + bass gives Tenor I, Tenor II, Baritone, Bass. A single-voice bottom staff gives SAB.
  7. **Emit names.** Use `<part-name>` for the full name and `<part-abbreviation>` for "S.", "A.", "T.", "B.". The part group gets `<group-name>` "Choir" (or the printed label, e.g. "SATB").
- Report names that were inferred rather than read in the UI ("Alto (inferred from layout)").

---

## 7. Lyrics: placement and which voices they apply to

### 7.1 What sources say

- Audiveris "connects single syllables to chords above or below, but it is not always evident which staff or voice the text concerns". By default it assumes lyrics sit below their staff ([Audiveris handbook/text][aud-text]).
- Its `LyricItemInter.lookupLink` picks the head chord with the **smallest Euclidean distance** to the syllable, within a maximum dx, on the staff above or below ([source][aud-src]). On a closed staff this tends to bind to the **lower voice** (alto), whose heads are nearer the text. Avoid that approach.
- LilyPond: when two voices with different rhythms share one lyric line, attaching it to one voice misaligns the other. The documented fix is a hidden `NullVoice` that merges both rhythms and carries the lyrics. For SATB on two staves each voice can get its own lyric context via `\lyricsto`, and lyrics placed between staves use `staff-affinity` ([LilyPond lyrics techniques][ly-lyr], [LSR 177][ly-lsr177]).
- Hymnal convention: one block of verses between the staves serves all four voices ([Finale hymns][finale-hymns], [LilyPond SATB vocal score][ly-satb]). No source states this outright as a rule; it is implied by every hymnal template.
- When converting closed to open score by hand, MuseScore users copy and paste lyrics from one staff to the other; Explode does not copy them ([MuseScore forum][ms-explode-lyrics]).
- Ground-truth caveat: the music21 Bach chorales carry lyrics on the soprano only (320/368 files, §0).

### 7.2 Recommended algorithm

1. **Lyric line to staff.** Each lyric line (a band of OCR words at a common baseline) belongs to the nearest staff *above* it in the same system. If there is no staff above, or the gap to the staff above is more than twice the gap to the staff below, it belongs to the staff below. Stacked lines under one staff are verses 1…n, ordered top to bottom. Strip leading verse numbers ("1.", "2.") and use them as `number`. Audiveris also isolates initial numbers ([source][aud-src]).
2. **Staff to voices.**
   - A line under a 2-voice staff applies to **both** voices of that staff.
   - In a closed SATB group with lyrics **only** between the staves (nothing under the bass staff), the block applies to **all four** voices.
   - If a separate block exists under the bass staff, T and B take that block instead.
   - In open score each staff carries its own text.
3. **Syllables to time slots.** Run a monotonic alignment (DP, like sequence alignment) between the syllables of one verse line and the onset slots of the *reference voice*, which is the upper voice of the staff above. Costs: x-distance between syllable centre and notehead centre (with a left-aligned variant for melisma starts); skipped onsets (melisma) are cheap after a syllable ending in an extender or hyphen and dearer otherwise; unmatched syllables are expensive. Alignment recovers from OCR splits and merges.
4. **Copy to each receiving voice.**
   - If the voice has an onset at the syllable's slot, attach a copy with the same `syllabic` and verse `number`.
   - If the voice is sustaining a note there, it does not take that syllable. Count a *conflict*.
   - If the voice has onsets with no syllable after a syllable, those notes are a **melisma** for that voice: add `<extend type="start"/>` on the syllable note (after word-final syllables only) and `<extend type="stop"/>` on the last melisma note, or a plain `<extend/>` for maximum importer compatibility ([W3C `<lyric>`][mx-lyric]).
   - Tied continuations never get syllables.
5. **Conflict check per voice.** If more than 15 % of a verse's syllables conflict for a voice, that voice probably has its own text, or the text is not meant for it. Keep the lyric on the reference voice only and warn: "Lyrics not applied to Alto: rhythm differs in N places".
6. **Record provenance** (read versus copied) per part, for the UI lyrics preview.

---

## 8. MusicXML representation

Reference points (MusicXML 4.0):
- `<backup>` and `<forward>` "are required to coordinate multiple voices in one part". `<backup>` has no `<voice>` or `<staff>` children. Its duration must be positive and must not cross a measure boundary or a mid-measure change of divisions ([W3C `<backup>`][mx-backup], [usermanuals][mx-backup-um]).
- `<staff>`: "Staff assignment is only needed for music notated on multiple staves", numbered from 1 at the top of the part ([W3C `<staff>`][mx-staff]).
- `<voice>` is a free string with no attributes and no numbering semantics ([W3C][mx-voice]). Conventions differ: Finale and MuseScore number voices across the whole multi-staff part, Sibelius per staff ([MuseScore forum][ms-voicenum]). Audiveris uses 1–4 for voices starting on staff 1, 5–8 for staff 2, and 9–12 for staff 3 ([`Voice.VoiceKind`][aud-voice]).
- `<part-group type="start|stop" number>` wraps `<score-part>`s. Its children are group-name, group-abbreviation, `group-symbol` (brace | bracket | line | square | none) and `group-barline` ([W3C part-group][mx-pg], [group-symbol values][mx-gsv]). Multi-staff parts get a brace by default ([usermanuals][mx-pg-um]).
- `<lyric number name>` with `syllabic` (single | begin | middle | end), `text`, `elision`, `extend` (whose `type` attribute dates from 3.0) and `end-line`/`end-paragraph`. `number` selects the line or verse; `name` holds labels such as verse or chorus ([W3C `<lyric>`][mx-lyric]).

### 8.1 Output A: split choir (default for vocal closed score)

```xml
<part-list>
  <part-group number="1" type="start">
    <group-name>Choir</group-name>
    <group-symbol>bracket</group-symbol>
    <group-barline>yes</group-barline>
  </part-group>
  <score-part id="P1"><part-name>Soprano</part-name><part-abbreviation>S.</part-abbreviation></score-part>
  <score-part id="P2"><part-name>Alto</part-name><part-abbreviation>A.</part-abbreviation></score-part>
  <score-part id="P3"><part-name>Tenor</part-name><part-abbreviation>T.</part-abbreviation></score-part>
  <score-part id="P4"><part-name>Bass</part-name><part-abbreviation>B.</part-abbreviation></score-part>
  <part-group number="1" type="stop"/>
</part-list>
```

- Each part is monophonic, with `<voice>1</voice>`. Omit `<stem>` so the renderer chooses.
- Tenor clef: either keep the printed bass clef or use the open-score convention `<clef><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change></clef>`. Pitches are absolute, so both are valid. Recommendation: treble-8, with a setting to change it.
- Unison notes and shared rests are **duplicated** into each part. Lyrics are copied as in §7.

### 8.2 Output B: closed score kept (ambiguous or user choice)

Use two parts, each with one staff and voices 1 and 2. This mirrors the MuseScore closed-SATB convention ([MuseScore 3 handbook][ms3-voices]).

```xml
<measure number="1">
  <attributes><divisions>2</divisions><time><beats>4</beats><beat-type>4</beat-type></time>
    <clef><sign>G</sign><line>2</line></clef></attributes>
  <note><pitch><step>E</step><octave>5</octave></pitch><duration>4</duration><voice>1</voice>
    <type>half</type><stem>up</stem>
    <lyric number="1"><syllabic>single</syllabic><text>Praise</text></lyric></note>
  <note><pitch><step>D</step><octave>5</octave></pitch><duration>4</duration><voice>1</voice>
    <type>half</type><stem>up</stem>
    <lyric number="1"><syllabic>single</syllabic><text>God</text></lyric></note>
  <backup><duration>8</duration></backup>
  <note><pitch><step>C</step><octave>5</octave></pitch><duration>4</duration><voice>2</voice>
    <type>half</type><stem>down</stem></note>
  <note><pitch><step>B</step><octave>4</octave></pitch><duration>4</duration><voice>2</voice>
    <type>half</type><stem>down</stem></note>
</measure>
```

- Unison: two `<note>`s with the same pitch, one per voice.
- Shared rest: a rest in voice 1, and in voice 2 either a rest with `print-object="no"` or a `<forward>` with `<voice>2</voice>`.

### 8.3 Output C: keyboard grand staff (never split)

```xml
<attributes><divisions>2</divisions><staves>2</staves>
  <clef number="1"><sign>G</sign><line>2</line></clef>
  <clef number="2"><sign>F</sign><line>4</line></clef></attributes>
<!-- staff 1: voices 1 (stem up) and 2 (stem down) separated by <backup> -->
<!-- staff 2: voices 5 and 6 -->
<note>...<voice>5</voice><staff>2</staff></note>
```

---

## 9. Algorithms survey

### 9.1 Image-side OMR

| System / paper | How voices are formed | Numbers | Licence and use |
|---|---|---|---|
| **Audiveris** 5.x ([code][aud-src], [handbook][aud-chords]) | (1) Chords into **slots**: shared stem → same slot, mirrored heads → same slot, same beam group on different stems → different slots, x only a hint. (2) Per slot, map new chords to active voices by `VoiceDistance` cost (stems, staff, rest bonus, pitch) with NextInVoice and SeparateVoices constraints. (3) Propagate through beams and ties. (4) Check slot times; take the lowest time on disagreement; unmapped chords start new voices. (5) Voice IDs 1–4 / 5–8 / 9–12 by starting staff. (6) Lyrics go to the nearest chord. (7) Parts come from staff counts, names from OCR `PartName`. **No automatic splitting of voices into parts.** | Not published | AGPL-3.0: ideas only |
| **Jin & Raphael** 2012/2015 ([2015][jin15]) | Graph per system measure. Voice edges ("onset of receiver = sender onset + duration") and coincidence edges (same x → same onset). Hard constraints: bar length, x-monotonic onsets, unique onset per vertex. Soft: beams, stem direction, staff height. Search with re-interpretation (implicit tuplets) | 355/371 (95.7 %) system measures on Rachmaninoff PC2. 100 % on a 180-measure score with triplets | Paper only |
| **BeadSolver** 2026 ([arXiv 2604.20522][bead]) | Measure events as "beads" threaded into one chain (BOS…EOS per voice). A 16-layer Transformer (3.24 M parameters) proposes next node, division and dots. MCTS-like search with structural loss | Greedy rule baseline: 55.09 % voice match, 50.54 % perfect measures. BeadSolver multipass: 92.42 % / 86.83 % (5,317 measures from a 107-score LilyPond test set, mostly piano: Bach, Chopin and Czerny are about 79 % of measures) | Paper; code repo has no stated licence |
| **SMT / SMT++** (Ríos-Vila et al., [arXiv 2402.07596][smt], [2405.12105][smtpp]) | End to end, image to bekern (Humdrum spines encode voices) for pianoform and quartets | CER 1.3 on quartets, 3.9 on GrandStaff (repo README) | MIT ([repo][smt-repo]); needs a large model |
| **LMX** (Mayer et al. 2024, [arXiv 2403.13763][lmx]) | End to end to linearized MusicXML (a depth-first token sequence close to MusicXML, so voices and staves survive into the output; see the paper for details). TEDn metric | OpenScore Lieder test sets: 1,438/1,493 systems | Paper and dataset |
| **homr** / **oemer** ([homr][homr]) | Segmentation (oemer UNet) plus a transformer (Polyphonic-TrOMR). Focus on pitch and rhythm | — | homr AGPL-3.0, oemer MIT |

### 9.2 Symbolic voice separation (fallbacks and offline checks)

| Method | Idea | Numbers | Licence |
|---|---|---|---|
| **Contig mapping**, Chew & Wu 2004 ([summary][vosa]); partitura implementation ([code][partitura-vs]) | Cut the piece into *contigs* with a constant number of sounding notes. Inside a contig, voices are ordered by pitch. Seed from maximal contigs and connect fragments outward with a greedy minimum cost (pitch distance; −MAX for the same note, +MAX for skips). Chords are treated as their highest note | 99.75 % fragment consistency, 94.50 % correct connections, 88.98 % average voice consistency | partitura Apache-2.0 |
| **Better contig connection**, Guiomard-Kagan et al. 2016 ([ISMIR][contig16]) | Use the whole fragment content to score connections; leave doubtful ones unconnected | Transition precision > 99 % on fugues if 25 % of links are left open (GA1-75 %) | Paper |
| **Voice vs. stream comparison** ([ISMIR 2015][cmp15]) | Benchmark of voice and stream segmentation in one framework | — | CC-BY paper |
| **VISA**, Karydis/Cambouropoulos 2007 ([ISMIR][visa]), revisited 2009 and VISA3 2016 | Perceptual *stream* separation: a stream may contain synchronous notes (chords). Sweep line plus bipartite matching; the number of voices need not be known | Precision 87.3–100 % on 10 works | Paper |
| **Kilian & Hoos** 2002 ([PDF][kilian]) | Stochastic local search over slices. Penalties for pitch distance, gaps, chord spread and irregular chords, and overlaps. **Chords allowed inside a voice**; user-tunable | — | Paper |
| **Perceptual principles**: Bregman ASA ([Wikipedia][asa]), Huron 2001 ([DOI][huron]) | Pitch proximity, temporal continuity, avoid crossing, tonal fusion: the source of the cost terms above | — | — |
| **HMM**, McLeod & Steedman 2016 ([PDF][mcleod], [code][mcleod-code]) | States are sets of monophonic voices. Voice pitch is a weighted average of recent notes; beam search (b = 25) | Average voice consistency 91.53 (Chew & Wu: 88.98). F-measure: WTC 0.97, Haydn 0.79 | MIT |
| **Neural greedy**, Gray & Bunescu 2016 ([ISMIR][gray16]) | One-hidden-layer network scoring note–voice pairs from perceptual features, applied left to right | Bach chorales F = 95.47 (baseline 93.18); pop 91.03 | Paper |
| **Chord-level model**, Gray & Bunescu 2020 ([arXiv 2011.03028][chordlevel]) | A note may belong to several voices (convergence and divergence = unisons). Scores joint assignments for a whole chord | Chorales F = 97.30; "Chords Many" F = 87.24 against a baseline of 56.72 | Paper |
| **DNN for lute and keyboard**, de Valk & Weyde ([ISMIR 2018][devalk]) | Feed-forward network with voice-entry heuristics | Lute tablature voice prediction ≈ 80–90 % | Paper |
| **GNN link prediction**, Karystinaios et al. IJCAI 2023 ([arXiv][gmtt], [code][gmtt-code]) | Heterogeneous GNN predicts note-to-next-note links, with a 1-in/1-out regulariser and linear assignment. Monophonic voices only | Link F1: Inventions 0.997, WTC I 0.976, Haydn quartets 0.872 (McLeod: 0.781) | MIT |
| **piano_svsep**, Foscarin et al. ISMIR 2024 ([arXiv][svsep], [code][svsep-code]) | GNN with chord clustering, voice edges and staff classifier; chord pooling plus linear assignment | Voice F1 96.6 (J-Pop) / 89.9 (DCML); staff accuracy 96.3 / 91.0; rule baseline 85.4 / 78.2 | MIT |

### 9.3 Tools that split voices into parts in notation software

| Tool | Behaviour |
|---|---|
| **music21** `Stream.voicesToParts(separateById=False)` / `explode()` ([source, music21 10.5.2][m21]) | For each measure, the k-th `Voice` goes to part k (`<id>-v0`, `-v1`, …). Missing voices get empty measures. Clefs, key and time are copied. With `separateById=True` voices are matched by id in order of first appearance. **It does nothing for single-stem chords or unisons, and lyrics stay on whichever voice held them.** `explode()` "currently just runs voicesToParts()". The inverse is `Score.partsToVoices(voiceAllocation=2)`, the ideal generator for synthetic closed scores. `makeVoices()` isolates overlaps into voices; `chordify()` produces a reduction. |
| **MuseScore Explode** ([handbook][ms-explode]) | Splits voices, or chord notes, of a selection onto the staves below; the staff count is the number of voices, or the largest chord. Extra notes are dropped when staves run out. Lyrics are not copied ([forum][ms-explode-lyrics]). |
| **Dorico condensing** ([docs][dorico-cond]) | The opposite direction (open to closed) with divisi-aware layout. Lyrics are a known weak spot ([forum][st-condense-lyrics]). |
| **LilyPond `\partCombine`** ([docs][ly-pc]) | Open to closed rules: a2, chords, apart, solo. Only two voices; it "only detects where notes start". |

**What this means for the project.** No reviewed tool does what we need end to end: detect a closed score from an image, de-combine single-stem chords and unisons, split into parts, and copy lyrics by rhythm. Audiveris (no part splitting, nearest-chord lyrics) and music21 (voices only) each cover a piece. The pipeline in §10 combines Audiveris-style slot and voice building (re-implemented from scratch), Jin & Raphael-style bar-length constraints, partCombine-inverse de-combining, and the slot-based lyric copy from §7.

---

## 10. Recommended pipeline (environment-agnostic JS core)

Input is detected primitives per system: staves, barlines, brace/bracket glyphs, noteheads (filled, open, whole), stems with direction, beams, flags, dots, rests with y-offset, ties and slurs, accidentals, clefs, key and time, and OCR text boxes. The core runs in browser and node.

1. **Staff grouping.** Group staves by brace/bracket glyphs and barline connectivity. Collate groups across systems into logical groups by staff count, clefs and labels (Audiveris-like collation).
2. **Chords and slots** per system measure. A stem plus its heads makes a chord. Split heads with stems on both sides into two mirrored chords. Group whole notes by x. Build slots: a shared stem means the same slot; the same beam group on different stems means different slots; otherwise use an x-overlap tolerance of about 0.6 staff space.
3. **Per-staff voice assignment** (two keys: U = upper, L = lower):
   - Stem up goes to U, stem down to L. Each beam group takes the majority direction of its stems.
   - On a 2-voice staff, a single-stem chord with ≥ 2 heads is split top → U, bottom → L. Middle heads are flagged divisi and attached as a chord to the nearer voice.
   - A single-stem single head with no opposite-stem event overlapping its span is a unison: copy to U and L.
   - Stemless heads: two in one slot go by pitch order. A single one goes to whichever voice lacks events in that span, otherwise to both.
   - Rests by y-offset: ≥ +1 space → U, ≤ −1 space → L, centred → shared unless one voice already covers that time.
   - Ties and beams keep the voice.
   - Keyboard staves use the same steps without de-combining chords. Allow up to 4 voices per staff; if a staff has no two-direction co-occurrence, it is one voice with chords.
4. **Rhythm solve and repair.** Compute per-voice onsets from durations, with x-monotonic onsets and coincident slots forced equal. Each voice must sum to the bar (or pickup) length. When it fails, search over the ambiguous choices (shared or private rest, unison copy, divisi placement, dot or flag misreads, implicit triplets) with a budget of 200 states per measure. Still failing: pad with `<forward>`, warn with the measure number, and lower the confidence.
5. **Staff-group classification** (§5 score) per logical group, aggregated over systems.
6. **Split decision and naming** (§11, §6).
7. **Lyrics** (§7).
8. **MusicXML emission** (§8): output A, B or C per group, plus a provenance record per part (source staff, voice key, split reason, confidence, lyric source) for the UI's per-part summary.

Symbolic fallback: when stem detection on a staff is unreliable (stem confidence below threshold in more than 20 % of chords), run a contig or linear-assignment separator (pitch-proximity cost) on that staff's notes for k = 2 streams and compare its result with the stem-based one. Disagreement lowers confidence.

---

## 11. Decision procedure: split or keep, and uncertain cases

```text
for each logical staff group G (whole piece):
  s = vocalScore(G)                       # §5 table, summed over systems
  if G.staves == 1:
     twoVoice = fraction of measures (where staff has notes) with ≥2 concurrent streams
     names    = labelNames(G)              # §6
     if names.count >= 2 and (s >= 1 or twoVoice >= 0.2):  split into names
     elif twoVoice >= 0.5 and allStreamsMonophonic and s >= 3: split into "<Name> 1", "<Name> 2"
     else: keep one part, voices 1/2 (warn if twoVoice > 0)
  elif G.staves == 2:
     if s >= 3:   SPLIT  -> per staff: k voices (k = max concurrent streams, usually 2; SAB → 2+1)
     elif s <= -1: KEEP as keyboard part, <staves>2</staves>, voices 1-4 / 5-8
     else:        KEEP as closed score (output B) + flag "ambiguous: split available"
  elif G.staves >= 3: KEEP (organ: 3 staves) unless every staff individually qualifies as vocal
  consistency: part count is fixed for the piece; measures with fewer visible voices
               duplicate unison material; never split per measure.
```

| Uncertain case | Action | User-facing note |
|---|---|---|
| Hymn staves braced, no labels, lyrics between staves | Split (score is high from lyrics plus stems) | "Split from shared staves: lyrics between staves, opposite stems in N % of bars" |
| Single-stem 2-note chords throughout one passage of a closed staff | De-combine top/bottom | Silent unless a chord has ≥ 3 heads |
| 3 or more heads on a closed staff (local divisi) | Keep the extra head as a chord in the nearer voice | "Divisi in bar N kept as chord in Alto" |
| Two-voice texture on a single open-score staff in < 50 % of bars, no label | Keep one part with voices | "Soprano has divisi in bars …" |
| Voice count differs between systems | Use the maximum for the piece and fill with unison copies or rests | — |
| Lyric rhythm conflicts in > 15 % of syllables for a voice | Do not copy the lyrics to that voice | "Lyrics not applied to Tenor (N conflicts)" |
| Bar-length failure after repair | `<forward>` padding, confidence < 0.5 for the measure | Bar highlighted in the overlay |
| Score in the ambiguous band (−1, 3) | Output B (lossless), toggle offered | "Could be piano or choir: currently kept together" |
| Vocal score with separate piano reduction below | Choir group split; piano kept | "Piano reduction kept as one part" |
| Instrumental shared staff labelled "1.2" or "a2" | Keep by default; split only if labelled with two names and monophonic | "Flutes 1.2 kept as one part (two voices)" |

Report confidence as one number per output part: the minimum of the classification confidence (a sigmoid of the §5 score), the voice-assignment confidence (the share of measures passing the bar check without repair) and the stem-detection confidence.

---

## 12. Evaluation plan (node harness)

- **Positive set (synthetic).** Take the music21 Bach chorales: 368 four-part, BSD code, with corpus terms per music21 ([about][m21-about]). Convert them to closed score with `partsToVoices(voiceAllocation=2)` and soprano lyrics. Export MusicXML, render with LilyPond `musicxml2ly` (available locally) to PDF/PNG, degrade (blur, noise, rotation, JPEG artefacts) to look scanned, and run the OMR core. Compare against the original 4-part score.
- **Positive set (real).** Public-domain hymnal scans from IMSLP or CPDL, hand-annotated, about 20 pages.
- **Negative set.** OpenScore Lieder (CC0, voice plus piano) rendered: the piano must never split and the voice staff must not split. Add DCML or other piano pieces for keyboard grand staves.
- **Metrics:**
  - Split-decision accuracy per staff group (target 100 % on hymns and Lieder).
  - Per-voice note accuracy after alignment.
  - Within-voice-pair F-measure, as in Gray & Bunescu and McLeod ([ISMIR 2016][gray16]).
  - The voice component of MV2H ([MV2H][mv2h], MIT; v2.1 supports homophonic voices).
  - Bar-check pass rate.
  - Lyric syllable accuracy on the soprano, plus copy correctness on A/T/B against rhythm-derived ground truth.
  - Part-name accuracy.
- **Target** with ground-truth symbols (isolating the voice logic): ≥ 99 % of notes in the correct voice on chorales. This is plausible: crossings are below 0.8 % and stems are explicit.

---

## 13. Licensing notes

| Component | Licence | Use |
|---|---|---|
| Audiveris ([repo][aud-repo]) | **AGPL-3.0** | Read for ideas; **no code or constants ported**. The algorithms are re-implemented from public descriptions |
| homr ([repo][homr]) | **AGPL-3.0** | Do not ship |
| oemer | MIT | Possible segmentation model source (check model weight terms separately) |
| music21 | BSD-3-Clause | Harness only (Python) |
| partitura | Apache-2.0 | Reference for the contig algorithm |
| piano_svsep, vocsep_ijcai2023, apmcleod/voice-splitting, MV2H | MIT | Reference or evaluation |
| SMT | MIT | Reference |
| OpenSheetMusicDisplay | BSD-3-Clause | Preview renderer |
| OpenScore Lieder / String Quartets | CC0-1.0 | Test data |
| BeadSolver "lotus" repo | No licence stated | Paper ideas only |

---

## 14. References

- [aud-src]: Audiveris source (AGPL-3.0), `sheet/rhythm/{MeasureRhythm,SlotsRetriever,VoiceDistance,ChordsMapper,Voices}.java`, `sig/inter/LyricItemInter.java`: https://github.com/Audiveris/audiveris/tree/development/app/src/main/java/org/audiveris/omr
- [aud-voice]: Audiveris `Voice.java` (VoiceKind ID families): https://github.com/Audiveris/audiveris/blob/development/app/src/main/java/org/audiveris/omr/sheet/rhythm/Voice.java
- [aud-repo]: https://github.com/Audiveris/audiveris
- [aud-chords]: Audiveris handbook, chord and voice tools: https://audiveris.github.io/audiveris/_pages/guides/ui/ui_tools/chords
- [aud-shared]: Audiveris handbook, shared head: https://audiveris.github.io/audiveris/_pages/ui_tools/shared_head
- [aud-limits]: Audiveris handbook, limitations: https://audiveris.github.io/audiveris/_pages/reference/limitations
- [aud-logical]: Audiveris handbook, logical parts: https://audiveris.github.io/audiveris/_pages/guides/specific/logical_parts
- [aud-text]: Audiveris handbook, text tools: https://audiveris.github.io/audiveris/_pages/guides/ui/ui_tools/text
- Audiveris example "O lux beata Trinitas": https://audiveris.github.io/audiveris/_pages/ui_examples/trinitas/README
- [jin15]: R. Jin, C. Raphael, "Graph-Based Rhythm Interpretation", ISMIR 2015: https://archives.ismir.net/ismir2015/paper/000226.pdf (2012 predecessor "Interpreting Rhythm in OMR": https://archives.ismir.net/ismir2012/paper/000151.pdf)
- [bead]: N. Xu et al., "From Image to Music Language: A Two-Stage Structure Decoding Approach for Complex Polyphonic OMR" (BeadSolver), arXiv 2604.20522: https://arxiv.org/abs/2604.20522
- [smt]: Ríos-Vila et al., Sheet Music Transformer: https://arxiv.org/abs/2402.07596 · [smtpp] SMT++: https://arxiv.org/abs/2405.12105 · [smt-repo] https://github.com/Jamesprocode/SMT
- [lmx]: Mayer, Straka, Hajič, Pecina, "Practical End-to-End OMR for Pianoform Music": https://arxiv.org/abs/2403.13763
- Edirisooriya et al., polyphonic OMR: https://arxiv.org/abs/2108.01769
- Sheet Music Benchmark / OMR-NED: https://arxiv.org/abs/2506.10488
- Calvo-Zaragoza, Hajič, Pacha, "Understanding OMR" (ACM CSUR 2020): https://arxiv.org/abs/1908.03608
- [homr]: https://github.com/liebharc/homr
- [vosa]: Chew & Wu, contig mapping (VoSA): https://infolab.usc.edu/imsc/research/project/vosa/vosa.pdf
- [partitura-vs]: partitura voice separation: https://partitura.readthedocs.io/en/latest/_modules/partitura/musicanalysis/voice_separation.html
- [contig16]: Guiomard-Kagan et al., "Improving Voice Separation by Better Connecting Contigs", ISMIR 2016: https://archives.ismir.net/ismir2016/paper/000129.pdf
- [cmp15]: Guiomard-Kagan et al., "Comparing Voice and Stream Segmentation Algorithms", ISMIR 2015: https://hal.archives-ouvertes.fr/hal-01246693v1
- [visa]: Karydis et al., "VISA", ISMIR 2007: https://archives.ismir.net/ismir2007/paper/000445.pdf · revisit SMC 2009: https://datalab-old.csd.auth.gr/wp-content/uploads/publications/SMC09rcm.pdf · VISA3: https://zenodo.org/record/851251
- [kilian]: Kilian & Hoos, "Voice Separation: A Local Optimisation Approach", ISMIR 2002: https://www.cs.ubc.ca/~hoos/Publ/KilHoo02.pdf
- [asa]: Auditory scene analysis: https://en.wikipedia.org/wiki/Auditory_scene_analysis
- [huron]: D. Huron, "Tone and Voice", Music Perception 19(1), 2001: https://doi.org/10.1525/mp.2001.19.1.1
- [mcleod]: McLeod & Steedman, "HMM-Based Voice Separation of MIDI Performance", JNMR 2016: https://apmcleod.github.io/pdf/VoiceSeparation.pdf · [mcleod-code] https://github.com/apmcleod/voice-splitting
- [mv2h]: MV2H metric: https://github.com/apmcleod/MV2H · paper: https://ismir2018.ismir.net/doc/pdfs/148_Paper.pdf
- [gray16]: Gray & Bunescu, "A Neural Greedy Model for Voice Separation in Symbolic Music", ISMIR 2016: https://archives.ismir.net/ismir2016/paper/000296.pdf
- [chordlevel]: "From Note-Level to Chord-Level Neural Network Models for Voice Separation in Symbolic Music": https://arxiv.org/abs/2011.03028
- [devalk]: de Valk & Weyde, ISMIR 2018: https://ismir2018.ismir.net/doc/pdfs/304_Paper.pdf
- [gmtt]: Karystinaios, Foscarin, Widmer, "Musical Voice Separation as Link Prediction", IJCAI 2023: https://arxiv.org/abs/2304.14848 · [gmtt-code] https://github.com/manoskary/vocsep_ijcai2023
- [svsep]: Foscarin et al., "Cluster and Separate: a GNN Approach to Voice and Staff Prediction for Score Engraving", ISMIR 2024: https://arxiv.org/abs/2407.21030 · [svsep-code] https://github.com/CPJKU/piano_svsep
- [m21]: music21 `Stream.voicesToParts` / `explode` / `Score.partsToVoices` (docs): https://www.music21.org/music21docs/moduleReference/moduleStreamBase.html · [m21-about] corpus terms: https://music21.org/music21docs/_sources/about/about.rst.txt
- [ms-voices]: MuseScore handbook, working with multiple voices: https://handbook.musescore.org/basics/working-with-multiple-voices
- [ms3-voices]: MuseScore 3 handbook, voices (closed SATB): https://musescore.org/en/handbook/3/voices
- [ms-explode]: MuseScore handbook, implode and explode: https://handbook.musescore.org/notation/instruments-staves-and-systems/implode-and-explode
- [ms-explode-lyrics]: MuseScore forum, splitting SATB and copying lyrics: https://musescore.org/en/node/358567 and https://musescore.org/en/node/327471
- [ms-shared]: MuseScore forum, shared noteheads (Gould pp. 50/307 quoted): https://musescore.org/en/node/290420 · [ms-unison]: https://musescore.org/en/node/25454
- [ms-rests]: MuseScore forum, rests shared by two voices (Gould p. 528 quoted): https://musescore.org/en/node/34511
- [ms-voicenum]: MuseScore forum, voice numbering in MusicXML (Sibelius per staff): https://musescore.org/en/node/345293 and https://musescore.org/en/node/267588
- [ms-brace]: MuseScore forum, brace and bracket usage: https://musescore.org/en/node/345919
- Gould, *Behind Bars*, table of contents: https://behindbarsnotation.co.uk/contents/toc.pdf
- [ly-pc]: LilyPond automatic part combining: https://lilypond.org/doc/v2.25/Documentation/notation/automatic-part-combining
- [ly-lyr]: LilyPond techniques specific to lyrics (NullVoice, divisi lyrics): https://lilypond.org/doc/v2.24/Documentation/notation/techniques-specific-to-lyrics
- [ly-satb]: LilyPond SATB vocal score template: https://lilypond.org/doc/v2.24/Documentation/learning/satb-vocal-score
- [ly-lsr177]: LSR 177, SATB on two staves with one text per voice: https://wiki.lilypond.community/wiki/LSR_177
- [finale-hymns]: Finale manual, Hymns: https://usermanuals.finalemusic.com/FinaleWin/Content/Finale/Hymns.htm
- [dorico-cond]: Dorico condensing: https://steinberg.help/dorico/v4/en/dorico/topics/page_formatting/page_formatting_condensing_enabling_disabling_t.html (and calculations: https://steinberg.help/dorico/v3/en/dorico/topics/page_formatting/page_formatting_condensing_calculations_considerations_c.html)
- [dorico-brace]: Dorico brackets and braces: https://steinberg.help/dorico/v4/en/dorico/topics/notation_reference/notation_reference_brackets_braces/notation_reference_brackets_braces_c.html
- [st-div]: Steinberg forum, divisi on same staff: https://forums.steinberg.net/t/divisi-on-same-staff/136606
- [st-condense-lyrics]: Steinberg forum, choral condensing, divisi, lyrics and XML export: https://forums.steinberg.net/t/choral-condensing-vs-divisi-lyrics-and-xml-export-a-major-workflow-gap/1038392
- [brace-nc]: Notation.com, brackets and braces: https://notation.com/MusicianDocs5/brackets_and_braces.htm
- [mw-close]: Merriam-Webster, close score: https://www.merriam-webster.com/dictionary/close%20score
- [mx-backup]: W3C MusicXML 4.0 `<backup>`: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/backup/ (example: https://www.w3.org/2021/06/musicxml40/musicxml-reference/examples/backup-element/) · [mx-backup-um]: https://usermanuals.musicxml.com/MusicXML/Content/EL-MusicXML-backup.htm
- [mx-voice]: W3C `<voice>`: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/voice/
- [mx-staff]: W3C `<staff>`: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/staff/
- [mx-pg]: W3C `<part-group>`: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/part-group/ · [mx-gsv] group-symbol-value: https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/group-symbol-value/ · [mx-pg-um]: https://usermanuals.musicxml.com/MusicXML/Content/EL-MusicXML-part-group.htm
- [mx-lyric]: W3C `<lyric>`: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/lyric/
- OpenScore Lieder (CC0): https://github.com/OpenScore/Lieder · String Quartets (CC0): https://github.com/OpenScore/StringQuartets
- PlayScore 2 (commercial; isolates SATB voices from scans, for comparison only): https://apps.apple.com/app/playscore2/id1449591118

[aud-src]: https://github.com/Audiveris/audiveris/tree/development/app/src/main/java/org/audiveris/omr
[aud-voice]: https://github.com/Audiveris/audiveris/blob/development/app/src/main/java/org/audiveris/omr/sheet/rhythm/Voice.java
[aud-repo]: https://github.com/Audiveris/audiveris
[aud-chords]: https://audiveris.github.io/audiveris/_pages/guides/ui/ui_tools/chords
[aud-shared]: https://audiveris.github.io/audiveris/_pages/ui_tools/shared_head
[aud-limits]: https://audiveris.github.io/audiveris/_pages/reference/limitations
[aud-logical]: https://audiveris.github.io/audiveris/_pages/guides/specific/logical_parts
[aud-text]: https://audiveris.github.io/audiveris/_pages/guides/ui/ui_tools/text
[jin15]: https://archives.ismir.net/ismir2015/paper/000226.pdf
[bead]: https://arxiv.org/abs/2604.20522
[smt]: https://arxiv.org/abs/2402.07596
[smtpp]: https://arxiv.org/abs/2405.12105
[smt-repo]: https://github.com/Jamesprocode/SMT
[lmx]: https://arxiv.org/abs/2403.13763
[homr]: https://github.com/liebharc/homr
[vosa]: https://infolab.usc.edu/imsc/research/project/vosa/vosa.pdf
[partitura-vs]: https://partitura.readthedocs.io/en/latest/_modules/partitura/musicanalysis/voice_separation.html
[contig16]: https://archives.ismir.net/ismir2016/paper/000129.pdf
[cmp15]: https://hal.archives-ouvertes.fr/hal-01246693v1
[visa]: https://archives.ismir.net/ismir2007/paper/000445.pdf
[kilian]: https://www.cs.ubc.ca/~hoos/Publ/KilHoo02.pdf
[asa]: https://en.wikipedia.org/wiki/Auditory_scene_analysis
[huron]: https://doi.org/10.1525/mp.2001.19.1.1
[mcleod]: https://apmcleod.github.io/pdf/VoiceSeparation.pdf
[mcleod-code]: https://github.com/apmcleod/voice-splitting
[mv2h]: https://github.com/apmcleod/MV2H
[gray16]: https://archives.ismir.net/ismir2016/paper/000296.pdf
[chordlevel]: https://arxiv.org/abs/2011.03028
[devalk]: https://ismir2018.ismir.net/doc/pdfs/304_Paper.pdf
[gmtt]: https://arxiv.org/abs/2304.14848
[gmtt-code]: https://github.com/manoskary/vocsep_ijcai2023
[svsep]: https://arxiv.org/abs/2407.21030
[svsep-code]: https://github.com/CPJKU/piano_svsep
[m21]: https://www.music21.org/music21docs/moduleReference/moduleStreamBase.html
[m21-about]: https://music21.org/music21docs/_sources/about/about.rst.txt
[ms-voices]: https://handbook.musescore.org/basics/working-with-multiple-voices
[ms3-voices]: https://musescore.org/en/handbook/3/voices
[ms-explode]: https://handbook.musescore.org/notation/instruments-staves-and-systems/implode-and-explode
[ms-explode-lyrics]: https://musescore.org/en/node/358567
[ms-shared]: https://musescore.org/en/node/290420
[ms-unison]: https://musescore.org/en/node/25454
[ms-rests]: https://musescore.org/en/node/34511
[ms-voicenum]: https://musescore.org/en/node/345293
[ms-brace]: https://musescore.org/en/node/345919
[ly-pc]: https://lilypond.org/doc/v2.25/Documentation/notation/automatic-part-combining
[ly-lyr]: https://lilypond.org/doc/v2.24/Documentation/notation/techniques-specific-to-lyrics
[ly-satb]: https://lilypond.org/doc/v2.24/Documentation/learning/satb-vocal-score
[ly-lsr177]: https://wiki.lilypond.community/wiki/LSR_177
[finale-hymns]: https://usermanuals.finalemusic.com/FinaleWin/Content/Finale/Hymns.htm
[dorico-cond]: https://steinberg.help/dorico/v4/en/dorico/topics/page_formatting/page_formatting_condensing_enabling_disabling_t.html
[dorico-brace]: https://steinberg.help/dorico/v4/en/dorico/topics/notation_reference/notation_reference_brackets_braces/notation_reference_brackets_braces_c.html
[st-div]: https://forums.steinberg.net/t/divisi-on-same-staff/136606
[st-condense-lyrics]: https://forums.steinberg.net/t/choral-condensing-vs-divisi-lyrics-and-xml-export-a-major-workflow-gap/1038392
[brace-nc]: https://notation.com/MusicianDocs5/brackets_and_braces.htm
[mw-close]: https://www.merriam-webster.com/dictionary/close%20score
[mx-backup]: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/backup/
[mx-backup-um]: https://usermanuals.musicxml.com/MusicXML/Content/EL-MusicXML-backup.htm
[mx-voice]: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/voice/
[mx-staff]: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/staff/
[mx-pg]: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/part-group/
[mx-gsv]: https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/group-symbol-value/
[mx-pg-um]: https://usermanuals.musicxml.com/MusicXML/Content/EL-MusicXML-part-group.htm
[mx-lyric]: https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/lyric/

---

## Appendix A: chorale statistics script

Run with the project venv (`.venv/bin/python`, music21 10.5.2) over `corpus.getComposer('bach')`, keeping the 368 files that have exactly four parts. A "slot" is any onset time in either voice of the pair (S/A or T/B). *Unison* means both voices sound the same MIDI pitch at the slot. *Crossing* means the upper voice is below the lower. *Rhythm-diverge* means only one of the two voices has an onset at that slot.

| Pair | Slots | Unison | Crossing | Rhythm diverges | One voice resting |
|---|---|---|---|---|---|
| S/A | 24,381 | 2.46 % | 0.24 % | 31.76 % | 0.82 % |
| T/B | 27,182 | 3.58 % | 0.78 % | 30.58 % | 0.80 % |

Lyrics present in part 0 (soprano) of 320 files and in no other part.

```python
# chorale_stats.py (abridged): per pair, walk the union of onsets and compare sounding pitches
from music21 import corpus, note, chord
def events(part):
    out = []
    for n in part.recurse().notesAndRests:
        p = (max(x.midi for x in n.pitches) if isinstance(n, chord.Chord)
             else n.pitch.midi if isinstance(n, note.Note) else None)
        out.append((float(n.getOffsetInHierarchy(part)), float(n.quarterLength), p))
    return out
# for each (upper, lower) in ((S,A),(T,B)): for t in sorted onsets of both:
#   pa/pb = pitch sounding at t; count unison (pa==pb), crossing (pa<pb),
#   rhythm-diverge (exactly one voice has an onset at t)
```
