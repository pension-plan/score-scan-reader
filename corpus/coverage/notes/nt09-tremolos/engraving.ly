\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Tremolos"
  subtitle = "single-note and two-note tremolos"
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
    \numericTimeSignature \time 4/4 \key c \major \stemDown c''4:8 d''4:16 e''4:32 f''4:16 |
    g''2:16 e''2:32 |
    c''1:16 | \break
    c''8:16[ d''8:16] e''8:32[ f''8:32] g''4:16 <c'' e'' g''>4:16 |
    \repeat tremolo 4 { c''16 e''16 } \repeat tremolo 4 { d''16 f''16 } |
    \repeat tremolo 8 { <c'' e''>16 <g'' c'''>16 } | \break
    \stemUp \repeat tremolo 8 { e'32 g'32 } \repeat tremolo 8 { f'32 a'32 } |
    <e' g' c''>2:16 <c' e' g' c''>2:32 |
    c''1 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major \stemUp c4:16 g,4:16 c4:16 g,4:16 |
    \repeat tremolo 4 { c,16 c16 } \repeat tremolo 4 { g,,16 g,16 } |
    \repeat tremolo 8 { c,16 c16 } |
    \stemDown <c g>2:16 <c e g>2:32 |
    \stemUp f,2:32 g,2:32 |
    \repeat tremolo 8 { c,32 g,32 } \repeat tremolo 8 { c,32 g,32 } |
    c,1:32 |
    <c, c>1:16 |
    c,1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
