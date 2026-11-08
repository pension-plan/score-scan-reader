\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Hemiola for Guitar"
  composer = "OMR coverage suite (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "stP1" \with { instrumentName = "Guitar" shortInstrumentName = "Gtr." } { \clef "treble_8"
      <<
        \new Voice = "vP1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff
    \time 6/8 \key e \minor \partial 1*1/8 \tempo "Andantino" \voiceOne b8 |
    e'4 fis'8 \tuplet 2/3 { g'8[ a'8] } |
    b'4.~ b'4 a'8 |
    \time 3/4 g'4 fis'4 e'4~ | \break
    \tuplet 3/2 { e'8[ dis'8 e'8] } b2 |
    \time 6/8 e'4.~ \tuplet 2/3 { e'8[ g'8] } |
    \tuplet 2/3 { fis'8[ e'8] } dis'4. |
    e'4.~ e'4 \bar "|."
        }
        \new Voice = "vP1x2" {
    \autoBeamOff
    \voiceTwo r8 |
    e4. b,4. |
    e4. dis4. |
    e4 a,4 b,4~ |
    b,2. |
    e4. c4. |
    a,4. b,4. |
    e4.~ e4
        }
      >>
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
