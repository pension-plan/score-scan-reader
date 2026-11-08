\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Joyful, Joyful, We Adore Thee"
  poet = "Henry van Dyke, 1907"
  composer = "HYMN TO JOY  87.87 D"
  arranger = "Melody: L. van Beethoven, 1824"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Termes"
  indent = 0
  system-system-spacing.basic-distance = #14
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \numericTimeSignature \time 4/4 \key g \major \voiceOne b'4 b'4 c''4 d''4 |
    d''4 c''4 b'4 a'4 |
    g'4 g'4 a'4 b'4 |
    b'4. a'8 a'2 |
    b'4 b'4 c''4 d''4 |
    d''4 c''4 b'4 a'4 |
    g'4 g'4 a'4 b'4 |
    a'4. g'8 g'2 |
    a'4 a'4 b'4 g'4 |
    a'4 b'8( c''8) b'4 g'4 |
    a'4 b'8( c''8) b'4 a'4 |
    g'4 a'4 d'2 |
    b'4 b'4 c''4 d''4 |
    d''4 c''4 b'4 a'4 |
    g'4 g'4 a'4 b'4 |
    a'4. g'8 g'2 \bar "|." |
          }
          \new Voice = "vAx1" {
    \voiceTwo d'4 e'4 e'4 g'4 |
    fis'4 fis'4 g'4 fis'4 |
    e'4 e'4 fis'4 g'4 |
    g'4. fis'8 fis'2 |
    d'4 e'4 e'4 g'4 |
    fis'4 fis'4 d'4 d'4 |
    b4 e'4 d'4 d'4 |
    c'4. b8 b2 |
    d'4 d'4 d'4 e'4 |
    fis'4 g'8~( g'8) g'4 g'4 |
    fis'4 e'8~( e'8) d'4 d'4 |
    e'4 cis'4 d'2 |
    d'4 e'4 e'4 g'4 |
    fis'4 fis'4 d'4 d'4 |
    b4 e'4 d'4 d'4 |
    c'4. b8 b2 |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "Joy" -- "ful," "joy" -- "ful," "we" "a" -- "dore" "thee," "God" "of" "glo" -- "ry,"
      "Lord" "of" "love;" "Hearts" "un" -- "fold" "like" "flowers" "be" -- "fore" "thee," "O" --
      "pening" "to" "the" "sun" "a" -- "bove." "Melt" "the" "clouds" "of" "sin" "and" __
      _ "sad" -- "ness;" "Drive" "the" __ _ "dark" "of" "doubt" "a" -- "way;" "Giv" --
      "er" "of" "im" -- "mor" -- "tal" "glad" -- "ness," "Fill" "us" "with" "the" "light"
      "of" "day!"
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "All" "thy" "works" "with" "joy" "sur" -- "round" "thee," "Earth" "and" "heaven" "re" --
      "flect" "thy" "rays," "Stars" "and" "an" -- "gels" "sing" "a" -- "round" "thee," "Cen" --
      "ter" "of" "un" -- "bro" -- "ken" "praise." "Field" "and" "for" -- "est," "vale" "and" __
      _ "moun" -- "tain," "Flower" -- "y" __ _ "mead" -- "ow," "flash" -- "ing" "sea," "Sing" --
      "ing" "bird" "and" "flow" -- "ing" "foun" -- "tain" "Call" "us" "to" "re" -- "joice"
      "in" "thee."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "3." 
      "Mor" -- "tals," "join" "the" "hap" -- "py" "cho" -- "rus" "Which" "the" "morn" -- "ing"
      "stars" "be" -- "gan;" "Fa" -- "ther" "love" "is" "reign" -- "ing" "o'er" "us," "Broth" --
      "er" "love" "binds" "man" "to" "man." "Ev" -- "er" "sing" -- "ing," "march" "we" __
      _ "on" -- "ward," "Vic" -- "tors" __ _ "in" "the" "midst" "of" "strife," "Joy" --
      "ful" "mu" -- "sic" "leads" "us" "sun" -- "ward" "In" "the" "tri" -- "umph" "song"
      "of" "life."
      }
      \new Staff = "lower" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \key g \major \voiceOne g4 g4 g4 b4 |
    d'4 d'4 d'4 d'4 |
    b4 c'4 a4 g4 |
    g4. a8 a2 |
    g4 g4 g4 b4 |
    a4 a4 g4 fis4 |
    g4 g4 fis4 g4 |
    fis4. d8 d2 |
    fis4 a4 g4 b4 |
    d'4 d'8~( d'8) d'4 e'4 |
    a4 g8~( g8) g4 fis4 |
    g4 g4 fis2 |
    g4 g4 g4 b4 |
    a4 a4 g4 fis4 |
    g4 g4 fis4 g4 |
    fis4. d8 d2 |
          }
          \new Voice = "vBx1" {
    \voiceTwo g4 e4 c4 g,4 |
    d4 d4 g4 d4 |
    e4 c4 d4 g4 |
    e4. d8 d2 |
    g4 e4 c4 g,4 |
    d4 d4 g,4 d4 |
    e4 c4 d4 g,4 |
    d4. g,8 g,2 |
    d4 fis4 g4 e4 |
    d4 g8~( g8) g4 e4 |
    d4 e,8~( e,8) g,4 d4 |
    c4 a,4 d2 |
    g,4 e4 c4 g,4 |
    d4 d4 g,4 d4 |
    e4 c4 d4 g,4 |
    d4. g,8 g,2 |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
