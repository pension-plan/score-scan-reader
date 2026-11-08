\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Nocturne in E-flat"
  subtitle = "for piano"
  composer = "Layout-challenge corpus (2026)"
  copyright = "Dedicated to the public domain (CC0 1.0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 14\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "up" { \clef "treble"
          \new Voice = "vPx1" {
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante cantabile" 4. = 52 \time 6/8 \key ees \major r2. |
    r4. r8 r8 bes'8 \bar "||" |
    \segnoMark 1 \stemUp bes'4.\mp^\markup { \italic "cantabile" } g''8( f''8 ees''8) |
    c''4.( ees''8 des''8 c''8) |
    \break d''4 f''8 aes''4 g''8 |
    g''4.~ g''4 r8 |
    ees''4.^\markup { \italic "cresc." } c''8( d''8 ees''8) |
    f''4. aes''8( g''8 f''8) \textEndMark \markup { \line {  \italic "To Coda"  \hspace #0.5 \raise #0.6 \musicglyph "scripts.coda" } } |
    \break f''4^\markup { \italic "dim." } d''8 bes'4 aes'8 |
    ees''4.~ ees''4 r8 |
    g''4.\mf^\markup { \italic "espressivo" } g''8( aes''8 g''8) |
    f''4. d''8( ees''8 f''8) |
    \break ees''4.\< c''4. |
    c''4.\!\f ees''8( f''8 ees''8) |
    aes''4.^\markup { \italic "dim." } f''8( ees''8 c''8) |
    d''4. f''8( aes''8 f''8) |
    \pageBreak \stemDown g''16\p[( ees''16 bes'16 g'16 ees'16 \change Staff = "down" \stemUp bes16] g16[ bes16 \change Staff = "up" \stemDown ees'16 g'16 bes'16 ees''16]) |
    \stemUp f''4.( d''8 c''8 bes'8) \textEndMark \markup { \bold \italic "D.S. al Coda" } \bar "||" |
    \break \codaMark 1 \tempo "Tranquillo" aes''4.\pp f''8( ees''8 c''8) |
    d''4. f''8( ees''8 d''8) |
    ees''4.~^\markup { \italic "rit." } ees''4. |
    c''4.( ees''4.) |
    <g' bes' ees''>2.\fermata^\markup { \italic "morendo" } \bar "|." |
          }
      }
      \new Staff = "down" { \clef "bass"
          \new Voice = "vPx5" {
    \key ees \major \stemUp ees,8\p\sustainOn_\markup { \italic "dolce" }[ bes,8 ees8] g8[ bes8 \change Staff = "up" \stemDown ees'8] |
    \change Staff = "down" \stemUp ees,8\sustainOff\sustainOn[ bes,8 ees8] g8[ bes8 \change Staff = "up" \stemDown ees'8] |
    \change Staff = "down" \stemUp ees,8\sustainOff\sustainOn[ bes,8 ees8] g8[ bes8 \change Staff = "up" \stemDown ees'8] |
    \change Staff = "down" \stemUp aes,8\sustainOff\sustainOn[ ees8 aes8] \change Staff = "up" \stemDown c'8[ ees'8 aes'8] |
    \change Staff = "down" \stemUp bes,,8\sustainOff\sustainOn[ f,8 bes,8] d8[ aes8 \change Staff = "up" \stemDown d'8] |
    \change Staff = "down" \stemUp ees,8\sustainOff\sustainOn[ bes,8 ees8] g8[ bes8 \change Staff = "up" \stemDown ees'8] |
    \change Staff = "down" \stemUp c,8\sustainOff\sustainOn[ g,8 c8] ees8[ g8 \change Staff = "up" \stemDown c'8] |
    \change Staff = "down" \stemUp f,8\sustainOff\sustainOn[ c8 f8] aes8[ \change Staff = "up" \stemDown c'8 f'8] |
    \change Staff = "down" \stemUp bes,,8\sustainOff\sustainOn[ f,8 bes,8] d8[ aes8 \change Staff = "up" \stemDown d'8] |
    \change Staff = "down" \stemUp ees,8\sustainOff\sustainOn[ bes,8 ees8] g8[ bes8 \change Staff = "up" \stemDown ees'8] |
    \change Staff = "down" \stemUp c,8\sustainOff\sustainOn[ g,8 c8] ees8[ g8 \change Staff = "up" \stemDown c'8] |
    \change Staff = "down" \stemUp g,8\sustainOff\sustainOn[ d8 g8] b8[ \change Staff = "up" \stemDown f'8 b'8] |
    \change Staff = "down" \stemUp c,8\sustainOff\sustainOn[ g,8 c8] ees8[ g8 \change Staff = "up" \stemDown c'8] |
    \change Staff = "down" \stemUp aes,8\sustainOff\sustainOn[ ees8 aes8] \change Staff = "up" \stemDown c'8[ ees'8 aes'8] |
    \change Staff = "down" \stemUp f,8\sustainOff\sustainOn[ c8 f8] aes8[ \change Staff = "up" \stemDown c'8 f'8] |
    \change Staff = "down" \stemUp bes,,8\sustainOff\sustainOn[ f,8 bes,8] d8[ aes8 \change Staff = "up" \stemDown d'8] |
    \change Staff = "down" \stemNeutral g,2.\sustainOff\sustainOn |
    \stemUp bes,,8\sustainOff\sustainOn[ f,8 bes,8] d8[ aes8 \change Staff = "up" \stemDown d'8] |
    \change Staff = "down" \stemUp f,8\sustainOff\sustainOn[ c8 f8] aes8[ \change Staff = "up" \stemDown c'8 f'8] |
    \change Staff = "down" \stemUp bes,,8\sustainOff\sustainOn[ f,8 bes,8] d8[ aes8 \change Staff = "up" \stemDown d'8] |
    \change Staff = "down" \stemUp ees,8\sustainOff\sustainOn[ bes,8 ees8] g8[ bes8 \change Staff = "up" \stemDown ees'8] |
    \change Staff = "down" \stemUp ees,8\sustainOff\sustainOn[ aes,8 c8] ees8[ aes8 \change Staff = "up" \stemDown c'8] |
    \change Staff = "down" \stemNeutral <ees, bes,>4.\fermata\sustainOff\sustainOn r4. |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
