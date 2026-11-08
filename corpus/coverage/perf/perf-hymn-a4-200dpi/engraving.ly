\version "2.24.0"
#(set-global-staff-size 18.5)
\header {
  title = "O God, Our Help in Ages Past"
  subtitle = "BENCHMARK  C.M."
  poet = "Isaac Watts, 1719"
  composer = "Tune and harmony: coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  top-margin = 12.00\mm
  bottom-margin = 12.00\mm
  left-margin = 15.00\mm
  right-margin = 15.00\mm
  indent = 0
  ragged-last-bottom = ##f
  system-system-spacing.basic-distance = #12
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "sa" { \clef "treble"
        <<
          \new Voice = "vSx1" {
    \set melismaBusyProperties = #'(melismaBusy slurMelismaBusy tieMelismaBusy)
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Moderato" 4 = 92 \time 3/4 \key ees \major \partial 1*1/4 \voiceOne bes'4\mf |
    ees''2 d''4 |
    c''2 bes'4 |
    aes'4( g'4) f'4 |
    \break g'2\fermata bes'4 |
    ees''2 f''4 |
    g''4.( f''8) ees''4 |
    d''2\fermata bes'4\f |
    \break ees''2 g''4 |
    aes''4( g''8 f''8) ees''4 |
    c''2 d''4 |
    ees''2\fermata bes'4\p |
    \break c''2\> aes'4 |
    g'2 f'4\! |
    ees'2.\fermata \bar "|." |
          }
          \new Voice = "vAx1" {
    \autoBeamOff
    \voiceTwo g'4 |
    g'2 f'4 |
    g'2 g'4 |
    f'2 d'4 |
    ees'2\fermata d'4 |
    g'2 bes'4 |
    g'2 aes'4 |
    f'2\fermata g'4 |
    g'2 bes'4 |
    aes'2 g'4 |
    ees'2 f'4 |
    g'2\fermata g'4 |
    ees'2 f'4 |
    ees'2 d'4 |
    bes2.\fermata |
          }
        >>
      }
      \new Lyrics \lyricsto "vSx1" {
      \set stanza = "1." "O" "God," "our" "help" "in" "a" -- "ges" "past," "Our" "hope" "for" "years" __
      "to" "come," "Our" "shel" -- "ter" "from" __ "the" "storm" -- "y" "blast," "And" "our"
      "e" -- "ter" -- "nal" "home."
      }
      \new Lyrics \lyricsto "vSx1" {
      \set stanza = "2." "Un" -- "der" "the" "sha" -- "dow" "of" __ "thy" "throne" "Thy" "saints" "have" "dwelt" __
      "se" -- "cure;" "Suf" -- "fi" -- "cient" "is" __ "thine" "arm" "a" -- "lone," "And" "our"
      "de" -- "fence" "is" "sure."
      }
      \new Lyrics \lyricsto "vSx1" {
      \set stanza = "3." "Be" -- "fore" "the" "hills" "in" "or" -- "der" "stood," "Or" "earth" "re" -- "ceived" __
      "her" "frame," "From" "ev" -- "er" -- "last" -- "ing" "thou" "art" "God," "To" "end" --
      "less" "years" "the" "same."
      }
      \new Lyrics \lyricsto "vSx1" {
      \set stanza = "4." "A" "thou" -- "sand" "a" -- "ges" "in" __ "thy" "sight" "Are" "like" "an" "eve" --
      "ning" "gone;" "Short" "as" "the" "watch" __ "that" "ends" "the" "night" "Be" -- "fore"
      "the" "ris" -- "ing" "sun."
      }
      \new Staff = "tb" { \clef "bass"
        <<
          \new Voice = "vTx1" {
    \autoBeamOff
    \key ees \major \voiceOne bes4\mf |
    bes2 bes4 |
    ees'2 ees'4 |
    c'2 bes4 |
    bes2\fermata aes4 |
    bes2 d'4 |
    ees'2 c'4 |
    bes2\fermata bes4\f |
    bes2 des'4 |
    c'2 c'4 |
    a2 bes4 |
    bes2\fermata bes4\p |
    aes2 c'4 |
    bes2 aes4 |
    g2.\fermata |
          }
          \new Voice = "vBx1" {
    \autoBeamOff
    \voiceTwo ees4 |
    ees2 d4 |
    c2 ees4 |
    f2 bes4 |
    ees2\fermata bes,4 |
    ees2 bes,4 |
    c2 aes,4 |
    bes,2\fermata ees4 |
    ees2 ees4 |
    aes,2 c4 |
    f2 bes,4 |
    ees2\fermata ees4 |
    aes,2 f,4 |
    bes,2 bes,4 |
    ees2.\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Score \remove "Bar_number_engraver" }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
