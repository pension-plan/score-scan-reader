\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Beam Groups"
  subtitle = "two to eight notes per beam, beams over rests, secondary beams"
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
    \time 2/4 \key c \major \stemDown c''8[ d''8] e''8[ f''8] |
    g''16[ f''16 e''16 d''16] \stemUp c''16[ b'16 a'16 g'16] |
    \time 3/4 \stemDown a'8[ b'8 c''8 d''8 e''8 f''8] |
    g''8[ e''8] c''8[ a'8] \stemUp f'8[ d'8] | \break
    \time 6/8 e'8[ g'8 c''8] \stemDown e''8[ c''8 g'8] |
    a'16[ b'16 c''16 d''16 e''16 f''16] g''16[ f''16 e''16 d''16 c''16 b'16] |
    c''8[ r8 c''8] d''8[ e''16 f''16 g''8] | \break
    \numericTimeSignature \time 4/4 a''8[ g''8 f''8 e''8 d''8 c''8 b'8 a'8] |
    g'16[ a'16 b'16 \set stemRightBeamCount = #1 c''16 \set stemLeftBeamCount = #1 d''16 e''16 f''16 g''16] a''16[ g''16 f''16 \set stemRightBeamCount = #1 e''16 \set stemLeftBeamCount = #1 d''16 c''16 b'16 a'16] | \break
    b'8.[ c''16] d''16[ e''8.] f''8[ g''16 a''16] b''16[ a''16 g''8] |
    c'''16[ r16 b''16 a''16] g''16[ r8 f''16] e''16[ r16 d''16 c''16] c''32[ d''32 e''32 f''32 g''16 a''16] | \break
    b''32[ a''32 g''32 f''32 e''32 d''32 c''32 b'32] \stemUp a'32[ g'32 f'32 e'32 d'32 e'32 f'32 g'32] \stemDown a'32[ b'32 c''32 d''32] e''16[ c''16] \stemUp g'8[ e'8] |
    \stemDown c''32[ d''16.] e''16.[ f''32] g''8[ f''8 e''8 d''8] c''4 | \break
    \time 3/4 e''8[ r8 d''8 r8 c''8 b'8] |
    \numericTimeSignature \time 4/4 <g' c''>8[ <a' d''>8 <b' e''>8 <c'' f''>8] <d'' g''>2 |
    c''1 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
