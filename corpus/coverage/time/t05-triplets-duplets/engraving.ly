\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Triplets and Duplets"
  subtitle = "for oboe"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Oboe" shortInstrumentName = "Ob." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 2/4 \key c \major \tempo "Vivace" \tuplet 3/2 { c''8[ d''8 e''8] } \tuplet 3/2 { f''8[ e''8 d''8] } |
    \tuplet 3/2 { c''4 b'4 a'4 } |
    \tuplet 3/2 { g'16[ a'16 b'16] } \tuplet 3/2 { c''16[ d''16 e''16] } \tuplet 3/2 { f''8[ e''8 d''8] } | \break
    \tuplet 3/2 { c''8[ r8 c''8] } \tuplet 3/2 { b'8 a'4 } |
    \defaultTimeSignature \time 2/2 \tuplet 3/2 { c''2 b'2 a'2 } |
    \tuplet 3/2 { g'4 a'4 b'4 } \tuplet 3/2 { c''4 d''4 e''4~ } | \break
    \time 6/8 \tuplet 2/3 { e''8[ d''8] } \tuplet 2/3 { c''8[ b'8] } |
    \tuplet 2/3 { a'4 g'4 } |
    \time 9/8 f'8[ g'8 a'8] \tuplet 2/3 { b'8[ c''8] } \tuplet 4/3 { d''8[ c''8 b'8 a'8] } | \break
    \time 12/8 \tuplet 2/3 { g'8[ a'8] } b'4. \tuplet 2/3 { c''8[ d''8] } e''4. |
    \time 2/4 \tuplet 3/2 { d''8[ c''8 b'8] } \tuplet 3/2 { a'16[ b'16 c''16] } r8 |
    c''4 r4 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
