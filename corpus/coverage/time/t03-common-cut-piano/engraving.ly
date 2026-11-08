\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Common and Cut Time"
  subtitle = "for piano"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \defaultTimeSignature \time 4/4 \key c \major \partial 1*3/8 \tempo "Andante" g'8[ a'8 b'8] |
    c''4 e''4 d''4. c''8 |
    \defaultTimeSignature \time 2/2 b'2 g'2~ | \break
    \numericTimeSignature \time 4/4 g'4 a'4 b'4 c''4 |
    \numericTimeSignature \time 2/2 d''2 e''2 |
    \defaultTimeSignature \time 4/4 f''4 e''8[ d''8] c''4 b'4~ | \break
    \defaultTimeSignature \time 2/2 b'2 c''2 |
    \numericTimeSignature \time 4/4 d''4. e''8 f''4 d''4 |
    \numericTimeSignature \time 2/2 c''2 b'2~ | \break
    \defaultTimeSignature \time 4/4 b'4 a'4 b'4 g'4 |
    \defaultTimeSignature \time 2/2 c''1 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major r8 r4 |
    <c e g>2 <g, b, d>2 |
    <c e g>2 <g, b, d>2~ |
    <g, b, d>2 <c e g>2 |
    <f a c'>2 <c e g>2~ |
    <c e g>4 c8[ d8] e4 g,4 |
    <c g>1 |
    <d f a>2 <g, b, f>2 |
    <a, c e>2 <g, b, d>2 |
    <g, d>2 <g, b, f>2 |
    <c, c>1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
