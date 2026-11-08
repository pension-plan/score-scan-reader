\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Odyssey Through the Keys"
  subtitle = "for solo violin"
  composer = "challenge corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 16\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #13
  top-margin = 14\mm
}
\score {
  <<
    \new Staff = "stV" \with { instrumentName = "Violin" shortInstrumentName = "Vln." } { \clef "treble"
        \new Voice = "vVx1" {
    \autoLineBreaksOff
    \numericTimeSignature \time 4/4 \key c \major c''4 e''8 d''8 c''4 g'4 |
    a'8 b'8 c''8 d''8 e''4 c''4 |
    f''4 e''8 d''8 c''4 b'4 |
    c''2 r2 \bar "||" |
    \break \key cis \major cis''4 eis''8 dis''8 cis''4 gis'4 |
    ais'8 bis'8 cis''8 dis''8 eis''4 fisis''4 |
    gis''4 fisis''8 eis''8 dis''4 bis'4 |
    cis''2 r2 \bar "||" |
    \key des \major des''4 f''8 ees''8 des''4 aes'4 |
    bes'8 c''8 des''8 ees''8 f''4 g''4 |
    \break aes''4 g''8 f''8 ees''4 c''4 |
    des''2 r2 \bar "||" |
    \key ces \major ces''4 ees''8 des''8 ces''4 ges'4 |
    aes'8 bes'8 ces''8 des''8 ees''4 f''4 |
    \break ges''4 f''8 ees''8 des''4 beses'4 |
    ces''2 r2 \bar "||" |
    \key b \major b'4 dis''8 cis''8 b'4 fis'4 |
    gis'8 ais'8 b'8 cis''8 dis''4 eis''4 |
    fis''4 eis''8 dis''8 cis''4 a'4 |
    b'2 r2 |
    \break \key fis \major fis'4 ais'8 gis'8 fis'4 cis''4 |
    dis''8 eis''8 fis''8 gis''8 ais''4 bis''4 |
    cis'''4 bis''8 ais''8 gis''4 e''4 |
    fis''2 r2 |
    \key ges \major ges'4 bes'8 aes'8 ges'4 des''4 |
    ees''8 f''8 ges''8 aes''8 bes''4 c'''4 |
    \break des'''4 c'''8 bes''8 aes''4 fes''4 |
    ges''2 r2 \bar "||" |
    \key a \minor a'4 c''8 b'8 a'4 e''4 |
    f''8 gis''8 a''8 b''8 c'''4 b''4 |
    a''4 gis''8 fis''8 e''4 dis''4 |
    e''4 gis'4 a'2 \bar "|." |
        }
    }
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
