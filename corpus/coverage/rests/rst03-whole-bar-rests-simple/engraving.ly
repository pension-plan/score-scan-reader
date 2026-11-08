\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Whole-Bar Rests I"
  subtitle = "whole-bar rests in 2/4, 3/4, 4/4, C, cut time, 3/2, 5/4 and 4/2 (violin)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Violin" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 2/4 \key c \major \tempo "Allegretto" c''4 d''4 |
    R2 |
    \time 3/4 e''2. |
    R2. | \break
    \numericTimeSignature \time 4/4 f''1 |
    R1 |
    \defaultTimeSignature \time 4/4 g''1 |
    R1 | \break
    \defaultTimeSignature \time 2/2 a''1 |
    R1 |
    \time 3/2 f''1. |
    R1. | \break
    \time 5/4 e''1 d''4 |
    R1*5/4\fermata |
    \time 4/2 c''\breve |
    R\breve \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
