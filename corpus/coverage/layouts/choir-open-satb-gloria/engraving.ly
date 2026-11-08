\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Gloria"
  subtitle = "for mixed choir (SATB)"
  poet = "Text: liturgical (public domain)"
  composer = "Coverage suite (2026)"
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
  indent = 16\mm
  short-indent = 7\mm
  system-system-spacing.basic-distance = #20
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "s" \with { instrumentName = "Soprano" shortInstrumentName = "S." } { \clef "treble"
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Allegro moderato" 2 = 60 \numericTimeSignature \time 4/4 \key a \major \stemDown e''4\mf cis''8 d''8 e''4 \stemUp a'4 |
    \stemDown b'4( cis''8[ d''8] e''4) d''4 |
    cis''4( b'4) \stemUp a'2 |
    r4 \stemDown e''4\f fis''4 e''8 d''8 |
    \break cis''4 b'8 \stemUp a'8 gis'4 a'4 |
    fis'2\>( gis'2) |
    a'1\fermata\! |
          }
      }
      \new Lyrics = "lyrsx1" \lyricsto "vSx1" { 
      "Glo" -- "ri" -- "a" "in" "ex" -- "cel" -- _ _ _ "sis" "De" -- _
      "o," "Glo" -- "ri" -- "a" "in" "ex" -- "cel" -- "sis" "De" -- "o." "A" -- _
      "men."
      }
      \new Staff = "a" \with { instrumentName = "Alto" shortInstrumentName = "A." } { \clef "treble"
          \new Voice = "vAx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key a \major R1 |
    \stemUp e'4\mf e'8 fis'8 gis'4 a'4 |
    fis'4( gis'8[ a'8] e'4) a'4 |
    gis'4( fis'4) e'2 |
    e'4\f e'8 fis'8 e'4 e'4 |
    d'2\>( e'2) |
    e'1\fermata\! |
          }
      }
      \new Lyrics = "lyrax1" \lyricsto "vAx1" { 
      "Glo" -- "ri" -- "a" "in" "ex" -- "cel" -- _ _ _ "sis" "De" -- _
      "o," "ex" -- "cel" -- "sis" "De" -- "o." "A" -- _ "men."
      }
      \new Staff = "t" \with { instrumentName = "Tenor" shortInstrumentName = "T." } { \clef "treble_8"
          \new Voice = "vTx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key a \major R1 |
    R1 |
    \stemUp a4\mf a8 \stemDown b8 cis'4 \stemUp a4 |
    \stemDown b4( cis'8[ d'8] e'4) cis'4 |
    \stemUp a4\f( \stemDown e'4) cis'2 |
    d'2\>( b2) |
    cis'1\fermata\! |
          }
      }
      \new Lyrics = "lyrtx1" \lyricsto "vTx1" { 
      "Glo" -- "ri" -- "a" "in" "ex" -- "cel" -- _ _ _ "sis" "De" -- _
      "o." "A" -- _ "men."
      }
      \new Staff = "b" \with { instrumentName = "Bass" shortInstrumentName = "B." } { \clef "bass"
          \new Voice = "vBx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \key a \major R1 |
    R1 |
    R1 |
    \stemDown e4\mf e8 e8 \stemUp a,4 cis4 |
    \stemDown a4\f gis8 fis8( e4) \stemUp a,4 |
    \stemDown d2\>( e2) |
    a,1\fermata\! |
          }
      }
      \new Lyrics = "lyrbx1" \lyricsto "vBx1" { 
      "Glo" -- "ri" -- "a" "in" "ex" -- "cel" -- "sis" "De" -- _ "o." "A" -- _
      "men."
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
