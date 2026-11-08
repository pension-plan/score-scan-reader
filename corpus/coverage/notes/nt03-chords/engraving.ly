\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Chord Study"
  subtitle = "chords of two to six notes"
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
    \numericTimeSignature \time 4/4 \key c \major \stemUp <e' g'>4 <e' g' c''>4 <d' f' g' b'>4 <c' e' g' c''>4 |
    <c' e' g' c'' e''>2 \stemDown <d' f' a' c'' e'' g''>2 |
    \stemUp <g' a'>4 <f' g' b'>4 <e' f' g'>8[ <d' e' g'>8] <c' d'>4 | \break
    \stemDown <fis' a' d''>8[ <g' bes' d''>8 <a' cis'' e''>8 <bes' d'' f''>8] <c'' ees'' g'' c'''>2 |
    <a'' c''' e'''>4 <g'' b'' d''' g'''>4 <f'' a'' c''' f'''>2 |
    \stemUp <e' gis' b' e''>16[ <fis' a' c''>16 <gis' b' d''>16 <a' c'' e''>16] \stemDown <b' d'' f''>16[ <c'' e'' g''>16 <d'' f'' a''>16 <e'' g'' b''>16] <c'' e'' a'' c'''>2 | \break
    \stemUp <c' e' g' c''>2. <b d' g'>4 |
    <c' g' c'' e'' g''>1 | \break
    <d' f' a'>2 \stemDown <e' g' c'' e'' g'' c'''>2 |
    <c' e' g' c''>1 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major \stemDown <c g>2 \stemUp <g, d g>2 |
    <c, c>2 <f, c f a>2 |
    <e, b, e g>4 \stemDown <a, e a>4 \stemUp <d, a, d f>4 \stemDown <g, d g b>4 |
    <d a>8[ <g, d g>8 <a, e a>8 <bes, f bes>8] <c g c'>2 |
    <a, e a>4 <g, d g b>4 \stemUp <f, c f a>2 |
    <e, b, e>2 \stemDown <a, e a c'>2 |
    \stemUp <c, g, c e g>2. <g, d f>4 |
    <c, c>1 |
    <d, a, d f>2 <c, g, c e g c'>2 |
    <c, g, c e>1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
