\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Tu scendi dalle stelle"
  subtitle = "Pastorale"
  poet = "Parole di S. Alfonso M. de’ Liguori"
  composer = "Musica: anon. (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "URW Bookman"
  indent = 14\mm
  ragged-last = ##f
}
\score {
  <<
    \new Staff = "voice" \with { instrumentName = "Canto" } { \clef "treble"
        \new Voice = "vVx1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \time 6/8 \key g \major \partial 1*1/8 d'8 |
    g'4 a'8 b'4 c''8 |
    d''4 c''8 b'4 a'8 |
    b'4. a'4 d'8 \break |
    g'4 a'8 b'4 c''8 |
    d''4 e''8 d''4 c''8 |
    b'4. a'4 b'8 \break |
    c''4 b'8 a'4 g'8 |
    a'4 b'8 g'4. |
    e''4 d''8 c''4 b'8 \break |
    a'4 g'8 fis'4. |
    g'4 a'8 b'4 c''8 |
    d''4. r4 d''8 \break |
    e''4 d''8 c''4 b'8 |
    a'4 b'8 c''4 a'8 |
    a'4. g'4.\fermata \bar "|." |
        }
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "1." 
      "Tu" "scen" -- "di" "dal" -- "le" "stel" -- "le~o" "Re" "del" "Cie" -- "lo," "e"
      "vie" -- "ni~in" "u" -- "na" "grot" -- "ta~al" "fred" -- "do~e~al" "ge" -- "lo." "O" "Bam" --
      "bi" -- "no" "mio" "di" -- "vi" -- "no," "io" "ti" "ve" -- "do" "qui~a" "tre" --
      "mar;" "o" "Dio" "be" -- "a" -- "to!" "Ah," "quan" -- "to" "ti" "co" -- "stò"
      "l'a" -- "ver" -- "mi~a" -- "ma" -- "to!"
    }
    \new Lyrics \lyricsto "vVx1" { \set stanza = "2." 
      "A" "te," "che" "sei" "del" "mon" -- "do~il" "Cre" -- "a" -- "to" -- "re," "man" --
      "ca" -- "no" "pan" -- "ni~e" "fuo" -- "co,~o" "mio" "Si" -- "gno" -- "re." "Ca" -- "ro~e" --
      "let" -- "to" "par" -- "go" -- "let" -- "to," "quan" -- "to" "que" -- "sta" "po" -- "ver" --
      "tà" "più" "m'in" -- "na" -- "mo" -- "ra," "giac" -- "ché" "ti" "fe" -- "ce~a" -- "mor"
      "po" -- "ve" -- "ro~an" -- "co" -- "ra!"
    }
    \new PianoStaff \with { instrumentName = "Pianoforte" } <<
      \new Staff = "pu" { \clef "treble"
          \new Voice = "vPx1" {
    \key g \major r8 |
    <b d' g'>4. <b d' g'>4. |
    <b d' g'>4. <a d' fis'>4. |
    <b d' g'>4. <a c' fis'>4. |
    <b d' g'>4. <b d' g'>4. |
    <b d' g'>4. <b d' g'>4. |
    <b d' g'>4. <a d' fis'>4. |
    <c' e' g'>4. <a d' fis'>4. |
    <a d' fis'>4. <b d' g'>4. |
    <c' e' g'>4. <b d' g'>4. |
    <a d' fis'>4. <a c' fis'>4. |
    <b d' g'>4. <b d' g'>4. |
    <b d' g'>4. <a d' fis'>4. |
    <c' e' g'>4. <b d' g'>4. |
    <a d' fis'>4. <a c' fis'>4. |
    <a d' fis'>4. <b d' g'>4.\fermata |
          }
      }
      \new Staff = "pl" { \clef "bass"
          \new Voice = "vPx5" {
    \key g \major r8 |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2. |
    <g, d>2.\fermata |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
