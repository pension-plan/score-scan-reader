\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Chorale Prelude"
  subtitle = "for organ (manuals and pedal)"
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
  indent = 18\mm
  short-indent = 10\mm
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Organ" } <<
      \new Staff = "man1" { \clef "treble"
        <<
          \new Voice = "vOx1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante maestoso" 4 = 63 \numericTimeSignature \time 4/4 \key a \minor \voiceOne \stemUp a'4\mf^\markup { \italic "Man. I: Principal 8', Octave 4'" } c''4 b'4 a'4 |
    gis'4 a'4 b'2\fermata |
    c''4 d''4 e''4 d''8[ c''8] |
    b'2 a'2\fermata |
    \break e''4\f d''4 c''4 b'4 |
    a'4 b'4 c''2\fermata |
    b'4 a'4 a'4 gis'4 |
    a'1\fermata |
          }
          \new Voice = "vOx2" {
    \autoBeamOff
    \voiceTwo \stemDown e'4 e'4 e'4 c'4 |
    e'4 e'4 e'2\fermata |
    e'4 f'4 g'4 g'8[ e'8] |
    e'2 e'2\fermata |
    e'4 g'4 e'4 gis'4 |
    f'4 d'4 e'2\fermata |
    e'4 c'4 d'4 b4 |
    cis'1\fermata |
          }
        >>
      }
      \new Staff = "man2" { \clef "bass"
          \new Voice = "vOx5" {
    \autoBeamOff
    \key a \minor \stemDown c'4^\markup { \italic "Man. II: Gedackt 8'" } c'4 gis4 a4 |
    b4 c'4 gis2\fermata |
    a4 a4 c'4 b8[ a8] |
    gis2 c'2\fermata |
    c'4 b4 c'4 e'4 |
    c'4 g4 g2\fermata |
    gis4 f4 f4 e4 |
    e1\fermata |
          }
      }
    >>
    \new Staff = "ped" \with { instrumentName = "Pedal" shortInstrumentName = "Ped." } { \clef "bass"
        \new Voice = "vOx9" {
    \autoBeamOff
    \key a \minor \stemDown a4^\markup { \italic "Ped.: Subbass 16', Octave 8'" } \stemUp c4 \stemDown e4 f4 |
    e4 \stemUp a,4 e,2\fermata |
    a,4 \stemDown d4 \stemUp c4 g,8[ a,8] |
    e,2 a,2\fermata |
    c4 \stemDown g4 a4 e4 |
    f4 g4 \stemUp c2\fermata |
    \stemDown e4 f4 d4 e4 |
    a,1\fermata |
        }
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
