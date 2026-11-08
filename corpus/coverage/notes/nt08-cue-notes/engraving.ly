\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Cue Notes"
  subtitle = "flute part with cues"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Flute" } { \clef "treble"
      <<
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \oneVoice \stemDown c''4 d''4 e''4 f''4 |
    g''2 e''2 |
    \voiceTwo R1 | \break
    R1 |
    r2 \stemDown g'4 a'4 |
    \oneVoice \stemDown b'2 c''2 | \break
    \voiceTwo R1 |
    r4 \stemDown e''4 d''4 c''4 |
    R1 |
    \oneVoice c''1 \bar "|." |
        }
        \new CueVoice = "vP1x2" {
    \autoBeamOff
    \oneVoice s1 |
    s1 |
    \voiceOne \stemUp e''8[^"Ob." f''8] g''8[ a''8] b''4 a''4 |
    g''4. f''8 e''2 |
    d''8[ c''8] b'8[ a'8] s1*1/2 |
    \oneVoice s1 |
    \voiceOne \stemUp c''16[^"Vln. I" d''16 e''16 f''16] g''4 g'2 |
    f'4 s1*3/4 |
    a'4^"Ob." b'4 <c'' e''>2 |
    \oneVoice s1 |
        }
      >>
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
