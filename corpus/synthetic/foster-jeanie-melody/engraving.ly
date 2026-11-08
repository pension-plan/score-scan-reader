\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Jeanie with the Light Brown Hair"
  composer = "Stephen C. Foster"
  tagline = ##f
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "TeX Gyre Schola"
}
\score {
  <<
    \new Staff = "stV" \with { instrumentName = "Voice" } { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \numericTimeSignature \time 4/4 \key c \major r2 d''2 \bar ".|:" |
    c''2. a'4 |
    bes'4 a'4 g'4 f'4 |
    a'2 c'4 d'4 |
    f'1 |
    f'2 g'4 a'4 |
    f''2 d''2 |
    c''4. a'8 g'4 f'4 |
    g'2. d''4 |
    c''2. a'4 |
    bes'4 a'4 g'4 f'4 |
    a'2 c'4 d'4 |
    f'1 |
    g'4 b'4 c''4 d''4 |
    e''4 f''4 a'4 d''4 |
    c''2 b'4 b'4 |
    c''2 r2 |
    g'4 a'4 g'4 f'4 |
    g'2 a'4 g'4 |
    f'4 e'4 f'4 a'4 |
    c''1 |
    d''4 c''4 d''4 f''4 |
    c''2 a'4 g'4 |
    f'2 d'4. d'8 |
    c'2. d''4 |
    c''2. a'4 |
    bes'4 a'4 g'4 f'4 |
    a'2 c'4 d'4 |
    f'1 |
    g'4 a'4 f''4. d''8 |
    c''4 d''4 f'4. g'8 |
    a'2 a'4 g'4 |
    f'2. d''4 \bar ":|." |
    a'2 a'4 g'4 |
    f'2 r2 \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "1." 
      "I" "dream" "of" "Jean" -- "nie" "with" "the" "light" "brown" __ _ "hair" "Borne"
      "like" "a" "va" -- "por" "on" "the" "sum" -- "mer" "air" "I" "see" "her"
      "trip" -- "ping" "where" "the" "bright" "streams" __ _ "play" "Hap" -- "py" "as" "the"
      "dai" -- _ "sies" "that" "dance" "on" "her" "way" "Man" -- "y" "were" "the"
      "wild" "notes" "her" "mer" -- "ry" "voice" "would" "pour," "Man" -- "y" "were" "the"
      "blithe" "birds" "that" "war" -- "bled" "them" "o'er" "I" "dream" "of" "Jean" -- "nie"
      "with" "the" "light" "brown" __ _ "hair" "Float" -- "ing" "like" "a" "va" -- "por"
      "on" "the" "soft" "sum" -- "mer" "air" "I" "bright" "wa" -- "ters" "flow."
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "2." 
      _ "long" "for" "Jean" -- "nie" "with" "the" "day" "dawn" __ _ "smile" "Ra" --
      "dia" -- "ting" "glad" -- "ness" "warm" "with" "win" -- "ning" "guile" "I" "hear" "her"
      "mel;" -- "o" -- "dies" "like" "joys" "gone" __ _ "by" "Sigh" -- "ing" "round" "my"
      "heart" __ _ "o'er" "the" "fond" "hopes" "that" "die." "Sigh" -- "ing" "like" "the"
      "night" "wind" "and" "sob" -- "bing" "like" "the" "rain" "Wait" -- "ing" "for" "the"
      "lost" "one" "that" "comes" "not" "a" -- "gain" "I" "long" "for" "Jean" -- "nie"
      "and" "my" "heart" "bows" __ _ "low" "Nev" -- "er" "more" "to" "find" "her"
      "where" "the" __
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
