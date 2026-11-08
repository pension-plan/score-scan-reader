\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Air with Graces"
  subtitle = "for violin and piano"
  composer = "OMR challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  system-system-spacing.basic-distance = #22
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Violin" } { \clef "treble"
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key d \major \tempo "Adagio cantabile" \acciaccatura e''8 d''4 \appoggiatura cis''8 b'4 a'8.[ b'16] \grace { a'16[ b'16] } cis''8.[ d''32 e''32] |
    fis''2\fermata r4 \grace { g''32[ fis''32 e''32] } fis''4 |
    e''16[ fis''16 g''16 a''16] b''32[ a''32 g''32 fis''32 e''32 d''32 cis''32 b'32] a'8[ r16 a'16] d''4 | \break
    \acciaccatura fis''8 g''4.\fermata fis''8 e''16[ d''16 cis''16 b'16] a'4 |
    a'8.[ a'32 g'32] fis'4 \grace { g'16[ a'16 b'16 cis''16] } d''2 |
    r8 d''16[ e''16] fis''8[ r16 fis''16] g''32[ fis''32 e''32 d''32] cis''8 r8 \acciaccatura e''8 d''8 | \break
    b'4~ b'16[ a'16 gis'16 a'16] \grace cis''16 e''2 |
    a''2.\fermata r4\fermata \bar "|." |
        }
    }
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "stP2s1" { \clef "treble"
          \new Voice = "vP2x1" {
    \autoBeamOff
    \key d \major \grace { s8 } <fis' a'>4 <fis' a'>4 <g' b'>4 <e' a'>4 |
    <a' d''>2\fermata r4 <a' d''>4 |
    <b' e''>4 <g' b'>4 <fis' a'>4 <a' d''>4 |
    <b' d''>4.\fermata <a' d''>8 <g' cis''>4 <e' a'>4 |
    <cis' e'>4 <d' fis'>4 r8 <fis' a'>8[ <g' b'>8 <fis' a'>8] |
    <fis' a'>4 <fis' a'>4 <e' g'>4 <e' g'>4 |
    <d' fis'>4 <d' e'>4 <cis' e'>2 |
    <cis'' e''>2.\fermata r4\fermata |
          }
      }
      \new Staff = "stP2s2" { \clef "bass"
          \new Voice = "vP2x5" {
    \autoBeamOff
    \key d \major \grace { s8 } d4 d4 g,4 a,4 |
    d2\fermata r4 d4 |
    e,8[ e8] g,8[ g8] a,8[ a8] fis,8[ fis8] |
    g,4.\fermata g8 a,4 a,4 |
    a,2 d2 |
    d4 b,4 a,4 a,4 |
    e,2 a,2 |
    <a,, a,>2.\fermata r4\fermata |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
