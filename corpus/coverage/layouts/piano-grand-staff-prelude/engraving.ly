\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Prelude in G"
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
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante" 4 = 76 \numericTimeSignature \time 4/4 \key g \major \stemDown b'4-3\p( d''8[ c''8] b'4 \stemUp a'4 |
    g'4 a'8[ b'8] \stemDown c''4 e''4) |
    d''4.\<( c''8 b'4 \stemUp g'4\!) |
    <fis' a'>2 <d' fis' a'>2\arpeggio |
    \break \stemDown b'8\mf[( c''8] d''8[ e''8] fis''4-4 g''4-5) |
    e''4( d''8[ cis''8] d''2) |
    c''4-.\< b'4-. \stemUp a'4-. g'4-. |
    <fis' a' d''>1\f \bar "||" |
    \break \stemDown g''4\p( fis''16[ e''16 d''16 c''16] b'4 \stemUp a'4) |
    g'8[( a'8] bes'8[ a'8] g'4 f'4) |
    e'4\>( fis'8[ g'8] a'4 \stemDown c''4\!) |
    <b'-1 d''-2 g''-5>1\arpeggio\fermata |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key g \major \stemUp g,8\sustainOn[ d8] \stemDown b8[ d8] \stemUp g,8[ d8] \stemDown b8[ d8\sustainOff] |
    c8\sustainOn[ g8] e'8[ g8] \stemUp a,8[ e8] \stemDown c'8[ e8\sustainOff] |
    d8[ a8] fis'8[ a8] \stemUp g,8[ d8] \stemDown b8[ d8] |
    \stemUp d,2 \stemDown <d c'>2 |
    \stemUp g,4 \stemDown <d g b>4 \stemUp b,4 \stemDown <d g b>4 |
    \stemUp a,4 \stemDown <e g cis'>4 d4 <fis a>4 |
    d4-. e4-. fis4-. g4-. |
    \stemUp d,8[ a,8] \stemDown d8[ fis8] a8[ fis8] \stemUp d8[ a,8] |
    e,8[ b,8] \stemDown e8[ g8] c8[ g8] e8[ c8] |
    \stemUp bes,8[ d8] \stemDown g8[ d8] \stemUp c4 \stemDown d4 |
    \stemUp c4 a,4 \stemDown d4 \stemUp d,4 |
    <g,, g,>1\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
