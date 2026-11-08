\version "2.24.0"
#(set-global-staff-size 21)
\header {
  title = "Accidental Storm"
  subtitle = "study for flute"
  composer = "challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 16\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #15
  top-margin = 16\mm
}
\score {
  <<
    \new Staff = "stFL" \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { \clef "treble"
        \new Voice = "vFLx1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key g \major g'4 b'8 d''8 cis''4 d''4 |
    e''8 cis''8 d''8 b'8 cis''4 a'4 |
    c''4 b'8 a'8 g'4 fis'4 |
    g'2 r4 d''4 |
    \break dis''4 e''8 fis''8 g''4 dis''4 |
    e''4 d''?4 c''8 b'8 a'4 |
    ais'4 b'8 cis''8 d''4 cis''4 |
    c''!4 b'2 r4 |
    \break fisis''4 gis''8 fis''8 f''4 e''4 |
    ees''4 d''8 des''8 c''4 ces''4 |
    bes'4 beses'8 bes'8 aes'4 g'4 |
    fis'2 r4 d'4 |
    \break d'8 dis'8 e'8 eis'8 fis'8 g'8 gis'8 a'8 |
    ais'8 b'8 c''8 cis''8 d''8 dis''8 e''8 f''8 |
    fis''?8 f''8 e''8 ees''8 d''8 des''8 c''8 b'8 |
    bes'8 a'8 aes'8 g'8 fis'4 r4 |
    \break g'4 gis'2.~ |
    gis'4 gis'4 a'2 |
    cis''8 e''8 a'4 c'8 e'8 c''4 |
    b'2 g'2 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
