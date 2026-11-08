\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Compound and Irregular Meters"
  subtitle = "for violoncello"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 6/8 \key f \major \partial 1*1/8 \tempo "Allegretto" c8 |
    f8[ g8 a8] bes4 a8 |
    \time 9/8 g8[ a8 bes8] c'4 bes8 a4.~ | \break
    \time 12/8 a8[ g8 f8] e4 f8 g4. c4. |
    \time 5/8 f8[ g8 a8] bes8[ c'8~] | \break
    \time 7/8 c'8[ bes8] a8[ g8] f8[ e8 d8] |
    \time 6/8 c4. r4. |
    \time 9/8 d8[ e8 f8] g4 a8 bes4.~ | \break
    \time 12/8 bes8[ a8 g8] a4. r8 c8[ d8] e4. |
    \time 5/8 f8[ e8] d8[ e8 f8~] | \break
    \time 7/8 f8[ g8 a8] bes8[ a8] g8[ e8] |
    \time 6/8 f4.~ f4 \bar "|."
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
