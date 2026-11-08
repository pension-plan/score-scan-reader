\version "2.24.0"
\header {
  title = "Elegy in Dynamics"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "P1s1" \with { instrumentName = "Violoncello" } { \clef "bass"
      \new Voice = "vP1s1" {
          \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key d \minor d2\pp\< e4 f4\! |
      g2\p a4\> g4\! |
      f4\mp e4 d4 c4 |
      d1\mf\> |
      \break a,1\p |
      bes,4\< c4 d4 e4 |
      f2\f e4\sfz d4 |
      a2\ff\> g4 f4\! |
      \break e4\fp d4 e4 f4 |
      g4\sf a4 bes4 a4\sf |
      g2\mf\< a4 bes4 |
      c'1\fff |
      \break bes2\fz\> a4 g4 |
      f2\mp e4\< f4\! |
      d2\sfp e4\> cis4\! |
      d1\ppp \bar "|." |
      }
    }
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
