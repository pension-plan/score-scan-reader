\version "2.24.0"
#(set-global-staff-size 21)
\header {
  title = "Les anges dans nos campagnes"
  subtitle = "Noël"
  poet = "Paroles : traditionnel"
  composer = "Mélodie : anon. (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "C059"
  indent = 0
  ragged-last = ##f
  system-system-spacing.basic-distance = #15
}
\score {
  <<
    \new Staff = "m" { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \numericTimeSignature \time 4/4 \key f \major a'4 a'8 a'8 a'4 c''4 |
    c''4. bes'8 a'2 |
    a'4 g'8 g'8 a'4 c''4 |
    a'4. g'8 f'2 \break |
    a'4 a'8 a'8 a'4 c''4 |
    c''4. bes'8 a'2 |
    a'4 g'8 g'8 a'4 c''4 |
    a'4. g'8 f'2 \bar "||" \break |
    c''2( d''8 c''8 bes'8 a'8 |
    bes'2 c''8 bes'8 a'8 g'8 |
    a'2 bes'8 a'8 g'8 f'8 |
    g'4.) c'8 f'4 g'4 \break |
    a'4 bes'4 a'4 g'4 |
    f'1 |
    c''2( d''8 c''8 bes'8 a'8 |
    bes'2 c''8 bes'8 a'8 g'8 \break |
    a'2 bes'8 a'8 g'8 f'8 |
    g'4.) c'8 f'4 g'4 |
    a'4 bes'4 a'4 g'4 |
    f'1\fermata \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "1." 
      "Les" "an" -- "ges" "dans" "nos" "cam" -- "pa" -- "gnes" "ont" "en" -- "ton" -- "né"
      "l'hym" -- "ne" "des" "cieux," "et" "l'é" -- "cho" "de" "nos" "mon" -- "ta" -- "gnes"
      "re" -- "dit" "ce" "chant" "mé" -- "lo" -- "di" -- "eux :" "Glo" -- _ _ _
      _ _ _ _ _ _ _ _ _ _ _ _
      "ri" -- "a" "in" "ex" -- "cel" -- "sis" "De" -- "o !" "Glo" -- _ _ _
      _ _ _ _ _ _ _ _ _ _ _ _
      "ri" -- "a" "in" "ex" -- "cel" -- "sis" "De" -- "o !"
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "2." 
      "Ber" -- "gers," "pour" "qui" "cet" -- "te" "fê" -- "te ?" "Quel" "est" "l'ob" -- "jet"
      "de" "tous" "ces" "chants ?" "Quel" "vain" -- "queur," "quel" -- "le" "con" -- "quê" -- "te"
      "mé" -- "ri" -- "te" "ces" "cris" "tri" -- "om" -- "phants ?"
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "3." 
      "Ils" "an" -- "non" -- "cent" "la" "nais" -- "san" -- "ce" "du" "li" -- "bé" -- "ra" --
      "teur" "d'Is" -- "ra" -- "ël," "et" "pleins" "de" "re" -- "con" -- "nais" -- "san" -- "ce"
      "chan" -- "tent" "en" "ce" "jour" "so" -- "len" -- "nel :"
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "4." 
      "Cher" -- "chons" "tous" "l'heu" -- "reux" "vil" -- "la" -- "ge" "qui" "l'a" "vu" "naî" --
      "tre" "sous" "ses" "toits ;" "of" -- "frons" -- "lui" "le" "ten" -- "dre~hom" -- "ma" -- "ge"
      "et" "de" "nos" "cœurs" "et" "de" "nos" "voix !"
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
