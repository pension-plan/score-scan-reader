\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "The Tyger"
  poet = "William Blake (Songs of Experience, 1794)"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Voice" } { \clef "treble"
        \new Voice = "vP1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 3/4 \key f \major \partial 1*1/4 \tempo "Gently" c'4 |
    f'4. g'8 a'4 |
    c''2~ c''8 a'8 |
    bes'4 a'4 g'4 |
    f'2.~ | \break
    \time 6/8 f'4 r8 a'8[ bes'8 c''8] |
    d''4. c''4 a'8 |
    \time 2/4 bes'8[ a'8] g'8[ f'8] | \break
    g'4 c'4 |
    \time 3/4 f'4. g'8 a'4 |
    c''4 bes'4 g'4~ | \break
    g'4 e'4 c'4 |
    f'2 \bar "|."
        }
    }
    \new Lyrics = "LvP1x1x1" \lyricsto "vP1x1" { 
      "Ty" -- "ger" "Ty" -- "ger," "burn" -- _ "ing" "bright," "In" "the" "for" -- _
      "ests" "of" "the" "night;" "What" "im" -- "mor" -- "tal" "hand" __ _ _ "or"
      "eye," "Could" "frame" "thy" "fear" -- "ful" __ _ "sym" -- "me" -- "try?"
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
