\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Changing Meters"
  subtitle = "for piano"
  composer = "OMR challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "stP1s1" { \clef "treble"
        <<
          \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key c \major \partial 1*1/4 \tempo "Con moto" \oneVoice e''4 |
    \voiceOne a''4. gis''8 a''4 e''4 |
    c'''4~ c'''16[ b''16 a''16 gis''16] a''2~ | \break
    \time 3/4 \oneVoice a''8[ g''8 f''8 e''8] d''4 |
    \time 5/8 c'''8[ b''8 a''8] g''8[ f''8] |
    e''4.~ e''8[ d''8] | \break
    \time 7/8 c''8[ d''8] e''8[ f''8] g''8[ a''8 b''8] |
    c'''4 b''8[ a''8] gis''4. |
    \time 2/4 a''8[ r8 e''8] r8 | \break
    \time 3/2 \voiceOne c'''2 b''2 a''2 |
    \time 9/8 \oneVoice e''8[ f''8 e''8] d''8[ e''8 d''8] c''4. |
    b'4 a'8 b'8.[ c''16 d''8] e''4. | \break
    \defaultTimeSignature \time 2/2 R1 |
    \voiceOne f''2~ f''8[ e''8 d''8 c''8] |
    \defaultTimeSignature \time 4/4 b'4. c''8 d''4 gis'4 |
    a'2.\fermata \bar "|."
          }
          \new Voice = "vP1x2" {
    \autoBeamOff
    \oneVoice s1*1/4 |
    \voiceTwo c''2 c''4 b'4 |
    e''4 d''4 c''2 |
    \oneVoice s1*3/4 |
    s1*1/4 s1*1/4 s1*1/8 |
    s1*1/4 s1*1/4 s1*1/8 |
    s1*1/2 s1*1/4 s1*1/8 |
    s1*1/2 s1*1/4 s1*1/8 |
    s1*1/2 |
    \voiceTwo e''1 d''2 |
    \oneVoice s1*3/8 s1*3/8 s1*3/8 |
    s1*3/8 s1*3/8 s1*3/8 |
    s1 |
    \voiceTwo a'2 a'2 |
    e'2 e'4 d'4 |
    <c' e'>2.\fermata
          }
        >>
      }
      \new Staff = "stP1s2" { \clef "bass"
          \new Voice = "vP1x5" {
    \autoBeamOff
    \key c \major r4 |
    a,8[ e8 a8 c'8] e,8[ b,8 e8 gis8] |
    a,4 d4 e4 e,4 |
    R2. |
    <a, a>4. <d a>4 |
    <a, e>4. <gis, e>4 |
    a,4 c4 e4. |
    <e, b,>2.. |
    a,8 r8 <c e>8 r8 |
    a,2 gis,2 a,2 |
    a,4. b,4. <c e>4.~ |
    <c e>4. <d f>4. <e gis>4. |
    a,2 \tuplet 3/2 { c4 d4 e4 } |
    d1 |
    e,8[ e8 e,8 e8] e,8[ e8 e,8 e8] |
    <a,, a,>2.\fermata
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
