\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Rests in Tuplets and Beams"
  subtitle = "rests inside tuplets (3, 5, 6, 7, 2, 4) and under beams (flute)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Flute" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \tempo "Leggiero" \tuplet 3/2 { r8 c''8[ d''8] } \tuplet 3/2 { e''8[ r8 f''8] } \tuplet 3/2 { g''8[ a''8] r8 } \tuplet 3/2 { r8 r8 b''8 } |
    \tuplet 3/2 { r4 c''4 d''4 } \tuplet 3/2 { e''4 r4 r4 } | \break
    \tuplet 5/4 { c''16[ r16 d''16 r16 e''16] } \tuplet 5/4 { r16 f''16[ g''16 r16 a''16] } \tuplet 6/4 { r16 b''16[ a''16 r16 g''16 f''16] } \tuplet 6/4 { e''16[ r16 r16 d''16 r16 c''16] } |
    \tuplet 7/4 { c''16[ d''16 r16 e''16 f''16 r16 g''16] } \tuplet 7/4 { r16 a''16[ g''16 r16 f''16 e''16 d''16] } r2 | \break
    c''8[ r8 r8 d''8] e''8[ r8 f''8] r8 |
    c''16[ r16 r16 d''16] e''16[ r8 f''16] g''16[ r16 r16 a''16] r16 b''16[ a''16 g''16] | \break
    c''32[ r32 d''32 r32 e''32 r32 r32 f''32] g''32[ r16 a''32 r16 r32 b''32] c'''4 r4 |
    \tuplet 3/2 { c''16[ r16 d''16] } \tuplet 3/2 { r16 e''16[ f''16] } r4 \tuplet 3/2 { g''8[ r8 a''8] } \tuplet 3/2 { r8 b''8[ c'''8] } | \break
    \time 6/8 \tuplet 2/3 { c''8 r8 } \tuplet 2/3 { r8 d''8 } |
    c''8[ r8 d''8] e''8[ r8 f''8] | \break
    g''16[ r16 a''16 r16 r16 b''16] c'''8[ r16 a''16 r16 g''16] |
    \tuplet 4/3 { c''8[ r8 d''8 e''8] } c''4.\fermata \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
