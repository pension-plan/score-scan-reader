\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Bright New Day"
  subtitle = "for mixed choir with divisi"
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
  short-indent = 8\mm
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "s" \with { instrumentName = "Soprano" shortInstrumentName = "S." } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Brightly" 4 = 108 \numericTimeSignature \time 4/4 \key c \major \oneVoice \stemDown c''4\mf c''4 d''4 e''4 |
    d''4 c''4 b'2 |
    \stemUp a'4 \stemDown b'4 c''4 d''4 |
    e''4 d''4 c''2 |
    \break \voiceOne \stemUp e''4\f^\markup { \italic "div." } e''4 f''4 g''4 |
    e''4 d''4 c''2 |
    \oneVoice \stemUp a'4^\markup { \italic "unis." } \stemDown c''4 b'4 \stemUp a'4 |
    g'4 \stemDown b'4 c''2\fermata |
          }
          \new Voice = "vSx2" {
    \autoBeamOff
    \oneVoice s1 |
    s1 |
    s1 |
    s1 |
    \voiceTwo \stemDown c''4 c''4 c''4 c''4 |
    c''4 b'4 g'2 |
    \oneVoice s1 |
    s1 |
          }
        >>
      }
      \new Lyrics = "lyrsx1" \lyricsto "vSx1" { 
      "Lift" "your" "voi" -- "ces," "sing" "and" "play," "wel" -- "come" "in" "the" "bright"
      "new" "day;" "let" "the" "hills" "and" "val" -- "leys" "ring," "all" "the" "world"
      "be" -- "gin" "to" "sing."
      }
      \new Staff = "a" \with { instrumentName = "Alto" shortInstrumentName = "A." } { \clef "treble"
          \new Voice = "vAx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key c \major \stemUp e'4\mf e'4 g'4 g'4 |
    g'4 g'4 g'2 |
    a'4 g'4 e'4 g'4 |
    g'4 g'4 e'2 |
    g'4 a'4 a'4 \stemDown c''4 |
    c''4 \stemUp g'4 e'2 |
    c'4 c'4 d'4 f'4 |
    e'4 f'4 g'2\fermata |
          }
      }
      \new Lyrics = "lyrax1" \lyricsto "vAx1" { 
      "Lift" "your" "voi" -- "ces," "sing" "and" "play," "wel" -- "come" "in" "the" "bright"
      "new" "day;" "let" "the" "hills" "and" "val" -- "leys" "ring," "all" "the" "world"
      "be" -- "gin" "to" "sing."
      }
      \new Staff = "t" \with { instrumentName = "Tenor" shortInstrumentName = "T." } { \clef "treble_8"
          \new Voice = "vTx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key c \major \stemUp g4\mf a4 \stemDown b4 c'4 |
    b4 e'4 d'2 |
    f'4 d'4 c'4 b4 |
    c'4 b4 c'2 |
    c'4 c'4 c'4 e'4 |
    c'4 b4 \stemUp g2 |
    f4 e4 g4 a4 |
    \stemDown c'4 d'4 e'2\fermata |
          }
      }
      \new Lyrics = "lyrtx1" \lyricsto "vTx1" { 
      "Lift" "your" "voi" -- "ces," "sing" "and" "play," "wel" -- "come" "in" "the" "bright"
      "new" "day;" "let" "the" "hills" "and" "val" -- "leys" "ring," "all" "the" "world"
      "be" -- "gin" "to" "sing."
      }
      \new Staff = "b" \with { instrumentName = "Bass" shortInstrumentName = "B." } { \clef "bass"
          \new Voice = "vBx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key c \major \stemUp c4\mf a,4 g,4 c4 |
    g,4 c4 \stemDown g2 |
    f4 g4 a4 g4 |
    \stemUp c4 g,4 c2 |
    c4 a,4 f,4 c4 |
    \stemDown a4 g4 \stemUp c2 |
    <f, f>4^\markup { \italic "div." } \stemDown <a, a>4 \stemUp <g, g>4 <d, d>4 |
    <g, g>4 <g, g>4 <c, c>2\fermata |
          }
      }
      \new Lyrics = "lyrbx1" \lyricsto "vBx1" { 
      "Lift" "your" "voi" -- "ces," "sing" "and" "play," "wel" -- "come" "in" "the" "bright"
      "new" "day;" "let" "the" "hills" "and" "val" -- "leys" "ring," "all" "the" "world"
      "be" -- "gin" "to" "sing."
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
