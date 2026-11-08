\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Calon Lân"
  subtitle = "quodlibet: four lines of the hymn sung at once"
  poet = "Geiriau: Daniel James (Gwyrosydd)"
  composer = "Cerddoriaeth: anon. (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "P052"
  indent = 16\mm
  ragged-last = ##f
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "Soprano" "Alto" } } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \numericTimeSignature \time 4/4 \key g \major \voiceOne d''4. c''8 b'2 |
    c''4 e''4 d''4. a'8 |
    b'2 r2 |
    r4 a'4 a'4 d''4 \break |
    d''4. b'8 g'2 |
    c''2( a'2) |
    e''1 |
    d''1\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \voiceTwo r4 g'4 g'4 g'4 |
    g'4 e'4 fis'4 fis'4 |
    g'4 e'2 e'4 |
    fis'2 fis'4 a'4 |
    g'2 e'2~ |
    e'2 fis'2 |
    g'1 |
    g'1\fermata |
          }
        >>
      }
      \new Lyrics \with { alignAboveContext = "upper" } \lyricsto "vSx1" { 
      "Ca" -- "lon" "lân" "yn" "llawn" "da" -- "io" -- "ni," "te" -- "cach" "yw" "na'r"
      "li" -- "li" "dlos:" __ _ "A" -- "men."
      }
      \new Lyrics \lyricsto "vAx1" { 
      "dim" "ond" "ca" -- "lon" "lân" "all" "ga" -- "nu," "ca" -- "nu'r" "dydd" "a"
      "cha" -- "nu'r" "nos." __ _ _ "A" -- "men."
      }
      \new Staff = "lower" \with { instrumentName = \markup \center-column { "Tenor" "Bass" } } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key g \major \voiceOne b4 d'8 d'8 d'4 b4 |
    c'4 c'4 a2 |
    b4 b8 b8 g2 |
    a4 a4 a2( |
    b2 g2 |
    a1) |
    c'1 |
    b1\fermata |
          }
          \new Voice = "vBx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \voiceTwo g,2 b,4 g,4 |
    c2 d2 |
    e4 e4 c2 |
    d4 d4 fis,4 a,4 |
    g,2 e,2 |
    a,2( d2) |
    c1 |
    g,1\fermata |
          }
        >>
      }
      \new Lyrics \with { alignAboveContext = "lower" } \lyricsto "vTx1" { 
      "Nid" "wy'n" "go" -- "fyn" "by" -- "wyd" "moe" -- "thus," "aur" "y" "byd" "na'i"
      "ber" -- "lau" "mân:" __ _ _ _ "A" -- "men."
      }
      \new Lyrics \lyricsto "vBx1" { 
      "go" -- "fyn" "wyf" "am" "ga" -- "lon" "ha" -- "pus," "ca" -- "lon" "o" -- "nest,"
      "ca" -- "lon" "lân." __ _ "A" -- "men."
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
