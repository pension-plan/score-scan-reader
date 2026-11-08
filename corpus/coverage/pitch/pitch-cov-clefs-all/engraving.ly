\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Eight Clefs"
  subtitle = "one staff-position pattern read in eight clefs"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 18\mm
  short-indent = 8\mm
  ragged-bottom = ##t
  ragged-last = ##f
  system-system-spacing.basic-distance = #16
  top-margin = 15\mm
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Melody" shortInstrumentName = "Mel." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key c \major c'4 e'4 g'4 b'4 |
    d''8 f''8 a''8 f''8 d''4 b'4 |
    \clef "bass" f,4 a,4 c4 e4 |
    g8 b8 d'4 b8 g8 e4 |
    \break \clef "alto" d4 f4 a4 c'4 |
    e'8 g'8 b'8 g'8 e'4 c'4 |
    \clef "tenor" c4 e4 g4 b4 |
    d'8 f'8 a'4 f'8 d'8 b4 |
    \break \clef "soprano" a4 c'4 e'4 g'4 |
    b'8 d''8 f''8 d''8 b'4 g'4 |
    \clef "treble_8" d4 f4 a4 c'4 |
    e'8 g'8 b'4 g'8 e'8 c'4 |
    \break \clef "treble^8" c''4 e''4 g''4 b''4 |
    d'''8 f'''8 a'''8 f'''8 d'''4 b''4 |
    \clef "bass_8" f,,4 a,,4 c,4 e,4 |
    g,8 b,8 d4 b,8 g,8 e,4 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
