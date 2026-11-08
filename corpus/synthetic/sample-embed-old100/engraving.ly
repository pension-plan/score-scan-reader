\version "2.24.0"
#(set-global-staff-size 21)
\header {
  title = "Old Hundredth"
  subtitle = "All people that on earth do dwell"
  poet = "William Kethe, 1561"
  composer = "Genevan Psalter, 1551"
  meter = "L.M."
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 0
  ragged-last = ##f
  top-margin = 18\mm
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \defaultTimeSignature \time 4/4 \key g \major \partial 1*1/2 \voiceOne g'2 |
    g'4 fis'4 e'4 d'4 |
    g'4 a'4 b'2\fermata |
    b'2 b'4 b'4 |
    a'4 g'4 c''4 b'4 |
    a'2\fermata g'2 |
    a'4 b'4 a'4 g'4 |
    e'4 fis'4 g'2\fermata |
    d''2 b'4 g'4 |
    a'4 c''4 b'4 a'4
    \set Timing.measurePosition = #(ly:make-moment 1/2) g'2\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo b2 |
    g4 a4 c'4 d'4 |
    e'4 d'4 d'2\fermata |
    d'2 e'4 d'4 |
    d'4 b4 e'4 d'4 |
    d'2\fermata d'2 |
    d'4 d'4 d'4 b4 |
    e'4 d'4 d'2\fermata |
    d'2 e'4 e'4 |
    d'4 c'4 d'4 c'4
    b2\fermata |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "All" "peo" -- "ple" "that" "on" "earth" "do" "dwell," "Sing" "to" "the" "Lord"
      "with" "cheer" -- "ful" "voice;" "Him" "serve" "with" "fear," "his" "praise" "forth" "tell,"
      "Come" "ye" "be" -- "fore" "him" "and" "re" -- "joice."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "The" "Lord," "ye" "know," "is" "God" "in" -- "deed;" "With" -- "out" "our" "aid"
      "he" "did" "us" "make;" "We" "are" "his" "folk," "he" "doth" "us" "feed,"
      "And" "for" "his" "sheep" "he" "doth" "us" "take."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "3." 
      "O" "en" -- "ter" "then" "his" "gates" "with" "praise," "Ap" -- "proach" "with" "joy"
      "his" "courts" "un" -- "to;" "Praise," "laud," "and" "bless" "his" "name" "al" -- "ways,"
      "For" "it" "is" "seem" -- "ly" "so" "to" "do."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "4." 
      "For" "why?" "the" "Lord" "our" "God" "is" "good;" "His" "mer" -- "cy" "is"
      "for" "ev" -- "er" "sure;" "His" "truth" "at" "all" "times" "firm" -- "ly" "stood,"
      "And" "shall" "from" "age" "to" "age" "en" -- "dure."
      }
      \new Staff = "lower" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key g \major \voiceOne g2 |
    g4 d4 g4 g4 |
    g4 fis4 g2\fermata |
    g2 g4 fis4 |
    fis4 g4 g4 g4 |
    fis2\fermata b2 |
    a4 g4 fis4 e4 |
    e4 a4 b2\fermata |
    b2 g4 g4 |
    fis4 e4 g4 fis4
    d2\fermata |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo g,2 |
    e,4 d4 c4 b,4 |
    c4 d4 g,2\fermata |
    g,2 e,4 b,4 |
    d4 e4 c4 g,4 |
    d2\fermata g,2 |
    fis,4 g,4 d4 e4 |
    c4 d4 g,2\fermata |
    g,2 e,4 c4 |
    d4 a,4 g,4 d4
    g,2\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
    \context { \Score \remove "Bar_number_engraver" }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
