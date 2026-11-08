\version "2.24.0"
#(set-global-staff-size 21)
\header {
  title = "Accidental Etude"
  subtitle = "sharps, flats, naturals, doubles and courtesy accidentals"
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
  system-system-spacing.basic-distance = #16
  top-margin = 15\mm
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key g \major g'4 ais'8 b'8 cis''4 dis''4 |
    e''8 eis''8 fis''4 f''4 e''4 |
    fis''?4 ees''4 des''4 c''4 |
    bes'4 aes'4 g'2 |
    \break fisis'4 gis'4 fis'4 f'4 |
    bes'4 beses'4 bes'4 a'4 |
    cisis''4 dis''4 eisis''4 fis''4 |
    geses''4 fes''4 eeses''4 des''4 |
    \break d''?4 e''!4 fis''!4 g''?4 |
    c''4 cis'''4 c'''4 cis''4 |
    f'4 fis'4 f'8 e'8 dis'4 |
    a'4 fis'?4 g'2 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
