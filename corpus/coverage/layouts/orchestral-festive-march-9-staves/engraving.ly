\version "2.24.0"
#(set-global-staff-size 15)
\header {
  title = "Festive March"
  subtitle = "full score (excerpt)"
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
  indent = 22\mm
  short-indent = 10\mm
  system-system-spacing.basic-distance = #14
  print-page-number = ##t
  print-first-page-number = ##f
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "fl" \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { \clef "treble"
          \new Voice = "vFLx1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Allegro marziale" 4 = 116 \numericTimeSignature \time 4/4 \key d \major \stemDown fis''4\f a''4 fis''4 d''4 |
    e''4 g''4 e''4 cis''4 |
    d''8[ e''8] fis''8[ g''8] a''4 a''4 |
    a''2 r2 |
    \pageBreak \mark \markup { \box \bold "B" } b''4.\mf a''8 g''4 b''4 |
    a''4 fis''4 e''8[ fis''8] g''8[ e''8] |
    d''4\< fis''8[ e''8] d''4 b'4 |
    d''1\fermata\!\ff |
          }
      }
      \new Staff = "ob" \with { instrumentName = "Oboe" shortInstrumentName = "Ob." } { \clef "treble"
          \new Voice = "vOBx1" {
    \autoBeamOff
    \key d \major \stemDown d''4\f fis''4 d''4 \stemUp a'4 |
    \stemDown cis''4 e''4 cis''4 \stemUp a'4 |
    \stemDown a'8[ cis''8] d''8[ e''8] fis''4 fis''4 |
    e''2 r2 |
    d''4.\mf d''8 d''4 d''4 |
    d''4 d''4 cis''2 |
    \stemUp a'4\< \stemDown d''8[ cis''8] b'4 \stemUp g'4 |
    a'1\fermata\!\ff |
          }
      }
      \new Staff = "bn" \with { instrumentName = "Bassoon" shortInstrumentName = "Bn." } { \clef "bass"
          \new Voice = "vBNx1" {
    \autoBeamOff
    \key d \major \stemDown d4\f d4 d4 d4 |
    \stemUp a,4 a,4 a,4 a,4 |
    \stemDown d4 d4 d4 d4 |
    \stemUp a,2 r2 |
    g,4\mf g,4 g,4 g,4 |
    a,4 a,4 a,2 |
    \stemDown d4\< d4 \stemUp g,4 g,4 |
    d1\fermata\!\ff |
          }
      }
    >>
    \new Staff = "tp" \with { instrumentName = "Trumpet in C" shortInstrumentName = "Tpt." } { \clef "treble"
        \new Voice = "vTPx1" {
    \autoBeamOff
    \key d \major \stemDown d''4\f d''4 d''4 d''4 |
    \stemUp a'4 a'4 a'4 a'4 |
    \stemDown d''4 d''8[ d''8] d''4 d''4 |
    \stemUp a'2 r2 |
    R1 |
    R1 |
    \stemDown d''4\< d''4 d''4 d''4 |
    d''1\fermata\!\ff |
        }
    }
    \new Staff = "ti" \with { instrumentName = "Timpani" shortInstrumentName = "Timp." } { \clef "bass"
        \new Voice = "vTIx1" {
    \autoBeamOff
    \key d \major \stemDown d4\f r4 \stemUp a,4 r4 |
    a,4 r4 a,4 r4 |
    \stemDown d4 r4 d4 r4 |
    \stemUp a,2 r2 |
    R1 |
    a,4\mf r4 a,4 r4 |
    \stemDown d4\< r4 d4 r4 |
    d1\fermata\!\ff |
        }
    }
    \new StaffGroup <<
      \new GrandStaff \with { systemStartDelimiter = #'SystemStartSquare } <<
        \new Staff = "v1" \with { instrumentName = "Violin I" shortInstrumentName = "Vn. I" } { \clef "treble"
            \new Voice = "vV1x1" {
    \autoBeamOff
    \key d \major \stemDown a'8\f[ d''8] fis''8[ a''8] d'''4 a''4 |
    g''8[ e''8] cis''8[ a'8] e''4 cis''4 |
    d''16[ e''16 fis''16 g''16] a''8[ a''8] d'''4 a''4 |
    <cis'' a''>2 r2 |
    b''8\mf[ a''8] g''8[ fis''8] g''4 b''4 |
    a''8[ g''8] fis''8[ e''8] e''2 |
    d''8\<[ e''8] fis''8[ d''8] b'4 g''4 |
    <d'' fis''>1\fermata\!\ff |
            }
        }
        \new Staff = "v2" \with { instrumentName = "Violin II" shortInstrumentName = "Vn. II" } { \clef "treble"
            \new Voice = "vV2x1" {
    \autoBeamOff
    \key d \major \stemUp fis'8\f[ a'8] \stemDown d''8[ fis''8] a''4 fis''4 |
    e''8[ cis''8] \stemUp a'8[ g'8] \stemDown cis''4 \stemUp a'4 |
    \stemDown a'16[ cis''16 d''16 e''16] fis''8[ fis''8] a''4 fis''4 |
    \stemUp <e' a'>2 r2 |
    \stemDown g''8\mf[ fis''8] e''8[ d''8] d''4 g''4 |
    fis''8[ e''8] d''8[ cis''8] cis''2 |
    a'8\<[ cis''8] d''8[ a'8] \stemUp g'4 \stemDown d''4 |
    <a' d''>1\fermata\!\ff |
            }
        }
      >>
      \new Staff = "va" \with { instrumentName = "Viola" shortInstrumentName = "Va." } { \clef "alto"
          \new Voice = "vVAx1" {
    \autoBeamOff
    \key d \major \stemDown d'4\f d'4 d'4 d'4 |
    e'4 e'4 e'4 e'4 |
    d'4 d'8[ d'8] d'4 d'4 |
    e'2 r2 |
    d'4\mf d'4 d'4 d'4 |
    \stemUp a4 a4 a2 |
    a4\< a8[ a8] \stemDown d'4 d'4 |
    d'1\fermata\!\ff |
          }
      }
      \new Staff = "vc" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vVCx1" {
    \autoBeamOff
    \key d \major \stemDown d4\f d4 d4 d4 |
    \stemUp a,4 a,4 a,4 a,4 |
    \stemDown d4 d8[ d8] d4 d4 |
    \stemUp a,2 r2 |
    g,4\mf g,4 g,4 g,4 |
    a,4 a,4 a,2 |
    \stemDown d4\< d4 \stemUp g,4 g,4 |
    d,1\fermata\!\ff |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
