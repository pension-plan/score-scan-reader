\version "2.24.0"
#(set-global-staff-size 21)
\header {
  title = "O God, Our Help in Ages Past"
  poet = "Isaac Watts, 1719"
  composer = "CROSSWAY  C.M."
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "C059"
  indent = 0
  top-margin = 16\mm
  ragged-last-bottom = ##t
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \time 3/4 \key f \major \partial 1*1/4 \voiceOne f'4 |
    a'2 bes'4 |
    c''2 a'4 |
    g'2 e'4 |
    f'2 c''4 |
    d''2 c''4 |
    bes'2 a'4 |
    g'2 c''4 |
    a'2 bes'4 |
    c''2 a'4 |
    f'2 g'4 |
    a'2 a'4 |
    bes'2 a'4 |
    g'2 g'4 |
    f'2. \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo c'4 |
    f'2 f'4 |
    f'2 f'4 |
    d'2 g'4 |
    f'2 a'4 |
    bes'2 a'4 |
    g'2 \once \omit Stem \once \omit Flag a'4 |
    e'2 r4 |
    f'2 f'4 |
    f'2 f'4 |
    a'2 g'4 |
    f'2 f'4 |
    f'2 f'4 |
    g'4 f'4 e'4 |
    f'2. |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "O" "God," "our" "help" "in" "a" -- "ges" "past," "Our" "hope" "for" "years"
      "to" "come," "Our" "shel" -- "ter" "from" "the" "storm" -- "y" "blast," "And" "our"
      "e" -- "ter" -- "nal" "home."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "Un" -- "der" "the" "sha" -- "dow" "of" "thy" "throne" "Thy" "saints" "have" "dwelt"
      "se" -- "cure;" "Suf" -- "fi" -- "cient" "is" "thine" "arm" "a" -- "lone," "And" "our"
      "de" -- "fence" "is" "sure."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "3." 
      "Be" -- "fore" "the" "hills" "in" "or" -- "der" "stood," "Or" "earth" "re" -- "ceived"
      "her" "frame," "From" "ev" -- "er" -- "last" -- "ing" "thou" "art" "God," "To" "end" --
      "less" "years" "the" "same."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "4." 
      "A" "thou" -- "sand" "a" -- "ges" "in" "thy" "sight" "Are" "like" "an" "eve" --
      "ning" "gone;" "Short" "as" "the" "watch" "that" "ends" "the" "night" "Be" -- "fore"
      "the" "ris" -- "ing" "sun."
      }
      \new Staff = "lower" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key f \major \voiceOne a4 |
    c'2 d'4 |
    c'2 d'4 |
    g2 g4 |
    a2 c'4 |
    bes2 c'4 |
    d'2 c'4 |
    c2 g4 |
    c'2 d'4 |
    c'2 d'4 |
    d'2 d'4 |
    c'2 f4 |
    d2 f4 |
    c'2 bes4 |
    a2. |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo f4 |
    f2 bes,4 |
    a,2 d4 |
    bes,2 c4 |
    f2 f4 |
    bes,2 f4 |
    bes,2 f4 |
    c2 e4 |
    f2 bes,4 |
    a,2 d4 |
    d2 bes,4 |
    f2 d4 |
    f2 c4 |
    c2 c4 |
    f,2. |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
