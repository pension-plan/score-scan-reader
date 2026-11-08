\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Modulating Chorale"
  subtitle = "key changes with cancellation naturals"
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
    \new PianoStaff \with { instrumentName = "Organ" shortInstrumentName = "Org." } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key e \major <e' gis'>2 <e' a'>2 |
    <dis' fis'>2 <e' gis'>2 \bar "||" |
    \key ees \major <ees' g'>2 <ees' aes'>2 |
    <d' f'>2 <ees' g'>2 \bar "||" |
    \break \key c \major <c' e'>2 <c' f'>2 |
    <b d'>2 <c' e'>2 \bar "||" |
    \key a \major <a' cis''>2 <a' d''>2 |
    <gis' b'>2 <a' cis''>2 |
    \break \key d \major <d' fis'>2 <d' g'>2 |
    <cis' e'>2 <d' fis'>2 \bar "||" |
    \key d \minor <d' f'>2 <d' g'>2 |
    <cis' e'>2 <d' f'>2 \bar "||" |
    \break \key b \major <b' dis''>2 <b' e''>2 |
    <ais' cis''>2 <b' dis''>2 \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \key e \major b2 cis'2 |
    b2 b2 |
    \key ees \major bes2 c'2 |
    bes2 bes2 |
    \key c \major g2 a2 |
    g2 g2 |
    \key a \major e'2 fis'2 |
    e'2 e'2 |
    \key d \major a2 b2 |
    a2 a2 |
    \key d \minor a2 bes2 |
    a2 a2 |
    \key b \major fis'2 gis'2 |
    fis'2 fis'2 |
          }
      }
    >>
    \new Staff = "stP1s3" \with { instrumentName = "Pedal" shortInstrumentName = "Ped." } { \clef "bass"
        \new Voice = "vP1x9" {
    \key e \major e,2 a,2 |
    b,2 e,2 |
    \key ees \major ees,2 aes,2 |
    bes,2 ees,2 |
    \key c \major c,2 f,2 |
    g,2 c,2 |
    \key a \major a,2 d2 |
    e2 a,2 |
    \key d \major d,2 g,2 |
    a,2 d,2 |
    \key d \minor d,2 g,2 |
    a,2 d,2 |
    \key b \major b,2 e2 |
    fis2 b,2 |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
