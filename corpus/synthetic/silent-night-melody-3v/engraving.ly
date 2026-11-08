\version "2.24.0"
#(set-global-staff-size 22)
\header {
  title = "Silent Night"
  poet = "Joseph Mohr, tr. J. F. Young"
  composer = "Franz X. Gruber"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "URW Bookman"
  indent = 0
}
\score {
  <<
    \new Staff = "stV" \with { instrumentName = "Voice" } { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \time 6/8 \key c \major g'4. a'8 g'4( |
    e'2.) |
    g'4. a'8 g'4( |
    e'2.) |
    d''2 d''4 |
    b'2. |
    c''2 c''4 |
    g'2. |
    a'2 a'4 |
    c''4. b'8 a'4 |
    g'4. a'8 g'4( |
    e'2.) |
    a'2 a'4 |
    c''4. b'8 a'4 |
    g'4. a'8 g'4 |
    e'2. |
    d''2 d''4 |
    f''4. d''8 b'4 |
    c''2.( |
    e''2.) |
    c''4 g'4 e'4 |
    g'4. f'8( d'4) |
    c'2.~ |
    c'2. \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "1." 
      "Si" -- "lent" "night," __ _ "ho" -- "ly" "night," __ _ "All" "is" "calm," "all"
      "is" "bright," "Round" "yon" "vir" -- "gin" "moth" -- "er" "and" "child." __ _ "Ho" --
      "ly" "in" -- "fant" "so" "ten" -- "der" "and" "mild," "Sleep" "in" "heav" -- "en" --
      "ly" "peace," __ _ "Sleep" "in" "heav" -- "en" -- "ly" __ _ "peace." __
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "2." 
      "Si" -- "lent" "night," __ _ "ho" -- "ly" "night," __ _ "Shep" -- "herds" "quake" "at"
      "the" "sight;" "Glo" -- "ries" "stream" "from" "heav" -- "en" "a" -- "far," __ _ "Heav" --
      "en" -- "ly" "hosts" "sing" "Al" -- "le" -- "lu" -- "ia!" "Christ" "the" "Sav" -- "ior"
      "is" "born," __ _ "Christ" "the" "Sav" -- "ior" "is" __ _ "born!" __
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "3." 
      "Si" -- "lent" "night," __ _ "ho" -- "ly" "night," __ _ "Son" "of" "God," "love's"
      "pure" "light;" "Ra" -- "diant" "beams" "from" "thy" "ho" -- "ly" "face" __ _ "With"
      "the" "dawn" "of" "re" -- "deem" -- "ing" __ _ "grace," "Je" -- "sus," "Lord," "at"
      "thy" "birth," __ _ "Je" -- "sus," "Lord," "at" "thy" __ _ "birth." __
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
