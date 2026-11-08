\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Nun danket alle Gott"
  poet = "Text: Martin Rinkart, 1636"
  composer = "Satz: Challenge-Korpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Pagella"
  top-margin = 20\mm
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "Sopran" "Alt" } shortInstrumentName = \markup \center-column { "S." "A." } } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \autoBeamOff
    \defaultTimeSignature \time 4/4 \key g \major \voiceOne b'4 b'4 a'4 g'4 |
    a'2 g'2 |
    d''4 d''4 c''4 b'4 |
    a'4 g'4 a'2 |
    b'4 c''4 d''4 b'4 |
    c''2 b'2 |
    d''4 c''4 b'4 a'4 |
    g'4 fis'4 g'2 |
    r1 |
    r1 |
    d''4 b'4 c''4 a'4 |
    a'2 g'2\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo g'4 g'4 fis'4 e'4 |
    fis'2 d'2 |
    b'4 b'4 g'4 g'4 |
    a'4 e'4 fis'2 |
    g'4 g'4 g'4 g'4 |
    fis'2 g'2 |
    g'4 g'4 g'4 fis'4 |
    d'4 d'4 d'2 |
    d'4\p e'4 d'4 c'4 |
    b4 a4 b2 |
    g'4\f g'4 g'4 fis'4 |
    fis'2 d'2\fermata |
          }
        >>
      }
      \new Lyrics \lyricmode { 
      "Nun"1*1/4 "dan"1*1/4 -- "ket"1*1/4 "al"1*1/4 -- "le"1*1/2 "Gott"1*1/2 "mit"1*1/4 "Her"1*1/4 -- "zen,"1*1/4 "Mund"1*1/4
      "und"1*1/4 "Hän"1*1/4 -- "den,"1*1/2 "der"1*1/4 "gro"1*1/4 -- "ße"1*1/4 "Din"1*1/4 -- "ge"1*1/2 "tut,"1*1/2 "an"1*1/4
      "uns"1*1/4 "und"1*1/4 "al"1*1/4 -- "len"1*1/4 "En"1*1/4 -- "den."1*1/2 "an"1*1/4 "uns"1*1/4 "und"1*1/4 "al"1*1/4 --
      "len"1*1/4 "En"1*1/4 -- "den."1*1/2 "Nun"1*1/4 "dan"1*1/4 -- "ket"1*1/4 "al"1*1/4 -- "le"1*1/2 "Gott!"1*1/2
      }
      \new Staff = "lower" \with { instrumentName = \markup \center-column { "Tenor" "Bass" } shortInstrumentName = \markup \center-column { "T." "B." } } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key g \major \voiceOne d'4 d'4 d'4 b4 |
    d'2 b2 |
    g4 d'4 e'4 d'4 |
    d'4 b4 d'2 |
    d'4 d'4 d'4 a4 |
    a2 d'2 |
    d'4 e'4 d'4 d'4 |
    b4 a4 b2 |
    b4\p c'4 b4 a4 |
    g4 fis4 g2 |
    d'4\f e'4 e'4 d'4 |
    c'2 b2\fermata |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo g,4 b,4 d4 e4 |
    d2 g,2 |
    g4. fis8 e4 g4 |
    fis4 e4 d2 |
    g4 c4 b,4 e4 |
    d2 g,2 |
    b,4 c4 d4 d4 |
    d4 d4 g,2 |
    r1 |
    r1 |
    b,4 e4 c4 d4 |
    d2 g,2\fermata |
          }
        >>
      }
      \new Lyrics \lyricmode { 
      "Nun"1*1/4 "dan"1*1/4 -- "ket"1*1/4 "al"1*1/4 -- "le"1*1/2 "Gott"1*1/2 "mit"1*3/8 "Her"1*1/8 -- "zen,"1*1/4 "Mund"1*1/4
      "und"1*1/4 "Hän"1*1/4 -- "den,"1*1/2 "der"1*1/4 "gro"1*1/4 -- "ße"1*1/4 "Din"1*1/4 -- "ge"1*1/2 "tut,"1*1/2 "an"1*1/4
      "uns"1*1/4 "und"1*1/4 "al"1*1/4 -- "len"1*1/4 "En"1*1/4 -- "den."1*1/2 "an"1*1/4 "uns"1*1/4 "und"1*1/4 "al"1*1/4 --
      "len"1*1/4 "En"1*1/4 -- "den."1*1/2 "Nun"1*1/4 "dan"1*1/4 -- "ket"1*1/4 "al"1*1/4 -- "le"1*1/2 "Gott!"1*1/2
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
