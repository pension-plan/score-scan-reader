\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Simple Meters"
  subtitle = "for flute"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 2/4 \key g \major \partial 1*1/4 \tempo "Moderato" d'4 |
    g'8[ a'8 b'8 c''8] |
    \time 3/4 d''4 g''4 fis''8[ e''8] |
    \numericTimeSignature \time 4/4 d''4. c''8 b'4 a'4~ | \break
    \time 5/4 a'4 g'4 a'4 b'4 c''4 |
    \numericTimeSignature \time 2/2 d''2 e''2~ | \break
    \time 3/2 e''2 d''4. c''8 b'2 |
    \time 2/4 a'8[ b'8 c''8 d''8] |
    \time 3/4 e''2 d''4~ | \break
    \numericTimeSignature \time 4/4 d''4 c''4 b'2 |
    \time 5/4 a'4 b'4 c''2.~ | \break
    \numericTimeSignature \time 2/2 c''2 b'2 |
    \time 3/2 a'2 fis'2 g'2 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
