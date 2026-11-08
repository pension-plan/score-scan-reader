\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "All Things Bright and Beautiful"
  subtitle = "Anthem for SATB choir and piano"
  poet = "Words: Cecil Frances Alexander (1848)"
  composer = "Music: layout-challenge corpus (2026)"
  copyright = "Dedicated to the public domain (CC0 1.0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 20\mm
  short-indent = 9\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #20
  oddHeaderMarkup = \markup \fill-line { \null \unless \on-first-page \italic "All Things Bright and Beautiful" \unless \on-first-page \fromproperty #'page:page-number-string }
  evenHeaderMarkup = \markup \fill-line { \unless \on-first-page \fromproperty #'page:page-number-string \unless \on-first-page \italic "All Things Bright and Beautiful" \null }
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "sa" \with { instrumentName = \markup \center-column { "Soprano" "Alto" } shortInstrumentName = \markup \center-column { "S." "A." } \RemoveAllEmptyStaves } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Allegretto" 4 = 104 \numericTimeSignature \time 4/4 \key g \major \voiceOne R1 |
    R1 |
    R1 |
    R1 |
    \break \segnoMark 1 \mark \markup { \box \bold "A" } g'4\mf b'4 d''4 d''4 |
    e''4 d''4 b'2 |
    c''4 b'4 a'4 g'4 |
    a'4 d'2. |
    \pageBreak g'4 b'4 d''4 g''4 |
    e''4 c''4 a'2 \textEndMark \markup { \line {  \italic "To Coda"  \hspace #0.5 \raise #0.6 \musicglyph "scripts.coda" } } |
    d''4 c''4 b'4 a'4 |
    g'4 g'2. \bar "||" |
    \break R1 |
    R1 \bar ".|:" |
    \pageBreak \mark \markup { \box \bold "B" } b'4\p b'4 a'4 g'4 |
    fis'4 g'4 a'2 |
    g'4 a'4 b'4 c''4 |
    \break d''4 d''2. |
    b'4 b'4 c''4 d''4 |
    e''4 d''4 b'2 |
    \pageBreak c''4 a'4 fis'4 g'4 |
    \set Score.repeatCommands = #'((volta "1.")) a'4 g'2. \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) a'4 d''2. \textEndMark \markup { \bold \italic "D.S. al Coda" } \bar "||" |
    \break \set Score.repeatCommands = #'((volta #f)) \codaMark 1 d''4\f c''4 b'4 a'4 |
    g'2^\markup { \italic "rit." } g'2~ |
    g'1\fermata |
    R1 \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo R1 |
    R1 |
    R1 |
    R1 |
    d'4 g'4 g'4 fis'4 |
    e'4 g'4 g'2 |
    e'4 g'4 fis'4 e'4 |
    cis'4 d'2. |
    d'4 g'4 fis'4 g'4 |
    g'4 a'4 fis'2 |
    g'4 fis'4 g'4 fis'4 |
    e'4 d'2. |
    R1 |
    R1 |
    g'4 g'4 fis'4 e'4 |
    dis'4 e'4 fis'2 |
    d'4 fis'4 e'4 e'4 |
    g'4 fis'2. |
    g'4 g'4 e'4 g'4 |
    g'4 g'4 g'2 |
    e'4 fis'4 d'4 d'4 |
    fis'4 d'2. |
    g'4 fis'2. |
    g'4 e'4 g'4 fis'4 |
    e'2 d'2~ |
    d'1\fermata |
    R1 |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { 
      "All" "things" "bright" "and" "beau" -- "ti" -- "ful," "All" "crea" -- "tures" "great" "and"
      "small," "All" "things" "wise" "and" "won" -- "der" -- "ful," "The" "Lord" "God" "made"
      "them" "all." "Each" "lit" -- "tle" "flower" "that" "o" -- "pens," "Each" "lit" -- "tle"
      "bird" "that" "sings," "He" "made" "their" "glow" -- "ing" "col" -- "ours," "He" "made"
      "their" "ti" -- "ny" "wings." _ _ "The" "Lord" "God" "made" "them" "all." __
      }
      \new Lyrics \lyricsto "vSx1" { 
      _ _ _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _ _ _
      _ _ "The" "pur" -- "ple" -- "head" -- "ed" "moun" -- "tain," "The" "ri" -- "ver"
      "run" -- "ning" "by," "The" "sun" -- "set" "and" "the" "mor" -- "ning," "That" "bright" --
      "ens" "up" _ _ "the" "sky."
      }
      \new Staff = "tb" \with { instrumentName = \markup \center-column { "Tenor" "Bass" } shortInstrumentName = \markup \center-column { "T." "B." } \RemoveAllEmptyStaves } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key g \major \voiceOne R1 |
    R1 |
    R1 |
    R1 |
    b4\mf b4 b4 b4 |
    g4 b4 b2 |
    a4 d'4 d'4 b4 |
    g4 fis2. |
    b4 d'4 b4 b4 |
    c'4 c'4 d'2 |
    b4 a4 g4 a4 |
    c'4 b2. |
    R1 |
    R1 |
    b4\p b4 d'4 b4 |
    a4 b4 d'2 |
    b4 a4 g4 g4 |
    b4 a2. |
    g4 d'4 c'4 b4 |
    c'4 b4 b2 |
    a4 a4 c'4 b4 |
    a4 b2. |
    cis'4 a2. |
    b4\f c'4 g4 a4 |
    c'2 b2~ |
    b1\fermata |
    R1 |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo R1 |
    R1 |
    R1 |
    R1 |
    g4 e4 g,4 b,4 |
    c4 g,4 e2 |
    a,4 g,4 d4 e4 |
    a,4 d2. |
    g,4 g,4 b,4 e4 |
    c4 a,4 d2 |
    g,4 d4 e4 d4 |
    c4 g2. |
    R1 |
    R1 |
    e4 e4 d4 e4 |
    b,4 e4 d2 |
    g4 d4 e4 c4 |
    g,4 d2. |
    e4 g4 a4 g4 |
    c4 g,4 e2 |
    a,4 d4 d4 g4 |
    d4 g2. |
    a4 d2. |
    g,4 a,4 g,4 d4 |
    c2 g,2~ |
    g,1\fermata |
    R1 |
          }
        >>
      }
      \new Lyrics \lyricsto "vTx1" { 
      "All" "things" "bright" "and" "beau" -- "ti" -- "ful," "All" "crea" -- "tures" "great" "and"
      "small," "All" "things" "wise" "and" "won" -- "der" -- "ful," "The" "Lord" "God" "made"
      "them" "all." "Each" "lit" -- "tle" "flower" "that" "o" -- "pens," "Each" "lit" -- "tle"
      "bird" "that" "sings," "He" "made" "their" "glow" -- "ing" "col" -- "ours," "He" "made"
      "their" "ti" -- "ny" "wings." _ _ "The" "Lord" "God" "made" "them" "all." __
      }
      \new Lyrics \lyricsto "vTx1" { 
      _ _ _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _ _ _
      _ _ "The" "pur" -- "ple" -- "head" -- "ed" "moun" -- "tain," "The" "ri" -- "ver"
      "run" -- "ning" "by," "The" "sun" -- "set" "and" "the" "mor" -- "ning," "That" "bright" --
      "ens" "up" _ _ "the" "sky."
      }
    >>
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "rh" { \clef "treble"
        <<
          \new Voice = "vPx1" {
    \key g \major \oneVoice <d' g'>4\p <g' b'>4 <fis' d''>4 <g' g''>4 |
    <g' e''>4 <a' c''>4 <fis' a'>2 |
    <g' d''>4 <fis' c''>4 <g' b'>4 <fis' a'>4 |
    <e' g'>4 <d' g'>2. |
    <d' g'>4\mf <g' b'>4 <g' d''>4 <fis' d''>4 |
    <e' e''>4 <g' d''>4 <g' b'>2 |
    <e' c''>4 <g' b'>4 <fis' a'>4 <e' g'>4 |
    <cis' a'>4 d'2. |
    <d' g'>4 <g' b'>4 <fis' d''>4 <g' g''>4 |
    <g' e''>4 <a' c''>4 <fis' a'>2 |
    <g' d''>4 <fis' c''>4 <g' b'>4 <fis' a'>4 |
    <e' g'>4 <d' g'>2. |
    <g' d''>4_\markup { \italic "cresc." } <fis' c''>4 <g' b'>4 <fis' a'>4 |
    <e' g'>4 <d' g'>2. |
    \voiceOne b'4\p^\markup { \italic "legato" } b'4 a'4 g'4 |
    fis'4 g'4 a'2 |
    g'4 a'4 b'4 c''4 |
    d''4 d''2. |
    b'4 b'4 c''4 d''4 |
    e''4 d''4 b'2 |
    c''4 a'4 fis'4 g'4 |
    a'4 g'2. |
    a'4 d''2. |
    \oneVoice <g' d''>4\f <e' c''>4 <g' b'>4 <fis' a'>4 |
    <e' g'>2 <d' g'>2~ |
    <d' g'>1 |
    <b' d'' g''>1\fermata\ff |
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
    \voiceTwo g'8 e'8 g'8 e'8 fis'8 d'8 e'8 b8 |
    dis'8 b8 e'8 b8 fis'8 d'8 fis'8 d'8 |
    d'8 b8 fis'8 d'8 e'8 b8 e'8 c'8 |
    g'8 d'8 fis'8 d'8 fis'8 d'8 fis'8 d'8 |
    g'8 e'8 g'8 d'8 e'8 c'8 g'8 d'8 |
    g'8 e'8 g'8 d'8 g'8 e'8 g'8 e'8 |
    e'8 c'8 fis'8 d'8 d'8 c'8 d'8 b8 |
    fis'8 d'8 d'8 b8 d'8 b8 d'8 b8 |
    g'8 e'8 fis'8 d'8 fis'8 d'8 fis'8 d'8 |
    \oneVoice s1 |
    s1 |
    s1 |
    s1 |
          }
        >>
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \key g \major <g,, g,>4 <g,, g,>4 <b,, b,>4 <e, e>4 |
    <c, c>4 <a,, a,>4 <d, d>2 |
    <g,, g,>4 <d, d>4 <e, e>4 <d, d>4 |
    <c, c>4 <g, g>2. |
    <g, g>4 <e, e>4 <g,, g,>4 <b,, b,>4 |
    <c, c>4 <g,, g,>4 <e, e>2 |
    <a,, a,>4 <g,, g,>4 <d, d>4 <e, e>4 |
    <a,, a,>4 <d, d>2. |
    <g,, g,>4 <g,, g,>4 <b,, b,>4 <e, e>4 |
    <c, c>4 <a,, a,>4 <d, d>2 |
    <g,, g,>4 <d, d>4 <e, e>4 <d, d>4 |
    <c, c>4 <g, g>2. |
    <g,, g,>4 <d, d>4 <e, e>4 <d, d>4 |
    <c, c>4 <g, g>2. |
    e4 e4 d4 e4 |
    b,4 e4 d2 |
    g4 d4 e4 c4 |
    g,4 d2. |
    e4 g4 a4 g4 |
    c4 g,4 e2 |
    a,4 d4 d4 g4 |
    d4 g2. |
    a4 d2. |
    <g,, g,>4 <a,, a,>4 <g,, g,>4 <d, d>4 |
    <c, c>2 <g,, g,>2~ |
    <g,, g,>1 |
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
