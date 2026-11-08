\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "All Things Bright and Beautiful"
  poet = "Cecil Frances Alexander, 1848"
  composer = "for SAB choir"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  top-margin = 18\mm
  indent = 22\mm
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "Soprano" "Alto" } shortInstrumentName = \markup \center-column { "S." "A." } } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \numericTimeSignature \time 4/4 \key d \major \voiceOne a'4 a'4 d''4 a'4 |
    b'4 a'4 fis'2 |
    g'4 a'4 b'4 g'4 |
    \oneVoice a'4 fis'2. |
    \voiceOne a'4 b'4 cis''4 d''4 |
    b'4 a'4 g'2 |
    b'4 a'4 g'4 b'4 |
    cis''4 d''2. \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo fis'4 fis'4 fis'4 e'4 |
    d'4 cis'4 d'2 |
    d'4 e'4 d'4 e'4 |
    \voiceOne \change Staff = "lower" cis'4 a2. |
    \voiceTwo \change Staff = "upper" fis'4 g'4 e'4 d'4 |
    d'4 cis'4 e'2 |
    d'4 d'4 e'4 g'4 |
    a'4 fis'2. |
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
      \new Staff = "lower" \with { instrumentName = "Baritone" shortInstrumentName = "Bar." } { \clef "bass"
          \new Voice = "vBarx1" {
    \autoBeamOff
    \key d \major d4 d4 b,4 cis4 |
    g4 a4 d2 |
    b,4 cis4 d4 cis4 |
    \voiceTwo a,4 d2. |
    \oneVoice d4 g4 a4 b4 |
    g4 a4 e2 |
    g4 fis4 e4 d4 |
    a,4 d2. |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
