\version "2.24.0"
#(set-global-staff-size 24)
\header {
  title = "Elegy"
  subtitle = "for violoncello solo"
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
  indent = 22\mm
  short-indent = 8\mm
  system-system-spacing.basic-distance = #20
  print-page-number = ##t
  print-first-page-number = ##f
}
\score {
  <<
    \new Staff = "vc" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Lento cantabile" 4 = 60 \time 3/4 \key g \minor \stemUp g,4\p( a,4 bes,4 |
    c4 \stemDown d4 ees4) |
    d4.( \stemUp c8 bes,8[ a,8]) |
    g,2 r4 |
    \break \stemDown d4\mf( fis4 g4 |
    a4 bes4 c'4) |
    d'2.~ |
    d'2 r4 |
    \pageBreak \clef "tenor" f'4\f( ees'8[ d'8] c'8[ bes8]) |
    a4( bes4 c'4) |
    d'4-> c'4-> bes4-> |
    a2.\> |
    \break \clef "bass" g4\!\p( fis4 g4) |
    ees4( d4 \stemUp c4) |
    \stemDown d4-- \stemUp d,4-- r4 |
    g,2.\fermata |
        }
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
