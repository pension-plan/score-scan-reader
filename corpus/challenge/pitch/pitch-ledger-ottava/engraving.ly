\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Heights and Depths"
  subtitle = "duet for flute and tuba"
  composer = "challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 16\mm
  ragged-bottom = ##t
  indent = 15\mm
  short-indent = 8\mm
  system-system-spacing.basic-distance = #22
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "stFL" \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { \clef "treble"
          \new Voice = "vFLx1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key c \major c''4 e''4 g''4 c'''4 |
    e'''4 g'''4 c''''2 |
    b'''4 a'''4 g'''4 f'''4 |
    e'''2 r2 |
    \break \ottava #1 c''''4 d''''4 b'''4 g'''4 |
    a'''4 c''''4 g'''2 \ottava #0 |
    c''''4 d''''4 b'''4 g'''4 |
    a'''4 c''''4 g'''2 |
    \break g''4 \ottava #1 g'''4 a'''4 b'''4 |
    c''''2 \ottava #0 c'''2 |
    e'''4 \ottava #1 f'''4 a'''4 c''''4 |
    b'''4 g'''4 e'''4 f'''4 |
    \break d'''4 b''4 \ottava #0 c'''2 |
    g''4 c'''4 e'''4 g'''4 |
    c''''1 |
    c'''1 \bar "|." |
          }
      }
      \new Staff = "stTU" \with { instrumentName = "Tuba" shortInstrumentName = "Tba." } { \clef "bass"
          \new Voice = "vTUx1" {
    \key c \major c,1 |
    g,,2 c,2 |
    g,,1 |
    c,2 r2 |
    \ottava #-1 c,,4 e,,4 g,,4 c,4 |
    f,,4 a,,4 g,,2 \ottava #0 |
    c,,4 e,,4 g,,4 c,4 |
    f,,4 a,,4 g,,2 |
    c,2 \ottava #-1 c,,2 |
    e,,4 d,,4 c,,2 \ottava #0 |
    c,1 |
    \ottava #-1 g,,2 d,,2 |
    c,,2 \ottava #0 c,2 |
    e,2 g,2 |
    c,1 |
    c,,1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
