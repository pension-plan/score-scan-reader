\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Sharps Ascending"
  subtitle = "the eight major keys from C to C sharp"
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
    \new Staff = "stP1" \with { instrumentName = "Violin" shortInstrumentName = "Vln." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key c \major c'4 e'4 g'4 c''4 |
    b'8 a'8 g'8 f'8 e'8 d'8 c'4 \bar "||" |
    \key g \major g'4 b'4 d''4 g''4 |
    fis''8 e''8 d''8 c''8 b'8 a'8 g'4 |
    \break \key d \major d'4 fis'4 a'4 d''4 |
    cis''8 b'8 a'8 g'8 fis'8 e'8 d'4 \bar "||" |
    \key a \major a'4 cis''4 e''4 a''4 |
    gis''8 fis''8 e''8 d''8 cis''8 b'8 a'4 \bar "||" |
    \break \key e \major e'4 gis'4 b'4 e''4 |
    dis''8 cis''8 b'8 a'8 gis'8 fis'8 e'4 |
    \key b \major b4 dis'4 fis'4 b'4 |
    ais'8 gis'8 fis'8 e'8 dis'8 cis'8 b4 \bar "||" |
    \break \key fis \major fis'4 ais'4 cis''4 fis''4 |
    eis''8 dis''8 cis''8 b'8 ais'8 gis'8 fis'4 \bar "||" |
    \key cis \major cis''4 eis''4 gis''4 cis'''4 |
    bis''8 ais''8 gis''8 fis''8 eis''8 dis''8 cis''4 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
