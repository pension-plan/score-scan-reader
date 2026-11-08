\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Lament"
  subtitle = "for string orchestra"
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
  indent = 20\mm
  short-indent = 10\mm
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new StaffGroup <<
      \new Staff = "v1" \with { instrumentName = "Violin I" shortInstrumentName = "Vn. I" } { \clef "treble"
        <<
          \new Voice = "vV1x1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante espressivo" 4 = 72 \numericTimeSignature \time 4/4 \key e \minor \oneVoice \stemDown b'4\mf e''4 g''4 fis''8[ e''8] |
    dis''4 e''4 fis''2 |
    \voiceOne \stemUp g''4^\markup { \italic "div." } a''4 b''2 |
    a''4 g''4 fis''2 |
    \break \oneVoice \stemDown e''4^\markup { \italic "unis." } g''8[ fis''8] e''4 b'4 |
    c''4 d''4 e''2 |
    \voiceOne \stemUp fis''4\<^\markup { \italic "div." } g''4 a''4 fis''4 |
    g''1\fermata\!\f |
          }
          \new Voice = "vV1x2" {
    \autoBeamOff
    \oneVoice s1 |
    s1 |
    \voiceTwo \stemDown e''4 fis''4 g''2 |
    c''4 b'4 dis''2 |
    \oneVoice s1 |
    s1 |
    \voiceTwo \stemDown dis''4 e''4 c''4 a'4 |
    e''1\fermata |
          }
        >>
      }
      \new Staff = "v2" \with { instrumentName = "Violin II" shortInstrumentName = "Vn. II" } { \clef "treble"
          \new Voice = "vV2x1" {
    \autoBeamOff
    \key e \minor \stemUp g'4\mf \stemDown b'4 b'4 \stemUp a'8[ g'8] |
    fis'4 g'4 a'2 |
    \stemDown <b' e''>4^\markup { \italic "div." } <c'' fis''>4 <d'' g''>2 |
    <c'' e''>4 <b' d''>4 <b' dis''>2 |
    \stemUp g'4^\markup { \italic "unis." } b'8[ a'8] g'4 g'4 |
    a'4 \stemDown b'4 c''2 |
    <a' c''>4\< <b' e''>4 <a' e''>4 \stemUp <fis' c''>4 |
    <g' b'>1\fermata\!\f |
          }
      }
      \new Staff = "va" \with { instrumentName = "Viola" shortInstrumentName = "Va." } { \clef "alto"
          \new Voice = "vVAx1" {
    \autoBeamOff
    \key e \minor \stemDown e'4\mf g'4 g'4 fis'4 |
    \stemUp b4 b4 \stemDown dis'2 |
    e'4 e'4 d'2 |
    e'4 e'4 fis'2 |
    e'4 e'4 e'4 e'4 |
    e'4 fis'4 g'2 |
    fis'4\< g'4 e'4 dis'4 |
    e'1\fermata\!\f |
          }
      }
      \new Staff = "vc" \with { instrumentName = "Violoncello" shortInstrumentName = "Vc." } { \clef "bass"
          \new Voice = "vVCx1" {
    \autoBeamOff
    \key e \minor \stemDown e4\mf e4 e4 \stemUp b,4 |
    b,4 \stemDown e4 \stemUp b,2 |
    \stemDown e4 a4 g2 |
    a4 e4 \stemUp b,2 |
    \stemDown e4 e4 \stemUp c4 c4 |
    a,4 b,4 c2 |
    b,4\< \stemDown e4 \stemUp a,4 b,4 |
    e,1\fermata\!\f |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
    \context { \Lyrics \override LyricHyphen.minimum-distance = #1.6 \override LyricExtender.minimum-length = #0.6 }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } \context { \ChordNames \remove "Note_performer" } }
}
