\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Song without Words"
  subtitle = "for piano"
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
  indent = 14\mm
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
        <<
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andantino" 4 = 92 \time 3/4 \key e \major \voiceOne \stemUp b'4\p( cis''4 dis''4 |
    e''2 b'4) |
    cis''4( b'4 a'4 |
    gis'2.) |
    \break b'4\mf( e''4 gis''4 |
    fis''2 e''4) |
    dis''4( cis''4 b'4 |
    e''2.\fermata) |
          }
          \new Voice = "vP1x2" {
    \autoBeamOff
    \voiceTwo \stemDown gis'2 fis'4 |
    gis'2 gis'4 |
    e'2 fis'4 |
    e'2 r4 |
    gis'2 b'4 |
    a'2 gis'4 |
    a'4 e'4 dis'4 |
    gis'2.\fermata |
          }
        >>
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key e \major \stemDown e4 <gis b>4 <gis b>4 |
    e4 <gis b>4 <gis b>4 |
    \stemUp a,4 \stemDown <e a>4 <e a>4 |
    e4 <gis b>4 <gis b>4 |
    e4 <gis b>4 <gis b>4 |
    \stemUp b,4 \stemDown <fis a>4 <fis a>4 |
    \stemUp b,4 \stemDown <fis a>4 <fis a>4 |
    \stemUp <e, e>2.\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
