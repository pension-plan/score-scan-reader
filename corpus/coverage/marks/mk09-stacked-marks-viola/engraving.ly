\version "2.24.0"
\header {
  title = "Etude in Stacked Marks"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "P1s1" \with { instrumentName = "Viola" } { \clef "alto"
      \new Voice = "vP1s1" {
          \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key c \minor \tempo "Moderato" 4 = 88 c'4-.-1\p ees'4_>-2 g'4-^-4 c''4\trill-1 |
      bes'4---3\< aes'4-.-2 g'4-!-1 f'4---4\! |
      ees'4->\mordent^0\mf d'4-.\prall_2 c'4--\turn^1 b4-!_3 |
      c'2\fermata-0_\markup \italic "espress." r4 g4-.-1\sfz |
      \break aes4->-2\f( bes4-.-3 c'4-.-4 d'4-.-1) |
      ees'8[-.-2 f'8-.-3 g'8-.-4 aes'8]-.-1 bes'4-^-2\sf c''4\trill-3\> |
      b'4--\turn-2\p c''4---3 d''4->-4\< ees''4-^-4\! |
      c''2.\fermata-1\ff^\markup \italic "sul A" r4 \bar "|." |
      }
    }
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
