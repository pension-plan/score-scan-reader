\version "2.24.0"
#(set-global-staff-size 24)
\header {
  title = "Who Has Seen the Wind?"
  poet = "Christina Rossetti, 1872"
  composer = "Melody: corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Bonum"
  indent = 0
  system-count = 4
  top-margin = 20\mm
  system-system-spacing.basic-distance = #22
}
\score {
  <<
    \new Staff = "voice" { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \time 3/4 \key f \major \partial 1*1/4 c'4 |
    f'4 f'4 g'4 |
    a'2 a'4 |
    c''4 bes'4 a'4 |
    g'2 c'4 |
    f'4 g'4 a'4 |
    bes'4 d''4. c''8 |
    a'2 g'4 |
    c''4 bes'4 a'4 |
    g'2( e'4)
    \set Timing.measurePosition = #(ly:make-moment 1/4) f'2 \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "1." 
      "Who" "has" "seen" "the" "wind?" "Nei" -- "ther" "I" "nor" "you:" "But" "when"
      "the" "leaves" "hang" "trem" -- _ "bling," "The" "wind" "is" "pass" -- "ing" __ _
      "through."
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "2." 
      "Who" "has" "seen" "the" "wind?" "Nei" -- "ther" "you" "nor" "I:" "But" "when"
      "the" "trees" "bow" "down" "their" "heads," "The" "wind" "is" "pass" -- "ing" __ _
      "by."
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
