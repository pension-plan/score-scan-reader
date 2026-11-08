\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Fives, Sixes and Sevens"
  subtitle = "for flute"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \defaultTimeSignature \time 4/4 \key c \major \partial 1*1/8 \tempo "Leggiero" g'8 |
    \tuplet 5/4 { c''16[ d''16 e''16 f''16 g''16] } \tuplet 5/4 { a''16[ g''16 f''16 e''16 d''16] } c''2 |
    \tuplet 6/4 { b'16[ c''16 d''16 e''16 f''16 g''16] } \tuplet 6/4 { a''16[ g''16 f''16 e''16 d''16 c''16] } b'2 | \break
    \tuplet 7/4 { c''16[ d''16 e''16 f''16 g''16 a''16 b''16] } c'''4 \tuplet 7/8 { b''32[ a''32 g''32 f''32 e''32 d''32 c''32] } b'4 |
    \tuplet 5/4 { a'8[ b'8 c''8 d''8 e''8] } \tuplet 6/4 { f''8[ e''8 d''8 c''8 b'8 a'8~] } |
    \tuplet 5/4 { a'4 b'4 c''4 d''4 e''4~ } | \break
    \tuplet 7/4 { e''8[ d''8 c''8 b'8 a'8 g'8 f'8] } e'2 |
    \tuplet 6/4 { g'16[ a'16 b'16 c''16 d''16 e''16] } f''4 \tuplet 5/4 { e''16[ d''16 r16 d''16 c''16] } b'4 |
    c''2.. \bar "|."
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
