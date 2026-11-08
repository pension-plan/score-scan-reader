\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Flats Descending"
  subtitle = "the seven major keys from F to C flat"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 18\mm
  short-indent = 8\mm
  ragged-bottom = ##t
  ragged-last = ##f
  system-system-spacing.basic-distance = #20
  top-margin = 15\mm
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key f \major f'4 a'4 c''4 f''4 |
    <c'' e'' g''>2 <a' c'' f''>2 |
    \key bes \major bes'4 d''4 f''4 bes''4 |
    <f'' a'' c'''>2 <d'' f'' bes''>2 \bar "||" |
    \break \key ees \major ees'4 g'4 bes'4 ees''4 |
    <bes' d'' f''>2 <g' bes' ees''>2 |
    \key aes \major aes'4 c''4 ees''4 aes''4 |
    <ees'' g'' bes''>2 <c'' ees'' aes''>2 \bar "||" |
    \break \key des \major des'4 f'4 aes'4 des''4 |
    <aes' c'' ees''>2 <f' aes' des''>2 |
    \key ges \major ges'4 bes'4 des''4 ges''4 |
    <des'' f'' aes''>2 <bes' des'' ges''>2 \bar "||" |
    \break \key ces \major ces'4 ees'4 ges'4 ces''4 |
    <ges' bes' des''>2 <ees' ges' ces''>2 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \key f \major f,2 c2 |
    c2 f,2 |
    \key bes \major bes,2 f2 |
    f2 bes,2 |
    \key ees \major ees,2 bes,2 |
    bes,2 ees,2 |
    \key aes \major aes,2 ees2 |
    ees2 aes,2 |
    \key des \major des,2 aes,2 |
    aes,2 des,2 |
    \key ges \major ges,2 des2 |
    des2 ges,2 |
    \key ces \major ces,2 ges,2 |
    ges,2 ces,2 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
