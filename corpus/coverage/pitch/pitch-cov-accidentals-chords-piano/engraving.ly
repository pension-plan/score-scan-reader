\version "2.24.0"
#(set-global-staff-size 21)
\header {
  title = "Chromatic Chords"
  subtitle = "stacked accidentals in chords"
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
  system-system-spacing.basic-distance = #22
  top-margin = 15\mm
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key aes \major <c'' ees'' aes''>4 <c'' e'' g''>4 <des'' f'' aes''>4 <d'' f'' b'>4 |
    <ees'' g'' bes''>2 <e'' gis'' b''>2 |
    <a' cis'' e''>4 <aes' c'' ees''>4 <fes' aes' ces''>2 |
    <bes' des'' f''>2 <beses' des'' fes''>2 |
    \break <bes'? des'' f''?>2 <b' dis'' fis''>2 |
    <b' dis'' fisis''>4 <b' dis'' fis''>4 <e'' gis'' b''>2 |
    <ees'' g'' bes''>4 <ees'' ges'' beses''>4 <des'' f'' aes''>2 |
    <c'' ees''! aes''>1 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \key aes \major aes,2 g,2 |
    <ees, ees>2 <e, e>2 |
    <a, a>4 <aes, aes>4 <fes, fes>2 |
    <bes,, bes,>2 <ees, bes,>2 |
    <bes,, bes,>2 <b,, b,>2 |
    <b,, b,>2 <e, e>2 |
    <ees, bes,>2 <des, aes,>2 |
    <aes,, aes,>1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
