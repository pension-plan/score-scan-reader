\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Hark! the Herald Angels Sing"
  poet = "Charles Wesley, 1739"
  composer = "(new tune, CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "URW Bookman"
  top-margin = 20\mm
  indent = 8\mm
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "S" "A" } shortInstrumentName = \markup \center-column { "S" "A" } } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \defaultTimeSignature \time 2/2 \key c \major \voiceOne c''4\f b'4 a'4 g'4 |
    a'4 b'4 c''2 |
    e''4 d''4 c''4 b'4 |
    a'4 b'4 g'2~ |
    g'2 r2 |
    R1 |
    c''4\f b'4 a'4 g'4 |
    a'4 b'4 c''2 |
    <a' c''>1 |
    <g' c''>1\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo c''4 b'4 a'4 g'4 |
    a'4 b'4 c''2 |
    g'2 e'2 |
    a'4 g'4 e'2 |
    g'2 r2 |
    R1 |
    r4 g'4 f'4 e'4 |
    f'4 f'4 e'2 |
    f'1 |
    e'1\fermata |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { 
      "Hark!" "the" "her" -- "ald" "an" -- "gels" "sing," "Glo" -- "ry" "to" "the" "new" --
      "born" "King;" __ _ "God" "and" "sin" -- "ners" "re" -- "con" -- "ciled." "A" -- "men."
      }
      \new Staff = "lower" \with { instrumentName = \markup \center-column { "T" "B" } shortInstrumentName = \markup \center-column { "T" "B" } } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key c \major \voiceOne e'4 b4 c'4 c'4 |
    f4 d'4 e'2 |
    c'2 c'2 |
    c'4 b4 c'2 |
    r1 |
    r1 |
    g2 a2~ |
    a4 g4 c'2 |
    c'1 |
    c'1\fermata |
          }
          \new Voice = "vBx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \voiceTwo c4 g4 f4 e4 |
    f4 g4 c2 |
    c2 e2 |
    f4 g4 c2 |
    r4 g4\mf g4 c'4 |
    b4 a4 g4 f4 |
    e4\f d4 c4 c4 |
    a4 d4 c2 |
    <f, f>1 |
    <c, c>1\fermata |
          }
        >>
      }
      \new Lyrics \lyricsto "vBx1" { 
      _ _ _ _ _ _ _ _ _ _ _ _
      "Peace" "on" "earth," "and" "mer" -- "cy" "mild,"
      }
    >>
  >>
  \layout {
    \context { \Staff \consists "Merge_rests_engraver" }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
