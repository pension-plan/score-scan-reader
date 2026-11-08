\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Ledger Lines"
  subtitle = "one to five ledger lines above and below both staves"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \stemDown a''4 c'''4 e'''4 g'''4 |
    b'''2 c''''2 |
    c'''8[ d'''8 e'''8 f'''8] g'''8[ a'''8 b'''8 c''''8] | \break
    <a'' c''' e'''>2 <c''' e''' g''' b'''>2 |
    \stemUp c'4 a4 f4 d4 |
    b,2 <c' e'>2 | \break
    b16[ a16 g16 f16] e16[ d16 c16 b,16] c'8[ e'8 g'8 c''8] |
    g'''1 | \break
    <f' a' c''>2 \stemDown a'''2 |
    c''1 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major \stemUp e,4 c,4 a,,4 f,,4 |
    d,,2 c,,2 |
    c,,8[ d,,8 e,,8 f,,8] g,,8[ a,,8 b,,8 c,8] |
    <a,, c, e,>2 <f,, a,, c,>2 |
    \stemDown c'4 e'4 g'4 b'4 |
    d''2 e''2 |
    d''16[ c''16 b'16 a'16] g'16[ f'16 e'16 d'16] c'8[ a8 f8 d8] |
    <c,, c,>1 |
    <c' e' g'>2 <e' g' b'>2 |
    c1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
