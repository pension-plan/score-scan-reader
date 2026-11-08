\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Quartet in Changing Meters"
  subtitle = "for string quartet"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "stP1" \with { instrumentName = "Violin I" shortInstrumentName = "Vn. I" } { \clef "treble"
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key a \minor \tempo "Allegro" e''4 \tuplet 3/2 { d''8[ c''8 b'8] } a'2~ |
    \time 3/4 a'4 \tuplet 3/2 { b'4 c''4 d''4 } |
    \time 5/8 e''8[ d''8 c''8] b'8[ a'8~] | \break
    \time 7/8 a'8[ gis'8] b'8[ c''8] d''8[ c''8 b'8] |
    \time 2/4 \tuplet 5/4 { a'16[ b'16 c''16 d''16 e''16] } f''4~ |
    \time 6/8 f''4. e''4.~ | \break
    \defaultTimeSignature \time 4/4 e''4 c''4 b'4 \tuplet 3/2 { c''8[ b'8 a'8] } |
    \defaultTimeSignature \time 2/2 a'1 \bar "|." |
          }
      }
      \new Staff = "stP2" \with { instrumentName = "Violin II" shortInstrumentName = "Vn. II" } { \clef "treble"
          \new Voice = "vP2x1" {
    \autoBeamOff
    \key a \minor c''2 \tuplet 3/2 { b'4 a'4 g'4 } |
    f'2 f'4 |
    c''4. g'4 |
    e'4 f'4 e'4. |
    \tuplet 3/2 { e'8[ f'8 g'8] } a'4 |
    \tuplet 2/3 { a'8[ b'8] } c''4. |
    b'2 gis'2 |
    e'1 |
          }
      }
      \new Staff = "stP3" \with { instrumentName = "Viola" shortInstrumentName = "Va." } { \clef "alto"
          \new Voice = "vP3x1" {
    \autoBeamOff
    \key a \minor a2 e'2 |
    d'2.~ |
    d'4. e'4 |
    c'4 d'4 b4. |
    c'4 \tuplet 3/2 { d'8[ c'8 b8] } |
    a4. a4. |
    f'2 e'2 |
    c'1 |
          }
      }
      \new Staff = "stP4" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vP4x1" {
    \autoBeamOff
    \key a \minor a,2 c2 |
    d2 d4 |
    e4. e,4 |
    a,4 d4 e4. |
    a,2 |
    d4. c4. |
    d2 e2 |
    a,1 |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
