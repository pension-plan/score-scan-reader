\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Canticle of Elisions"
  poet = "Words: Gloria (trad.); vv. 2-3 coverage suite"
  composer = "Melody: coverage suite (2026)"
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
  indent = 0
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new Staff = "v" { \clef "treble"
        \new Voice = "vP1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante" 4 = 76 \time 3/4 \key f \major \partial 1*1/4 \stemUp c'4\mp |
    f'4 g'4 a'4 |
    \stemDown bes'4( \stemUp a'4) g'4 |
    a'2 f'4 |
    \stemDown c''4\< c''4 d''4 |
    c''2.\! |
    \break \stemUp a'4 \stemDown bes'4 c''4 |
    \stemUp g'2 g'4 |
    a'4( \stemDown bes'4) \stemUp a'4 |
    g'2\> e'4
    \set Timing.measurePosition = #(ly:make-moment 1/4) f'2\! \bar "|." |
        }
    }
    \new Lyrics = "lyrvx1" \lyricsto "vP1x1" { 
      \set stanza = "1." "Glo" -- "ri" -- "a~in" "ex" -- "cel" -- _ "sis" "De" -- "o," "et~in" "ter" -- "ra"
      "pax" "ho" -- "mi" -- "ni" -- "bus" "bo" -- "nae" __ _ "vo" -- "lun" -- "ta" -- "tis."
    }
    \new Lyrics = "lyrvx2" \lyricsto "vP1x1" { 
      \set stanza = "2." "Can" -- "ta~e" "lo" -- "da~il" "Si" -- _ "gno" -- "re," "can" -- "ta~an" -- "co" -- "ra~u" --
      "na" "vol" -- "ta" "con" "la" "vo" -- "ce~e" __ _ "con" "il" "cuo" -- "re."
    }
    \new Lyrics = "lyrvx3" \lyricsto "vP1x1" { 
      \set stanza = "3." "Can" -- "ta~y" "a" -- "la" -- "ba~al" __ _ "Se" -- "ñor," "can" -- "ta~o" -- "tra" "vez"
      "con" "a" -- "mor," "y" "con" "la" "voz" __ _ "y~el" "co" -- "ra" -- "zón."
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
