\version "2.24.0"
\header {
  title = "Nocturne in Brackets (pedal lines)"
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
      \set Staff.pedalSustainStyle = #'bracket
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key a \minor \tempo "Lento" e''4\p d''4 c''4 b'4 |
      <a' c'' e''>2 <gis' b' e''>2 |
      a'4 b'4 c''4 d''4 |
      e''2 <c'' e''>2 |
      \break f''4\mf e''4 d''4 c''4 |
      <b' d'' f''>2 <c'' e'' a''>2 |
      b'4 a'4 gis'4 a'4 |
      <a' c'' e''>1 |
      \break c''4\p e''4 g''4 e''4 |
      <f' a' d''>2 <e' gis' b' e''>2 |
      c''4 b'4 a'4 gis'4 |
      <a' c'' e'' a''>1\pp \bar "|." |
        }
      }
      \new Staff = "P1s2" { \clef "bass"
        \new Voice = "vP1s2" {
            \autoBeamOff
      \set Staff.pedalSustainStyle = #'bracket
      \numericTimeSignature \key a \minor a,4\sustainOn e4 a4 e4 |
      <a, e>2\sustainOff\sustainOn <e, e>2\sustainOff\sustainOn |
      f,4\sustainOff\sustainOn c4 f4 c4 |
      c,4\sustainOff\sustainOn g,4 c4 g,4 |
      d,4\sustainOff\sustainOn a,4 d4 a,4 |
      <g, d>2\sustainOff\sustainOn <a, e>2\sustainOff\sustainOn |
      e,4\sustainOff\sustainOn b,4 e4 b,4 |
      a,1\sustainOff\sustainOn |
      c4\sustainOff\sustainOn g4 c'4 g4 |
      <d, a,>2\sustainOff\sustainOn <e, b,>2\sustainOff\sustainOn |
      f,4\sustainOff\sustainOn c4 e,4\sustainOff\sustainOn b,4 |
      <a,, a,>2\sustainOff\sustainOn r2\sustainOff |
        }
      }
    >>
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
