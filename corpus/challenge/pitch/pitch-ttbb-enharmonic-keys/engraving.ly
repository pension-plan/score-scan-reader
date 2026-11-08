\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Now the Day Is Over"
  subtitle = "for male voices (TTBB)"
  poet = "Sabine Baring-Gould, 1865"
  composer = "challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 16\mm
  ragged-bottom = ##t
  indent = 14\mm
  system-system-spacing.basic-distance = #17
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = "T. I II" shortInstrumentName = "T." } { \clef "treble_8"
        <<
          \new Voice = "vT1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key ges \major \voiceOne bes4 bes4 ces'4 ces'4 |
    des'2 bes2 |
    aes4 aes4 bes4 ges4 |
    aes1 |
    bes4 bes4 ces'4 ces'4 |
    \break des'2 ees'2 |
    des'4 ces'4 bes4 aes4 |
    ges1 \bar "||" |
    \key fis \major ais4 ais4 b4 b4 |
    cis'2 ais2 |
    \break gis4 gis4 ais4 fis4 |
    gis1 |
    ais4 ais4 b4 b4 |
    cis'2 dis'2 |
    cis'4 b4 ais4 gis4 |
    \break fis1 \bar "||" |
    \key d \major fis'4 e'4 d'4 cis'4 |
    d'1 |
    d'1 |
    d'1 \bar "|." |
          }
          \new Voice = "vT2x1" {
    \autoBeamOff
    \voiceTwo ges4 ges4 ges4 aes4 |
    aes2 ges2 |
    f4 ees4 ges4 ees4 |
    f1 |
    ges4 f4 ees4 ges4 |
    bes2 ges2 |
    bes4 aes4 ges4 f4 |
    des1 |
    fis4 fis4 fis4 gis4 |
    gis2 fis2 |
    dis4 d4 fis4 dis4 |
    eis1 |
    fis4 fisis4 gis4 fis4 |
    ais2 b2 |
    ais4 gis4 fis4 eis4 |
    cis1 |
    fis4 a4 fis4 g4 |
    a1 |
    bes1 |
    a1 |
          }
        >>
      }
      \new Lyrics \lyricsto "vT1x1" { 
      "Now" "the" "day" "is" "o" -- "ver," "Night" "is" "draw" -- "ing" "nigh," "Shad" --
      "ows" "of" "the" "eve" -- "ning" "Steal" "a" -- "cross" "the" "sky." "Now" "the"
      "dark" -- "ness" "gath" -- "ers," "Stars" "be" -- "gin" "to" "peep," "Birds" "and" "beasts"
      "and" "flow" -- "ers" "Soon" "will" "be" "a" -- "sleep." "Soon" "will" "be" "a" --
      "sleep." "A" -- "men."
      }
      \new Staff = "lower" \with { instrumentName = "Bar. B." shortInstrumentName = "B." } { \clef "bass"
        <<
          \new Voice = "vBRx1" {
    \autoBeamOff
    \key ges \major \voiceOne des4 ees4 ees4 ees4 |
    f2 des2 |
    des4 ces4 des4 c4 |
    des1 |
    des4 des4 ces4 eeses4 |
    f2 ees?2 |
    ges4 f4 des4 ces4 |
    bes,1 |
    \key fis \major cis4 dis4 dis4 dis4 |
    eis2 cis2 |
    b,4 b,4 ais,4 bis,4 |
    cis1 |
    cis4 cis4 dis4 d4 |
    fis2 fis2 |
    fis4 eis4 cis4 b,4 |
    ais,1 |
    \key d \major a,4 cis4 d4 e4 |
    fis1 |
    g1 |
    fis1 |
          }
          \new Voice = "vBSx1" {
    \autoBeamOff
    \voiceTwo ges,4 ees,4 ces4 aes,4 |
    des,2 ges,2 |
    des,4 aes,4 ges,4 aes,4 |
    des,1 |
    ges,4 bes,4 ces4 ces4 |
    bes,2 ces2 |
    des4 des4 ges,4 des,4 |
    ges,1 |
    fis,4 dis,4 b,4 gis,4 |
    cis,2 fis,2 |
    gis,4 e,4 fis,4 gis,4 |
    cis,1 |
    fis,4 dis,4 gis,4 b,4 |
    cis2 b,2 |
    cis4 cis4 fis,4 cis,4 |
    fis,1 |
    d,4 a,4 b,4 a,4 |
    d,1 |
    g,1 |
    d,1 |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
