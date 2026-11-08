\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Quartet in Changing Clefs"
  subtitle = "alto and tenor clefs, clef changes in viola and cello"
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
  indent = 20\mm
  short-indent = 10\mm
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "stV1" \with { instrumentName = "Violin I" shortInstrumentName = "Vl. I" } { \clef "treble"
          \new Voice = "vV1x1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key d \major fis''4 a''4 d'''4 a''4 |
    b''4 g''4 e''4 cis'''4 |
    d'''2 a''2 |
    g''4 fis''4 e''4 d''4 |
    \break fis''4 e''8 d''8 cis''4 a'4 |
    b'4 d''4 g''4 fis''4 |
    e''4 a''4 g''4 cis''4 |
    d''1 \bar "|." |
          }
      }
      \new Staff = "stV2" \with { instrumentName = "Violin II" shortInstrumentName = "Vl. II" } { \clef "treble"
          \new Voice = "vV2x1" {
    \key d \major a'4 d''4 fis''4 d''4 |
    d''4 b'4 cis''4 e''4 |
    fis''2 fis''2 |
    b'4 a'4 g'4 fis'4 |
    a'4 cis''8 b'8 a'4 e'4 |
    d'4 fis'4 b'4 a'4 |
    cis''4 e''4 b'4 g'4 |
    fis'1 |
          }
      }
      \new Staff = "stVA" \with { instrumentName = "Viola" shortInstrumentName = "Vla." } { \clef "alto"
          \new Voice = "vVAx1" {
    \key d \major d'4 fis'4 a'4 fis'4 |
    g'4 d'4 e'4 a'4 |
    a'2 \clef "treble" d''4 cis''4 |
    d''4 a'4 b'4 a'4 |
    \clef "alto" d'4 a4 e'4 cis'4 |
    g4 b4 d'4 d'4 |
    a4 cis'4 d'4 e'4 |
    a1 |
          }
      }
      \new Staff = "stVC" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vVCx1" {
    \key d \major d4 d4 a,4 d4 |
    \clef "tenor" g4 b4 a4 cis'4 |
    d'4 \clef "treble" fis'4 a'4 fis'4 |
    g'4 e'4 \clef "tenor" d'4 a4 |
    d'4 cis'4 b4 a4 |
    \clef "bass" g,4 b,4 d4 g4 |
    a,4 a4 \clef "tenor" b4 cis'4 |
    \clef "bass" d1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
