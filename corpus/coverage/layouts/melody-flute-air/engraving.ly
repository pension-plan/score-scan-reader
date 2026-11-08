\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Air for Flute"
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
  indent = 16\mm
  system-system-spacing.basic-distance = #14
}
\score {
  <<
    \new Staff = "fl" \with { instrumentName = "Flute" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Allegretto" 4 = 96 \time 2/4 \key d \major \stemDown a'8\mf[( d''8] fis''8[ a''8] |
    g''8[ fis''8] e''8[ d''8]) |
    cis''8-.[ d''8-.] e''8-.[ fis''8-.] |
    e''4\trill d''8 r8 |
    \break a''4->\f( g''8[ fis''8]) |
    e''16[( fis''16 g''16 e''16] cis''8[) a'8-.] |
    \tuplet 3/2 { b'8[( cis''8 d''8] } e''8[ fis''8]) |
    d''4 \breathe r4 |
    \break \mark \markup { \box \bold "A" } fis''8.\p[( g''16] a''8[ fis''8]) |
    e''8.[( fis''16] g''8[ e''8]) |
    d''8--[ cis''8--] \stemUp b'8--[ ais'8--] |
    \stemDown b'2~\< |
    \break b'8\![ cis''8\mp]( d''8[ e''8] |
    f''8[ e''8] d''8[ c''8]) |
    \stemUp b'8\>[ a'8]( g'8[ e'8]) |
    d'2\fermata\! |
        }
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
