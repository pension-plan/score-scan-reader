\version "2.24.0"
\header {
  title = "Nocturne Study (pedal, arpeggio, fingering)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "P1s1" { \clef "treble"
        \new Voice = "vP1s1" {
            \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key a \minor \tempo "Andante" 4 = 72 e''4-3\p d''4-2 c''4-1 b'4-3 |
      <a'^1 c''^2 e''^4>2\arpeggio <gis'^1 b'^2 e''^5>2\arpeggio |
      a'4-1\< b'4-2 c''4-3 d''4-4 |
      e''2-5\! <c'' e''>2\arpeggio |
      \break f''4-4\mf e''4-3 d''4-2 c''4-1 |
      <b'^1 d''^2 f''^4>2\arpeggio <c''^1 e''^2 a''^5>2\arpeggio |
      b'4-2\> a'4-1 gis'4-3 a'4-4 |
      <a' c'' e''>1\!\arpeggio |
      \break c''4-1\p e''4-3 g''4-5 e''4-3 |
      <f'^1 a'^2 d''^5>2\arpeggio <e'^1 gis'^2 b'^3 e''^5>2\arpeggio |
      c''4-3\> b'4-2 a'4-1 gis'4-2 |
      <a'^1 c''^2 e''^3 a''^5>1\pp\arpeggio \bar "|." |
        }
      }
      \new Staff = "P1s2" { \clef "bass"
        \new Voice = "vP1s2" {
            \autoBeamOff
      \numericTimeSignature \key a \minor a,4_5\sustainOn e4_3 a4_1 e4_3 |
      <a, e>2\sustainOff\sustainOn\arpeggio <e, e>2\sustainOff\sustainOn\arpeggio |
      f,4_5\sustainOff\sustainOn c4_2 f4_1 c4_2 |
      c,4_5\sustainOff\sustainOn g,4_2 c4_1 g,4_2 |
      d,4_5\sustainOff\sustainOn a,4_2 d4_1 a,4_2 |
      <g, d>2\sustainOff\sustainOn\arpeggio <a, e>2\sustainOff\sustainOn\arpeggio |
      e,4_5\sustainOff\sustainOn b,4_2 e4_1 b,4_2 |
      a,1_5\sustainOff\sustainOn |
      c4_5\sustainOff\sustainOn g4_2 c'4_1 g4_2 |
      <d, a,>2\sustainOff\sustainOn <e, b,>2\sustainOff\sustainOn |
      f,4_5\sustainOff\sustainOn c4_3 e,4_4\sustainOff\sustainOn b,4_2 |
      <a,, a,>2\sustainOff\sustainOn\arpeggio r2\sustainOff |
        }
      }
    >>
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
