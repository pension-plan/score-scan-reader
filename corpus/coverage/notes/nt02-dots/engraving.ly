\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Dotted Rhythms"
  subtitle = "single and double dots on every value"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Oboe" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 3/2 \key c \major c''1. |
    \stemDown d''2. b'2. |
    \stemUp g'2.. a'8 \stemDown b'2 |
    \stemUp e'2. f'2. | \break
    \numericTimeSignature \time 4/4 g'4. a'8 \stemDown b'4. c''8 |
    d''4.. e''16 f''4.. d''16 |
    c''8.[ d''16] e''8.[ f''16] g''16[ a''8.] b''8.[ g''16] | \break
    a''8..[ g''32] f''8..[ e''32] d''16.[ c''32] \stemUp b'16.[ a'32] g'8.[ a'16] |
    \stemDown b'16.[ c''32 d''16. e''32] f''32.[ g''64 a''32. b''64 c'''16 b''16] a''4. g''8 | \break
    \stemUp <e' g'>4. <f' a'>8 <g' b'>2 |
    \stemDown <c'' e''>2. <b' d''>4 | \break
    \time 6/8 e''4. d''8.[ c''16 b'8] |
    \stemUp a'4. g'4. |
    \numericTimeSignature \time 4/4 \stemDown c''16..[ d''64 e''16.. f''64] g''4.. a''16 b'4 | \break
    \stemUp a'2.. \stemDown b'8 |
    c''1 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
