\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "The Long Road"
  subtitle = "lead sheet"
  poet = "Words: coverage suite (2026)"
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
  indent = 0
  system-system-spacing.basic-distance = #17
}
\score {
  <<
    \new ChordNames \with { majorSevenSymbol = \markup { maj7 } } \chordmode { bes1*1/2 g1*1/2:m7 c1*1/2:m7 f1*1/2:7 bes1*1/2 d1*1/2:m c1*1/2:m7 f1*1/2:7 bes1*1/2 g1*1/2:m7 ees1*1/2 f1*1/2:7 bes1*1/2/d c1*1/4:m7 f1*1/4:7 bes1*1/2 f1*1/2:7 bes1 ees1*1/2 ees1*1/2:m bes1*1/2/f g1*1/2:7 c1*1/2:m7 f1*1/2:7 c1*1/2:m7 f1*1/2:7 bes1*1/2 g1*1/2:m c1*1/2:m7 f1*1/2:7 bes1:6 }
    \new Staff = "mel" { \clef "treble"
        \new Voice = "vP1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Moderately" 4 = 100 \numericTimeSignature \time 4/4 \key bes \major \stemDown bes'4\mf c''4 d''4 f''4 |
    ees''2 d''4 c''4 |
    bes'4. c''8 d''4 bes'4 |
    c''1 |
    \break bes'4 c''4 d''4 f''4 |
    g''2 f''4 ees''4 |
    d''4 c''8 bes'8 c''4 d''4 |
    \set Score.repeatCommands = #'((volta "1.")) bes'1 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) bes'2. r4 \bar "||" |
    \break \set Score.repeatCommands = #'((volta #f)) g''4 g''4 f''4 ees''4 |
    d''2 c''2 |
    f''4 f''4 ees''4 d''4 |
    c''1 |
    \break bes'4 c''4 d''4 ees''4 |
    f''4 g''8 f''8 d''4 c''4 |
    bes'1\fermata \bar "|." |
        }
    }
    \new Lyrics = "lyrmelx1" \lyricsto "vP1x1" { 
      \set stanza = "1." "Walk" -- "ing" "down" "the" "long" "and" "wind" -- "ing" "road," "the" "sun" "is"
      "warm" "up" -- "on" "my" "face," "and" "all" "the" "world" "is" "wide" "to" --
      "day." _ "Oh," "the" "road" "goes" "on" "and" "on," "through" "the" "val" --
      "ley," "o" -- "ver" "the" "hill" "and" "back" "a" -- "gain" "to" "you."
    }
    \new Lyrics = "lyrmelx2" \lyricsto "vP1x1" { 
      \set stanza = "2." "Sing" -- "ing" "ev" -- "ery" "song" "I" "know," "the" "wind" "is" "soft" "and"
      "slow," "I'm" "go" -- "ing" "where" "the" "riv" -- "ers" "run," "I'll" "find" "my"
      _ "way."
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
