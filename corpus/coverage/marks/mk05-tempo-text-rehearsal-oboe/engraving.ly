\version "2.24.0"
\header {
  title = "Promenade (tempo, text, rehearsal marks)"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new Staff = "P1s1" \with { instrumentName = "Oboe" } { \clef "treble"
      \new Voice = "vP1s1" {
          \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \numericTimeSignature \time 4/4 \key d \major \mark \default \tempo "Allegretto" 4 = 112 d'4 fis'8[ a'8] d''4 cis''8[ b'8] |
      a'4. g'8 fis'4 e'4 |
      d'8[ e'8 fis'8 g'8] a'4 b'4 |
      a'2 r2 |
      \break \mark \default \tempo "Meno mosso" b'2_\markup \italic "dolce" a'4 g'4 |
      fis'4. g'8 a'2 |
      b'4^\markup \italic "espress." cis''4 d''4 b'4 |
      a'2 g'4^\markup \italic "rit." fis'4 |
      \break \time 6/8 \mark \default \tempo 4. = 60 fis'8[_\markup \italic "leggiero" g'8 a'8] b'8[ a'8 g'8] |
      fis'4. e'4. |
      d'8[ e'8 fis'8] g'8[ a'8 b'8] |
      a'4.^\markup \italic "poco rit." r4. |
      \break \numericTimeSignature \time 4/4 \mark \default \tempo "Tempo I" 4 = 112 d''4^\markup \italic "cantabile" cis''8[ b'8] a'4 g'4 |
      fis'4 e'8[ fis'8] g'4 a'4 |
      b'2^\markup \italic "allargando" cis''4 d''4 |
      d''1_\markup \italic "morendo" \bar "|." |
      }
    }
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
