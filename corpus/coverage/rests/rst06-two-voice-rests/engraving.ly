\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Hocket for Two Flutes"
  subtitle = "raised and lowered rests, two voices on one staff (flutes 1.2)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Flutes 1.2" } { \clef "treble"
      <<
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \tempo "Allegro moderato" \voiceOne e''4 f''4\rest g''4 f''4\rest |
    c'''2 f''2\rest |
    g''8 f''8\rest a''8 f''8\rest b''8 f''8\rest c'''4 | \break
    \once \override MultiMeasureRest.staff-position = #2 R1 |
    d''4 e''4 f''4 g''4 |
    g''16 f''16\rest e''16 f''16\rest d''4 f''2\rest | \break
    f''4.\rest e''8 d''2 |
    c'''4 b''4 a''4 f''4\rest |
    \once \override MultiMeasureRest.staff-position = #2 R1 | \break
    f''8\rest e''8 f''8\rest g''8 f''4\rest a''4 |
    f''2\rest g''2 |
    e''2 c''2\fermata \bar "|." |
        }
        \new Voice = "vP1x2" {
    \autoBeamOff
    \voiceTwo e'4\rest g'4 e'4\rest a'4 |
    e'2\rest b'2 |
    e'8\rest g'8 e'8\rest a'8 e'8\rest b'8 e'4\rest |
    g'4 a'4 b'4 c''4 |
    \once \override MultiMeasureRest.staff-position = #-6 R1 |
    e'4\rest g'16 e'16\rest a'16 e'16\rest b'2 |
    g'2 e'4.\rest g'8 |
    a'4 g'4 f'4 e'4\rest |
    \once \override MultiMeasureRest.staff-position = #-6 R1 |
    e'8\rest c''8 e'8\rest b'8 e'4\rest c''4 |
    c''2 e'2\rest |
    g'2 e'2\fermata |
        }
      >>
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
