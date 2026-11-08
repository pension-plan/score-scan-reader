\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Note Values"
  subtitle = "breve to sixty-fourth, beamed and flagged"
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
    \time 4/2 \key c \major g'\breve |
    a'1 b'1 |
    c''1 \stemDown d''2 e''2 |
    f''\breve | \break
    \numericTimeSignature \time 4/4 e''4 c''4 \stemUp a'4 f'4 |
    g'8[ a'8] \stemDown b'8[ c''8] d''8 e''8 f''8 d''8 |
    \stemUp e'8 f'8 g'8[ a'8] \stemDown b'8[ c''8] d''4 | \break
    c''16[ d''16 e''16 f''16] g''16[ f''16 e''16 d''16] c''16 b'16 \stemUp a'16 g'16 f'4 |
    e'16[ f'16 g'16 a'16] \stemDown b'16[ c''16 d''16 e''16] f''16 g''16 a''16 b''16 c'''4 | \break
    c'''32[ b''32 a''32 g''32 f''32 e''32 d''32 c''32] \stemUp b'32[ a'32 g'32 f'32 e'32 d'32 c'32 d'32] e'32 f'32 g'32 a'32 \stemDown b'8 c''4 |
    d''32[ e''32 f''32 g''32 a''32 b''32 c'''32 d'''32] c'''32 b''32 a''32 g''32 f''8 e''2 | \break
    c''64[ d''64 e''64 f''64 g''64 a''64 b''64 c'''64 d'''64 c'''64 b''64 a''64 g''64 f''64 e''64 d''64] c''64 b'64 \stemUp a'64 g'64 f'16 e'8 d'2 |
    e'64[ f'64 g'64 a'64 b'64 c''64 d''64 e''64] \stemDown f''64[ g''64 a''64 b''64 c'''64 b''64 a''64 g''64] f''64 e''64 d''64 c''64 b'16 \stemUp a'8 g'2 | \break
    \time 4/2 a'1 g'2 e'2 |
    c''\breve \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
