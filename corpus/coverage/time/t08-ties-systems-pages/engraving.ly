\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Tied Across the Page"
  subtitle = "for piano"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #14
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 3/4 \key c \major \tempo "Sostenuto" e''2.~ |
    e''4 d''4 c''4~ | \break
    c''4 b'4 <f' a'~>4 |
    <g' a'>4 g'4 fis'4~ | \break
    fis'4 g'4 <g' b'>4~ |
    <g' b'>2 r4 | \break
    g'4 a'4 \tuplet 3/2 { b'8[ c''8 d''8~] } |
    d''2.~ | \pageBreak
    d''4 c''4 a'4~ |
    \time 6/8 a'4.~ a'8[ b'8 c''8~] | \break
    c''4. b'4.~ |
    b'4.~ b'8[ a'8 g'8~] | \break
    \time 3/4 g'2 f'4~ |
    f'4 e'4 d'4~ | \break
    d'2.~ |
    d'2. \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major <c g>2.~ |
    <c g>2 r4 |
    f,4 a,4 c4 |
    g,2.~ |
    g,2 d4~ |
    d4 c4 b,4 |
    c4 e4 g4 |
    <g, d>2.~ |
    <g, d>2 g,4 |
    a,4. e4.~ |
    e4. e,4. |
    a,4. c4. |
    d2 d4~ |
    d4 g,2~ |
    g,2. |
    c2. |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
