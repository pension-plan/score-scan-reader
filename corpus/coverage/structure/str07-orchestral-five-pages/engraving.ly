\version "2.24.0"
#(set-global-staff-size 16)
\header {
  title = "Little Overture"
  subtitle = "for small orchestra"
  composer = "Coverage corpus (2026)"
  copyright = "CC0 1.0"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  indent = 20\mm
  short-indent = 10\mm
  ragged-bottom = ##f
  system-system-spacing.basic-distance = #16
  top-margin = 12\mm
  bottom-margin = 12\mm
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "fl" \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { \clef "treble"
          \new Voice = "vFLx1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Allegro moderato" 4 = 112 \defaultTimeSignature \time 4/4 \key g \major R1 |
    R1 |
    R1 |
    R1 |
    \break \segnoMark 1 \mark \markup { \box \bold "A" } \stemDown g''4\mf d''4 b'4 d''4 |
    e''4 g''4 e''4 c''4 |
    d''4 fis''4 a''4 fis''4 |
    g''2 r2 |
    \pageBreak e''4 g''4 b''4 g''4 |
    a''4 e''4 fis''4 d''4 |
    b'4 d''4 e''4 c''4 |
    \stemNeutral a'1 |
    \break \stemDown d''8[ c''8] b'8[ c''8] d''4 g''4 |
    e''8[ d''8] c''8[ d''8] e''4 a''4 |
    fis''4 a''4 c'''4 fis''4 |
    \stemNeutral g''1 \textEndMark \markup { \bold \italic "Fine" } \bar ".|:-|." |
    \pageBreak \mark \markup { \box \bold "B" } R1 |
    R1 |
    R1 |
    R1 |
    \break R1 |
    R1 |
    R1 |
    \set Score.repeatCommands = #'((volta "1.")) R1 |
    \pageBreak R1 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) R1 |
    R1 \bar "||" |
    \set Score.repeatCommands = #'((volta #f)) \mark \markup { \box \bold "C" } R1 \bar ".|:-|" |
    \break R1 |
    R1 |
    R1 |
    R1 \bar ":|." |
    \pageBreak \mark \markup { \box \bold "D" } \stemDown g''4\f b''4 d'''4 b''4 |
    c'''4 g''4 e''4 c''4 |
    a''4 e''4 d''4 fis''4 |
    d''2 g''2 |
    \break e''4 b'4 c''4 e''4 |
    \stemUp a'4 \stemDown c''4 fis''4 a''4 |
    g''4 b''4 a''4 fis''4 |
    \stemNeutral g''1 \textEndMark \markup { \bold \italic "D.S. al Fine" } \bar "||" |
          }
      }
      \new Staff = "ob" \with { instrumentName = "Oboe" shortInstrumentName = "Ob." } { \clef "treble"
          \new Voice = "vOBx1" {
    \autoBeamOff
    \key g \major R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    \stemDown b'4\p e''4 g''4 e''4 |
    c''4 e''4 a''4 e''4 |
    dis''4 fis''4 a''4 fis''4 |
    e''2 b'2 |
    c''4 e''4 g''4 e''4 |
    \stemUp a'4 \stemDown c''4 d''4 \stemUp fis'4 |
    g'4 \stemDown b'4 e''4 g''4 |
    a''4 e''4 dis''4 b'4 |
    e''2. r4 |
    c''4 e''4 d''4 c''4 |
    \stemNeutral b'1 |
    \stemDown e''4\mf g''4 c'''4 g''4 |
    g''4 d''4 b'4 \stemUp g'4 |
    \stemDown c''4 e''4 d''4 fis''4 |
    g''4 e''4 a''4 e''4 |
    d''2 c''2 |
    g''4\f b''4 d'''4 b''4 |
    c'''4 g''4 e''4 c''4 |
    a''4 e''4 d''4 fis''4 |
    d''2 g''2 |
    e''4 b'4 c''4 e''4 |
    \stemUp a'4 \stemDown c''4 fis''4 a''4 |
    g''4 b''4 a''4 fis''4 |
    \stemNeutral g''1 |
          }
      }
      \new Staff = "bn" \with { instrumentName = "Bassoon" shortInstrumentName = "Bn." } { \clef "bass"
          \new Voice = "vBNx1" {
    \autoBeamOff
    \key g \major R1 |
    R1 |
    R1 |
    R1 |
    \stemUp g,4\mf \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 \stemUp c4 \stemDown g4 |
    d4 a4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp e,4 b,4 e,4 b,4 |
    a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp c4 \stemDown g4 |
    d4 a4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 \stemUp a,4 \stemDown e4 |
    d4 a4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    \stemUp c4\mf \stemDown g4 \stemUp c4 \stemDown g4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 d4 a4 |
    \stemUp e,4 b,4 a,4 \stemDown e4 |
    d4 a4 d4 a4 |
    \stemUp g,4\f \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 \stemUp c4 \stemDown g4 |
    \stemUp a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp e,4 b,4 c4 \stemDown g4 |
    \stemUp a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
          }
      }
    >>
    \new StaffGroup <<
      \new Staff = "v1" \with { instrumentName = "Violin I" shortInstrumentName = "Vl. I" } { \clef "treble"
          \new Voice = "vV1x1" {
    \autoBeamOff
    \key g \major \stemDown d''2\f b'2 |
    c''4 e''4 d''4 \stemUp a'4 |
    \stemDown b'4 d''4 e''4 b'4 |
    c''2 c''4 c''4 |
    g''4 d''4 b'4 d''4 |
    e''4 g''4 e''4 c''4 |
    d''4 fis''4 a''4 fis''4 |
    g''2 r2 |
    e''4 g''4 b''4 g''4 |
    a''4 e''4 fis''4 d''4 |
    b'4 d''4 e''4 c''4 |
    \stemNeutral a'1 |
    \stemDown d''8[ c''8] b'8[ c''8] d''4 g''4 |
    e''8[ d''8] c''8[ d''8] e''4 a''4 |
    fis''4 a''4 c'''4 fis''4 |
    \stemNeutral g''1 |
    \stemDown b'4\p e''4 g''4 e''4 |
    c''4 e''4 a''4 e''4 |
    dis''4 fis''4 a''4 fis''4 |
    e''2 b'2 |
    c''4 e''4 g''4 e''4 |
    \stemUp a'4 \stemDown c''4 d''4 \stemUp fis'4 |
    g'4 \stemDown b'4 e''4 g''4 |
    a''4 e''4 dis''4 b'4 |
    e''2. r4 |
    c''4 e''4 d''4 c''4 |
    \stemNeutral b'1 |
    \stemDown e''4\mf g''4 c'''4 g''4 |
    g''4 d''4 b'4 \stemUp g'4 |
    \stemDown c''4 e''4 d''4 fis''4 |
    g''4 e''4 a''4 e''4 |
    d''2 c''2 |
    g''4\f b''4 d'''4 b''4 |
    c'''4 g''4 e''4 c''4 |
    a''4 e''4 d''4 fis''4 |
    d''2 g''2 |
    e''4 b'4 c''4 e''4 |
    \stemUp a'4 \stemDown c''4 fis''4 a''4 |
    g''4 b''4 a''4 fis''4 |
    \stemNeutral g''1 |
          }
      }
      \new Staff = "v2" \with { instrumentName = "Violin II" shortInstrumentName = "Vl. II" } { \clef "treble"
          \new Voice = "vV2x1" {
    \autoBeamOff
    \key g \major \stemUp g'2\f g'2 |
    g'2 fis'2 |
    g'2 g'2 |
    a'2 a'2 |
    g'2 g'2 |
    g'2 g'2 |
    fis'2 fis'2 |
    g'2 g'2 |
    g'2 g'2 |
    a'2 a'2 |
    g'2 g'2 |
    fis'2 fis'2 |
    g'2 g'2 |
    g'2 a'2 |
    a'2 a'2 |
    g'2 g'2 |
    g'2\p g'2 |
    a'2 a'2 |
    a'2 a'2 |
    g'2 g'2 |
    g'2 g'2 |
    e'2 d'2 |
    d'2 e'2 |
    e'2 dis'2 |
    e'2 e'2 |
    e'2 d'2 |
    d'2 d'2 |
    c'2\mf c'2 |
    b2 b2 |
    c'2 d'2 |
    e'2 e'2 |
    d'2 d'2 |
    d'2\f d'2 |
    c'2 c'2 |
    c'2 d'2 |
    d'2 d'2 |
    e'2 e'2 |
    e'2 d'2 |
    d'2 d'2 |
    d'2 d'2 |
          }
      }
      \new Staff = "va" \with { instrumentName = "Viola" shortInstrumentName = "Va." } { \clef "alto"
          \new Voice = "vVAx1" {
    \autoBeamOff
    \key g \major \stemUp g2\f g2 |
    g2 fis2 |
    g2 g2 |
    a2 a2 |
    g2 g2 |
    g2 g2 |
    fis2 fis2 |
    g2 g2 |
    g2 g2 |
    a2 a2 |
    g2 g2 |
    fis2 fis2 |
    g2 g2 |
    g2 a2 |
    a2 a2 |
    g2 g2 |
    g2\p g2 |
    a2 a2 |
    a2 a2 |
    g2 g2 |
    g2 g2 |
    a2 a2 |
    g2 g2 |
    a2 a2 |
    g2 g2 |
    a2 a2 |
    g2 g2 |
    g2\mf g2 |
    g2 g2 |
    g2 fis2 |
    g2 a2 |
    a2 a2 |
    g2\f g2 |
    g2 g2 |
    a2 a2 |
    g2 g2 |
    g2 g2 |
    a2 a2 |
    g2 fis2 |
    g2 g2 |
          }
      }
      \new Staff = "vc" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vVCx1" {
    \autoBeamOff
    \key g \major \stemUp g,4\f \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp e,4 b,4 |
    a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 \stemUp c4 \stemDown g4 |
    d4 a4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp e,4 b,4 e,4 b,4 |
    a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp c4 \stemDown g4 |
    d4 a4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 \stemUp a,4 \stemDown e4 |
    d4 a4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp e,4\p b,4 e,4 b,4 |
    a,4 \stemDown e4 \stemUp a,4 \stemDown e4 |
    \stemUp b,4 \stemDown fis4 \stemUp b,4 \stemDown fis4 |
    \stemUp e,4 b,4 e,4 b,4 |
    c4 \stemDown g4 \stemUp c4 \stemDown g4 |
    \stemUp a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp e,4 b,4 |
    a,4 \stemDown e4 \stemUp b,4 \stemDown fis4 |
    \stemUp e,4 b,4 e,4 b,4 |
    a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4\mf \stemDown g4 \stemUp c4 \stemDown g4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 d4 a4 |
    \stemUp e,4 b,4 a,4 \stemDown e4 |
    d4 a4 d4 a4 |
    \stemUp g,4\f \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp c4 \stemDown g4 \stemUp c4 \stemDown g4 |
    \stemUp a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
    \stemUp e,4 b,4 c4 \stemDown g4 |
    \stemUp a,4 \stemDown e4 d4 a4 |
    \stemUp g,4 \stemDown d4 d4 a4 |
    \stemUp g,4 \stemDown d4 \stemUp g,4 \stemDown d4 |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
