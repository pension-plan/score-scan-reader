\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Song of Rejoicing"
  subtitle = "for SATB choir and piano"
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
  indent = 18\mm
  short-indent = 9\mm
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "sa" \with { instrumentName = \markup \center-column { "Soprano" "Alto" } shortInstrumentName = \markup \center-column { "S." "A." } } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Joyfully" 4 = 112 \numericTimeSignature \time 4/4 \key c \major \voiceOne R1 |
    \stemUp e'4\mf g'4 c''4 b'4 |
    a'4 g'4 e'2 |
    f'4 a'4 g'4 e'4 |
    d'4 e'4 d'2 |
    \break c''4\f c''4 b'4 a'4 |
    g'4 a'4 g'2 |
    e'4 g'4 f'4 d'4 |
    c'4 d'4 c'2 |
    R1 |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo R1 |
    \stemDown c'4 c'4 c'4 d'4 |
    f'4 e'4 e'2 |
    d'4 c'4 c'4 c'4 |
    b4 c'4 b2 |
    c'4 c'4 d'4 f'4 |
    e'4 f'4 e'2 |
    e'4 e'4 d'4 b4 |
    g4 b4 g2 |
    R1 |
          }
        >>
      }
      \new Lyrics = "lyrsax1" \lyricsto "vSx1" { 
      "Come," "ye" "peo" -- "ple," "raise" "the" "song," "let" "the" "cho" -- "rus" "now"
      "be" "strong;" "hand" "in" "hand" "and" "voice" "with" "voice," "all" "cre" -- "a" --
      "tion," "now" "re" -- "joice."
      }
      \new Staff = "tb" \with { instrumentName = \markup \center-column { "Tenor" "Bass" } shortInstrumentName = \markup \center-column { "T." "B." } } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key c \major \voiceOne R1 |
    \stemUp g4\mf e4 e4 g4 |
    c'4 c'4 c'2 |
    a4 f4 e4 e4 |
    g4 g4 g2 |
    e4\f e4 g4 c'4 |
    c'4 c'4 c'2 |
    c'4 c'4 a4 g4 |
    e4 d4 e2 |
    R1 |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo R1 |
    \stemDown c4 c4 a,4 g,4 |
    f,4 c4 a2 |
    d4 f,4 c4 a,4 |
    g,4 c4 g2 |
    c4 a,4 g,4 f,4 |
    c4 f,4 c2 |
    a4 c4 d4 g,4 |
    c4 g,4 c2 |
    R1 |
          }
        >>
      }
    >>
    \new PianoStaff \with { instrumentName = "Piano" shortInstrumentName = "Pno." } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vPx1" {
    \autoBeamOff
    \key c \major \stemUp <e' g' c''>2\mf <d' g' b'>2 |
    <e' g' c''>2 <c' e' a'>4 <d' g' b'>4 |
    <c' f' a'>2 <c' e' g'>2 |
    <d' f' a'>2 <c' e' g'>2 |
    <b d' g'>2 <b d' g'>2 |
    <e' g' c''>4 <c' e' a'>4 <d' g' b'>4 <c' f' a'>4 |
    <e' g' c''>2 <c' e' g'>2 |
    <c' e' a'>2 <d' f' a'>4 <b d' g'>4 |
    <c' e' g'>2\< <b d' g'>2 |
    <e' g' c''>1\fermata\!\f |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \autoBeamOff
    \key c \major \stemUp c4 g,4 c4 g,4 |
    c4 \stemDown e4 \stemUp a,4 g,4 |
    f,4 a,4 c2 |
    \stemDown d4 f4 \stemUp c4 a,4 |
    g,4 \stemDown d4 \stemUp g,2 |
    a,4 f,4 g,4 f,4 |
    c4 f,4 c2 |
    a,4 c4 \stemDown d4 \stemUp g,4 |
    c4 g,4 c2 |
    <c, c>1\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
