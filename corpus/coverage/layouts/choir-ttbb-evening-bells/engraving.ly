\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Evening Bells"
  subtitle = "for male choir (TTBB)"
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
  indent = 20\mm
  short-indent = 10\mm
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "tt" \with { instrumentName = \markup \center-column { "Tenor I" "Tenor II" } shortInstrumentName = \markup \center-column { "T. I" "T. II" } } { \clef "treble_8"
        <<
          \new Voice = "vT1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Calmly" 4 = 69 \numericTimeSignature \time 4/4 \key bes \major \voiceOne \stemUp d'4\p ees'4 f'4 d'4 |
    g'4 f'4 d'2 |
    c'4 d'4 ees'4 c'4 |
    f'4 ees'4 d'2\fermata |
    \break d'4\mf f'4 g'4 a'4 |
    bes'4 a'4 g'2 |
    f'4\pp d'4 ees'4 c'4 |
    d'4 c'4 bes2\fermata \bar "|." |
          }
          \new Voice = "vT2x1" {
    \autoBeamOff
    \voiceTwo \stemDown bes4 g4 a4 bes4 |
    bes4 a4 bes2 |
    c'4 bes4 c'4 a4 |
    d'4 bes4 bes2\fermata |
    bes4 a4 ees'4 c'4 |
    d'4 c'4 bes2 |
    bes4 bes4 c'4 a4 |
    bes4 a4 bes2\fermata |
          }
        >>
      }
      \new Lyrics = "lyrttx1" \lyricsto "vT1x1" { 
      "Hear" "the" "bells" "of" "eve" -- "ning" "ring," "o" -- "ver" "field" "and" "qui" --
      "et" "spring;" "rest," "my" "broth" -- "ers," "day" "is" "done," "sleep" "be" -- "neath"
      "the" "set" -- "ting" "sun."
      }
      \new Staff = "bb" \with { instrumentName = \markup \center-column { "Baritone" "Bass" } shortInstrumentName = \markup \center-column { "Bar." "B." } } { \clef "bass"
        <<
          \new Voice = "vB1x1" {
    \autoBeamOff
    \key bes \major \voiceOne \stemUp f4\p ees4 c4 d4 |
    d4 f4 f2 |
    a4 g4 g4 f4 |
    f4 g4 f2\fermata |
    f4\mf f4 bes4 f4 |
    f4 f4 d2 |
    d4\pp g4 g4 f4 |
    d4 ees4 d2\fermata |
          }
          \new Voice = "vB2x1" {
    \autoBeamOff
    \voiceTwo \stemDown bes,4 c4 f,4 bes,4 |
    g,4 f,4 bes,2 |
    f4 g4 c4 f4 |
    bes,4 ees4 bes,2\fermata |
    bes,4 d4 ees4 f4 |
    bes,4 f,4 g,2 |
    bes,4 g,4 c4 f,4 |
    g,4 f,4 bes,2\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
