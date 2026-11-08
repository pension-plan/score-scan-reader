\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Morning and Evening"
  subtitle = "song in two stanzas"
  poet = "Words: coverage corpus (2026)"
  composer = "Music: coverage corpus (2026)"
  copyright = "CC0 1.0"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  indent = 14\mm
  ragged-bottom = ##t
  ragged-last-bottom = ##t
  system-system-spacing.basic-distance = #13
  print-page-number = ##t
  top-margin = 12\mm
  bottom-margin = 12\mm
}
\score {
  <<
    \new Staff = "voice" \with { instrumentName = "Voice" } { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante" 4 = 76 \numericTimeSignature \time 4/4 \key ees \major R1 |
    R1 \bar ".|:-||" |
    \break \stemUp ees'4\mf g'4 \stemDown bes'4 \stemUp g'4 |
    aes'4 \stemDown c''4 bes'4 \stemUp aes'4 |
    g'2 f'2~ |
    \break f'2 r4 \stemDown bes'4 |
    c''4 bes'4 \stemUp aes'4 f'4 |
    \break g'4( aes'4) \stemDown bes'2 |
    \set Score.repeatCommands = #'((volta "1.")) c''4 bes'4 \stemUp g'4 ees'4 |
    \pageBreak \stemNeutral f'1 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) \stemDown c''4 d''4 ees''4 \stemUp g'4 |
    \stemNeutral bes'1~ |
    \break \set Score.repeatCommands = #'((volta #f)) \stemDown bes'4 r4 ees''4 d''4 |
    c''4 bes'4 \stemUp aes'4 g'4 |
    \break f'4 g'4 aes'4 f'4 |
    \stemNeutral ees'1 \bar "|." |
        }
    }
    \new Lyrics = "LVx1x1" \lyricsto "vVx1" { 
      \set stanza = "1." "Morn" -- "ing" "light" "is" "break" -- "ing" "o" -- "ver" "hill" "and" __ _ "field,"
      "ev" -- "ery" "val" -- "ley" "wakes" __ _ "to" "hear" "the" "bird" -- "song" "ring."
    }
    \new Lyrics = "LVx1x2" \lyricsto "vVx1" { 
      \set stanza = "2." "Eve" -- "ning" "shad" -- "ows" "gath" -- "er" "gen" -- "tly" "o" -- "ver" __ _ "all,"
      "lamps" "are" "lit" "in" "ev" -- _ "ery" _ _ _ _ _
      "win" -- "dow," "home" -- "ward" "bound" __ _ "we" "go," "rest" -- "ing" "till" "the"
      "morn" -- "ing" "light" "re" -- "turns."
    }
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vPx1" {
    \autoBeamOff
    \key ees \major \stemDown <g' bes' ees''>2\p <g' bes' ees''>2 |
    \stemUp <f' aes' d''>2 <f' aes' bes'>2 |
    <ees' g' bes'>2 <ees' g' bes'>2 |
    <ees' aes' c''>2 <ees' aes' c''>2 |
    <ees' g' bes'>2 <d' f' bes'>2~ |
    <d' f' bes'>2 <d' f' aes'>2 |
    <ees' aes' c''>2 <d' f' aes'>2 |
    \stemNeutral <ees' g' bes'>1 |
    \stemUp <ees' g' c''>2 <d' f' bes'>2~ |
    <d' f' bes'>2 <d' f' aes'>2 |
    <ees' aes' c''>2 <ees' g' bes'>2 |
    \stemNeutral <d' f' bes'>1~ |
    \stemUp <d' f' bes'>4 r4 \stemDown <g' bes' ees''>4 \stemUp <f' bes' d''>4 |
    <ees' aes' c''>2 <ees' g' bes'>2 |
    <d' f' aes'>2 <d' f' aes'>2 |
    \stemNeutral <ees' g' bes'>1 |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \autoBeamOff
    \key ees \major \stemUp ees,2 \stemDown ees2 |
    \stemUp bes,2 bes,2 |
    ees,2 g,2 |
    aes,2 c2 |
    ees,2 bes,2 |
    \stemNeutral bes,1 |
    \stemUp aes,2 bes,2 |
    \stemNeutral ees,1 |
    \stemUp c2 bes,2 |
    \stemNeutral bes,1 |
    \stemUp aes,2 \stemDown ees2 |
    \stemNeutral bes,1~ |
    \stemUp bes,4 r4 \stemDown ees4 \stemUp bes,4 |
    aes,2 \stemDown ees2 |
    \stemNeutral bes,1 |
    ees,1 |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
