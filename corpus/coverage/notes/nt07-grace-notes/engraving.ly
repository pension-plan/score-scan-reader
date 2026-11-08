\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Grace Notes"
  subtitle = "acciaccaturas, appoggiaturas, slashed and unslashed graces, grace groups"
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
    \numericTimeSignature \time 4/4 \key c \major \acciaccatura d''8 \stemDown c''4 \appoggiatura d''8 c''4 \grace e''16 d''4 \slashedGrace e''8 d''4 |
    \grace { c''16[ d''16] } e''4 \grace { e''16[ f''16 g''16] } a''4 \grace { a''16[ g''16 f''16 e''16] } d''4 \grace { f''32[ e''32 d''32 c''32] } b'4 |
    \appoggiatura e''4 d''2 \acciaccatura fis''8 g''4 \acciaccatura cis''8 d''4 | \break
    \appoggiatura { a'16[ b'16] } c''4 \grace <e'' g''>8 f''4 \grace { g'16[ a'16 b'16] } c''2 |
    \acciaccatura g'8 \stemUp a'4 \acciaccatura bes'8 a'4 \acciaccatura gis'8 a'4 \acciaccatura b'8 a'4 |
    \grace { d'16[ e'16 f'16 g'16 a'16 b'16] } \stemDown c''2. \slashedGrace b'8 c''4 | \break
    \grace { c'''32[ b''32 a''32 g''32] } f''4 \grace d''16 e''4 \appoggiatura f''16 e''4 \acciaccatura g''8 f''4 |
    \slashedGrace c'''8 b''2 \appoggiatura { c'''16[ b''16] } a''2 | \break
    \acciaccatura a''8 g''4 \acciaccatura f''8 e''4 \acciaccatura d''8 c''2 |
    \grace { b'16[ c''16 d''16] } c''1 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
