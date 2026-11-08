\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Left-Hand Silences"
  subtitle = "rests in both hands of a grand staff (piano)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "stP1s1" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \tempo "Andante" c''4 e''4 g''4 c'''4 |
    d''2 b'2 |
    c''1 |
    R1 | \break
    e''4 d''4 c''4 b'4 |
    a'2 r2 |
    g'4. r8 g'4 r4 |
    e''2 d''2 | \break
    \time 3/4 c''2 r4 |
    f''4 e''4 d''4 |
    e''2. | \break
    d''4 r4 b'4 |
    \numericTimeSignature \time 4/4 R1\fermata |
    <e' g' c''>1\fermata \bar "|." |
          }
      }
      \new Staff = "stP1s2" { \clef "bass"
        <<
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major \oneVoice c4 r4 g,4 r4 |
    r8 g,8 r8 d8 r8 g8 r4 |
    r16 c16[ e16 g16] r4 r16 g,16[ b,16 d16] r4 |
    c2 g,2 |
    R1 |
    r2 f,2 |
    r4. g,8 r4. g,8 |
    r32 c32 r16 r8 r4 r32 g,32 r16 r8 r4 |
    r8. c16 r8. e16 r8. g16 |
    R2. |
    \voiceOne e4 a4\rest g4 |
    a4\rest f4 a4\rest |
    \oneVoice R1\fermata |
    <c, c>1\fermata |
          }
          \new Voice = "vP1x6" {
    \autoBeamOff
    \oneVoice s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1*3/4 |
    s1*3/4 |
    \voiceTwo g,4\rest c4 g,4\rest |
    d2 g,4\rest |
    \oneVoice s1 |
    s1 |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
