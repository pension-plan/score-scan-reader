\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Minuet and Trio"
  subtitle = "Fine and D.C. al Fine"
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
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Tempo di Minuetto" \time 3/4 \key g \major \stemDown d''4 \stemUp g'4 a'8[ b'8] |
    \stemDown c''4 \stemUp a'4 fis'4 |
    g'8[ a'8] \stemDown b'8[ c''8] d''4 |
    \stemUp a'2. \bar ":|." |
    \break \stemDown b'4 d''4 g''4 |
    e''4 c''8[ d''8] e''8[ c''8] |
    \stemUp a'4 \stemDown fis''4 a''4 |
    g''2. \textEndMark \markup { \bold \italic "Fine" } \bar ".|:-|." |
    \break \textMark \markup { \bold "Trio" } e''4 g''4 e''4 |
    d''4 b'8[ c''8] d''8[ b'8] |
    c''4 \stemUp a'4 \stemDown c''4 |
    \stemUp fis'2. \bar ":|.|:" |
    \break g'4 \stemDown b'4 d''4 |
    e''8[ d''8] c''8[ b'8] \stemUp a'8[ g'8] |
    fis'4 a'4 \stemDown c''4 |
    b'2. \textEndMark \markup { \bold \italic "D.C. al Fine" } \bar ":|." |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \autoBeamOff
    \key g \major \stemUp g,4 \stemDown <d g b>4 <d g b>4 |
    d4 <d fis a c'>4 <d fis a c'>4 |
    \stemUp g,4 \stemDown <d g b>4 <d g b>4 |
    d4 <d fis a>4 <d fis a>4 |
    \stemUp g,4 \stemDown <d g b>4 <d g b>4 |
    \stemUp c4 \stemDown <e g c'>4 <e g c'>4 |
    d4 <d fis a c'>4 <d fis a c'>4 |
    \stemUp g,4 \stemDown <d g b>4 <d g b>4 |
    \stemUp c4 \stemDown <e g c'>4 <e g c'>4 |
    \stemUp g,4 \stemDown <d g b>4 <d g b>4 |
    \stemUp a,4 \stemDown <e a c'>4 <e a c'>4 |
    d4 <d fis a>4 <d fis a>4 |
    \stemUp g,4 \stemDown <d g b>4 <d g b>4 |
    \stemUp c4 \stemDown <e g c'>4 <e g c'>4 |
    d4 <d fis a c'>4 <d fis a c'>4 |
    \stemUp g,4 \stemDown <d g b>4 <d g b>4 |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
