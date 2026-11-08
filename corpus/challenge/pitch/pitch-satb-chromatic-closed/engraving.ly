\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Abide with Me"
  poet = "H. F. Lyte, 1847"
  composer = "chromatic setting (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 16\mm
  ragged-bottom = ##t
  indent = 12\mm
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = "S. A." shortInstrumentName = "S.A." } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key ees \major \partial 1*1/4 \voiceOne g'4 |
    g'4 aes'4 bes'4 ees''4 |
    d''4 c''4 bes'4 a'4 |
    bes'2 r4 bes'4 |
    \break c''4 ces''4 bes'4 aes'4 |
    g'4 f'4 e'4 f'4 |
    g'2 r4 g'4 |
    \break aes'4 g'4 fis'4 g'4 |
    c''4 bes'4 aes'4 a'4 |
    bes'2 r4 bes'4 |
    \break ees''4 d''4 des''4 c''4 |
    b'4 c''4 aes'4 f'4
    \set Timing.measurePosition = #(ly:make-moment 1/4) ees'2. \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo ees'4 |
    ees'4 c'4 ees'4 ees'4 |
    bes'4 a'4 f'4 ees'4 |
    d'2 r4 ees'4 |
    ees'4 ees'4 ees'4 d'4 |
    bes4 bes4 bes4 c'4 |
    ees'?2 r4 ees'4 |
    f'4 ees'4 c'4 f'4 |
    c'4 ees'4 ees'4 ees'4 |
    ees'2 r4 d'4 |
    g'4 f'4 g'4 ees'4 |
    f'4 ees'4 c'4 d'4
    bes2. |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "A" -- "bide" "with" "me;" "fast" "falls" "the" "e" -- "ven" -- "tide;" "The" "dark" --
      "ness" "deep" -- "ens;" "Lord," "with" "me" "a" -- "bide." "When" "oth" -- "er" "help" --
      "ers" "fail" "and" "com" -- "forts" "flee," "Help" "of" "the" "help" -- "less," "O"
      "a" -- "bide" "with" "me."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "Swift" "to" "its" "close" "ebbs" "out" "life's" "lit" -- "tle" "day;" "Earth's" "joys"
      "grow" "dim," "its" "glo" -- "ries" "pass" "a" -- "way;" "Change" "and" "de" -- "cay"
      "in" "all" "a" -- "round" "I" "see;" "O" "thou" "who" "chang" -- "est" "not,"
      "a" -- "bide" "with" "me."
      }
      \new Staff = "lower" \with { instrumentName = "T. B." shortInstrumentName = "T.B." } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key ees \major \voiceOne bes4 |
    bes4 aes4 g4 c'4 |
    bes4 ees'4 bes4 c'4 |
    bes2 r4 g4 |
    aes4 aes4 g4 f4 |
    ees4 f4 g4 aes4 |
    bes2 r4 c'4 |
    c'4 c'4 a4 bes4 |
    aes4 g4 ces'4 ges4 |
    g?2 r4 aes4 |
    bes4 bes4 bes4 aes4 |
    b4 g4 aes4 aes4
    g2. |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo ees4 |
    ees4 f4 g4 aes,4 |
    bes,4 f4 d4 f4 |
    bes,2 r4 ees4 |
    aes,4 aes,4 bes,4 bes,4 |
    ees4 d4 c4 f,4 |
    g,2 r4 c4 |
    f,4 c4 d4 g,4 |
    aes,4 ees4 aes,4 ces4 |
    bes,2 r4 bes,4 |
    ees4 d4 ees4 aes4 |
    g4 c4 f,4 bes,4
    ees2. |
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
