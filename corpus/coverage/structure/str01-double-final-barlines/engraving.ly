\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Sectional Study"
  subtitle = "double and final bar lines"
  composer = "Coverage corpus (2026)"
  copyright = "CC0 1.0"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  indent = 12\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "fl" \with { instrumentName = "Flute" } { \clef "treble"
        \new Voice = "vFLx1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \numericTimeSignature \time 4/4 \key c \major \stemDown c''4 e''4 g''4 e''4 |
    f''4 d''4 c''2 \bar "||" |
    \stemUp g'8[ a'8] \stemDown b'8[ c''8] d''4 \stemUp g'4 |
    \stemDown e''4 d''8[ c''8] d''2 \bar "||" |
    \break e''4. f''8 g''4 c''4 |
    \stemUp a'4 \stemDown b'4 c''2 \bar "||" |
    d''8[ e''8] f''8[ d''8] e''4 c''4 |
    b'4 d''4 c''2 \bar "|." |
    \break a''4 g''4 f''4 e''4 |
    d''2 g''2 \bar "||" |
    c'''4 b''4 a''4 g''4 \bar "||" |
    f''2. r4 \bar "||" |
    \break e''8[ f''8] g''8[ a''8] g''4 e''4 |
    f''4 a''4 g''2 \bar "||" |
    c''4 e''8[ d''8] c''4 b'4 |
    \stemNeutral c''1 \bar "|." |
        }
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
