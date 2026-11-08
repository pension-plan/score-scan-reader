\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Abendlied"
  subtitle = "„Der Mond ist aufgegangen“"
  poet = "Text: Matthias Claudius, 1779"
  composer = "Satz: anon. (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Pagella"
  indent = 14\mm
  system-system-spacing.basic-distance = #18
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "Sopran" "Alt" } shortInstrumentName = \markup \center-column { "S." "A." } } { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \numericTimeSignature \time 4/4 \key g \major \partial 1*1/4 \voiceOne d'4 |
    g'4 a'4 b'4 c''4 |
    b'4 a'2 d''4 |
    d''4 e''4 d''4 c''4 \break |
    b'4 a'2 g'4 |
    c''4 b'4 a'4 g'4 |
    a'4( fis'4 g'4) d''4 \break \pageBreak |
    d''4 b'4 c''4 d''4 |
    e''4 d''2 b'4 |
    c''4 a'4 b'4 c''4 \break |
    b'4 a'2 d'4 |
    g'4 b'4 a'4 g'4 |
    c''4 b'8( a'8) g'2\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \voiceTwo a4 |
    b4 d'4 d'4 e'4 |
    d'4 fis'2 g'4 |
    g'4 g'4 g'4 e'4 |
    e'4 fis'2 d'4 |
    e'4 d'4 d'4 b4 |
    d'4~( d'4 d'4) d'4 |
    d'4 e'4 e'4 g'4 |
    g'4 d'2 d'4 |
    c'4 d'4 d'4 e'4 |
    d'4 d'2 b4 |
    b4 b4 d'4 e'4 |
    e'4 g'8( fis'8) d'2\fermata |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "1." 
      "Der" "Mond" "ist" "auf" -- "ge" -- "gan" -- "gen," "die" "gold" -- "nen" "Stern" -- "lein"
      "pran" -- "gen" "am" "Him" -- "mel" "hell" "und" "klar;" __ _ _ "der" "Wald"
      "steht" "schwarz" "und" "schwei" -- "get," "und" "aus" "den" "Wie" -- "sen" "stei" -- "get"
      "der" "wei" -- "ße" "Ne" -- "bel" "wun" -- "der" -- _ "bar."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "2." 
      "Wie" "ist" "die" "Welt" "so" "stil" -- "le" "und" "in" "der" "Dämm" -- "rung"
      "Hül" -- "le" "so" "trau" -- "lich" "und" "so" "hold!" __ _ _ "Als" "ei" --
      "ne" "stil" -- "le" "Kam" -- "mer," "wo" "ihr" "des" "Ta" -- "ges" "Jam" -- "mer"
      "ver" -- "schla" -- "fen" "und" "ver" -- "ges" -- "sen" __ _ "sollt."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "3." 
      "Seht" "ihr" "den" "Mond" "dort" "ste" -- "hen?" "Er" "ist" "nur" "halb" "zu"
      "se" -- "hen" "und" "ist" "doch" "rund" "und" "schön." __ _ _ "So" "sind"
      "wohl" "man" -- "che" "Sa" -- "chen," "die" "wir" "ge" -- "trost" "be" -- "la" -- "chen,"
      "weil" "uns" -- "re" "Au" -- "gen" "sie" "nicht" __ _ "sehn."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "4." 
      "Wir" "stol" -- "ze" "Men" -- "schen" -- "kin" -- "der" "sind" "ei" -- "tel" "ar" -- "me"
      "Sün" -- "der" "und" "wis" -- "sen" "gar" "nicht" "viel;" __ _ _ "wir" "spin" --
      "nen" "Luft" -- "ge" -- "spin" -- "ste" "und" "su" -- "chen" "vie" -- "le" "Küns" -- "te"
      "und" "kom" -- "men" "wei" -- "ter" "von" "dem" __ _ "Ziel."
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "5." 
      "Gott," "laß" "dein" "Heil" "uns" "schau" -- "en," "auf" "nichts" "Ver" -- "gäng" -- "lichs"
      "trau" -- "en," "nicht" "Ei" -- "tel" -- "keit" "uns" "freun!" __ _ _ "Laß" "uns"
      "ein" -- "fäl" -- "tig" "wer" -- "den" "und" "vor" "dir" "hier" "auf" "Er" -- "den"
      "wie" "Kin" -- "der" "fromm" "und" "fröh" -- "lich" __ _ "sein!"
      }
      \new Lyrics \lyricsto "vSx1" { \set stanza = "6." 
      "Wollst" "end" -- "lich" "son" -- "der" "Grä" -- "men" "aus" "die" -- "ser" "Welt" "uns"
      "neh" -- "men" "durch" "ei" -- "nen" "sanf" -- "ten" "Tod!" __ _ _ "Und" "wenn"
      "du" "uns" "ge" -- "nom" -- "men," "laß" "uns" "in'" "Him" -- "mel" "kom" -- "men,"
      "du" "un" -- "ser" "Herr" "und" "un" -- "ser" __ _ "Gott!"
      }
      \new Staff = "lower" \with { instrumentName = \markup \center-column { "Tenor" "Bass" } shortInstrumentName = \markup \center-column { "T." "B." } } { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \key g \major \voiceOne fis4 |
    d4 d4 g4 g4 |
    g4 a2 b4 |
    b4 g4 g4 a4 |
    g4 a2 b4 |
    g4 g4 fis4 g4 |
    fis4~( fis4 b4) b4 |
    b4 g4 a4 g4 |
    g4 fis2 g4 |
    e4 fis4 g4 g4 |
    g4 fis2 g4 |
    g4 g4 fis4 g4 |
    a4 g8( c'8) b2\fermata |
          }
          \new Voice = "vBx1" {
    \voiceTwo d4 |
    g,4 fis,4 g,4 c4 |
    g,4 d2 g,4 |
    g,4 c4 b,4 a,4 |
    e4 d2 g4 |
    c4 g,4 d4 e4 |
    d4~( d4 g,4) g,4 |
    g,4 e4 a,4 b,4 |
    c4 d2 g,4 |
    a,4 d4 g,4 c4 |
    g,4 d2 g4 |
    g4 e4 d4 c4 |
    a,4 d8( d8) g2\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
    \context { \Lyrics \override LyricText.font-size = #0.5 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
