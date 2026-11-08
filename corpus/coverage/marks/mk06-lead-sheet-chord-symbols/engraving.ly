\version "2.24.0"
\header {
  title = "Harbour Lights (lead sheet)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new ChordNames = "cnP1" \chordmode { bes2:maj7 g2:m7 c2:m7 f2:7 d2:m7 g2:7 c2:m7 f2:9 bes1 ees2:maj7 ees2:6 a2:m7.5- d2:7 g2:m g2:m6 c2:m c2:m/bes aes2:7 g2:7 ees2:sus4 ees2 e2:dim7 f2:7 bes2/d f2:aug g2:m7 c2:9 f2:sus4 f2:7 bes1:6 }
    \new Staff = "P1s1" \with { instrumentName = "Melody" } { \clef "treble"
      \new Voice = "vP1s1" {
          \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key bes \major \tempo "Medium swing" 4 = 120 d''4 c''8[ bes'8] f'2 |
      g'4 a'4 bes'4 c''4 |
      d''2 b'4 g'4 |
      c''2 a'2 |
      \break f'4 bes'4 d''4 f''4 |
      g''2 ees''4 c''4 |
      c''4 a'4 fis'4 d''4 |
      bes'2 g'2 |
      \break ees''4 d''4 c''4 bes'4 |
      aes'2 b'2 |
      bes'4 aes'4 g'4 ees'4 |
      e'2 c''2 |
      \break d''4 bes'4 cis''2 |
      d''4 c''4 bes'4 a'4 |
      bes'2 a'2 |
      bes'1 \bar "|." |
      }
    }
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
