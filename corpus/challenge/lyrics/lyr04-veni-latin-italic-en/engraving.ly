\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Veni, veni, Emmanuel"
  subtitle = "O come, O come, Emmanuel"
  poet = "Latin, 18th c.; tr. J. M. Neale, 1851"
  composer = "Melody: anon. (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 0
  ragged-last = ##f
  system-system-spacing.basic-distance = #14
}
\score {
  <<
    \new Staff = "m" { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \numericTimeSignature \time 4/4 \key e \minor \partial 1*1/4 e'4 |
    g'4 b'4 b'4 b'4 |
    a'8( c''8) b'4 a'2 \break |
    r4 a'4 b'4 g'4 |
    e'4 g'8( a'8) fis'4 e'4 |
    d'2 r4 e'4 \break |
    g'4 b'4 b'4 b'4 |
    a'8( c''8) b'4 a'2 \break |
    r4 a'4 b'4 g'4 |
    e'4 g'8( a'8) fis'4 e'4 |
    d'2 r4 d''4 \break |
    d''2 b'4 b'4 |
    a'4 b'8( c''8) b'4 a'4( |
    g'2.) a'4 \break |
    b'4 g'4 e'4 g'4 |
    a'8( g'8) fis'4 e'2\fermata \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { 
      "Ve" -- "ni," "ve" -- "ni," "Em" -- "ma" -- _ "nu" -- "el," "cap" -- "ti" -- "vum"
      "sol" -- "ve" __ _ "Is" -- "ra" -- "el," "qui" "ge" -- "mit" "in" "ex" -- "si" --
      _ "li" -- "o," "pri" -- "va" -- "tus" "De" -- "i" __ _ "Fi" -- "li" -- "o."
      "Gau" -- "de!" "Gau" -- "de!" "Em" -- "ma" -- _ "nu" -- "el" __ _ "na" -- "sce" --
      "tur" "pro" "te," "Is" -- _ "ra" -- "el."
    }
    \new Lyrics \with { \override LyricText.font-shape = #'italic \override LyricText.font-size = #-1 } \lyricsto "vVx1" { 
      "O" "come," "O" "come," "Em" -- "man" -- _ "u" -- "el," "and" "ran" -- "som"
      "cap" -- "tive" __ _ "Is" -- "ra" -- "el," "that" "mourns" "in" "lone" -- "ly" "ex" --
      _ "ile" "here" "un" -- "til" "the" "Son" "of" __ _ "God" "ap" -- "pear."
      "Re" -- "joice!" "Re" -- "joice!" "Em" -- "man" -- _ "u" -- "el" __ _ "shall" "come"
      "to" "thee," "O" "Is" -- _ "ra" -- "el."
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
