\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Gloria in excelsis"
  subtitle = "Aria for soprano and keyboard"
  poet = "Luke 2:14; liturgical"
  composer = "anon. (CC0, 2026)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Termes"
  indent = 12\mm
  ragged-last = ##f
}
\score {
  <<
    \new Staff = "voice" \with { instrumentName = "Soprano" } { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \defaultTimeSignature \time 4/4 \key d \major a'4 d''4 fis''16( e''16 d''16 e''16 fis''16 g''16 a''16 fis''16 |
    g''16 fis''16 e''16 d''16 cis''8 e''8) a'4 r8 a'8 |
    d''4 e''4 fis''2 |
    e''16( fis''16 g''16 a''16 g''16 fis''16 e''16 d''16 cis''16 d''16 e''16 fis''16 e''16 d''16 cis''16 b'16 \break |
    a'8 b'8 cis''8 d''8 e''4) r4 |
    r4 a'8 a'8 d''4. d''8 |
    fis''2.~ fis''8( e''16 d''16 \break |
    cis''16 d''16 e''16 fis''16 g''16 fis''16 e''16 d''16 cis''16 b'16 a'16 b'16 cis''8 a'8) |
    d''4.( e''8 d''4) r4 |
    r8 a'8 b'8 cis''8 d''4 e''8 fis''8 |
    g''4. fis''8 e''4 d''8( cis''8 \break |
    d''2) r2 |
    a'4 b'8 cis''8 d''16( e''16 fis''16 g''16 a''16 g''16 fis''16 e''16) |
    fis''4( e''8 d''8 cis''4) r4 \break |
    r4 d''8 d''8 e''4 fis''4( |
    g''2 fis''4 e''4) |
    a'2 a'4( b'8 cis''8 |
    d''1\fermata) \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { 
      "Glo" -- "ri" -- "a" __ _ _ _ _ _ _ _ _ _
      _ _ _ _ "in" "ex" -- "cel" -- "sis" "De" -- "o." __ _ _
      _ _ _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ "Et" "in" "ter" -- "ra" "pax" __ _
      _ _ _ _ _ _ _ _ _ _ _ _
      _ _ _ _ _ _ _ "ho" -- "mi" -- "ni" -- "bus" "bo" --
      "nae" "vo" -- "lun" -- "ta" -- "tis." __ _ _ "Al" -- "le" -- "lu" -- _ _
      _ _ _ _ _ _ "ia," __ _ _ _ "al" -- "le" --
      "lu" -- "ia." __ _ _ _ "A" -- "men." __
    }
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "pu" { \clef "treble"
          \new Voice = "vPx1" {
    \key d \major <d' fis' a'>2 <d' fis' a'>2 |
    <cis' e' a'>2 <cis' e' a'>2 |
    <d' fis' a'>2 <d' fis' a'>2 |
    <cis' e' a'>2 <cis' e' g'>2 |
    <cis' e' a'>2 <cis' e' a'>2 |
    <d' fis' a'>2 <d' fis' a'>2 |
    <d' fis' a'>2 <d' fis' a'>2 |
    <cis' e' a'>2 <cis' e' a'>2 |
    <d' fis' a'>2 <d' fis' a'>2 |
    <cis' e' a'>2 <d' fis' a'>2 |
    <d' g' b'>2 <cis' e' a'>2 |
    <d' fis' a'>2 <d' fis' a'>2 |
    <d' fis' a'>2 <cis' e' g'>2 |
    <d' fis' a'>2 <cis' e' a'>2 |
    <d' fis' a'>2 <cis' e' a'>2 |
    <d' g' b'>2 <cis' e' a'>2 |
    <cis' e' a'>2 <cis' e' g'>2 |
    <d' fis' a'>1\fermata |
          }
      }
      \new Staff = "pl" { \clef "bass"
          \new Voice = "vPx5" {
    \key d \major d2 a,2 |
    a,2 a,2 |
    d2 d2 |
    a,2 a,2 |
    a,2 a,2 |
    d2 d2 |
    d2 a,2 |
    a,2 a,2 |
    d2 d2 |
    a,2 d2 |
    g,2 a,2 |
    d2 d2 |
    d2 a,2 |
    d2 a,2 |
    d2 a,2 |
    g,2 a,2 |
    a,2 a,2 |
    d1\fermata |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
