\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Amazing Grace"
  poet = "John Newton, 1779"
  composer = "NEW BRITAIN  C.M."
  arranger = "American folk melody, 1829"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 0
  system-count = 4
  system-system-spacing.basic-distance = #16
  top-margin = 15\mm
  left-margin = 16\mm
  right-margin = 16\mm
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \time 3/4 \key g \major \partial 1*1/4 \voiceOne d'4 |
    g'2 b'8( g'8) |
    b'2 a'4 |
    g'2 e'4 |
    d'2 d'4 |
    g'2 b'8( g'8) |
    b'2 a'4 |
    d''2.~ |
    d''2 b'4 |
    d''4.( b'8) d''8( b'8) |
    g'2 d'4 |
    e'4.( g'8) g'8( e'8) |
    d'2 d'4 |
    g'2 b'8( g'8) |
    b'2 a'4 |
    g'2.~
    \set Timing.measurePosition = #(ly:make-moment 1/4) g'2 \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo b4 |
    b2 b8~( b8) |
    b2 d'4 |
    e'2 c'4 |
    b2 b4 |
    b2 b8~( b8) |
    b2 d'4 |
    d'2.~ |
    d'2 d'4 |
    d'4.~( d'8) d'8~( d'8) |
    e'2 b4 |
    b4.~( b8) c'8~( c'8) |
    b2 a4 |
    b2 b8~( b8) |
    d'2 c'4 |
    b2.~
    b2 |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "A" -- "ma" -- "zing" __ _ "grace!" "how" "sweet" "the" "sound" "That" "saved" "a" __
      _ "wretch" "like" "me!" __ _ "I" "once" __ _ "was" __ _ "lost," "but"
      "now" __ _ "am" __ _ "found," "Was" "blind," "but" __ _ "now" "I" "see." __
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "'Twas" "grace" "that" __ _ "taught" "my" "heart" "to" "fear," "And" "grace" "my" __
      _ "fears" "re" -- "lieved;" __ _ "How" "pre" -- _ "cious" __ _ "did" "that"
      "grace" __ _ "ap" -- _ "pear" "The" "hour" "I" __ _ "first" "be" -- "lieved!" __
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "3." 
      "Through" "ma" -- "ny" __ _ "dan" -- "gers," "toils," "and" "snares," "I" "have" "al" --
      _ "rea" -- "dy" "come;" __ _ "'Tis" "grace" __ _ "hath" __ _ "brought" "me"
      "safe" __ _ "thus" __ _ "far," "And" "grace" "will" __ _ "lead" "me" "home." __
      }
      \new Staff = "lower" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key g \major \voiceOne g4 |
    g2 g8~( g8) |
    g2 fis4 |
    g2 g4 |
    g2 g4 |
    g2 g8~( g8) |
    g2 fis4 |
    fis2.~ |
    fis2 g4 |
    b4.~( b8) g8~( g8) |
    g2 g4 |
    g4.~( g8) e8~( e8) |
    g2 fis4 |
    g2 g8~( g8) |
    g2 fis4 |
    d2.~
    d2 |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo g4 |
    g2 g8~( g8) |
    e2 d4 |
    c2 c4 |
    g,2 b,4 |
    g,2 e,8~( e,8) |
    e,2 d4 |
    d2.~ |
    d2 g,4 |
    g,4.~( g,8) b,8~( b,8) |
    c2 g4 |
    e4.~( e8) c8~( c8) |
    g,2 d4 |
    g,2 e,8~( e,8) |
    d2 d4 |
    g,2.~
    g,2 |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
