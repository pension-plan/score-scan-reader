\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Rest Values"
  subtitle = "every rest value from breve to 64th (oboe)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Oboe" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \tempo "Moderato" c''4 r4 e''4 r4 |
    d''2 r2 |
    r2 f''4 r4 | \break
    g''8 r8 e''8 r8 c''8 r8 r4 |
    r8 a'8 r4 r8 b'8 r4 |
    e''16 r16 r8 f''16 r16 r8 g''16 r16 r8 a''16 r16 r8 | \break
    r16 d''16 r8 r16 e''16 r8 r4 r16 c''16 r8 |
    b''32 r32 r16 r8 a''32 r32 r16 r8 g''32 r32 r16 r8 f''32 r32 r16 r8 | \break
    e''64 r64 r32 r16 r8 r4 d''64 r64 r32 r16 r8 r4 |
    r64 f''64 r32 r16 r8 r64 a''64 r32 r16 r8 r64 c'''64 r32 r16 r8 r64 e''64 r32 r16 r8 | \break
    g''64 r64 r32 r16 r8 e''64 r64 r32 r16 r8 c''64 r64 r32 r16 r8 a'64 r64 r32 r16 r8 |
    \time 4/2 r1 r2 c''2 |
    r\breve | \break
    c''1 r1 |
    r\breve |
    r1 r2 c''2\fermata \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
