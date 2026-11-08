\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Flags and Stems"
  subtitle = "unbeamed values, stems up and down, forced stems"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Violin" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 3/4 \key c \major \stemUp c'8 d'8 e'8 f'8 g'8 a'8 |
    \stemDown b'8 c''8 d''8 e''8 f''8 g''8 |
    a''16 g''16 f''16 e''16 d''8 c''8 b'4 |
    \stemUp g'16 f'16 e'16 d'16 c'8 d'8 e'4 | \break
    \stemDown c''32 d''32 e''32 f''32 g''16 a''16 b''8 c'''8 d'''4 |
    \stemUp a'32 g'32 f'32 e'32 d'16 c'16 b8 c'8 d'4 |
    \stemDown e''64 f''64 g''64 a''64 b''64 a''64 g''64 f''64 e''8 d''8 c''8 b'4 | \break
    \stemUp d'64 e'64 f'64 g'64 a'64 g'64 f'64 e'64 d'8 \stemDown c'8 d'8 e'4 |
    \stemUp f''8 g''8 a''8 b''8 c'''4 |
    \stemDown g'16 a'16 b'16 c''16 \stemUp d''16 e''16 f''16 g''16 \stemDown a''4 | \break
    b'8 b'8 \stemUp b'8 b'8 \stemDown b'4 |
    \stemUp g''2 \stemDown d'4 |
    e''4 c''4 \stemUp a'4 |
    g'2. \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
