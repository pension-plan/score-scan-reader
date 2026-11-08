\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Ave verum corpus"
  poet = "Latin, 14th century"
  composer = "for mixed choir (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Termes"
  top-margin = 15\mm
  system-system-spacing.basic-distance = #22
  ragged-last-bottom = ##t
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "stS" \with { instrumentName = "Soprano" shortInstrumentName = "S." } { \clef "treble"
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \numericTimeSignature \time 4/4 \key ees \major bes'2 c''2 |
    bes'2. aes'4 |
    g'2 f'2 |
    bes'4 bes'4 c''4 d''4 |
    ees''2 d''2 |
    c''4 bes'4 bes'2 |
    g'2 aes'2 |
    g'2 f'2 |
    bes'4 c''4 d''4 ees''4 |
    f''2 ees''4 d''4 |
    c''2 bes'4 aes'4 |
    g'1 |
    g'2\p g'2 |
    aes'2 g'2 |
    f'4 g'4 aes'2 |
    g'1 |
    bes'4\mf c''4 d''4 ees''4 |
    <aes' ees''>2^\markup \italic "div." <aes' c''>2 |
    bes'2^\markup \italic "unis." bes'2 |
    <aes' c''>1^\markup \italic "div." |
    <g' bes'>1\fermata \bar "|." |
          }
      }
      \new Lyrics \lyricsto "vSx1" { 
      "A" -- "ve" "ve" -- "rum" "cor" -- "pus," "na" -- "tum" "de" "Ma" -- "ri" -- "a"
      "Vir" -- "gi" -- "ne," "ve" -- "re" "pas" -- "sum," "im" -- "mo" -- "la" -- "tum" "in"
      "cru" -- "ce" "pro" "ho" -- "mi" -- "ne," "cu" -- "jus" "la" -- "tus" "per" -- "fo" --
      "ra" -- "tum" "flu" -- "xit" "a" -- "qua" "et" "san" -- "gui" -- "ne." "A" -- "men."
      }
      \new Staff = "stA" \with { instrumentName = "Alto" shortInstrumentName = "A." } { \clef "treble"
          \new Voice = "vAx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key ees \major ees'2 ees'2 |
    ees'2. f'4 |
    ees'2 d'2 |
    ees'4 ees'4 aes'4 f'4 |
    ees'2 f'2 |
    aes'4 g'4 f'2 |
    ees'2 f'2 |
    ees'2 d'2 |
    ees'4 ees'4 d'4 g'4 |
    bes'2 ees'4 f'4 |
    aes'2 g'4 f'4 |
    ees'1 |
    ees'2\p ees'2 |
    c'2 c'2 |
    f'4 ees'4 c'2 |
    b1 |
    g'4\mf aes'4 f'4 ees'4 |
    ees'2 f'2 |
    g'2 aes'2 |
    ees'1 |
    ees'1\fermata |
          }
      }
      \new Lyrics \lyricsto "vAx1" { 
      "A" -- "ve" "ve" -- "rum" "cor" -- "pus," "na" -- "tum" "de" "Ma" -- "ri" -- "a"
      "Vir" -- "gi" -- "ne," "ve" -- "re" "pas" -- "sum," "im" -- "mo" -- "la" -- "tum" "in"
      "cru" -- "ce" "pro" "ho" -- "mi" -- "ne," "cu" -- "jus" "la" -- "tus" "per" -- "fo" --
      "ra" -- "tum" "flu" -- "xit" "a" -- "qua" "et" "san" -- "gui" -- "ne." "A" -- "men."
      }
      \new Staff = "stT" \with { instrumentName = "Tenor" shortInstrumentName = "T." } { \clef "treble_8"
        <<
          \new Voice = "vTx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key ees \major \oneVoice g2 aes2 |
    g2. bes4 |
    bes2 bes2 |
    g4 bes4 ees'4 bes4 |
    g2 bes2 |
    ees'4 ees'4 d'2 |
    \voiceOne c'2^\markup \italic "div." c'2 |
    bes2 aes2 |
    \oneVoice bes4^\markup \italic "unis." aes4 bes4 c'4 |
    bes2 g4 bes4 |
    ees'2 ees'4 d'4 |
    bes1 |
    c'2\p g2 |
    f2 g2 |
    bes4 bes4 f2 |
    g1 |
    ees'4\mf ees'4 bes4 g4 |
    c'2 c'2 |
    ees'2 d'2 |
    c'1 |
    g1\fermata |
          }
          \new Voice = "vTx2" {
    \autoBeamOff
    \oneVoice s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    \voiceTwo ees2 aes2 |
    ees2 f2 |
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
          }
        >>
      }
      \new Lyrics \lyricsto "vTx1" { 
      "A" -- "ve" "ve" -- "rum" "cor" -- "pus," "na" -- "tum" "de" "Ma" -- "ri" -- "a"
      "Vir" -- "gi" -- "ne," "ve" -- "re" "pas" -- "sum," "im" -- "mo" -- "la" -- "tum" "in"
      "cru" -- "ce" "pro" "ho" -- "mi" -- "ne," "cu" -- "jus" "la" -- "tus" "per" -- "fo" --
      "ra" -- "tum" "flu" -- "xit" "a" -- "qua" "et" "san" -- "gui" -- "ne." "A" -- "men."
      }
      \new Staff = "stB" \with { instrumentName = "Bass" shortInstrumentName = "B." } { \clef "bass"
          \new Voice = "vBx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key ees \major ees2 aes,2 |
    ees2. d4 |
    ees2 bes2 |
    ees4 g4 aes4 bes,4 |
    c2 d2 |
    aes,4 bes,4 bes,2 |
    c2 aes,2 |
    bes,2 bes,2 |
    g,4 aes,4 d4 c4 |
    d2 c4 bes,4 |
    aes,2 bes,4 bes,4 |
    ees1 |
    c2\p c2 |
    f2 ees2 |
    d4 ees4 f2 |
    g,1 |
    g,4\mf c4 bes,4 c4 |
    aes,2 f2 |
    bes2 bes2 |
    <aes, aes>1^\markup \italic "div." |
    <ees, ees>1\fermata |
          }
      }
      \new Lyrics \lyricsto "vBx1" { 
      "A" -- "ve" "ve" -- "rum" "cor" -- "pus," "na" -- "tum" "de" "Ma" -- "ri" -- "a"
      "Vir" -- "gi" -- "ne," "ve" -- "re" "pas" -- "sum," "im" -- "mo" -- "la" -- "tum" "in"
      "cru" -- "ce" "pro" "ho" -- "mi" -- "ne," "cu" -- "jus" "la" -- "tus" "per" -- "fo" --
      "ra" -- "tum" "flu" -- "xit" "a" -- "qua" "et" "san" -- "gui" -- "ne." "A" -- "men."
      }
    >>
  >>
  \layout {
    \context { \Staff \consists "Merge_rests_engraver" }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
