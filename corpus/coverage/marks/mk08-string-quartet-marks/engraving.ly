\version "2.24.0"
\header {
  title = "Scherzino for String Quartet"
  composer = "OMR coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
}
\score {
  <<
    \new StaffGroup \with { systemStartDelimiter = #'SystemStartBracket } <<
      \new Staff = "P1s1" \with { instrumentName = "Violin I" } { \clef "treble"
        \new Voice = "vP1s1" {
            \autoBeamOff
      \set Score.rehearsalMarkFormatter = #format-mark-box-letters
      \autoLineBreaksOff \autoPageBreaksOff
      \time 3/4 \key g \major \tempo "Allegro" 4 = 132 d''4-.\f g''4-. fis''4-. |
      e''8[( d''8]) c''8[( b'8]) a'4-> |
      g'4-. b'4-. d''4-. |
      g''2-> r4 |
      \break \mark \default b'4\p( c''4 d''4) |
      e''4\< fis''4 g''4\! |
      a''2\sfz g''4-- |
      fis''4-- e''4-- d''4-- |
      \break \mark \default d''4-^\ff c''4-^ b'4-^ |
      a'8[ b'8 c''8 d''8] e''4\> |
      d''4 c''4 b'4\! |
      g'2.\fermata\p \bar "|." |
        }
      }
      \new Staff = "P2s1" \with { instrumentName = "Violin II" } { \clef "treble"
        \new Voice = "vP2s1" {
            \autoBeamOff
      \key g \major b'4-.\f d''4-. d''4-. |
      c''8[( b'8]) a'8[( g'8]) fis'4-> |
      d'4-. g'4-. b'4-. |
      b'2-> r4 |
      g'4\p( a'4 b'4) |
      c''4\< d''4 e''4\! |
      fis''2\sfz e''4-- |
      d''4-- c''4-- b'4-- |
      b'4-^\ff a'4-^ g'4-^ |
      fis'8[ g'8 a'8 b'8] c''4\> |
      b'4 a'4 g'4\! |
      d'2.\fermata\p |
        }
      }
      \new Staff = "P3s1" \with { instrumentName = "Viola" } { \clef "alto"
        \new Voice = "vP3s1" {
            \autoBeamOff
      \key g \major g4\f^\markup \italic "pizz." b4 a4 |
      g4 fis4 d'4 |
      b4 d'4 g'4 |
      d'2 r4 |
      d'2.\p^\markup \italic "arco"( |
      e'4\< fis'4 g'4\!) |
      a'2\sfz a'4-- |
      a'4-- g'4-- fis'4-- |
      g'4-^\ff e'4-^ d'4-^ |
      d'2 a'4\> |
      g'4 fis'4 d'4\! |
      b2.\fermata\p |
        }
      }
      \new Staff = "P4s1" \with { instrumentName = "Violoncello" } { \clef "bass"
        \new Voice = "vP4s1" {
            \autoBeamOff
      \key g \major g,4\f^\markup \italic "pizz." g,4 d4 |
      c4 d4 d,4 |
      g,4 g4 d4 |
      g,2 r4 |
      g2.\p^\markup \italic "arco" |
      c4\< d4 e4\! |
      d2\sfz cis4-- |
      d4-- d4-- d4-- |
      g4-^\ff a4-^ b4-^ |
      d'2 c'4\> |
      d4 d4 d4\! |
      g,2.\fermata\p |
        }
      }
    >>
  >>
  \layout {
  }
  \midi { \context { \ChordNames \remove "Note_performer" } }
}
