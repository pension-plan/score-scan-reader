\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Interlude"
  subtitle = "Oboe (orchestral part)"
  composer = "OMR challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Oboe" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \set Score.skipBars = ##t
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \tempo "Andante" R1*12 |
    \mark "A" c''4 r4 r8 d''8 r16 e''16 r32 f''32 r64 g''64 r64 a''64 |
    r4. e''8 d''4.. r16 | \break
    r8. c''16 r8.. b'32 a'2 |
    r2.. g'8 |
    c''1\fermata |
    \time 3/4 R2.*3 |
    \mark "B" R2.\fermata | \break
    \time 6/8 c''8[ r8 c''8] d''8[ r8 d''8] |
    e''4. r4. |
    r4 r8 f''8[ g''8 a''8] |
    R2. |
    \tuplet 2/3 { g''8 r8 } r4. | \break
    \defaultTimeSignature \time 2/2 \mark "C" R1*5 |
    \tuplet 3/2 { r4 c''4 d''4 } e''2 |
    r1 | \break
    \time 4/2 c''1 r1 |
    R\breve | \break
    \numericTimeSignature \time 4/4 \mark "D" R1*2 |
    r4 c''4 r4 r8.. c''32 |
    \tuplet 3/2 { c''8[ r8 c''8] } r4 r2 |
    c''2.\fermata r4\fermata \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
