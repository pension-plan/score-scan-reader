\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Andantino"
  subtitle = "for piano"
  composer = "Corpus composition (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Pagella"
  top-margin = 18\mm
  system-count = 4
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "pu" { \clef "treble"
        <<
          \new Voice = "vPx1" {
    \numericTimeSignature \time 4/4 \key d \major \oneVoice a'4\p( d''4 fis''4 e''4) |
    d''4( cis''8 b'8) a'2 |
    b'4( d''4 g''4 fis''4) |
    e''2 r4 a'4 |
    a'4( d''4 fis''4 a''4) |
    g''4( fis''8 e''8) d''4 b'4 |
    a'4-. d''4-. e''4-. cis''4-. |
    d''2. r4 |
    fis''4\mf( g''8 a''8 g''4 fis''4) |
    e''4( fis''8 g''8 fis''4 e''4) |
    d''4( e''8 fis''8 e''4 d''4) |
    cis''2 a'2 |
    \voiceOne a''2\f( g''4 fis''4) |
    e''2 d''4 cis''4 |
    d''4 fis''4 e''4 cis''4 |
    d''1\fermata \bar "|." |
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
    \voiceTwo d''2 cis''2 |
    b'2 a'4 g'4 |
    fis'4 a'4 g'4 e'4 |
    fis'1 |
          }
        >>
      }
      \new Staff = "pl" { \clef "bass"
          \new Voice = "vPx5" {
    \key d \major d4 <fis a>4 a,4 <fis a>4 |
    d4 <fis a>4 a,4 <fis a>4 |
    g,4 <g b>4 d4 <g b>4 |
    a,4 <e g cis'>4 a,4 r4 |
    d4 <fis a>4 a,4 <fis a>4 |
    g,4 <g b>4 g,4 <g b>4 |
    a,4-. a,4-. a,4-. a,4-. |
    d2. r4 |
    d4 <a d'>4 d4 <a d'>4 |
    a,4 <a cis'>4 a,4 <a cis'>4 |
    b,4 <fis b>4 b,4 <fis b>4 |
    a,2 <e a cis'>2 |
    d2 a,2 |
    g,2 a,2 |
    d2 a,2 |
    <d, d>1\fermata |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
