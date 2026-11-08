\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Round Trip"
  subtitle = "Segno, To Coda, D.S. al Coda"
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
    \new Staff = "vn" \with { instrumentName = "Violin" } { \clef "treble"
        \new Voice = "vVNx1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Moderato" 4 = 96 \numericTimeSignature \time 4/4 \key bes \major \stemDown bes'4 d''4 f''4 d''4 |
    c''2 r2 \bar "||" |
    \segnoMark 1 f''4. ees''8 d''4 bes'4 |
    c''4 d''8[ ees''8] f''2 |
    \break g''4 f''4 ees''4 d''4 |
    c''4 bes'4 \stemUp a'4 \stemDown c''4 |
    d''4 f''4 ees''4 c''4 |
    \stemNeutral bes'1 \textEndMark \markup { \line {  \italic "To Coda"  \hspace #0.5 \raise #0.6 \musicglyph "scripts.coda" } } |
    \break \stemDown d''4 d''8[ ees''8] f''4 bes''4 |
    a''4 g''8[ f''8] ees''4 c''4 |
    f''4 ees''4 d''4 c''4 |
    bes'2 \stemUp f'2 \textEndMark \markup { \bold \italic "D.S. al Coda" } \bar "||" |
    \break \codaMark 1 \stemDown bes'4 c''8[ d''8] ees''4 f''4 |
    g''4 a''8[ bes''8] a''4 f''4 |
    d''4 c''4 ees''4 \stemUp a'4 |
    \stemNeutral bes'1 \bar "|." |
        }
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
