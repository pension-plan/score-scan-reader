\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Summer Song"
  subtitle = "for three-part choir (SAB)"
  poet = "Words: coverage suite (2026)"
  composer = "Coverage suite (2026)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  ragged-bottom = ##t
  ragged-last-bottom = ##t
  top-margin = 14\mm
  bottom-margin = 14\mm
  left-margin = 18\mm
  right-margin = 16\mm
  indent = 18\mm
  short-indent = 9\mm
  system-system-spacing.basic-distance = #22
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "s" \with { instrumentName = "Soprano" shortInstrumentName = "S." } { \clef "treble"
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Lightly" 4 = 104 \defaultTimeSignature \time 4/4 \key g \major \stemDown b'4\mp b'4 \stemUp a'4 g'4 |
    a'4 \stemDown b'4 \stemUp g'2 |
    \stemDown b'4 c''4 d''4 b'4 |
    \stemUp a'4 g'4 a'2 |
    \break \stemDown d''4\f d''4 c''4 b'4 |
    c''4 b'4 \stemUp a'2 |
    g'4\> \stemDown b'4 \stemUp a'4 g'4 |
    fis'4 a'4\! g'2\fermata \bar "|." |
          }
      }
      \new Lyrics = "lyrsx1" \lyricsto "vSx1" { 
      "Green" "the" "fields" "and" "blue" "the" "sky," "swift" "the" "swal" -- "lows" "dart"
      "and" "fly;" "sing," "O" "sing," "the" "sum" -- "mer" "long," "all" "the" "earth"
      "is" "full" "of" "song."
      }
      \new Staff = "a" \with { instrumentName = "Alto" shortInstrumentName = "A." } { \clef "treble"
          \new Voice = "vAx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key g \major \stemUp g'4\mp g'4 fis'4 e'4 |
    fis'4 g'4 d'2 |
    g'4 a'4 \stemDown b'4 \stemUp g'4 |
    fis'4 e'4 fis'2 |
    \stemDown b'4\f b'4 \stemUp a'4 g'4 |
    a'4 g'4 fis'2 |
    e'4\> g'4 fis'4 e'4 |
    d'4 c'4\! b2\fermata |
          }
      }
      \new Lyrics = "lyrax1" \lyricsto "vAx1" { 
      "Green" "the" "fields" "and" "blue" "the" "sky," "swift" "the" "swal" -- "lows" "dart"
      "and" "fly;" "sing," "O" "sing," "the" "sum" -- "mer" "long," "all" "the" "earth"
      "is" "full" "of" "song."
      }
      \new Staff = "b" \with { instrumentName = "Baritone" shortInstrumentName = "Bar." } { \clef "bass"
          \new Voice = "vBx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key g \major \stemDown g4\mp e4 d4 \stemUp c4 |
    \stemDown d4 g4 \stemUp b,2 |
    \stemDown e4 a4 g4 e4 |
    d4 \stemUp c4 \stemDown d2 |
    g4\f \stemUp b,4 a,4 \stemDown e4 |
    \stemUp c4 \stemDown g4 d2 |
    \stemUp c4\> \stemDown g4 d4 e4 |
    d4 d4\! g2\fermata |
          }
      }
      \new Lyrics = "lyrbx1" \lyricsto "vBx1" { 
      "Green" "the" "fields" "and" "blue" "the" "sky," "swift" "the" "swal" -- "lows" "dart"
      "and" "fly;" "sing," "O" "sing," "the" "sum" -- "mer" "long," "all" "the" "earth"
      "is" "full" "of" "song."
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
