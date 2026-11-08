\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Changing Hands"
  subtitle = "clef changes on the grand staff"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 18\mm
  short-indent = 8\mm
  ragged-bottom = ##t
  ragged-last = ##f
  system-system-spacing.basic-distance = #20
  top-margin = 15\mm
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \time 3/4 \key f \major a'4 c''4 f''4 |
    e''4 g''4 c''4 |
    f''2 a'4 |
    \break bes'4 d''4 g''4 |
    a'4 \clef "bass" f4 c4 |
    a,4 c4 f4 |
    \break \clef "treble" c''4 a'4 f'4 |
    g'4 bes'4 e''4 |
    f''4 e''8 d''8 c''4 |
    \break \clef "bass" c'4 a4 f4 |
    g4 \clef "treble" bes'4 d''4 |
    f''2. \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \key f \major f,4 c4 a,4 |
    c4 bes,4 \clef "treble" g'4 |
    f'4 c'4 a4 |
    \clef "bass" g,4 d4 bes,4 |
    f,2 c,4 |
    d,8 e,8 f,4 c,4 |
    f,4 a,4 c4 |
    \clef "treble" c'4 e'4 \clef "bass" c4 |
    f,4 a,4 c4 |
    f,2 c4 |
    c4 \clef "treble" e'4 g'4 |
    \clef "bass" f,2. |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
