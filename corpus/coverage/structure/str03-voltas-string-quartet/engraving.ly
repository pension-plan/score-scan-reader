\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Three Endings"
  subtitle = "for string quartet"
  composer = "Coverage corpus (2026)"
  copyright = "CC0 1.0"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  indent = 22\mm
  short-indent = 10\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "v1" \with { instrumentName = "Violin I" shortInstrumentName = "Vl. I" } { \clef "treble"
          \new Voice = "vV1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \numericTimeSignature \time 4/4 \key d \major \stemUp a'4 \stemDown d''4 fis''4 e''4 |
    d''4 b'4 cis''4 d''4 |
    e''4 fis''4 g''4 e''4 |
    \set Score.repeatCommands = #'((volta "1.")) fis''2 e''2 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) \stemNeutral d''1 \bar ".|:-||" |
    \break \set Score.repeatCommands = #'((volta #f)) \stemDown fis''4 g''4 a''4 fis''4 |
    g''4 fis''4 e''4 d''4 |
    cis''4 d''4 e''4 \stemUp a'4 |
    \set Score.repeatCommands = #'((volta "1.")) \stemDown b'4 cis''4 d''4 b'4 |
    \break e''2 cis''2 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) b'4 cis''4 d''4 g''4 |
    fis''2 d''2 \bar ".|:-||" |
    \break \set Score.repeatCommands = #'((volta #f)) a''4 g''4 fis''4 e''4 |
    \set Score.repeatCommands = #'((volta "1.")) d''2 e''2 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) fis''2 e''2 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "3.")) \stemNeutral d''1 \bar "|." |
    \set Score.repeatCommands = #'((volta #f))
          }
      }
      \new Staff = "v2" \with { instrumentName = "Violin II" shortInstrumentName = "Vl. II" } { \clef "treble"
          \new Voice = "vV2x1" {
    \autoBeamOff
    \key d \major \stemUp fis'4 fis'4 a'4 a'4 |
    \stemDown b'4 \stemUp g'4 e'4 fis'4 |
    a'4 a'4 \stemDown b'4 \stemUp a'4 |
    a'2 a'2 |
    \stemNeutral a'1 |
    \stemDown d''4 b'4 d''4 d''4 |
    b'4 \stemUp a'4 a'4 fis'4 |
    a'4 a'4 a'4 fis'4 |
    g'4 e'4 fis'4 g'4 |
    e'2 e'2 |
    g'4 e'4 fis'4 g'4 |
    a'2 a'2 |
    \stemDown d''4 b'4 d''4 cis''4 |
    \stemUp a'2 \stemDown cis''2 |
    d''2 cis''2 |
    \stemNeutral a'1 |
          }
      }
      \new Staff = "va" \with { instrumentName = "Viola" shortInstrumentName = "Va." } { \clef "alto"
          \new Voice = "vVAx1" {
    \autoBeamOff
    \key d \major \stemUp a4 a4 a4 \stemDown cis'4 |
    d'4 d'4 \stemUp a4 a4 |
    \stemDown cis'4 d'4 d'4 cis'4 |
    d'2 cis'2 |
    \stemNeutral fis'1 |
    \stemDown a'4 g'4 fis'4 d'4 |
    d'4 d'4 cis'4 d'4 |
    e'4 fis'4 cis'4 d'4 |
    d'4 \stemUp a4 a4 b4 |
    \stemDown cis'2 \stemUp a2 |
    \stemDown d'4 \stemUp a4 a4 g4 |
    \stemDown d'2 fis'2 |
    fis'4 g'4 a'4 a'4 |
    fis'2 e'2 |
    d'2 e'2 |
    \stemNeutral fis'1 |
          }
      }
      \new Staff = "vc" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vVCx1" {
    \autoBeamOff
    \key d \major \stemDown d4 d4 d4 a4 |
    g4 g4 a4 d4 |
    \stemUp a,4 \stemDown d4 \stemUp g,4 a,4 |
    \stemDown d2 \stemUp a,2 |
    \stemNeutral d1 |
    \stemDown d4 e4 d4 b4 |
    g4 d4 a4 b4 |
    a4 d4 \stemUp a,4 \stemDown d4 |
    \stemUp g,4 a,4 \stemDown d4 g4 |
    \stemUp a,2 a,2 |
    g,4 a,4 \stemDown d4 e4 |
    d2 d2 |
    d4 e4 d4 a4 |
    d'2 a2 |
    b2 a2 |
    \stemNeutral d'1 |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
