\version "2.24.0"
\include "omrtruth.ily"
#(set-global-staff-size 18)
\paper { #(set-paper-size "a4") }
%% Short piano piece composed for this test (CC0): chords, beams, seconds, 2 voices, ledger lines.
\header { title = "Little Study" composer = "Test (CC0)" tagline = ##f }
rh = { \omrVoice "RH" \clef treble \key c \major \time 4/4
  <e' g' c''>4 <f' a' c''> <g' b' d''>2 | <e' g' c''>4 e''8 d'' c''4 g' |
  a'4 <f' a' c''> <d' g' b'>2 | <e' g' c''>1 |
  c''8 d'' e'' f'' g''4 <g'' a''> | <f'' a''>4 e''8 d'' <c'' d''>2 |
  << { e''4 f'' g'' a'' } \\ { c''2 b' } >> | <c'' e''>2. r4 |
  g''8 a'' b'' c''' d'''4 c''' | b''4 a''8 g'' f''4 e'' |
  d''8 c'' b' a' g'4 <b' d''> | <c'' e'' g''>1 \bar "|." }
lh = { \omrVoice "LH" \clef bass \key c \major \time 4/4
  c8 g e' g c g e' g | c8 g e' g c g e' g |
  f,8 c a c g, d b d | c8 g e' g c2 |
  <c e>4 <c e> <b, d> <b, f> | <a, c>4 <a, f> <g, b,>2 |
  << { g4 a b2 } \\ { c2 g, } >> | c2. r4 |
  e,8 b, g b f, c a c | g,8 d b d c g e g |
  f,4 g, a, g, | <c, c>1 }
\score {
  \new PianoStaff <<
    \new Staff = "up" \new Voice = "rh" \rh
    \new Staff = "down" \new Voice = "lh" \lh
  >>
  \layout { }
}
