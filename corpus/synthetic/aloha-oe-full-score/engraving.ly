\version "2.24.0"
#(set-global-staff-size 16)
\header {
  title = "Aloha Oe"
  subtitle = "Farewell to Thee"
  composer = "Liliuokalani"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Bonum"
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "stV" \with { instrumentName = "Solo Voice" shortInstrumentName = "Solo" } { \clef "treble"
          \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \numericTimeSignature \time 4/4 \key g \major \partial 1*1/4 r4 |
    R1 |
    R1 |
    r1
    \set Timing.measurePosition = #(ly:make-moment 1/4) r2. \bar "||"
    \set Timing.measurePosition = #(ly:make-moment 3/4) d'8 g'8 |
    b'4. a'8 g'8 fis'8 g'8 e'8 |
    d'2 r4 b'4 |
    a'4. gis'8 a'8 a'8 c''8 b'8 |
    a'2. d'8 g'8 |
    b'4. a'8 g'8 fis'8 g'8 e'8 |
    d'2 r4 d'8 d'8 |
    e'4 a'8 g'8 fis'8 b'8 a'8 fis'8
    \set Timing.measurePosition = #(ly:make-moment 3/8) g'2~ g'8 \bar "||"
    \set Timing.measurePosition = #(ly:make-moment 5/8) r8 r4 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 \bar "|." |
          }
      }
      \new Lyrics \lyricsto "vVx1" { \set stanza = "1." 
      "Ha" -- "a" -- "heo" "ka" "u" -- "a" "i" -- "na" "pali" "Ke" "nihi" "a" --
      "e" -- "la" "ka" "na" -- "hele" "E" "ha" -- "ha" -- "i" "a" -- "na" "i"
      "ka" "\"liko,\"" "Pu" -- "a" "A" -- "hi" -- "hi" "le" -- "hu" -- "a" "o" "uka..." __
      }
      \new Lyrics \lyricsto "vVx1" { \set stanza = "2." 
      "Proud" -- "ly" "swept" "the" "rain" __ _ "by" "the" "cliffs" "As" "on" "it"
      "gli" -- "ded" "through" "the" "trees" "Still" __ _ "foll'" -- "wing" "ev" -- "er" "the" __
      _ "\"liko,\"" "The" __ _ "A" -- "hi" -- "hi" "le" -- "hu" -- "a" "of the" "vale..." __
      }
      \new Staff = "stS" \with { instrumentName = "Soprano" shortInstrumentName = "S." } { \clef "treble"
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \key g \major r4 |
    R1 |
    R1 |
    r1
    r2.
    r4 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    r1
    r2 r8
    g'8 g'8 fis'8 |
    e'4( g'4) c''8 e'8 e'8 e'8 |
    d'4( g'4) b'4 g'8\p g'8 |
    fis'8 fis'8 fis'8 g'8 a'8 gis'8 a'8 c''8 |
    b'2 g'4 r8 fis'8 |
    e'4 g'4 c''4. e'8 |
    d'8 d'8 g'8 g'8 b'4. g'8 |
    fis'4. g'8 b'8( a'4) fis'8 |
    g'2. s1*1/4 |
          }
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "A" -- "lo" -- "ha" "o" -- _ "e," "a" -- "lo" -- "ha" "o" -- _ "e,"
      "E" "ke" "o" -- "na" -- "o" -- "na" "no" -- "ho" "i" -- "ka" "li" -- "po"
      "A" "fond" "em" -- "brace" "a" "ho" -- "i" "a" -- "e" "au," "Un" -- "til"
      "we" "meet" __ _ "a" -- "gain."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "Fare" -- "well" "to" "thee," __ _ _ "fare" -- "well" "to" "thee," __ _ _
      "Thou" __ _ "char" -- "ming" "one" "who" "dwells" "in" "sha" -- "ded" "bow'" -- "rs"
      "One" "fond" "em" -- "brace" __ _ "e'er" "I" __ _ "de" -- "part," "Un" -- "til"
      "we" "meet" __ _ "a" -- "gain."
      }
      \new Staff = "stA" \with { instrumentName = "Alto" shortInstrumentName = "A." } { \clef "treble"
          \new Voice = "vAx1" {
    \key g \major r4 |
    R1 |
    R1 |
    r1
    r2.
    r4 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    r1
    r2 r8
    d'8 d'8 d'8 |
    e'2 g'8 e'8 e'8 e'8 |
    d'2 d'4 d'8\p d'8 |
    d'8 d'8 d'8 d'8 d'8 d'8 fis'8 fis'8 |
    g'2 d'4 r8 d'8 |
    e'4 e'4 g'4. e'8 |
    d'8 d'8 d'8 d'8 d'4. d'8 |
    d'4. d'8 d'4. d'8 |
    d'2. s1*1/4 |
          }
      }
      \new Staff = "stT" \with { instrumentName = "Tenor" shortInstrumentName = "T." } { \clef "treble_8"
          \new Voice = "vTx1" {
    \set melismaBusyProperties = #'()
    \key g \major r4 |
    R1 |
    R1 |
    r1
    r2.
    r4 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    r1
    r2 r8
    b8 b8 b8 |
    <g c'>2 e'8 c'8 c'8 c'8 |
    b2 d'4 b8\p b8 |
    a8 a8 a8 b8 c'8 b8 c'8 e'8 |
    d'2 b4 r8 b8 |
    c'4 c'4 e'4. c'8 |
    b8 b8 b8 b8 d'4. g8 |
    a4. b8 d'8( c'4) a8 |
    b2. s1*1/4 |
          }
      }
      \new Lyrics \lyricsto "vTx1" { \set stanza = "1." 
      "A" -- "lo" -- "ha" "o" -- "e," "a" -- "lo" -- "ha" "o" -- "e," "E" "ke"
      "o" -- "na" -- "o" -- "na" "no" -- "ho" "i" -- "ka" "li" -- "po" "A" "fond"
      "em" -- "brace" "a" "ho" -- "i" "a" -- "e" "au," "Un" -- "til" "we" "meet" __
      _ "a" -- "gain."
      }
      \new Lyrics \lyricsto "vTx1" { \set stanza = "2." 
      "Fare" -- "well" "to" "thee," __ _ "fare" -- "well" "to" "thee," __ _ "Thou" __ _
      "char" -- "ming" "one" "who" "dwells" "in" "sha" -- "ded" "bow'" -- "rs" "One" "fond"
      "em" -- "brace" __ _ "e'er" "I" __ _ "de" -- "part," "Un" -- "til" "we" "meet" __
      _ "a" -- "gain."
      }
      \new Staff = "stB" \with { instrumentName = "Bass" shortInstrumentName = "B." } { \clef "bass"
          \new Voice = "vBx1" {
    \key g \major r4 |
    R1 |
    R1 |
    r1
    r2.
    r4 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    r1
    r2 r8
    g8 g8 g,8 |
    c2 c8 c8 c8 c8 |
    g2 g,4 g8\p g8 |
    d8 d8 d8 d8 d8 d8 d8 d8 |
    g2 g,4 r8 g,8 |
    c4 c4 c4. c8 |
    g8 g8 d8 d8 g,4. b,8 |
    d4. d8 d4. d8 |
    g,2. s1*1/4 |
          }
      }
    >>
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "stPs1" { \clef "treble"
          \new Voice = "vPx1" {
    \key g \major d'8( g'8) |
    b'4.( a'8 g'8 fis'8 g'8 e'8) |
    d'2 r4 d'4 |
    e'4( a'8 g'8) fis'4( b'8 a'8)
    g'2.
    r4 |
    r8 d'8-.( <b g'>8 d'8) r8 c'8( <e' g'>8 c'8) |
    r8 d'8( <b g'>8 d'8) r8 d'8( <b g'>8 d'8) |
    r8 d'8( <a fis'>8 d'8) r8 d'8( <a fis'>8 d'8) |
    r8 d'8( <c' fis'>8 d'8) <c' fis'>4 r4 |
    r8 d'8( <b g'>8 d'8) r8 c'8( <e' g'>8 c'8) |
    r8 d'8( <b g'>8 d'8) r8 d'8( <b g'>8 d'8) |
    r8 e'8( <c' a'>8 e'8) r8 d'8( <c' fis'>8 d'8)
    r8 d'8( <b g'>8 d'8) <b g'>8
    r8 r4 |
    <g c' e'>4( <c' e' g'>4 <e' g' c''>8) <g c' e'>8 <g c' e'>8 <g c' e'>8 |
    s1*1/4 <b d' g'>4 <d' g' b'>4 <b g'>8\p( d'8) |
    s1*1/2 <c' d' a'>8 <b d' gis'>8 <c' fis' a'>8 <e' fis' c''>8 |
    r8 b'8 g'8 d'8 <b g'>8 r8 r4 |
    s1*1/4 <c' e' g'>4 <e' g' c''>8 e'8( <c' g'>8 e'8) |
    s1*1/4 <b d' g'>4 <d' g' b'>8 d'8( <b g'>8 d'8) |
    r8 d'8( <a fis'>8 <b g'>8) <d' b'>8( <c' a'>8 d'8 <c' fis'>8) |
    r8 d'8( <b g'>8 d'8) <b g'>4 s1*1/4 |
          }
      }
      \new Staff = "stPs2" { \clef "bass"
        <<
          \new Voice = "vPx5" {
    \key g \major \oneVoice r4 |
    g,8-. d8( <g b>8 d8) c8-. e8( <g c'>8 e8) |
    g,8-. d8( <g b>8 d8) g,8-. d8( <g b>8 d8) |
    c8-. e8( <a c'>8 e8) d8-. fis8( <a c'>8 fis8)
    g,8-. d8( <g b>8 d8) <g b>4
    r4 |
    <g, g>4 r4 <c, c>4 r4 |
    <g, g>4 r4 <g, g>4 r4 |
    d4 r4 d4 r4 |
    d4 r4 d,4 r4 |
    <g, g>4 r4 <g, g>4 r4 |
    <g, g>4 r4 <g, g>4 r4 |
    <c, c>4 r4 <d, d>4 r4
    <g, g>2~ <g, g>8
    r8 r4 |
    c2~ c8 c8 c8 c8 |
    \voiceOne <b d'>4 s1*3/4 |
    <a d' fis'>8 <a d' fis'>8 <a d' fis'>8 <b d' g'>8 s1*1/2 |
    \oneVoice g2( g,8) b,8( d8 g,8) |
    \voiceOne <g c' e'>4 s1*3/4 |
    <b d'>4 s1*3/4 |
    \oneVoice d4 r4 d4. d8 |
    g,2. s1*1/4 |
          }
          \new Voice = "vPx6" {
    \oneVoice s1*1/4 |
    s1 |
    s1 |
    s1
    s1*3/4
    s1*1/4 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1
    s1*5/8
    s1*3/8 |
    s1 |
    \voiceTwo g4( d4 g,4 g4) |
    d4 r4 d4 r4 |
    \oneVoice s1 |
    \voiceTwo c2~ c8 r8 r8 c8 |
    g4( d4 g,4) r4 |
    \oneVoice s1 |
    s1 |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
