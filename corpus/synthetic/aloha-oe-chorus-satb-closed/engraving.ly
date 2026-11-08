\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Aloha Oe"
  subtitle = "Chorus"
  composer = "Liliuokalani"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "Liberation Serif"
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \numericTimeSignature \time 4/4 \key g \major \partial 1*3/8 \voiceOne g'8 g'8 fis'8 |
    e'4( g'4) c''8 e'8 e'8 e'8 |
    d'4( g'4) b'4 g'8\p g'8 |
    fis'8 fis'8 fis'8 g'8 a'8 gis'8 a'8 c''8 |
    b'2 g'4 r8 fis'8 |
    e'4 g'4 c''4. e'8 |
    d'8 d'8 g'8 g'8 b'4. g'8 |
    fis'4. g'8 b'8( a'4) fis'8
    \set Timing.measurePosition = #(ly:make-moment 1/4) g'2. \bar "|." |
          }
          \new Voice = "vAx1" {
    \voiceTwo d'8 d'8 d'8 |
    e'2 g'8 e'8 e'8 e'8 |
    d'2 d'4 d'8\p d'8 |
    d'8 d'8 d'8 d'8 d'8 d'8 fis'8 fis'8 |
    g'2 d'4 r8 d'8 |
    e'4 e'4 g'4. e'8 |
    d'8 d'8 d'8 d'8 d'4. d'8 |
    d'4. d'8 d'4. d'8
    d'2. |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "A" -- "lo" -- "ha" "o" -- _ "e," "a" -- "lo" -- "ha" "o" -- _ "e,"
      "E" "ke" "o" -- "na" -- "o" -- "na" "no" -- "ho" "i" -- "ka" "li" -- "po"
      "A" "fond" "em" -- "brace" "a" "ho" -- "i" "a" -- "e" "au," "Un" -- "til"
      "we" "meet" __ _ "a" -- "gain."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "Fare" -- "well" "to" "thee," __ _ _ "fare" -- "well" "to" "thee," __ _ _
      "Thou" __ _ "char" -- "ming" "one" "who" "dwells" "in" "sha" -- "ded" "bow'" -- "rs"
      "One" "fond" "em" -- "brace" __ _ "e'er" "I" __ _ "de" -- "part," "Un" -- "til"
      "we" "meet" __ _ "a" -- "gain."
      }
      \new Staff = "lower" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \set melismaBusyProperties = #'()
    \key g \major \voiceOne b8 b8 b8 |
    <g c'>2 e'8 c'8 c'8 c'8 |
    b2 d'4 b8\p b8 |
    a8 a8 a8 b8 c'8 b8 c'8 e'8 |
    d'2 b4 r8 b8 |
    c'4 c'4 e'4. c'8 |
    b8 b8 b8 b8 d'4. g8 |
    a4. b8 d'8( c'4) a8
    b2. |
          }
          \new Voice = "vBx1" {
    \voiceTwo g8 g8 g,8 |
    c2 c8 c8 c8 c8 |
    g2 g,4 g8\p g8 |
    d8 d8 d8 d8 d8 d8 d8 d8 |
    g2 g,4 r8 g,8 |
    c4 c4 c4. c8 |
    g8 g8 d8 d8 g,4. b,8 |
    d4. d8 d4. d8
    g,2. |
          }
        >>
      }
      \new Lyrics \lyricsto "vTx1" { \set stanza = "1." 
      "A" -- "lo" -- "ha" "o" -- "e," "a" -- "lo" -- "ha" "o" -- "e," "E" "ke"
      "o" -- "na" -- "o" -- "na" "no" -- "ho" "i" -- "ka" "li" -- "po" "A" "fond"
      "em" -- "brace" "a" "ho" -- "i" "a" -- "e" "au," "Un" -- "til" "we" "meet" __
      _ "a" -- "gain."
      }
      \new Lyrics \lyricsto "vTx1" { \set stanza = "2." 
      "Fare" -- "well" "to" "thee," __ _ "fare" -- "well" "to" "thee," __ _ "Thou" __ _
      "char" -- "ming" "one" "who" "dwells" "in" "sha" -- "ded" "bow'" -- "rs" "One" "fond"
      "em" -- "brace" __ _ "e'er" "I" __ _ "de" -- "part," "Un" -- "til" "we" "meet" __
      _ "a" -- "gain."
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
