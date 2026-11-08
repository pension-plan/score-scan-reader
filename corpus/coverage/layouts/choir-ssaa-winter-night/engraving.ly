\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Winter Night"
  subtitle = "for women's choir (SSAA)"
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
  indent = 22\mm
  short-indent = 10\mm
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "ss" \with { instrumentName = \markup \center-column { "Soprano I" "Soprano II" } shortInstrumentName = \markup \center-column { "S. I" "S. II" } } { \clef "treble"
        <<
          \new Voice = "vS1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Tranquillo" 4 = 72 \time 3/4 \key f \major \voiceOne \stemUp c''4\p c''4 d''4 |
    c''4 a'4 f'4 |
    g'2. |
    a'4 bes'4 c''4 |
    d''4 c''4 bes'4 |
    a'2. |
    \break f''4\mp e''4 d''4 |
    c''4 bes'4 a'4 |
    g'2. |
    a'4\> c''4 bes'4 |
    a'4 g'4 f'8[( g'8]) |
    f'2.\fermata\!\pp |
          }
          \new Voice = "vS2x1" {
    \autoBeamOff
    \voiceTwo \stemDown a'4 a'4 bes'4 |
    a'4 f'4 d'4 |
    e'2. |
    f'4 g'4 a'4 |
    bes'4 a'4 g'4 |
    f'2. |
    a'4 g'4 f'4 |
    f'4 g'4 f'4 |
    e'4( d'4 e'4) |
    f'4 a'4 g'4 |
    f'4 e'4 d'8[( e'8]) |
    c'2.\fermata |
          }
        >>
      }
      \new Lyrics = "lyrssx1" \lyricsto "vS1x1" { 
      "Snow" "is" "fall" -- "ing" "soft" "and" "white," "cov" -- "er" -- "ing" "the" "hills"
      "to" -- "night;" "hush," "the" "world" "is" "fast" "a" -- "sleep," "stars" "their" "qui" --
      "et" "vig" -- "il" __ _ "keep."
      }
      \new Staff = "aa" \with { instrumentName = \markup \center-column { "Alto I" "Alto II" } shortInstrumentName = \markup \center-column { "A. I" "A. II" } } { \clef "treble"
        <<
          \new Voice = "vA1x1" {
    \autoBeamOff
    \key f \major \voiceOne \stemUp f'4\p f'4 f'4 |
    f'4 c'4 a4 |
    c'2. |
    c'4 d'4 f'4 |
    f'4 f'4 d'4 |
    c'2. |
    f'4\mp e'4 d'4 |
    c'4 d'4 c'4 |
    c'2. |
    c'4\> f'4 e'4 |
    c'4 bes4 bes4 |
    a2.\fermata\!\pp |
          }
          \new Voice = "vA2x1" {
    \autoBeamOff
    \voiceTwo \stemDown c'4 c'4 bes4 |
    f4 f4 f4 |
    g2. |
    a4 bes4 a4 |
    bes4 a4 g4 |
    a2. |
    d'4 c'4 bes4 |
    a4 g4 f4 |
    g2. |
    a4 a4 c'4 |
    a4 g4 g4 |
    f2.\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
