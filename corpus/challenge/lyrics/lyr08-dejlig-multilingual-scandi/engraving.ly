\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Dejlig er jorden"
  subtitle = "Härlig är jorden · Deilig er jorden · Fairest Lord Jesus"
  poet = "Ingemann 1850 · Bååth-Holmberg 1884 · Willis 1850"
  composer = "Melodi: CC0"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Heros"
  indent = 0
  ragged-last = ##f
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new Staff = "m" { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \time 3/4 \key d \major d'2 d'4 |
    e'2 fis'4 |
    d'2. |
    fis'2 g'4 |
    a'2 a'4 |
    b'4 a'2 \break |
    d''2 cis''4 |
    b'2 a'4 |
    g'4 fis'4 e'4 |
    d'2. \break |
    fis'2 fis'4 |
    g'2 g'4 |
    a'2. |
    b'2 b'4 |
    a'2 g'4 |
    fis'2. \break |
    a'2 b'4 |
    a'2 fis'4 |
    g'4 fis'4 e'4 |
    d'2.\fermata \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "1. EN" 
      "Fair" -- "est" "Lord" "Je" -- "sus," "Rul" -- "er" "of" "all" "na" -- "ture," "O"
      "thou" "of" "God" "and" "man" "the" "Son," "Thee" "will" "I" "cher" -- "ish,"
      "Thee" "will" "I" "hon" -- "or," "Thou," "my" "soul's" "glo" -- "ry," "joy," "and"
      "crown."
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "2. DA" 
      "Dej" -- "lig" "er" "jor" -- "den," "præg" -- "tig" "er" "Guds" "him" -- "mel," "skøn"
      "er" "sjæ" -- "le" -- "nes" "pil" -- "grims" -- "gang." "Gen" -- "nem" "de" "fag" -- "re"
      "ri" -- "ger" "på" "jor" -- "den" "går" "vi" "til" "Pa" -- "ra" -- "dis" "med"
      "sang."
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "3. SV" 
      "Här" -- "lig" "är" "jor" -- "den," "här" -- "lig" "är" "Guds" "him" -- "mel," "skön"
      "är" "sjä" -- "lar" -- "nas" "pil" -- "grims" -- "gång." "Ge" -- "nom" "de" "fag" -- "ra"
      "ri" -- "ken" "på" "jor" -- "den" "gå" "vi" "till" "pa" -- "ra" -- "dis" "med"
      "sång."
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "4. NO" 
      "Dei" -- "lig" "er" "jor" -- "den," "prek" -- "tig" "er" "Guds" "him" -- "mel," "skjønn"
      "er" "sje" -- "le" -- "nes" "pil" -- "grims" -- "gang." "Gjen" -- "nom" "de" "fag" -- "re"
      "ri" -- "ker" "på" "jor" -- "den" "går" "vi" "til" "pa" -- "ra" -- "dis" "med"
      "sang."
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "5. DA" 
      "Ti" -- "der" "skal" "kom" -- "me," "ti" -- "der" "skal" "hen" -- "rul" -- "le," "slægt"
      "skal" "føl" -- "ge" "slæg" -- _ "ters" "gang;" "al" -- "drig" "for" -- "stum" -- "mer"
      "to" -- "nen" "fra" "him" -- "len" "i" "sjæ" -- "lens" "gla" -- "de" "pil" -- "grims" --
      "sang."
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
