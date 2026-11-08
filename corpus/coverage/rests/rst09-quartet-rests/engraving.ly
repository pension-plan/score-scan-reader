\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Quartet Fughetta"
  subtitle = "rests in a string quartet: staggered entries and a general pause"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #22
  indent = 24\mm
  short-indent = 12\mm
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "stP1" \with { instrumentName = "Violin I" shortInstrumentName = "Vn. I" } { \clef "treble"
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 3/4 \key f \major \tempo "Allegretto" c''4 f''4 a''4 |
    g''8[ f''8] e''4 c''4 |
    d''4 r4 r8 c''8 |
    bes'4 r4 r4 | \break
    R2. |
    r4 a'4 c''4 |
    f''2 r4 |
    r8. e''16 d''4 r4 | \break
    R2.\fermata |
    c''4 r8 a'8 f'4 |
    g'4. r8 a'4 |
    f'2.\fermata \bar "|." |
          }
      }
      \new Staff = "stP2" \with { instrumentName = "Violin II" shortInstrumentName = "Vn. II" } { \clef "treble"
          \new Voice = "vP2x1" {
    \autoBeamOff
    \key f \major R2. |
    R2. |
    f'4 bes'4 d''4 |
    c''8[ bes'8] a'4 f'4 |
    g'4 r4 r4 |
    r4 f'4 a'4 |
    c''4 r4 r4 |
    r4 g'4 r4 |
    R2.\fermata |
    a'4 r8 f'8 c'4 |
    e'4. r8 e'4 |
    c'2.\fermata |
          }
      }
      \new Staff = "stP3" \with { instrumentName = "Viola" shortInstrumentName = "Va." } { \clef "alto"
          \new Voice = "vP3x1" {
    \autoBeamOff
    \key f \major R2. |
    R2. |
    R2. |
    R2. |
    c'4 f'4 a'4 |
    g'8[ f'8] e'4 c'4 |
    r4 a4 c'4 |
    bes4 r4 r4 |
    R2.\fermata |
    f4 r4 a4 |
    c'4. r8 c'4 |
    a2.\fermata |
          }
      }
      \new Staff = "stP4" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vP4x1" {
    \autoBeamOff
    \key f \major R2. |
    R2. |
    r2 bes,4 |
    a,4 r4 r4 |
    r4 c4 r4 |
    f,2 r4 |
    r4 r8 c8 a,4 |
    bes,4 r4 r4 |
    R2.\fermata |
    f,4 r4 f,4 |
    c4. r8 c4 |
    f,2.\fermata |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
