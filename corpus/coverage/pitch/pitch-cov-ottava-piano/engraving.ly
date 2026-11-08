\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Octave Signs"
  subtitle = "8va, 15ma and 8vb brackets"
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
  system-system-spacing.basic-distance = #24
  top-margin = 15\mm
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key c \major c''4 e''4 g''4 c'''4 |
    \ottava #1 e'''4 g'''4 c''''2 |
    b'''4 g'''4 \ottava #0 e'''4 c'''4 |
    g''4 \ottava #2 c''''4 e''''4 g''''4 |
    \break c'''''2 \ottava #0 c'''2 |
    \ottava #1 a'''4 f'''4 d'''4 b''4 |
    c'''1 \ottava #0 |
    g''2 e''2 |
    \break c''4 \ottava #1 g'''4 a'''4 b'''4 |
    c''''4 d''''4 e''''2 \ottava #0 |
    c'''4 g''4 e''4 c''4 |
    c''1 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \key c \major c2 g,2 |
    c,2 e,2 |
    \ottava #-1 c,,4 g,,4 e,,2 \ottava #0 |
    g,1 |
    \ottava #-1 a,,,2 e,,2 |
    f,,2 g,,2 \ottava #0 |
    c,1 |
    e,2 g,2 |
    c4 e4 g4 c'4 |
    \ottava #-1 c,,4 e,,4 g,,4 c,4 |
    e,,2 \ottava #0 g,2 |
    c,1 |
          }
      }
    >>
  >>
  \layout {
    \context { \Staff ottavationMarkups = #'((2 . "15ma") (1 . "8va") (-1 . "8vb") (-2 . "15mb")) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
