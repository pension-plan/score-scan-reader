\version "2.24.0"
#(set-global-staff-size 21)
\header {
  title = "Love Came Down at Christmas"
  poet = "Christina Rossetti, 1885"
  composer = "for SSAA choir and piano (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "P052"
  top-margin = 14\mm
  system-system-spacing.basic-distance = #20
  ragged-last-bottom = ##t
  max-systems-per-page = #2
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "Soprano I" "Soprano II" } shortInstrumentName = \markup \center-column { "S. I" "S. II" } } { \clef "treble"
        <<
          \new Voice = "vS1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \time 3/4 \key a \major \voiceOne R1*3/4 |
    R1*3/4 |
    e''2\mp cis''4 |
    b'2 a'4 |
    b'2 cis''4 |
    d''2 cis''4 |
    b'2 a'4 |
    gis'2 a'4 |
    b'2. |
    \pageBreak e''2 cis''4 |
    b'2 a'4 |
    d''2 cis''4 |
    b'2 cis''4 |
    d''2 cis''4 |
    b'2 gis'4 |
    a'2.\fermata \bar "|." |
          }
          \new Voice = "vS2x1" {
    \autoBeamOff
    \voiceTwo R1*3/4 |
    R1*3/4 |
    cis''2 a'4 |
    gis'2 e'4 |
    gis'2 a'4 |
    a'2 a'4 |
    gis'2 fis'4 |
    e'2 fis'4 |
    gis'2. |
    a'2 gis'4 |
    gis'2 fis'4 |
    a'2 a'4 |
    gis'2 a'4 |
    fis'2 e'4 |
    e'2 e'4 |
    e'2.\fermata |
          }
        >>
      }
      \new Lyrics \lyricsto "vS1x1" { \set stanza = "1." 
      "Love" "came" "down" "at" "Christ" -- "mas," "Love" "all" "love" -- "ly," "Love" "Di" --
      "vine;" "Love" "was" "born" "at" "Christ" -- "mas," "Star" "and" "An" -- "gels" "gave"
      "the" "sign."
      }
      \new Lyrics \lyricsto "vS1x1" { \set stanza = "2." 
      "Wor" -- "ship" "we" "the" "God" -- "head," "Love" "In" -- "car" -- "nate," "Love" "Di" --
      "vine;" "Wor" -- "ship" "we" "our" "Je" -- "sus:" "But" "where" -- "with" "for" "sa" --
      "cred" "sign?"
      }
      \new Staff = "middle" \with { instrumentName = \markup \center-column { "Alto I" "Alto II" } shortInstrumentName = \markup \center-column { "A. I" "A. II" } } { \clef "treble"
        <<
          \new Voice = "vA1x1" {
    \autoBeamOff
    \key a \major \voiceOne R1*3/4 |
    R1*3/4 |
    a'2\mp e'4 |
    e'2 cis'4 |
    e'2 e'4 |
    fis'2 e'4 |
    e'2 cis'4 |
    cis'2 cis'4 |
    e'2. |
    cis'2 e'4 |
    e'2 cis'4 |
    fis'2 e'4 |
    e'2 e'4 |
    d'2 e'4 |
    e'2 d'4 |
    cis'2.\fermata |
          }
          \new Voice = "vA2x1" {
    \autoBeamOff
    \voiceTwo R1*3/4 |
    R1*3/4 |
    e'2 a4 |
    e'2 a4 |
    e'2 cis'4 |
    a2 a4 |
    b2 cis'4 |
    cis'2 cis'4 |
    b2. |
    a2 cis'4 |
    e'2 a4 |
    a2 a4 |
    b2 a4 |
    a2 a4 |
    b2 b4 |
    a2.\fermata |
          }
        >>
      }
    >>
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "rh" { \clef "treble"
        <<
          \new Voice = "vPx1" {
    \key a \major \voiceOne a'4\p b'4 cis''4 |
    b'2. |
    e''2 cis''4 |
    b'2 a'4 |
    b'2 cis''4 |
    d''2 cis''4 |
    b'2 a'4 |
    gis'2 a'4 |
    b'2. |
    e''2 cis''4 |
    b'2 a'4 |
    d''2 cis''4 |
    b'2 cis''4 |
    d''2 cis''4 |
    b'2 gis'4 |
    a'2.\fermata |
          }
          \new Voice = "vPx2" {
    \voiceTwo <cis' e'>2. |
    <d' gis'>2. |
    <a' cis''>2 <e' a'>4 |
    <e' gis'>2 <cis' e'>4 |
    <e' gis'>2 <e' a'>4 |
    <fis' a'>2 <e' a'>4 |
    <e' gis'>2 <cis' fis'>4 |
    <cis' e'>2 <cis' fis'>4 |
    <e' gis'>2. |
    <cis' a'>2 <e' gis'>4 |
    <e' gis'>2 <cis' fis'>4 |
    <fis' a'>2 <e' a'>4 |
    <e' gis'>2 <e' a'>4 |
    <d' fis'>2 <cis' e'>4 |
    <e' gis'>2 <d' e'>4 |
    <cis' e'>2. |
          }
        >>
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \key a \major a,4 <e a cis'>4 <e a cis'>4 |
    e,4 <e gis b>4 <d gis b>4 |
    a,4 <e a cis'>4 <e a cis'>4 |
    e,4 <e gis b>4 <e a cis'>4 |
    e,4 <e gis b>4 <cis e a>4 |
    d,4 <d fis a>4 <e a cis'>4 |
    e,4 <e gis b>4 <fis a cis'>4 |
    cis,4 <e gis cis'>4 <fis a cis'>4 |
    e,4 <e gis b>4 <e gis b>4 |
    a,4 <e a cis'>4 <e gis cis'>4 |
    e,4 <e gis b>4 <fis a cis'>4 |
    d,4 <d fis a>4 <e a cis'>4 |
    e,4 <e gis b>4 <e a cis'>4 |
    d,4 <d fis a>4 <e a cis'>4 |
    e,4 <e gis b>4 <d gis b>4 |
    <a,, a,>2.\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Staff \consists "Merge_rests_engraver" }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
