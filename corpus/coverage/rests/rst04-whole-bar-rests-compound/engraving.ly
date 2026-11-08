\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Whole-Bar Rests II"
  subtitle = "whole-bar rests in 3/8, 6/8, 9/8, 12/8, 5/8, 7/8, 6/4 and 3/4 (viola, alto clef)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Viola" } { \clef "alto"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 3/8 \key c \major \tempo "Vivace" c'8[ d'8 e'8] |
    R4. |
    \time 6/8 f'4. g'4. |
    R2. | \break
    \time 9/8 a'4. g'4. f'4. |
    R1*9/8 |
    \time 12/8 e'4. d'4. c'4. d'4. |
    R1. | \break
    \time 5/8 e'4 f'4. |
    R1*5/8 |
    \time 7/8 g'4 a'4 g'4. |
    R2.. | \break
    \time 6/4 f'1. |
    R1. |
    \time 3/4 e'2. |
    R2.\fermata \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
