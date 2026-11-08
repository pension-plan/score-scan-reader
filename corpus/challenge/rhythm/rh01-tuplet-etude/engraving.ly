\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Tuplet Etude"
  subtitle = "for flute"
  composer = "OMR challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \defaultTimeSignature \time 4/4 \key c \major \tempo "Allegretto" c''4 \tuplet 3/2 { b'8[ c''8 d''8] } e''4 \tuplet 3/2 { d''8[ c''8 b'8] } |
    \tuplet 3/2 { a'4 b'4 c''4 } d''2 |
    \tuplet 3/2 { r8 g'8[ a'8] } \tuplet 3/2 { b'8[ r8 b'8] } \tuplet 3/2 { c''4 d''8 } e''4 |
    \tuplet 5/4 { c''16[ d''16 e''16 f''16 g''16] } \tuplet 6/4 { a''16[ g''16 f''16 e''16 d''16 c''16] } \tuplet 7/4 { b'16[ c''16 d''16 e''16 f''16 g''16 a''16] } b''4 | \break
    \tuplet 3/2 { g''8[ f''8 e''8] } \tuplet 3/2 { d''8[ e''8 f''8] } \tuplet 3/2 { e''8[ d''8 c''8] } \tuplet 3/2 { b'8[ c''8 d''8] } |
    \once \omit TupletNumber \once \omit TupletBracket \tuplet 3/2 { e''8[ d''8 c''8] } \once \omit TupletNumber \once \omit TupletBracket \tuplet 3/2 { b'8[ a'8 g'8] } \once \omit TupletNumber \once \omit TupletBracket \tuplet 3/2 { a'8[ b'8 c''8] } \once \omit TupletNumber \once \omit TupletBracket \tuplet 3/2 { d''8[ e''8 fis''8] } |
    g''2~ \tuplet 3/2 { g''4 fis''4 e''4 } |
    d''2. r4\fermata | \break
    \defaultTimeSignature \time 2/2 \tuplet 3/2 { c''2 d''2 e''2 } |
    f''2 \tuplet 3/2 { e''4 d''4 c''4 } |
    \tuplet 3/2 { b'4 c''2 } \tuplet 3/2 { a'2 g'4 } |
    \tuplet 3/2 { f'4 g'4 a'4 } \tuplet 3/2 { b'4 r4 b'4 } |
    c''1 | \break
    \time 6/8 c''8[ d''8 e''8] \tuplet 2/3 { f''8[ g''8] } |
    \tuplet 2/3 { a''8[ g''8] } \tuplet 2/3 { f''8[ e''8] } |
    d''4. \tuplet 4/3 { c''8[ b'8 a'8 g'8] } |
    a'8[ r8 a'8] g'4. | \pageBreak
    \time 12/8 \tuplet 4/3 { c''8[ d''8 e''8 f''8] } g''4. \tuplet 2/3 { a''8[ g''8] } f''8[ e''8 d''8] |
    c''4.~ c''8[ b'8 a'8] g'8[ \tuplet 3/2 { a'16 b'16 c''16 } d''8] e''4. | \break
    \numericTimeSignature \time 4/4 \tuplet 3/2 { c''16[ d''16 e''16 } \tuplet 3/2 { f''16 e''16 d''16] } c''4 \tuplet 3/2 { b'32[ c''32 d''32] } e''8. r4 |
    \tuplet 5/4 { d''8[ e''8 f''8 g''8 a''8] } \tuplet 3/2 { b''4 a''4 g''4 } | \break
    \tuplet 3/2 { f''4 e''8 } \tuplet 3/2 { d''8 c''4 } \tuplet 6/4 { b'16[ c''16 d''16 e''16 f''16 g''16] } a''4 |
    c'''2.\fermata r4 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
