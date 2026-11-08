\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Minor Keys with Sharps"
  subtitle = "harmonic minor, A minor to A sharp minor"
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
    \new Staff = "stP1" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
        \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \time 3/4 \key a \minor a,4 c4 e4 |
    f8 gis8 a2 \bar "||" |
    \key e \minor e,4 g,4 b,4 |
    c8 dis8 e2 \bar "||" |
    \break \key b \minor b,4 d4 fis4 |
    g8 ais8 b2 |
    \key fis \minor fis,4 a,4 cis4 |
    d8 eis8 fis2 \bar "||" |
    \break \key cis \minor cis4 e4 gis4 |
    a8 bis8 cis'2 \bar "||" |
    \key gis \minor gis,4 b,4 dis4 |
    e8 fisis8 gis2 |
    \break \key dis \minor dis4 fis4 ais4 |
    b8 cisis'8 dis'2 \bar "||" |
    \key ais \minor ais,4 cis4 eis4 |
    fis8 gisis8 ais2 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
