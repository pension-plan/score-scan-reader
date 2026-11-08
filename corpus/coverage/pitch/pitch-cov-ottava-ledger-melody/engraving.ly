\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Ledger Lines and Octave Signs"
  subtitle = "the same passages with ledger lines and with 8 / 15"
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
  system-system-spacing.basic-distance = #22
  top-margin = 15\mm
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Melody" shortInstrumentName = "Mel." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \time 2/4 \key c \major c'''8 d'''8 e'''8 f'''8 |
    g'''8 a'''8 b'''8 c''''8 |
    \ottava #1 c'''8 d'''8 e'''8 f'''8 |
    g'''8 a'''8 b'''8 c''''8 \ottava #0 |
    \break a8 g8 f8 e8 |
    d4 c4 |
    \ottava #-1 a8 g8 f8 e8 |
    d4 c4 \ottava #0 |
    \break \ottava #2 c''''8 e''''8 g''''8 c'''''8 |
    g''''4 c'''''4 \ottava #0 |
    c'''4 g''4 |
    c''2 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
