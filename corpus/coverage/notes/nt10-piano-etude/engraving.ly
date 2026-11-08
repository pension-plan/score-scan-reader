\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Etude in C"
  subtitle = "all note symbols in a piano texture"
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
    \numericTimeSignature \time 4/4 \key c \major \stemDown e''8[ c''8 g'8 c''8] e''16[ d''16 c''16 d''16] e''8.[ g''16] |
    <f'' a''>4 <e'' g''>8[ <d'' f''>8] \acciaccatura d''8 c''4 r4 |
    a'16[ b'16 c''16 d''16 e''16 f''16 g''16 a''16] b''32[ a''32 g''32 f''32 e''32 d''32 c''32 b'32] c''4 | \break
    <g' b' d'' g''>2 \grace { a''16[ b''16] } c'''2 |
    c'''16[ b''16 a''16 g''16] f''8.[ e''16] d''4.. c''16 |
    \stemUp <e' g' c''>4. <f' a' d''>8 \stemDown <g' b' e''>4 <a' c'' f''>4 | \break
    g''8[ r8 a''8 b''8] c'''16[ d'''16 e'''16 f'''16] g'''4 |
    f'''32[ e'''32 d'''32 c'''32 b''32 a''32 g''32 f''32] e''8[ d''8] c''4 b'4 |
    \slashedGrace d''8 c''4 \stemUp b'8[ a'8] g'16[ a'16 b'16 c''16] \stemDown d''4 |
    <c'' e'' g'' c'''>1 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major \stemUp c4 \stemDown <e g>4 \stemUp c4 \stemDown <e g>4 |
    \stemUp f,8[ c8 f8 a8] \stemDown g,8[ d8 g8 b8] |
    \stemUp a,4 \stemDown <c e a>4 d4 <f a d'>4 |
    \stemUp g,,2 \stemDown <g, d g b>2 |
    \stemUp f,16[ a,16 c16 f16] \stemDown a,16[ c16 f16 a16] \stemUp b,8[ d8] g,4 |
    c4. f,8 g,4 f,4 |
    e,4 c,4 f,,4 g,,4 |
    c,8[ e,8 g,8 c8] d,4 g,4 |
    a,,4 <e, a, c>4 g,,4 <d, g, b,>4 |
    <c,, c,>1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
