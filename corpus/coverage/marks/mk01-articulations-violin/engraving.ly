\version "2.24.0"
\header {
  title = "Bowing Study in Articulations"
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
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key g \major g'8[-. a'8-. b'8-. c''8]-. d''4-> d''4-> |
      e''8[-! d''8-! c''8-! b'8]-! a'4-- g'4-- |
      fis'8[-. g'8-. a'8-. b'8]-. c''4-^ e''4^^ |
      d''2-> d''4-- r4 |
      \break b'4-_( c''4-_ d''4-_ e''4-_) |
      fis''8[-> e''8-. d''8-. c''8]-. b'8[-> a'8-. g'8-. fis'8]-. |
      e'4-- fis'4_- g'4-^ a'4-^ |
      b'4-! b'4-! b'4-! r4 |
      \break <g d'>4-> <g d'>4-> <d' a'>2-- |
      g''8[-. fis''8-. e''8-. d''8]-. c''8[-^ b'8-^ a'8-^ g'8]-^ |
      a'4->-. b'4->-. c''4---. d''4---. |
      g'2.-> r4 \bar "|." |
      }
    }
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
