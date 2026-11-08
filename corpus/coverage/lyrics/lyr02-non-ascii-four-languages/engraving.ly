\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Morning in Four Tongues"
  subtitle = "8.7.8.7."
  poet = "Words: coverage suite (2026)"
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
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new Staff = "v" { \clef "treble"
        \new Voice = "vP1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Freely" 4 = 88 \numericTimeSignature \time 4/4 \key g \major \stemUp d'4\mf g'4 \stemDown b'4 \stemUp a'4 |
    g'4 \stemDown b'4 d''4 d''4 |
    e''4 d''8[( c''8]) b'4 \stemUp a'4 |
    \stemDown b'4 \stemUp a'4 g'2 |
    \break a'4\< \stemDown b'4 c''4 \stemUp a'4 |
    \stemDown b'4 c''4 d''4\! b'4 |
    c''4\> \stemUp b'8[( a'8]) g'4 e'4 |
    d'4 fis'4 g'2\! \bar "|." |
        }
    }
    \new Lyrics = "lyrvx1" \lyricsto "vP1x1" { 
      \set stanza = "1." "Mor" -- "gen" -- "licht" "auf" "grü" -- "nen" "Hö" -- "hen," "Vö" -- "gel" __ _ "sin" --
      "gen" "süß" "und" "froh;" "laß" "uns" "still" "zum" "Flus" -- "se" "ge" -- "hen,"
      "wo" "die" __ _ "Bä" -- "che" "rau" -- "schen" "so."
    }
    \new Lyrics = "lyrvx2" \lyricsto "vP1x1" { 
      \set stanza = "2." "Dou" -- "ce" "lu" -- "miè" -- "re" "au" "ma" -- "tin," "chan" -- "te" __ _ "l'â" --
      "me" "et" "le" "cœur;" "près" "de" "l'eau," "le" "long" "du" "che" -- "min,"
      "al" -- "lons" __ _ "sans" "crain" -- "te" "ni" "peur."
    }
    \new Lyrics = "lyrvx3" \lyricsto "vP1x1" { 
      \set stanza = "3." "¡Can" -- "ta," "can" -- "ta," "mi" "co" -- "ra" -- "zón!" "la" "ma" -- _ "ña" --
      "na" "ya" "lle" -- "gó." "¿Quién" "no" "can" -- "ta" "en" "el" "cam" -- "po"
      "con" "el" __ _ "rí" -- "o" "y" "el" "sol?"
    }
    \new Lyrics = "lyrvx4" \lyricsto "vP1x1" { 
      \set stanza = "4." "Zpí" -- "vej," "srd" -- "ce," "rá" -- "no" "zá" -- "ří," "slun" -- "ce" __ _ "sví" --
      "tí" "nad" "ře" -- "kou," "ptá" -- "ci" "zpí" -- "va" -- "jí" "nad" "lu" -- "kou,"
      "a" "my" __ _ "jde" -- "me" "do" -- "mů" "dál."
    }
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
