\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Variation"
  subtitle = "for piano - 1 page"
  composer = "coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  top-margin = 10\mm
  bottom-margin = 10\mm
  left-margin = 14\mm
  right-margin = 14\mm
  ragged-last-bottom = ##f
  print-page-number = ##t
  print-first-page-number = ##f
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
        <<
          \new Voice = "vPx1" {
    \autoLineBreaksOff \autoPageBreaksOff \mark \markup { \box \bold "1" } \tempo "Var. 1  Maestoso" 4 = 66 \defaultTimeSignature \time 4/4 \key c \major \oneVoice <c'' e'' g''>4--\mf <c'' e'' g''>4 <c'' e'' g''>2 |
    <d'' fis'' a''>4-- <d'' fis'' a''>4 <d'' fis'' a''>2 |
    <g' b' d''>4-- <g'' b'' d'''>4 <g' b' d''>2 |
    <c'' e'' g''>1\fermata |
    \break <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <e'' g'' b''>4-- <e'' g'' b''>4 <e'' g'' b''>2 |
    <f'' a'' c'''>4-- <f'' a'' c'''>4 <f'' a'' c'''>2 |
    <g' b' d''>1\fermata |
    \break <d'' f'' a''>4-- <d'' f'' a''>4 <d'' f'' a''>2 |
    <g' b' d''>4-- <g'' b'' d'''>4 <g' b' d''>2 |
    <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <c'' e'' g''>1\fermata |
    \break <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <a' cis'' e''>4-- <a' cis'' e''>4 <a' cis'' e''>2 |
    <g' b' d''>4-- <g'' b'' d'''>4 <g' b' d''>2 |
    <c'' e'' g''>1\fermata \bar "|." |
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
    s1 |
    s1 |
    s1 |
    s1 |
          }
        >>
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \key c \major <c, c>2 g,2 |
    <d, d>2 a,2 |
    <g, g>2 d2 |
    <c, c>1\fermata |
    <c, c>2 g,2 |
    <e, e>2 b,2 |
    <f, f>2 c2 |
    <g, g>1\fermata |
    <d, d>2 a,2 |
    <g, g>2 d2 |
    <c, c>2 g,2 |
    <c, c>1\fermata |
    <c, c>2 g,2 |
    <a, a>2 e2 |
    <g, g>2 d2 |
    <c, c>1\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
