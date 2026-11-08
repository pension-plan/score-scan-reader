\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Tacet Interludes"
  subtitle = "multi-bar rests: H-bars and church-rest symbols (trumpet in C part)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #20
  indent = 32\mm
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Trumpet in C" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \set Score.skipBars = ##t
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \tempo "Allegro" R1*16 |
    \mark "A" c''4 e''4 g''4 e''4 |
    R1*2 |
    g'4 c''4 e''4 g''4 | \break
    R1*3 |
    c'''2 g''2 |
    R1*4 | \break
    \time 3/4 \mark "B" R2.*6 |
    e''2 d''4 |
    \once \override MultiMeasureRest.expand-limit = #1 R2.*5 | \break
    \time 6/8 c''4. g'4. |
    R2.*12 |
    \defaultTimeSignature \time 2/2 \mark "C" R1*7 | \break
    \numericTimeSignature \time 4/4 \mark "D" R1*32 |
    c''4 e''4 g''4 c'''4 |
    c'''1\fermata \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
