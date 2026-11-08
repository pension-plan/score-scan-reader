\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Light of Morning"
  subtitle = "SATB"
  poet = "Words: coverage suite (2026)"
  composer = "Coverage suite (2026)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  ragged-bottom = ##t
  ragged-last-bottom = ##t
  top-margin = 14\mm
  bottom-margin = 14\mm
  left-margin = 18\mm
  right-margin = 16\mm
  indent = 18\mm
  short-indent = 8\mm
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "sa" \with { instrumentName = \markup \center-column { "Soprano" "Alto" } shortInstrumentName = \markup \center-column { "S." "A." } } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Moderato" 4 = 88 \numericTimeSignature \time 4/4 \key d \major \voiceOne \stemUp fis'4\mf a'4 b'4 a'4 |
    d''4 cis''4 b'2 |
    a'4 b'8[( cis''8]) d''4 a'4 |
    g'4 fis'4 e'2\fermata |
    \break fis'4\p g'4 a'4 d''4 |
    cis''4 b'4 a'2 |
    b'4\< a'4 g'4 fis'4 |
    e'4\! e'4 d'2\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo \stemDown d'4 d'4 d'4 d'4 |
    d'4 e'4 g'2 |
    fis'4 g'8[( e'8]) fis'4 fis'4 |
    e'4 d'4 cis'2\fermata |
    d'4 b4 d'4 d'4 |
    e'4 g'4 fis'2 |
    d'4 d'4 b4 d'4 |
    b4 cis'4 a2\fermata |
          }
        >>
      }
      \new Lyrics = "lyrsax1" \lyricsto "vSx1" { 
      "Light" "of" "morn" -- "ing," "bright" "and" "clear," "bring" "the" __ _ "wak" -- "ing"
      "world" "to" "cheer;" "let" "the" "val" -- "leys" "and" "the" "hills" "sing" "with"
      "all" "the" "run" -- "ning" "rills."
      }
      \new Staff = "tb" \with { instrumentName = \markup \center-column { "Tenor" "Bass" } shortInstrumentName = \markup \center-column { "T." "B." } } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key d \major \voiceOne \stemUp a4\mf fis4 g4 fis4 |
    fis4 a4 d'2 |
    d'4 d'8[( a8]) a4 d'4 |
    b4 a4 a2\fermata |
    a4\p g4 fis4 fis4 |
    a4 d'4 d'2 |
    b4 fis4 g4 a4 |
    g4 g4 fis2\fermata |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo \stemDown d4 d4 g,4 d4 |
    b,4 a,4 g,2 |
    d4 g,8[( a,8]) d4 d4 |
    e4 fis4 a2\fermata |
    d4 e4 d4 b,4 |
    a,4 g,4 d2 |
    g,4 d4 e4 d4 |
    e4 a,4 d2\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
