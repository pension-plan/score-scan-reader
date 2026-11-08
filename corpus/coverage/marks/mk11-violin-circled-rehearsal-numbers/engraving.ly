\version "2.24.0"
\header {
  title = "Signposts (circled rehearsal numbers)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "P1s1" \with { instrumentName = "Violin" } { \clef "treble"
      \new Voice = "vP1s1" {
          \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-circle-numbers
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key g \major \mark \default \tempo "Allegro" g'4 b'8[ d''8] g''4 d''4 |
      e''4 c''4 a'2 |
      \mark \default b'4 d''8[ g''8] fis''4 e''4 |
      d''1 |
      \break \mark \default e''4 g''8[ e''8] c''4 a'4 |
      b'4 g'4 d'2 |
      \mark \default c''4 e''8[ c''8] a'4 fis'4 |
      g'1 |
      \break \mark \default d''4 fis''8[ a''8] d'''4 a''4 |
      b''4 g''4 e''2 |
      \mark \default fis''4 d''8[ a'8] fis'4 a'4 |
      g'1 \bar "|." |
      }
    }
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
