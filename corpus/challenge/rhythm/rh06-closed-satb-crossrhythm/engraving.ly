\version "2.24.0"
#(set-global-staff-size 21)
\header {
  title = "O God, Our Help in Ages Past"
  poet = "Isaac Watts (1719)"
  composer = "OMR challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "Soprano" "Alto" } shortInstrumentName = \markup \center-column { "S." "A." } } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key g \major \partial 1*1/4 \tempo "Moderato" \voiceOne d'4 |
    g'4 a'4 b'4 c''4 |
    d''4. c''8 b'2\fermata |
    b'4 a'8[( g'8]) a'4 b'4 | \break
    a'4 g'2.\fermata |
    r4 d''4 d''4 c''4 |
    b'4 c''4 d''4 e''4 | \break
    d''2.\fermata d''4 |
    c''4 b'4 a'4. g'8 |
    g'2.\fermata \bar "|."
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo b4 |
    \tuplet 3/2 { d'4 e'4 fis'4 } g'4 g'4 |
    fis'8[ g'8 fis'8 e'8] d'2\fermata |
    r4 d'4 \tuplet 3/2 { e'4 d'4 c'4 } |
    d'4~ d'8[ c'8] b2\fermata |
    r2 fis'4 fis'4 |
    g'4 a'8[ b'8] c''8[ b'8 a'8 g'8] |
    fis'2~ fis'4\fermata fis'4 |
    e'8[ fis'8 g'8 e'8] e'4 d'4 |
    b4 d'2\fermata
          }
        >>
      }
      \new Lyrics = "LvSx1x1" \lyricsto "vSx1" { \set stanza = "1." 
      "O" "God," "our" "help" "in" "a" -- "ges" "past," "Our" "hope" __ _ "for"
      "years" "to" "come," "Our" "shel" -- "ter" "from" "the" "storm" -- "y" "blast," "And"
      "our" "e" -- "ter" -- "nal" "home."
      }
      \new Lyrics = "LvSx1x2" \lyricsto "vSx1" { \set stanza = "2." 
      "Un" -- "der" "the" "sha" -- "dow" "of" "thy" "throne" "Thy" "saints" __ _ "have"
      "dwelt" "se" -- "cure;" "Suf" -- "fi" -- "cient" "is" "thine" "arm" "a" -- "lone," "And"
      "our" "de" -- "fence" "is" "sure."
      }
      \new Staff = "lower" \with { instrumentName = \markup \center-column { "Tenor" "Bass" } shortInstrumentName = \markup \center-column { "T." "B." } } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key g \major \voiceOne g4 |
    b4 \tuplet 3/2 { c'8[ b8 a8] } b4 c'4 |
    d'4. e'8 d'2\fermata |
    d'4 \tuplet 3/2 { c'8[ b8 a8] } d'4 d'4 |
    c'4 b4. a8 b4\fermata |
    r4 b4 b4 a4 |
    g4 g4 a4 c'4 |
    b2.\fermata b4 |
    a4 g4 e4 d4 |
    d2.\fermata
          }
          \new Voice = "vBx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \voiceTwo g,4 |
    g,4. fis,8 g,4 a,4 |
    b,4 a,4 g,2\fermata |
    g,2 fis,4 g,4 |
    e,4 d,4 g,2\fermata |
    R1 |
    g,8 g,8 g,4 c8 c8 d4 |
    d4 g,2\fermata g,4 |
    c4 d4 d4 d4 |
    g,2.\fermata
          }
        >>
      }
      \new Lyrics = "LvBx1x1" \lyricsto "vBx1" { 
      "O" "God," "our" "help" "in" "a" -- "ges" "past," "Our" "hope" "for" "years"
      "to" "come," "Our" "shel" -- "ter" "from" "the" "storm" -- "y" "blast," "And" "our"
      "e" -- "ter" -- "nal" "home."
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
