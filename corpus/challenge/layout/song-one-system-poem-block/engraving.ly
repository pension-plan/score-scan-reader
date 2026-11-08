\version "2.24.0"
#(set-global-staff-size 14)
\header {
  dedication = \markup \italic "for the Tuesday evening singers"
  title = "A Red, Red Rose"
  subtitle = "Song for medium voice and piano"
  poet = "Words: Robert Burns (1794)"
  composer = "Music: layout-challenge corpus (2026)"
  copyright = "Dedicated to the public domain (CC0 1.0). Text: R. Burns, 1794."
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 11\mm
  top-margin = 22\mm
  left-margin = 11\mm
  right-margin = 10\mm
  markup-system-spacing.basic-distance = #22
  ragged-bottom = ##t
}
\score {
  <<
    \new Staff = "voice" \with { instrumentName = "Voice" } { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante con espressione" 4 = 66 \numericTimeSignature \time 4/4 \key f \major \partial 1*1/4 c'4\p |
    f'4 f'4 g'4 a'4 |
    c''4 bes'4 a'2 |
    g'4 f'4 g'4 a'4 |
    g'4 f'2 c'4 |
    f'4\mf f'4 g'4 a'4 |
    d''4\< c''4 a'2\! |
    bes'4^\markup { \italic "rit." } a'4 g'4 f'4
    \set Timing.measurePosition = #(ly:make-moment 1/4) g'4 f'2\fermata \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { 
      \set stanza = "1." "O" "my" "Luve's" "like" "a" "red," "red" "rose," "That's" "new" -- "ly" "sprung"
      "in" "June;" "O" "my" "Luve's" "like" "the" "mel" -- "o" -- "die" "That's" "sweet" --
      "ly" "play'd" "in" "tune."
    }
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vPx1" {
    \key f \major r4 |
    <a c' f'>2\p <c' e' g'>4 <a c' f'>4 |
    <a c' f'>4 <bes d' f'>4 <a c' f'>2 |
    <c' e' g'>4 <a d' f'>4 <c' e' g'>4 <a c' f'>4 |
    <c' e' g'>4 <a c' f'>4 <a c' f'>4 <c' e' g'>4 |
    <a c' f'>2 <c' e' g'>4 <a c' f'>4 |
    <bes d' f'>4 <a c' f'>4 <a d' f'>2 |
    <bes d' g'>4 <a c' f'>4 <c' e' g'>4 <bes d' f'>4
    <bes c' e'>4 <a c' f'>4 <a c' f'>4\fermata |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \key f \major r4 |
    f,2 c,2 |
    f,2 f,2 |
    c,2 c,2 |
    c,2 f,2 |
    f,2 c,2 |
    bes,2 d,2 |
    g,2 c,2
    c,4 f,2\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricText.font-size = #-0.4 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
\markup { \vspace #3 }
\markup { \fill-line { \hspace #2 \column { \line { \bold "2." \hspace #1 \column { "As fair art thou, my bonnie lass," "So deep in luve am I;" "And I will luve thee still, my dear," "Till a' the seas gang dry." } } \vspace #1.2 \line { \bold "3." \hspace #1 \column { "Till a' the seas gang dry, my dear," "And the rocks melt wi' the sun:" "I will luve thee still, my dear," "While the sands o' life shall run." } } } \hspace #3 \column { \line { \bold "4." \hspace #1 \column { "And fare thee weel, my only luve!" "And fare thee weel awhile!" "And I will come again, my luve," "Tho' it were ten thousand mile." } } } \hspace #2 } }
