\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Nested Tuplets"
  subtitle = "for violin"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Violin" shortInstrumentName = "Vn." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \tempo "Moderato" \tuplet 3/2 { c''8[ \tuplet 3/2 { d''16 e''16 f''16 } g''8] } \tuplet 3/2 { a''8[ g''8 f''8] } e''2 |
    \tuplet 3/2 { \tuplet 3/2 { c''8[ d''8 e''8] } f''4 g''4 } d''2 | \break
    \tuplet 5/4 { c''8[ d''8 \tuplet 3/2 { e''16 f''16 g''16 } a''8 b''8] } c'''2 |
    \tuplet 3/2 { e''4 \tuplet 5/4 { d''16[ c''16 b'16 a'16 g'16] } f'4 } \tuplet 3/2 { g'4 a'4 \tuplet 3/2 { b'8[ c''8 d''8] } } | \break
    \tuplet 3/2 { r8 \tuplet 3/2 { e''16[ d''16 c''16 } b'8] } \tuplet 3/2 { \tuplet 3/2 { a'16[ b'16 c''16 } d''8 e''8] } c''2 | \break
    \time 6/8 \tuplet 2/3 { c''8[ \tuplet 3/2 { d''16 e''16 f''16] } } a'4. |
    g'4.~ g'4. \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
