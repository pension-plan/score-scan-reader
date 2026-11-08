\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "The Crooked Road"
  subtitle = "jig, slip jig and slide"
  composer = "OMR challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Fiddle" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 6/8 \key g \major \partial 1*1/8 \tempo "Lively" d'8 |
    g'8[ a'8 b'8] \acciaccatura e''8 d''8[ b'8 g'8] |
    a'8[ r8 a'8] a'8.[ b'16 a'8] |
    g'8[ a'8 b'8] c''8[ d''8 e''8] |
    d''4.~ d''8[ b'8 g'8] | \break
    c''8[ e''8 c''8] b'8[ d''8 b'8] |
    a'8[ g'8 fis'8] e'8[ fis'8 a'8~] |
    \time 3/4 a'4 c''4 e''4 |
    \time 6/8 d''4. <g' d''>4 r8 | \break
    \time 9/8 \mark "B" b'8[ d''8 b'8] a'8[ b'8 a'8] g'4 a'8 |
    b'4.~ b'8[ a'8 g'8] fis'8[ r8 fis'8] |
    g'8.[ a'16 b'8] \grace c''16 d''4 b'8 a'4. |
    g'4. r4. r4. | \break
    \time 12/8 \mark "C" d''4 e''8 d''4 b'8 g'4. \tuplet 2/3 { a'8[ b'8] } |
    <d' b'>4.~ <d' b'>4 a'8 g'8.[ fis'16 g'8] r4. | \break
    \time 6/8 b'8[ c''8 d''8] \acciaccatura e''8 d''8[ c''8 b'8] |
    a'4.\fermata g'8[ fis'8 g'8] |
    a'8.[ b'16 c''8] b'8[ a'8 g'8] |
    g'4. g'4 \bar "|."
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
