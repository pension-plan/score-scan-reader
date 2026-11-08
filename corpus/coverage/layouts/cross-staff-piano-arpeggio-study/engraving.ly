\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Arpeggio Study"
  subtitle = "for piano"
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
  indent = 14\mm
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Con moto" 4 = 80 \numericTimeSignature \time 4/4 \key c \minor \stemUp g'2\p( f'2 |
    ees'2 d'2) |
    \stemDown c''2( bes'2 |
    \stemUp aes'2 g'2) |
    \break \stemDown ees''2\mf( d''2 |
    c''2 b'2) |
    c''4 \change Staff = "lh" g4( \change Staff = "rh" c''2) |
    <ees' g' c''>1\fermata \bar "|." |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \minor \stemUp c8\sustainOn[ g8 \change Staff = "rh" \stemDown c'8 ees'8] \change Staff = "lh" \stemUp b,8[ g8\sustainOff \change Staff = "rh" \stemDown d'8 f'8] |
    \change Staff = "lh" \stemUp c8[ g8 \change Staff = "rh" \stemDown c'8 ees'8] \change Staff = "lh" \stemUp g,8[ g8 \change Staff = "rh" \stemDown b8 d'8] |
    \change Staff = "lh" \stemUp aes,8\sustainOn[ ees8 \change Staff = "rh" \stemDown c'8 ees'8] \change Staff = "lh" \stemUp ees8[ g8\sustainOff \change Staff = "rh" \stemDown bes8 ees'8] |
    \change Staff = "lh" \stemUp f,8[ c8 \change Staff = "rh" \stemDown aes8 c'8] \change Staff = "lh" \stemUp g,8[ d8 \change Staff = "rh" \stemDown b8 d'8] |
    \change Staff = "lh" \stemUp c8\<[ g8 \change Staff = "rh" \stemDown c'8 ees'8] \change Staff = "lh" \stemUp g,8[ d8 \change Staff = "rh" \stemDown b8 f'8\!] |
    \change Staff = "lh" \stemUp aes,8[ ees8 \change Staff = "rh" \stemDown c'8 ees'8] \change Staff = "lh" \stemUp g,8[ d8 \change Staff = "rh" \stemDown g8 b8] |
    \change Staff = "lh" \stemUp c8[ g8 \change Staff = "rh" \stemDown c'8 ees'8] \change Staff = "lh" \stemUp f,8[ c8 \change Staff = "rh" \stemDown aes8 c'8] |
    \change Staff = "lh" <c, c>1\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
