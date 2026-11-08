\version "2.24.0"
#(set-global-staff-size 23)
\header {
  title = "Lead, Kindly Light"
  subtitle = "song for soprano (two stanzas)"
  poet = "J. H. Newman, 1833"
  composer = "challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 16\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #17
  top-margin = 15\mm
  print-page-number = ##t
}
\score {
  <<
    \new Staff = "stS" \with { instrumentName = "Soprano" shortInstrumentName = "S." } { \clef "treble"
        \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff
    \autoPageBreaksOff
    \numericTimeSignature \time 4/4 \key aes \major c''2 bes'4 aes'4 |
    ees''2 r4 c''4 |
    des''4 c''4 bes'4 g'4 |
    aes'2 r2 |
    \break c''4 cis''4 d''2 |
    ees''2. r4 |
    r4 c''4 des''4 c''4 |
    ces''2 bes'4 aes'4 |
    \break g'4 aes'4 fes'4 ees'4~ |
    ees'2 r2 |
    ees''4 d''4 des''2 |
    c''2. r4 |
    \break aes'4 bes'4 c''4 des''4 |
    r4 ees''4 f''4 ges''4 |
    f''4 e''4 f''2 |
    r4 ees''4 des''4 c''4 |
    \break bes'2 r4 aes'4 |
    g'4 aes'4 bes'4 beses'4 |
    aes'1 |
    r1 \bar "||" |
    \pageBreak \key e \major gis'4 a'4 b'4 cis''4 |
    dis''4 e''2 b'4 |
    bis'4 cis''4 e''2 |
    e''4 eis''4 fis''4 fisis''4( |
    \break gis''2.) r4 |
    r4 e''4 dis''4 d''4 |
    cis''2 c''4 b'4 |
    ais'4 b'4 r4 b'4 |
    \break e''1 |
    gis'4 a'4 b'4 bis'4~ |
    bis'2 cis''4 r4 |
    r4 b'4 cis''4 d''4 |
    \break e''4 fis''4 g''2 |
    r4 g''4 fis''4 eis''4 |
    fis''1 |
    a''4 gis''4 fis''4 e''4 |
    \break r4 cis''4 d''4 dis''4 |
    e''4 dis''4 e''2~ |
    e''1 \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vSx1" { 
      "Lead," "kind" -- "ly" "Light," "a" -- "mid" "th'en" -- "cir" -- "cling" "gloom," "Lead" "thou"
      "me" "on;" "The" "night" "is" "dark," "and" "I" "am" "far" "from" "home;" __
      _ "Lead" "thou" "me" "on." "Keep" "thou" "my" "feet;" "I" "do" "not"
      "ask" "to" "see" "The" "dis" -- "tant" "scene;" "one" "step" "e" -- "nough" "for"
      "me." "I" "was" "not" "ev" -- "er" "thus," "nor" "prayed" "that" "thou" "Shouldst"
      "lead" "me" "on;" __ _ "I" "loved" "to" "choose" "and" "see" "my" "path;"
      "but" "now" "Lead" "thou" "me" "on." __ _ _ "I" "loved" "the" "gar" --
      "ish" "day," "and," "spite" "of" "fears," "Pride" "ruled" "my" "will:" "re" -- "mem" --
      "ber" "not" "past" "years." __
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
