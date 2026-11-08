\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Night Song"
  subtitle = "for voice and piano"
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
  indent = 16\mm
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new Staff = "v" \with { instrumentName = "Voice" } { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante tranquillo" 4 = 66 \numericTimeSignature \time 4/4 \key ees \major R1 |
    r2 r4 \stemDown bes'4\mp |
    ees''2 r4 bes'4 |
    c''4 d''4 ees''4 f''4 |
    \break g''2.( f''4) |
    ees''4 d''8 c''8 bes'4 c''4 |
    bes'2 r4 bes'4 |
    aes''4\mf g''4 f''4 ees''4 |
    \break f''4. ees''8 d''4 c''4 |
    bes'4\> c''4 d''4 ees''4 |
    ees''1\fermata\! \bar "|." |
        }
    }
    \new Lyrics = "lyrvx1" \lyricsto "vVx1" { 
      "Sleep" "now," "the" "stars" "are" "keep" -- "ing" "watch" __ _ "the" "moon" "is"
      "on" "the" "sea;" "the" "wind" "has" "fold" -- "ed" "up" "its" "wings," "and"
      "all" "is" "still" "for" "thee."
    }
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vPx1" {
    \autoBeamOff
    \key ees \major \stemUp g'8\p[( bes'8] \stemDown ees''8[ bes'8] \stemUp g'8[ bes'8] \stemDown ees''8[ bes'8]) |
    \stemUp f'8[( aes'8] \stemDown d''8[ aes'8] \stemUp f'8[ aes'8] \stemDown d''8[ aes'8]) |
    \stemUp <g' bes'>4 <g' bes'>4 <g' bes'>4 <g' bes'>4 |
    \stemDown <aes' c''>4 <aes' c''>4 \stemUp <g' bes'>4 \stemDown <aes' c''>4 |
    <g' bes' ees''>2 \stemUp <f' aes' d''>2 |
    <g' bes'>4 \stemDown <aes' c''>4 \stemUp <g' bes'>4 \stemDown <aes' c''>4 |
    \stemUp <f' aes' d''>2 <f' aes' d''>4 r4 |
    \stemDown <aes' c'' ees''>2 <aes' c'' f''>2 |
    <aes' d'' f''>2 <aes' d''>2 |
    <g' bes' ees''>2\< <aes' c'' ees''>2 |
    <g' bes' ees''>1\fermata\! |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \autoBeamOff
    \key ees \major \stemDown ees2\sustainOn \stemUp bes,2\sustainOff |
    bes,2 \stemDown d2 |
    ees2 g2 |
    \stemUp aes,2 c2 |
    bes,2 bes,2 |
    \stemDown ees2 \stemUp aes,2 |
    bes,2 bes,4 r4 |
    aes,2 f,2 |
    bes,2 bes,,2 |
    \stemDown ees2 \stemUp aes,2 |
    ees,1\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
