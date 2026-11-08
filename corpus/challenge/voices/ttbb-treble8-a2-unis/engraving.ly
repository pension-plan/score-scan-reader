\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Integer vitae"
  poet = "Horace, Carmina I.22"
  composer = "for male choir TTBB (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "DejaVu Serif"
  top-margin = 18\mm
  indent = 20\mm
}
\score {
  <<
    \new ChoirStaff <<
      \new Staff = "upper" \with { instrumentName = \markup \center-column { "Tenor I" "Tenor II" } shortInstrumentName = \markup \center-column { "T. I" "T. II" } } { \clef "treble_8"
        <<
          \new Voice = "vT1x1" {
    \set melismaBusyProperties = #'()
    \autoBeamOff
    \numericTimeSignature \time 4/4 \key bes \major \voiceOne d'4\mf d'4 ees'4 f'4 |
    g'4 f'4 ees'4 d'4 |
    c'4 ees'4 d'2 |
    \oneVoice f'4\f^\markup \italic "a 2" ees'4 d'4 c'4 |
    bes4 c'4 d'4 ees'4 |
    f'8 ees'8 d'4 c'2 |
    \voiceOne d'4\p d'4 ees'4 f'4 |
    g'4 g'4 f'4 ees'4 |
    d'4 c'4 bes2 |
    f'2\mf d'2 |
    ees'4 c'4 bes2 |
    \oneVoice f'2\f^\markup \italic "a 2" d'2 |
    \voiceOne ees'4 c'4 d'2\fermata \bar "|." |
          }
          \new Voice = "vT2x1" {
    \autoBeamOff
    \voiceTwo bes4 bes4 c'4 bes4 |
    bes4 bes4 g4 bes4 |
    a4 a4 bes2 |
    \oneVoice s1*1/4 s1*1/4 s1*1/4 s1*1/4 |
    s1*1/4 s1*1/4 s1*1/4 s1*1/4 |
    s1*1/8 s1*1/8 s1*1/4 s1*1/2 |
    \voiceTwo bes4 bes4 c'4 bes4 |
    bes4 bes4 a4 a4 |
    f4 f4 f2 |
    bes2 bes2 |
    c'4 a4 f2 |
    \oneVoice s1*1/2 s1*1/2 |
    \voiceTwo s1*1/4 s1*1/4 bes2\fermata |
          }
        >>
      }
      \new Lyrics \lyricsto "vT1x1" { 
      "In" -- "te" -- "ger" "vi" -- "tae" "sce" -- "le" -- "ris" -- "que" "pu" -- "rus" "non"
      "e" -- "get" "Mau" -- "ris" "ia" -- "cu" -- "lis" "ne" -- "que" "ar" -- "cu" "nec"
      "ve" -- "ne" -- "na" -- "tis" "gra" -- "vi" -- "da" "sa" -- "git" -- "tis," "Fus" -- "ce,"
      "pha" -- "re" -- "tra," "Fus" -- "ce," "pha" -- "re" -- "tra."
      }
      \new Staff = "lower" \with { instrumentName = \markup \center-column { "Bass I" "Bass II" } shortInstrumentName = \markup \center-column { "B. I" "B. II" } } { \clef "bass"
        <<
          \new Voice = "vB1x1" {
    \autoBeamOff
    \key bes \major \voiceOne f4 g4 g4 f4 |
    ees4 f4 c4 f4 |
    f4 f4 f2 |
    f4 g4 g4 c4 |
    d4 f4 f4 c4 |
    f4 f4 f2 |
    \oneVoice bes,4^\markup \italic "unis." g,4 c4 d4 |
    ees4 e4 f4 f,4 |
    bes,4 a,4 bes,2 |
    \voiceOne d2 bes,2 |
    ees4 ees4 d2 |
    \oneVoice d2^\markup \italic "unis." g2 |
    \voiceOne c4 f,4 f2\fermata |
          }
          \new Voice = "vB2x1" {
    \autoBeamOff
    \voiceTwo bes,4 g,4 c4 d4 |
    ees4 d4 c4 bes,4 |
    f,4 f,4 bes,2 |
    d4 c4 g,4 a,4 |
    g,4 a,4 bes,4 c4 |
    d4 bes,4 f,2 |
    \oneVoice s1*1/4 s1*1/4 s1*1/4 s1*1/4 |
    s1*1/4 s1*1/4 s1*1/4 s1*1/4 |
    s1*1/4 s1*1/4 s1*1/2 |
    \voiceTwo d2 g,2 |
    c4 f,4 bes,2 |
    \oneVoice s1*1/2 s1*1/2 |
    \voiceTwo s1*1/4 s1*1/4 bes,2\fermata |
          }
        >>
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
