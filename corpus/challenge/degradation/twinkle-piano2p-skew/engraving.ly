\version "2.24.0"
#(set-global-staff-size 25)
\header {
  title = "Theme and Variation"
  subtitle = "on \"Ah! vous dirai-je, maman\""
  composer = "Corpus composition (CC0)"
  arranger = "Theme: French air, c. 1761"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "C059"
  top-margin = 15\mm
  bottom-margin = 15\mm
  system-count = 6
  systems-per-page = 3
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "pu" { \clef "treble"
        <<
          \new Voice = "vPx1" {
    \numericTimeSignature \time 4/4 \key c \major \oneVoice c''4\mp c''4 g''4 g''4 |
    a''4 a''4 g''2 |
    f''4 f''4 e''4 e''4 |
    d''4 d''4 c''2 |
    g''4 g''4 f''4 f''4 |
    e''4 e''4 d''2 |
    g''4 g''4 f''4 f''4 |
    e''4 e''4 d''2 |
    c''4 c''4 g''4 g''4 |
    a''4 a''4 g''2 |
    f''4 f''4 e''4 e''4 |
    d''4 d''4 c''2 \bar "||" |
    \voiceOne c''8\mf( d''8 c''8 d''8) g''8( a''8 g''8 a''8) |
    a''8( b''8 a''8 b''8) g''2 |
    f''8( g''8 f''8 g''8) e''8( f''8 e''8 f''8) |
    d''8( e''8 d''8 e''8) c''2 |
    g''8( a''8 g''8 a''8) f''8( g''8 f''8 g''8) |
    e''8( f''8 e''8 f''8) d''2 |
    g''8( a''8 g''8 a''8) f''8( g''8 f''8 g''8) |
    e''8( f''8 e''8 f''8) d''2 |
    c''8\f( d''8 c''8 d''8) g''8( a''8 g''8 a''8) |
    a''8( b''8 a''8 b''8) g''2 |
    f''8( g''8 f''8 g''8) e''8( f''8 e''8 fis''8) |
    g''4 d''4 c''2\fermata \bar "|." |
          }
          \new Voice = "vPx2" {
    \oneVoice s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    \voiceTwo e'2 e'2 |
    f'2 e'2 |
    a'2 g'2 |
    f'2 e'2 |
    e'2 d'2 |
    c'2 b2 |
    e'2 d'2 |
    c'2 b2 |
    e'2 e'2 |
    f'2 e'2 |
    a'2 g'4 c''4 |
    f'4 f'4 e'2 |
          }
        >>
      }
      \new Staff = "pl" { \clef "bass"
          \new Voice = "vPx5" {
    \key c \major c2 e2 |
    f2 e2 |
    d2 c2 |
    g,2 c2 |
    e2 d2 |
    c2 g,2 |
    e2 d2 |
    c2 g,2 |
    c2 e2 |
    f2 e2 |
    d2 c2 |
    g,2 c2 |
    c4 g4 e4 g4 |
    f4 a4 e4 g4 |
    d4 a4 c4 g4 |
    g,4 g4 c4 g4 |
    e4 g4 d4 g4 |
    c4 g4 g,4 g4 |
    e4 g4 d4 g4 |
    c4 g4 g,4 g4 |
    c4 g4 e4 g4 |
    f4 a4 e4 g4 |
    d4 a4 c4 a4 |
    g,2 <c, c>2\fermata |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
