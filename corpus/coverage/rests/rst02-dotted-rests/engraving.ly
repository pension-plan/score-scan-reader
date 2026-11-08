\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Dotted Rests"
  subtitle = "dotted and double-dotted rests in simple and compound meters (violoncello)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Violoncello" } { \clef "bass"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \tempo "Andante" d4 r2. |
    r4. f8 a4 r4 |
    g4 r8. a16 b4 r4 |
    a8 r16. b32 c'8 r8 r2 | \break
    g16 r32. a64 r8 r4 r2 |
    r4.. a16 g2 |
    f2 r8.. e32 d4 |
    r2.. d8 | \break
    \time 3/4 r4. c8 d4 |
    e4 r8. f16 g4 |
    \time 6/8 r4. d4. |
    d8[ e8 f8] r4. | \break
    \time 9/8 r4. a4. r4. |
    \time 12/8 r2. g4. r4. |
    r4. r8 a8[ b8] c'4. r4. |
    \numericTimeSignature \time 4/4 r8. d16 r8.. d32 d2\fermata \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
