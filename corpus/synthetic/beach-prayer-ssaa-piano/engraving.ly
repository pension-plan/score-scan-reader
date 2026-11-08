\version "2.24.0"
#(set-global-staff-size 17)
\header {
  title = "A Prayer of a Tired Child"
  subtitle = "for women's chorus (SSAA) and piano"
  composer = "Amy Beach, Op. 75, No. 4"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "P052"
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "Soprano I" "Soprano II" } shortInstrumentName = "S. I-II" } { \clef "treble"
        <<
          \new Voice = "vS1x1" {
    \set melismaBusyProperties = #'()
    \defaultTimeSignature \time 4/4 \key ees \major \voiceOne r2 r4 bes'4\pp |
    bes'4 bes'4 bes'4. bes'8 |
    bes'4. bes'8 bes'4 bes'4 |
    bes'4 aes'4 aes'4. g'8 |
    g'4( aes'4 g'4) ges'4 |
    f'4 c''4 c''4. c''8 |
    c''4 b'4 d''4. c''8 |
    bes'4 ees''4\pp d''4 c''4 |
    d''4( ees''4 d''4 c''4 |
    d''4 ees''4 c''4) d''4 |
    b'4 c''4 g'4. g'8 |
    g'4. g'8 g'4 g'4 |
    f'4 c''4 c''4 b'4 |
    g''4( f''4 ees''4.) ees''8 |
    d''4 c''4 c''4. c''8 |
    ees''4. d''8 c''4. c''8 |
    bes'4 ees''4 d''4 c''4 |
    d''4 ees''4 d''4 c''4 \bar "|." |
          }
          \new Voice = "vS2x1" {
    \voiceTwo r2 r4 ees'4\pp |
    f'4 ees'4 d'4 c'8( d'8) |
    ees'4. d'8 c'4 f'8( g'8) |
    aes'4 ees'4 f'8( ees'8) d'4 |
    ees'4( f'4 ees'4) ees'4 |
    d'4 ees'4 d'4 c'8( d'8) |
    d'4. d'8 c'4 ees'4 |
    d'4 c'4\pp d'4 ees'4 |
    d'4( c'4 bes4 a4 |
    bes4 c'4 a4) bes4 |
    f'4 ees'4 d'4( c'8) d'8 |
    ees'4. d'8 c'4 b8( c'8) |
    aes'4 ees'4 f'4 d'4 |
    ees'4( d'4 c'4.) c'8 |
    b4 c'4 f'4( ees'8) f'8 |
    ees'4 b4 c'4 ees'4 |
    d'4 c'4 d'4 ees'4 |
    d'4 c'4 bes4 a4 |
          }
        >>
      }
      \new Lyrics \lyricsto "vS1x1" { 
      "Our" "Fa" -- "ther," "hear" "a" "tir" -- "ed" "child" "Who" "has" "for" -- "got"
      "her" "prayer," __ _ _ "And" "can" -- "not" "find" "the" "words" "of" "it,"
      "Which" "wan" -- "der" "ev" -- "'ry" -- "where." __ _ _ _ _ _ _
      "You" "used" "to" "car" -- "ry" "in" "your" "arms" "The" "lamb" -- "kins" "dumb"
      "and" "white," __ _ _ "Who" "had" "grown" "wear" -- "y" "of" "their" "play"
      "And" "stum" -- "bled" "in" "the" "night." __
      }
      \new Staff = "lower" \with { instrumentName = \markup \center-column { "Alto I" "Alto II" } shortInstrumentName = "A. I-II" } { \clef "treble"
        <<
          \new Voice = "vA1x1" {
    \key ees \major \voiceOne r2 r4 g'4\p |
    aes'4 g'4 f'4 ees'8( f'8) |
    g'4. f'8 ees'4 d'8( ees'8) |
    f'4 c'4 d'8( ees'8) f'8( g'8) |
    bes'2. a'4\p |
    aes'4 g'4 f'4 ees'8( f'8) |
    g'4. f'8 ees'4 g'8( a'8) |
    bes'4 g'8( a'8) bes'4 g'8( a'8) |
    bes'2( g'2~ |
    g'2.) g'4\p |
    aes'4 g'4 f'4( ees'8) f'8 |
    g'4. f'8 ees'4 d'8( ees'8) |
    f'4 c'4 d'8( ees'8) f'8( aes'8) |
    g'2. fis'4 |
    f'4 ees'4 d'4 c'8( d'8) |
    g'4. f'8 ees'4 g'8 a'8 |
    bes'4 g'8( a'8) bes'4 g'8( a'8) |
    bes'2 g'2 |
          }
          \new Voice = "vA2x1" {
    \set melismaBusyProperties = #'()
    \voiceTwo r2 r4 bes4\pp |
    bes4 bes4 bes4. bes8 |
    bes4. bes8 bes4 bes4 |
    bes4 bes4 bes4. bes8 |
    bes2. bes4 |
    bes4 bes4 aes4. aes8 |
    g4. g8 g4 g4 |
    g1~ |
    g4 g4 g4. g8 |
    g2. g4 |
    g4. g8 g4. g8 |
    g4. g8 g4. g8 |
    g4. g8 g2~ |
    g4. g8 g4. g8 |
    g4 g4 g4. g8 |
    g4. g8 g4 g4 |
    g1~ |
    g4 g4 g4. g8 |
          }
        >>
      }
      \new Lyrics \lyricsto "vA2x1" { 
      "Our" "Fa" -- "ther," "hear" "a" "tir" -- "ed" "child" "Who" "has" "for" -- "got"
      "her" "prayer," "And" "can" -- "not" "find" "the" "words" "of" "it," "Which" "wan" --
      _ "der" "ev" -- "'ry" -- "where." "You" "used" "to" "car" -- "ry" "in" "your"
      "arms" "The" "lamb" -- "kins" "dumb" __ _ "and" "white," "Who" "had" "grown" "wear" --
      "y" "of" "their" "play" "And" "stum" -- _ "bled" "in" "the"
      }
    >>
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "pu" { \clef "treble"
        <<
          \new Voice = "vPx1" {
    \key ees \major \voiceOne g'8 bes'8 g'8 bes'8 g'8 bes'8 g'8 bes'8 |
    aes'8 bes'8 g'8 bes'8 f'8 bes'8 ees'8 f'8 |
    g'8 bes'8 ees'8 f'8 ees'8 bes'8 f'8 g'8 |
    aes'8 bes'8 aes'8 ees''8 aes'8 f''8 aes'8 d''8 |
    g'4 aes'4 bes'4 a'4 |
    aes'8 d''8 g'8 c''8 f'8 c''8 ees'8 f'8 |
    f'8 c''8 f'8 b'8 ees'8 d''8 ees'8 c''8 |
    d'8 bes'8 ees'8 a'8 d'8 bes'8 ees'8 a'8 |
    d'4 ees'4 d'4 c'4 |
    d'4 ees'4 c'4 d'4 |
    aes'8 b'8 g'8 c''8 f'8 g'8 ees'8 f'8 |
    g'8 c''8 ees'8 f'8 ees'8 g'8 d'8 ees'8 |
    f'8 aes'8 ees'8 c''8 f'8 c''8 aes'8 b'8 |
    g'4 g'4 g'4 fis'4 |
    f'8 d''8 ees'8 c''8 f'8 c''8 ees'8 f'8 |
    g'4 f'4 ees'4 g'4 |
    d'8 bes'8 ees'8 a'8 d'8 bes'8 ees'8 a'8 |
    d'4 ees'4 d'4 c'4 |
          }
          \new Voice = "vPx2" {
    \voiceTwo g'4 g'4 g'4 g'4 |
    aes'4 g'4 f'4 s1*1/4 |
    g'4 s1*1/4 ees'4 s1*1/4 |
    aes'4 aes'4 aes'4 aes'4 |
    g'8 g''8 aes'8 d''8 bes'8 f''8 a'8 ees''8 |
    aes'4 g'4 f'4 s1*1/4 |
    f'4 f'4 ees'4 ees'4 |
    d'4 ees'4 d'4 ees'4 |
    d'8 d''8 ees'8 ees''8 d'8 d''8 c'8 c''8 |
    d'8 d''8 ees'8 ees''8 c'8 c''8 d'8 d''8 |
    aes'4 g'4 f'4 s1*1/4 |
    g'4 s1*1/4 ees'4 s1*1/4 |
    f'4 ees'4 f'4 aes'4 |
    g'8 g''8 g'8 f''8 g'8 ees''8 fis'8 ees''8 |
    f'4 ees'4 f'4 s1*1/4 |
    g'8 ees''8 f'8 d''8 ees'8 c''8 g'8 a'8 |
    d'4 ees'4 d'4 ees'4 |
    d'8 d''8 ees'8 ees''8 d'8 d''8 c'8 c''8 |
          }
        >>
      }
      \new Staff = "pl" { \clef "treble"
        <<
          \new Voice = "vPx5" {
    \key ees \major \voiceOne s1*1/4 ees'8\pp bes8 d'8 bes8 ees'8 bes8 |
    f'8 bes8 ees'8 bes8 d'8 bes8 c'8 d'8 |
    ees'8 bes8 c'8 d'8 c'8 bes8 d'8 ees'8 |
    f'8 bes8 c'8 bes8 d'8 bes8 f'8 bes8 |
    ees'8 bes8 f'8 bes8 g'8 bes8 ges'8 bes8 |
    f'8 bes8 ees'8 bes8 d'8 aes8 c'8 d'8 |
    d'8 g8 d'8 g8 c'8 g8 c'8 g8 |
    bes8 g8 c'8 g8 bes8 g8 c'8 g8 |
    bes8 g8 c'8 g8 bes8 g8 a8 g8 |
    bes8 g8 c'8 g8 a8 g8 bes8 g8 |
    f'8\pp g8 ees'8 g8 d'8 g8 c'8 d'8 |
    ees'8 g8 c'8 d'8 c'8 g8 b8 c'8 |
    d'8 g8 c'8 g8 d'8 g8 f'8 g8 |
    ees'8 g8 d'8 g8 c'8 g8 a8 g8 |
    b8 g8 c'8 g8 d'8 g8 c'8 d'8 |
    ees'8 g8 b8 g8 c'8 g8 ees'8 c'8 |
    bes8 g8 c'8 g8 bes8 g8 c'8 g8 |
    bes8 g8 c'8 g8 bes8 g8 a8 g8 |
          }
          \new Voice = "vPx6" {
    \voiceTwo s1*1/4 ees'4 d'4 ees'4 |
    f'4 ees'4 d'4 s1*1/4 |
    ees'4 s1*1/4 c'4 s1*1/4 |
    f'4 c'4 d'4 f'4 |
    ees'4 f'4 g'4 ges'4 |
    f'4 ees'4 d'4 s1*1/4 |
    d'4 d'4 c'4 c'4 |
    bes4 c'4 bes4 c'4 |
    bes4 c'4 bes4 a4 |
    bes4 c'4 a4 bes4 |
    f'4 ees'4 d'4 s1*1/4 |
    ees'4 s1*1/4 c'4 s1*1/4 |
    d'4 c'4 d'4 f'4 |
    ees'4 d'4 c'4 a4 |
    b4 c'4 d'4 s1*1/4 |
    ees'4 b4 c'4 s1*1/4 |
    bes4 c'4 bes4 c'4 |
    bes4 c'4 bes4 a4 |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
