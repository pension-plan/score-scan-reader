\version "2.24.0"
\header {
  title = "Pastorale with Ornaments"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "P1s1" \with { instrumentName = "Flute" } { \clef "treble"
      \new Voice = "vP1s1" {
          \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \time 3/4 \key f \major c''4\trill a'8[ bes'8] c''4 |
      d''4\mordent c''4\prall bes'4\turn |
      a'2\fermata r4\fermata |
      f'4\trill g'8[ a'8] bes'4\mordent \breathe |
      \break c''4.\turn d''8 c''4\prall |
      bes'4\reverseturn a'4\trill g'4\mordent |
      f'2.\fermata \breathe |
      a'8[ bes'8] c''4\trill \breathe d''4\prall |
      \break e''4\turn f''4\mordent g''4\trill |
      a''2\fermata g''8[ f''8] \breathe |
      e''4\reverseturn d''4\prall c''4\trill |
      f''2.\fermata \bar "|." |
      }
    }
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
