\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Waltz in Repeats"
  composer = "Coverage corpus (2026)"
  copyright = "CC0 1.0"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  indent = 14\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vPx1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \time 3/4 \key f \major \stemDown c''4 \stemUp a'4 f'4 |
    g'4 \stemDown c''4 e''4 |
    f''2 \stemUp a'4 |
    g'2. \bar ":|.|:" |
    \break \stemDown d''4 f''4 d''4 |
    c''4 bes'4 \stemUp g'4 \bar ":|.|:" |
    a'4 \stemDown d''4 f''4 |
    e''2. \bar ":|.|:" |
    \break a''4 g''8[ f''8] e''8[ f''8] |
    g''4 c''4 bes'4 \bar ":|." |
    d''4 bes'4 \stemUp f'4 |
    g'2 r4 \bar ".|:-||" |
    \break \stemDown c''8[ d''8] c''8[ bes'8] a'8[ c''8] |
    d''4 f''4 bes''4 |
    a''4 g''4 e''4 |
    f''2. \bar ":|." |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \autoBeamOff
    \key f \major \stemUp f,4 \stemDown <f a c'>4 <f a c'>4 |
    \stemUp c4 \stemDown <e g bes c'>4 <e g bes c'>4 |
    \stemUp f,4 \stemDown <f a c'>4 <f a c'>4 |
    \stemUp c4 \stemDown <e g c'>4 <e g c'>4 |
    \stemUp bes,4 \stemDown <d f bes>4 <d f bes>4 |
    \stemUp c4 \stemDown <e g bes c'>4 <e g bes c'>4 |
    d4 <d f a>4 <d f a>4 |
    \stemUp c4 \stemDown <e g c'>4 <e g c'>4 |
    \stemUp f,4 \stemDown <f a c'>4 <f a c'>4 |
    \stemUp c4 \stemDown <e g bes c'>4 <e g bes c'>4 |
    \stemUp bes,4 \stemDown <d f bes>4 <d f bes>4 |
    \stemUp c4 \stemDown <e g c'>4 <e g c'>4 |
    \stemUp f,4 \stemDown <f a c'>4 <f a c'>4 |
    \stemUp bes,4 \stemDown <d f bes>4 <d f bes>4 |
    \stemUp c4 \stemDown <e g bes c'>4 <e g bes c'>4 |
    \stemUp f,4 \stemDown <f a c'>4 <f a c'>4 |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
