\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Clef Carousel"
  subtitle = "duet for viola and violoncello"
  composer = "challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 16\mm
  ragged-bottom = ##t
  indent = 18\mm
  short-indent = 9\mm
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "stVA" \with { instrumentName = "Viola" shortInstrumentName = "Vla." } { \clef "alto"
          \new Voice = "vVAx1" {
    \autoLineBreaksOff
    \time 3/4 \key f \major a4 c'4 f'4 |
    d'4 f'4 bes'4 |
    c''4 bes'4 e'4 |
    f'2. |
    \break f4 g4 a4 |
    bes4 d'4 bes4 |
    e'4 c'4 e'4 |
    f'2. |
    \break bes4 f4 d4 |
    c4 e4 g4 |
    a4 c'4 f'4 |
    g'4 e'4 c'4 |
    \break \clef "treble" a'4 c''4 f''4 |
    e''4 cis''4 a'4 |
    d''4 f''4 a''4 |
    g''4 f''4 d''4 |
    \break d''4 bes'4 \clef "alto" g'4 |
    e'4 c'4 e'4 |
    g'4 e'4 c'4 |
    a2. \bar "|." |
          }
      }
      \new Staff = "stVC" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vVCx1" {
    \key f \major f,4 a,4 c4 |
    bes,4 d4 f4 |
    c4 e4 g4 |
    f2. |
    \clef "tenor" d'4 e'4 f'4 |
    g'4 \clef "treble" bes'4 d''4 |
    c''4 bes'4 g'4 |
    a'2. |
    \clef "tenor" f'4 d'4 bes4 |
    g4 c'4 e'4 |
    \clef "bass" f4 c4 a,4 |
    c4 g,4 c4 |
    f,4 c4 f4 |
    a,4 cis4 e4 |
    d4 a,4 f,4 |
    bes,4 d4 f4 |
    g4 \clef "tenor" d'4 bes4 |
    c'4 e'4 g'4 |
    \clef "bass" bes4 g4 e4 |
    f2. |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
