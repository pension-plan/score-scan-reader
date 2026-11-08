\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Toccatina"
  subtitle = "for piano"
  composer = "OMR challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #24
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "stP1s1" { \clef "treble"
        <<
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 2/4 \key c \major \tempo "Presto" \voiceOne e''2 |
    d''4. c''8 |
    \oneVoice c''32[ d''32 e''32 f''32 g''32 a''32 b''32 c'''32] d'''16[ c'''16 b''16 a''16] |
    g''8.[ a''32 g''32] f''16[ e''16 d''16 c''16] | \break
    \tuplet 6/4 { c''16[ e''16 g''16 c'''16 g''16 e''16] } \tuplet 6/4 { d''16[ f''16 a''16 d'''16 a''16 f''16] } |
    e''16.[ f''32 g''16. a''32] b''8..[ c'''32] |
    c'''64[ b''64 a''64 g''64 f''64 e''64 d''64 c''64] b'16[ c''16] d''4 |
    r16 g''16[ e''16 c''16] r16 a''16[ f''16 d''16] | \break
    e''8[ r8 e''32 f''32 g''32 a''32] b''8 |
    \tuplet 3/2 { c'''16[ b''16 a''16] } \tuplet 3/2 { g''16[ f''16 e''16] } \tuplet 3/2 { d''16[ c''16 b'16] } \tuplet 3/2 { a'16[ g'16 f'16] } |
    \voiceOne e'4~ e'16[ f'16 g'16 a'16] |
    \oneVoice <e' g' c''>2\fermata \bar "|." |
          }
          \new Voice = "vP1x2" {
    \autoBeamOff
    \voiceTwo g'16[ c''16 e'16 c''16] g'16[ c''16 e'16 c''16] |
    f'16[ b'16 g'16 b'16] f'16[ b'16 g'16 b'16] |
    \oneVoice s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    \voiceTwo c'4 r4 |
    \oneVoice s1*1/2 |
          }
        >>
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major c16[ g16 e16 g16] c16[ g16 e16 g16] |
    g,16[ d16 f16 d16] g,16[ d16 f16 d16] |
    e16[ c'16 g16 c'16] f16[ c'16 a16 c'16] |
    g,16[ d16 f16 d16] g,8 r8 |
    c8[ r16 c16] d8[ r16 d16] |
    \tuplet 3/2 { g,16[ b,16 d16] } \tuplet 3/2 { g16[ d16 b,16] } g,4 |
    <g, f>4 <g, f>4 |
    c8[ r8 d8] r8 |
    <c e g>4 <c e g>4 |
    g,8[ g8] g,8[ g8] |
    c4 c,4 |
    <c, c>2\fermata |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
