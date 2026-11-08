\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Minuet"
  subtitle = "for string quartet"
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
  indent = 20\mm
  short-indent = 10\mm
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "v1" \with { instrumentName = "Violin I" shortInstrumentName = "Vn. I" } { \clef "treble"
          \new Voice = "vV1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Tempo di Minuetto" 4 = 126 \time 3/4 \key c \major \stemDown e''4\f( g''4 e''4) |
    d''4-. f''4-. d''4-. |
    c''8[( d''8] e''8[ f''8] g''4) |
    a''4-> g''4-> f''4-> |
    \break e''2 g''4 |
    c'''4( b''4 a''4) |
    f''4.( e''8 d''4) |
    c''2 r4 \bar ":|." |
    \break g''4\p^\markup { \italic "dolce" } a''8[( g''8] f''8[ e''8]) |
    d''4( g''2) |
    <c'' e''>4\< <b' d''>4 <b' f''>4\! |
    \stemUp <e' c''>2.\fermata |
          }
      }
      \new Staff = "v2" \with { instrumentName = "Violin II" shortInstrumentName = "Vn. II" } { \clef "treble"
          \new Voice = "vV2x1" {
    \autoBeamOff
    \key c \major \stemDown c''4\f( e''4 c''4) |
    b'4-. d''4-. b'4-. |
    \stemUp g'4( \stemDown c''4 e''4) |
    f''4-> e''4-> d''4-> |
    c''2 e''4 |
    \stemUp a'4( g'4 fis'4) |
    a'4.( g'8 f'4) |
    e'2 r4 |
    \stemDown e''4\p f''8[( e''8] d''8[ c''8]) |
    b'4( d''2) |
    \stemUp g'4\< g'4 g'4\! |
    g'2.\fermata |
          }
      }
      \new Staff = "va" \with { instrumentName = "Viola" shortInstrumentName = "Va." } { \clef "alto"
          \new Voice = "vVAx1" {
    \autoBeamOff
    \key c \major \stemDown g'4\f g'4 g'4 |
    g'4-. g'4-. g'4-. |
    e'4 g'4 c''4 |
    c''4-> c''4-> b'4-> |
    g'2 c''4 |
    e'4 e'4 e'4 |
    d'4 d'4 \stemUp b4 |
    \stemDown c'2 r4 |
    c'4\p^\markup { \italic "pizz." } r4 c'4 |
    \stemUp g4 r4 g4 |
    \stemDown e'4\<^\markup { \italic "arco" } f'4 d'4\! |
    e'2.\fermata |
          }
      }
      \new Staff = "vc" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vVCx1" {
    \autoBeamOff
    \key c \major \stemUp c4\f c4 c4 |
    g,4-. g,4-. g,4-. |
    c4 \stemDown e4 g4 |
    f4-> g4-> \stemUp g,4-> |
    c2 c4 |
    a,4 a,4 a,4 |
    \stemDown d4 g4 \stemUp g,4 |
    c2 r4 |
    c4\p^\markup { \italic "pizz." } r4 c4 |
    g,4 r4 g,4 |
    c4\<^\markup { \italic "arco" } \stemDown g4 \stemUp g,4\! |
    c2.\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
