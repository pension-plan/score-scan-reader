\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Who Has Seen the Wind?"
  poet = "Christina Rossetti (Sing-Song, 1872)"
  composer = "OMR challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Voice" } { \clef "treble"
        \new Voice = "vP1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 3/4 \key f \major \partial 1*1/8 \tempo "Gently" c'8 |
    f'4. g'8 a'4 |
    c''2.~ |
    c''4 r8 a'8 bes'8. a'16 |
    g'4.. f'16( f'4~ | \break
    \numericTimeSignature \time 4/4 f'2..) r8 |
    r8 c'8 f'8. g'16 a'4 bes'4 |
    d''4.. c''16( c''8 a'8) r4 | \break
    \time 3/4 r8 c'8 f'4 g'8. a'16 |
    bes'8..( a'32) g'2~ |
    g'2.~ | \pageBreak
    g'4 r4 r8 c'8 |
    \time 6/8 f'8 g'8 a'8 c''4.~ |
    c''4. r8 a'8 bes'8 |
    a'4 g'8 f'4.~ | \break
    f'4. r4 c'8 |
    f'8 g'8 a'8 bes'8. a'16 bes'8 |
    d''4.~ d''8( c''8 bes'8) |
    \time 9/8 r4 c'8 f'4 g'8 a'8. bes'16[( g'8]) | \break
    \time 3/4 f'2.~ |
    f'2~ f'8\fermata \bar "|."
        }
    }
    \new Lyrics = "LvP1x1x1" \lyricsto "vP1x1" { 
      "Who" "has" "seen" "the" "wind?" __ _ "Nei" -- "ther" "I" "nor" "you:" __ _
      _ "But" "when" "the" "leaves" "hang" "trem" -- "bling," __ _ _ "The" "wind"
      "is" "pass" -- "ing" __ _ "through." __ _ _ "Who" "has" "seen" "the" "wind?" __
      _ "Nei" -- "ther" "you" "nor" "I:" __ _ "But" "when" "the" "trees" "bow"
      "down" "their" "heads," __ _ _ _ "The" "wind" "is" "pass" -- "ing" __ _
      "by." __
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
