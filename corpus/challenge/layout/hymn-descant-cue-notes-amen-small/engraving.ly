\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Old Hundredth"
  subtitle = "All people that on earth do dwell"
  poet = "William Kethe (1561); Doxology: Thomas Ken (1674)"
  composer = "Genevan Psalter (1551)"
  arranger = "Harmonisation and descant: layout-challenge corpus"
  meter = "L.M."
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 0
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #16
  score-system-spacing.basic-distance = #14
}
\score {
  <<
    \new Staff = "desc" \with { instrumentName = "Descant" \RemoveAllEmptyStaves \magnifyStaff #3/4 } { \clef "treble"
        \new Voice = "vDx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Maestoso" 2 = 60 \defaultTimeSignature \time 4/4 \key g \major \partial 1*1/2 r2 |
    R1 |
    R1 |
    R1 |
    R1 |
    R1 |
    \break R1 |
    R1 |
    R1 |
    r1
    \set Timing.measurePosition = #(ly:make-moment 1/2) r2 \bar "||"
    \pageBreak \textMark \markup { \bold "Verse 4 (Doxology) - with descant" } \set Timing.measurePosition = #(ly:make-moment 1/2) \set fontSize = #-4 g'2^\markup { \italic "(melody)" } |
    g'4 fis'4 e'4 d'4 |
    g'4 a'4 b'2 |
    \unset fontSize d''2\f g''4 fis''4 |
    fis''4 e''4 e''4 d''4 |
    d''2\fermata b'2 |
    \break d''4 d''4 fis''4 g''4 |
    g''4 a''4 b''2\fermata |
    b''2 g''4 e''4 |
    fis''4 e''4 d''4 c''4
    \set Timing.measurePosition = #(ly:make-moment 1/2) b'2\fermata \bar "||" |
        }
    }
    \new Lyrics \lyricsto "vDx1" { 
      _ _ _ _ _ _ _ _ "Praise" "him," "all" "crea" --
      "tures" "here" "be" -- "low;" "Praise" "him" "a" -- "bove," "ye" "heaven" -- "ly" "host;"
      "Praise" "Fa" -- "ther," "Son," "and" "Ho" -- "ly" "Ghost."
    }
    \new ChoirStaff <<
      \new Staff = "sa" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key g \major \voiceOne g'2\mf |
    g'4 fis'4 e'4 d'4 |
    g'4 a'4 b'2\fermata |
    b'2 b'4 b'4 |
    a'4 g'4 c''4 b'4 |
    a'2\fermata g'2 |
    a'4 b'4 a'4 g'4 |
    e'4 fis'4 g'2\fermata |
    d''2 b'4 g'4 |
    a'4 c''4 b'4 a'4
    g'2\fermata
    g'2\f |
    g'4 fis'4 e'4 d'4 |
    g'4 a'4 b'2\fermata |
    b'2 b'4 b'4 |
    a'4 g'4 c''4 b'4 |
    a'2\fermata g'2 |
    a'4 b'4 a'4 g'4 |
    e'4 fis'4 g'2\fermata |
    d''2 b'4 g'4 |
    a'4 c''4 b'4 a'4
    g'2\fermata |
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
    b2\fermata
    b2 |
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
      \new Lyrics \lyricsto "vSx1" { 
      \set stanza = "1." "All" "peo" -- "ple" "that" "on" "earth" "do" "dwell," "Sing" "to" "the" "Lord"
      "with" "cheer" -- "ful" "voice;" "Him" "serve" "with" "fear," "his" "praise" "forth" "tell,"
      "Come" "ye" "be" -- "fore" "him" "and" "re" -- "joice."
      }
      \new Lyrics \lyricsto "vSx1" { 
      \set stanza = "2." "The" "Lord," "ye" "know," "is" "God" "in" -- "deed;" "With" -- "out" "our" "aid"
      "he" "did" "us" "make;" "We" "are" "his" "folk," "he" "doth" "us" "feed,"
      "And" "for" "his" "sheep" "he" "doth" "us" "take."
      }
      \new Lyrics \lyricsto "vSx1" { 
      \set stanza = "3." "O" "en" -- "ter" "then" "his" "gates" "with" "praise," "Ap" -- "proach" "with" "joy"
      "his" "courts" "un" -- "to;" "Praise," "laud," "and" "bless" "his" "name" "al" -- "ways,"
      "For" "it" "is" "seem" -- "ly" "so" "to" "do."
      }
      \new Lyrics \lyricsto "vSx1" { 
      _ _ _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ _ \set stanza = "4." "Praise" "God," "from" "whom"
      "all" "bless" -- "ings" "flow;" "Praise" "him," "all" "crea" -- "tures" "here" "be" -- "low;"
      "Praise" "him" "a" -- "bove," "ye" "heaven" -- "ly" "host;" "Praise" "Fa" -- "ther," "Son,"
      "and" "Ho" -- "ly" "Ghost."
      }
      \new Staff = "tb" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key g \major \voiceOne g2\mf |
    g4 d4 g4 g4 |
    g4 fis4 g2\fermata |
    g2 g4 fis4 |
    fis4 g4 g4 g4 |
    fis2\fermata b2 |
    a4 g4 fis4 e4 |
    e4 a4 b2\fermata |
    b2 g4 g4 |
    fis4 e4 g4 fis4
    d2\fermata
    g2\f |
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
    g,2\fermata
    g,2 |
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
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Score \remove "Bar_number_engraver" }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "sa" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \set Score.currentBarNumber = #22 \defaultTimeSignature \time 4/4 \key g \major \voiceOne g'1\p^\markup { \italic "rall." } |
    g'1\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo e'1 |
    d'1\fermata |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { 
      "A" -- "men."
      }
      \new Staff = "tb" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key g \major \voiceOne c'1\p |
    b1\fermata |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo c1 |
    g,1\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
    #(layout-set-staff-size 14)
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Score \remove "Bar_number_engraver" }
    \context { \Staff \omit TimeSignature }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
