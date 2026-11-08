\version "2.24.0"
#(set-global-staff-size 17)
\header {
  title = "Minuet and Trio"
  subtitle = "for violin, violoncello and piano"
  subsubtitle = "Piano score"
  composer = "Layout-challenge corpus (2026)"
  copyright = "Dedicated to the public domain (CC0 1.0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  left-margin = 24\mm
  indent = 22\mm
  short-indent = 0
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #12
  top-margin = 12\mm
  bottom-margin = 12\mm
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "vn" \with { instrumentName = "Violin" \magnifyStaff #3/4 } { \clef "treble"
          \new Voice = "vVNx1" {
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Tempo di Menuetto" 4 = 120 \textMark \markup { \bold "Menuetto" } \time 3/4 \key g \major d''2\p b'4 |
    c''4 a'4 fis'4 |
    g'8( a'8 b'8 c''8) d''4 |
    e''4( d''2) |
    \break b'4 d''4 g''4 |
    e''4 c''4 g'4 |
    fis'8( g'8 a'8 b'8 c''8 a'8) |
    g'2 r4 \bar ":|.|:" |
    \break a'4\f d''4 fis''4 |
    e''4 cis''4 a'4 |
    d''8( e''8 fis''8 g''8) a''4 |
    c''4 a'4 fis'4 |
    \break g'4\p b'4 d''4 |
    e''4 g''4 e''4 |
    d''8( c''8 b'8 a'8 c''8 a'8) |
    g'2. \textEndMark \markup { \bold \italic "Fine" } \bar ":|.|:" |
    \pageBreak \textMark \markup { \bold "Trio" } \key c \major e''2\mf^\markup { \italic "dolce" } g''4 |
    f''4 d''4 b'4 |
    c''4 e''4 g''4 |
    d''2. |
    \break a''4 f''4 c''4 |
    g''4 e''4 c''4 |
    d''8( e''8 f''8 d''8 b'8 g'8) |
    c''2 r4 \bar ":|.|:" |
    \break b'4 d''4 g''4 |
    g''4 e''4 c''4 |
    fis''4 d''4 c''4 |
    d''2 r4 |
    \break e''4\< g''4 c'''4 |
    a''4\!\f f''4 c''4 |
    b'8( c''8 d''8 f''8 e''8 d''8) |
    c''2. \textEndMark \markup { \bold \italic "Menuetto D.C. al Fine" } \bar ":|." |
          }
      }
      \new Staff = "vc" \with { instrumentName = "Violoncello" \magnifyStaff #3/4 } { \clef "bass"
          \new Voice = "vVCx1" {
    \key g \major g,4\p b,4 d4 |
    fis,2 d,4 |
    g,4 b,4 g,4 |
    d,4 fis,4 a,4 |
    g,2. |
    c4 e4 c4 |
    d4 c4 d,4 |
    g,2 r4 |
    d4\f fis4 a4 |
    a,4 cis4 e4 |
    d2. |
    c2 a,4 |
    b,4\p d4 g4 |
    c4 e4 g4 |
    d2 d,4 |
    g,2. |
    \key c \major c2.\mf |
    b,2 g,4 |
    c4 e4 g4 |
    g,2. |
    f,4 a,4 c4 |
    e,4 g,4 c4 |
    g,2 f,4 |
    c2 r4 |
    g,4 b,4 d4 |
    c4 e4 g4 |
    fis,2 d,4 |
    g,2 r4 |
    c4\< e4 g4 |
    f,4\!\f a,4 c4 |
    g,4 f,4 g,4 |
    c2. |
          }
      }
    >>
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vPx1" {
    \key g \major r4 <d' g' b'>4-.\p <d' g' b'>4-. |
    r4 <d' fis' a'>4-. <d' fis' a'>4-. |
    r4 <d' g' b'>4-. <d' g' b'>4-. |
    r4 <d' fis' a'>4-. <d' fis' a'>4-. |
    r4 <d' g' b'>4-. <d' g' b'>4-. |
    r4 <e' g' c''>4-. <e' g' c''>4-. |
    r4 <d' fis' a'>4-. <d' fis' a'>4-. |
    r4 <d' g' b'>4-. <d' g' b'>4-. |
    r4 <d' fis' a'>4-.\f <d' fis' a'>4-. |
    r4 <e' g' a'>4-. <e' g' a'>4-. |
    r4 <d' fis' a'>4-. <d' fis' a'>4-. |
    r4 <d' fis' a'>4-. <d' fis' a'>4-. |
    r4 <d' g' b'>4-.\p <d' g' b'>4-. |
    r4 <e' g' c''>4-. <e' g' c''>4-. |
    r4 <d' fis' a'>4-. <d' fis' a'>4-. |
    r4 <d' g' b'>4-. <d' g' b'>4-. |
    \key c \major r4 <e' g' c''>4-.\mf <e' g' c''>4-. |
    r4 <f' g' b'>4-. <f' g' b'>4-. |
    r4 <e' g' c''>4-. <e' g' c''>4-. |
    r4 <d' g' b'>4-. <d' g' b'>4-. |
    r4 <f' a' c''>4-. <f' a' c''>4-. |
    r4 <e' g' c''>4-. <e' g' c''>4-. |
    r4 <f' g' b'>4-. <f' g' b'>4-. |
    r4 <e' g' c''>4-. <e' g' c''>4-. |
    r4 <d' g' b'>4-.\mf <d' g' b'>4-. |
    r4 <e' g' c''>4-. <e' g' c''>4-. |
    r4 <d' fis' a'>4-. <d' fis' a'>4-. |
    r4 <d' g' b'>4-. <d' g' b'>4-. |
    r4 <e' g' c''>4-. <e' g' c''>4-. |
    r4 <f' a' c''>4-. <f' a' c''>4-. |
    r4 <f' g' b'>4-. <f' g' b'>4-. |
    r4 <e' g' c''>4-. <e' g' c''>4-. |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \key g \major <g,, g,>4 r4 r4 |
    <d, d>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <d, d>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <c, c>4 r4 r4 |
    <d, d>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <d, d>4 r4 r4 |
    <a,, a,>4 r4 r4 |
    <d, d>4 r4 r4 |
    <d, d>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <c, c>4 r4 r4 |
    <d, d>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    \key c \major <c, c>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <c, c>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <f, f>4 r4 r4 |
    <c, c>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <c, c>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <c, c>4 r4 r4 |
    <d, d>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <c, c>4 r4 r4 |
    <f, f>4 r4 r4 |
    <g,, g,>4 r4 r4 |
    <c, c>4 r4 r4 |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
