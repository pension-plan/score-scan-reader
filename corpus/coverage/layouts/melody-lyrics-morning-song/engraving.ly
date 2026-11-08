\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Morning Song"
  poet = "Words: coverage suite (2026)"
  composer = "Coverage suite (2026)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  ragged-bottom = ##t
  ragged-last-bottom = ##t
  top-margin = 14\mm
  bottom-margin = 14\mm
  left-margin = 18\mm
  right-margin = 16\mm
  indent = 0
  system-system-spacing.basic-distance = #15
}
\score {
  <<
    \new Staff = "v" { \clef "treble"
        \new Voice = "vP1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Gently" 4 = 84 \time 3/4 \key f \major \partial 1*1/4 \stemUp c'4\mp |
    f'4 g'4 a'4 |
    \stemDown bes'4 \stemUp a'8[( g'8]) f'4 |
    g'2.~ |
    g'4 r4 c'4 |
    \break f'4\< a'4 \stemDown c''4 |
    d''4\! c''8[( bes'8]) \stemUp a'4 |
    g'2. \breathe |
    r2 \stemDown c''4\mf |
    \break \stemUp a'4 \stemDown bes'4 c''4 |
    d''4 c''8[( bes'8]) \stemUp a'4 |
    g'2.~ |
    g'4 r4 c'4\p |
    \break f'4 g'4 a'4 |
    \stemDown c''4\> \stemUp a'4 g'8[( a'8]) |
    f'2.~ |
    f'2\! r4 |
        }
    }
    \new Lyrics = "lyrvx1" \lyricsto "vP1x1" { 
      "The" "morn" -- "ing" "light" "is" "on" __ _ "the" "hill," __ "the" "riv" -- "er"
      "runs" "so" "clear" __ _ "and" "still;" "come" "walk" "with" "me" "a" -- "long" __
      _ "the" "way," __ "and" "sing" "the" "sun" -- "rise" "in" -- "to" __ _ "day." __
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
