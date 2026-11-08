\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Minor Keys with Flats"
  subtitle = "harmonic minor, D minor to A flat minor"
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
  system-system-spacing.basic-distance = #16
  top-margin = 15\mm
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Viola" shortInstrumentName = "Vla." } { \clef "alto"
        \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \time 6/8 \key d \minor d'4 f'8 a'4 f'8 |
    cis'4 e'8 d'4. |
    \key g \minor g4 bes8 d'4 bes8 |
    fis4 a8 g4. \bar "||" |
    \break \key c \minor c'4 ees'8 g'4 ees'8 |
    b4 d'8 c'4. \bar "||" |
    \key f \minor f4 aes8 c'4 aes8 |
    e4 g8 f4. |
    \break \key bes \minor bes4 des'8 f'4 des'8 |
    a4 c'8 bes4. \bar "||" |
    \key ees \minor ees'4 ges'8 bes'4 ges'8 |
    d'4 f'8 ees'4. \bar "||" |
    \break \key aes \minor aes4 ces'8 ees'4 ces'8 |
    g4 bes8 aes4. \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
