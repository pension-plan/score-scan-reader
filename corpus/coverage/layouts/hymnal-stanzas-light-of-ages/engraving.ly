\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Light of Ages"
  subtitle = "L.M."
  poet = "Words: coverage suite (2026)"
  composer = "Tune and harmony: coverage suite (2026)"
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
  indent = 0
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "sa" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Steadily" 2 = 56 \numericTimeSignature \time 4/4 \key g \major \partial 1*1/4 \voiceOne \stemUp d'4 |
    g'4 a'4 b'4 g'4 |
    c''4 b'4 a'4\fermata d''4 |
    \break b'4 g'4 a'4 b'4 |
    a'4 g'4 fis'4\fermata d'4 |
    g'4 a'4 b'4 c''4 |
    \break d''4 c''4 b'4\fermata b'4 |
    c''4 b'4 a'4 g'4
    \set Timing.measurePosition = #(ly:make-moment 1/4) a'4 fis'4 g'4\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo \stemDown b4 |
    b4 d'4 d'4 e'4 |
    e'4 d'4 d'4\fermata d'4 |
    d'4 e'4 d'4 b4 |
    d'4 b4 d'4\fermata d'4 |
    d'4 fis'4 g'4 e'4 |
    g'4 e'4 e'4\fermata d'4 |
    e'4 d'4 c'4 b4
    c'4 c'4 b4\fermata |
          }
        >>
      }
      \new Lyrics = "lyrsax1" \lyricsto "vSx1" { 
      \set stanza = "1." "O" "Light" "that" "breaks" "the" "dark" "of" "night," "shine" "on" "the" "path"
      "our" "feet" "must" "tread;" "make" "plain" "the" "way," "make" "clear" "the" "sight,"
      "and" "lead" "us" "where" "the" "lost" "are" "led."
      }
      \new Lyrics = "lyrsax2" \lyricsto "vSx1" { 
      \set stanza = "2." "O" "Word" "that" "speaks" "through" "wind" "and" "flame," "call" "out" "our" "names"
      "in" "ev" -- "ery" "land;" "teach" "us" "to" "praise" "your" "ho" -- "ly" "name,"
      "and" "hold" "us" "in" "your" "gen" -- "tle" "hand."
      }
      \new Lyrics = "lyrsax3" \lyricsto "vSx1" { 
      \set stanza = "3." "O" "Love" "that" "will" "not" "let" "us" "go," "come" "down" "like" "rain"
      "on" "thirst" -- "y" "ground;" "make" "deep" "the" "roots," "make" "strong" "the" "flow,"
      "till" "all" "the" "lost" "at" "last" "are" "found."
      }
      \new Lyrics = "lyrsax4" \lyricsto "vSx1" { 
      \set stanza = "4." "To" "Fa" -- "ther," "Son," "and" "Spir" -- "it" "be" "all" "praise" "and" "hon" --
      "or," "glo" -- "ry," "might," "through" "all" "the" "a" -- "ges" "yet" "to" "be,"
      "in" "end" -- "less" "day" "and" "change" -- "less" "light."
      }
      \new Staff = "tb" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key g \major \voiceOne \stemUp g4 |
    g4 fis4 g4 g4 |
    g4 g4 fis4\fermata b4 |
    g4 g4 fis4 g4 |
    fis4 g4 a4\fermata b4 |
    b4 d'4 d'4 c'4 |
    b4 a4 g4\fermata g4 |
    g4 g4 e4 e4
    e4 d4 d4\fermata |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo \stemDown g,4 |
    g,4 d4 g,4 e4 |
    c4 g,4 d4\fermata g,4 |
    g,4 c4 d4 e4 |
    d4 e4 d4\fermata g4 |
    g4 d4 g,4 a,4 |
    g,4 a,4 e4\fermata g4 |
    c4 g,4 a,4 e4
    a,4 d4 g,4\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
    \context { \Score \remove "Bar_number_engraver" }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
