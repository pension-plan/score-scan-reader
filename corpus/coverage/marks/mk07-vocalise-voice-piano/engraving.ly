\version "2.24.0"
\header {
  title = "Vocalise (voice and piano)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "P1s1" \with { instrumentName = "Voice" } { \clef "treble"
      \new Voice = "vP1s1" {
          \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key ees \major R1 |
      R1 |
      bes'2\p\< c''4 d''4\! |
      ees''2-- d''4( c''4) \breathe |
      \break bes'4\mf\> aes'4 g'4 f'4\! |
      g'2._\markup \italic "dolce" r4 |
      c''4\< d''4 ees''4 f''4\! |
      g''2->\f f''4( ees''4) \breathe |
      \break d''4\> c''4 bes'4 aes'4\! |
      g'2-- f'4^\markup \italic "rit." ees'4 |
      \tempo "a tempo" bes'2\pp\< c''4 d''4\! |
      ees''2.\fermata r4 \bar "|." |
      }
    }
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "P2s1" { \clef "treble"
        \new Voice = "vP2s1" {
            \autoBeamOff
      \numericTimeSignature \key ees \major \tempo "Lento" 4 = 60 <g' bes' ees''>2\p\arpeggio <aes' c'' ees''>2\arpeggio |
      <g' bes' ees''>2\arpeggio <f' bes' d''>2\arpeggio |
      <g' bes'>4 <g' bes'>4 <aes' c''>4 <aes' c''>4 |
      <g' bes'>2 <f' aes'>2 |
      <ees' g'>4 <ees' g'>4 <d' f'>4 <d' f'>4 |
      <ees' g' bes'>2.\arpeggio r4 |
      <ees' aes'>4\< <f' aes'>4 <g' bes'>4 <aes' c''>4\! |
      <bes' ees''>2\f <aes' c''>2 |
      <f' aes'>4\> <ees' g'>4 <d' f'>4 <c' ees'>4\! |
      <bes ees'>2 <bes d'>2 |
      <g' bes' ees''>2\pp\arpeggio <aes' c'' ees''>2\arpeggio |
      <g' bes' ees''>2.\fermata\arpeggio r4 |
        }
      }
      \new Staff = "P2s2" { \clef "bass"
        \new Voice = "vP2s2" {
            \autoBeamOff
      \numericTimeSignature \key ees \major ees,4\sustainOn bes,4 g4 bes,4 |
      ees,2\sustainOff\sustainOn bes,,2\sustainOff\sustainOn |
      ees4-.\sustainOff g4-. aes4-. aes4-. |
      bes,2 bes,2 |
      ees4-. ees4-. bes,4-. bes,4-. |
      ees,2.\sustainOn r4\sustainOff |
      c4 d4 ees4 aes,4 |
      g,2 aes,2 |
      bes,4 bes,4 bes,4 bes,4 |
      ees2 bes,2 |
      ees,2\sustainOn aes,2\sustainOff\sustainOn |
      <ees,, ees,>2.\fermata\sustainOff\sustainOn r4\sustainOff |
        }
      }
    >>
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
