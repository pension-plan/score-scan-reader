\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "All Things Bright and Beautiful"
  subtitle = "SATB, extreme ranges"
  poet = "C. F. Alexander, 1848"
  composer = "challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 16\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #20
  top-margin = 18\mm
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff
    \time 3/4 \key d \major \voiceOne d''4 fis''4 a''4 |
    b''4 a''4 fis''4 |
    a''2 r4 |
    g''4 fis''4 e''4 |
    fis''4 e''2 |
    d''2. |
    \break d''4 fis''4 a''4 |
    d'''4 cis'''4 b''4 |
    a''2 r4 |
    b''4 a''4 g''4 |
    fis''4 e''2 |
    d''2. \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo a4 d'4 fis'4 |
    g'4 d'4 d'4 |
    e'2 r4 |
    e'4 d'4 cis'4 |
    d'4 cis'2 |
    d'2. |
    fis'4 d''4 cis''4 |
    b'4 a'4 fis'4 |
    cis''2 r4 |
    d''4 d''4 b'4 |
    d''4 cis''2 |
    a'2. |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "All" "things" "bright" "and" "beau" -- "ti" -- "ful," "All" "crea" -- "tures" "great" "and"
      "small," "All" "things" "wise" "and" "won" -- "der" -- "ful," "The" "Lord" "God" "made"
      "them" "all."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "Each" "lit" -- "tle" "flower" "that" "o" -- "pens," "Each" "lit" -- "tle" "bird" "that"
      "sings," "He" "made" "their" "glow" -- "ing" "col" -- "ours," "He" "made" "their" "ti" --
      "ny" "wings."
      }
      \new Staff = "lower" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key d \major \voiceOne fis4 a4 d'4 |
    d'4 a4 b4 |
    cis'2 r4 |
    b4 a4 a4 |
    a4 g2 |
    fis2. |
    d'4 a'4 a'4 |
    g'4 e'4 d'4 |
    e'2 r4 |
    g'4 a'4 e'4 |
    fis'4 g'2 |
    fis'2. |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo d,4 fis,4 a,4 |
    g,4 fis,4 b,,4 |
    a,,2 r4 |
    e,4 fis,4 a,,4 |
    d,4 a,,2 |
    d,2. |
    b,,4 d,4 fis,4 |
    g,4 a,4 b,4 |
    a,2 r4 |
    g,4 fis,4 e,4 |
    a,,4 a,,2 |
    d,2. |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
