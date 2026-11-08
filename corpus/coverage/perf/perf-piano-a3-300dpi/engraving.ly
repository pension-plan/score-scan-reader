\version "2.24.0"
#(set-global-staff-size 26.87)
\header {
  title = "Toccatina"
  subtitle = "symbol-dense piano page"
  composer = "coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a3")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  top-margin = 16.97\mm
  bottom-margin = 16.97\mm
  left-margin = 19.80\mm
  right-margin = 19.80\mm
  ragged-last-bottom = ##f
  system-system-spacing.basic-distance = #16
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
        <<
          \new Voice = "vPx1" {
    \autoLineBreaksOff \autoPageBreaksOff \bar ".|:" \tempo "Allegro" 4 = 132 \mark \markup { \box \bold "A" } \defaultTimeSignature \time 4/4 \key g \major \oneVoice g''16-1\f( a''16 b''16 c'''16 d'''8-.) d'''8-. \tuplet 3/2 { e'''8( d'''8 c'''8) } b''4-> |
    <b' d''>8.( cis''16 <a' c''>8. b'16) <g' b'>2 |
    \slashedGrace { fis''8 } g''4\trill a''8( b''8) \grace { c'''16 d'''16 } e'''4 d'''8 c'''8 |
    \set Score.repeatCommands = #'((volta "1.")) b''4\mordent a''8.\turn g''16 g''2\fermata \bar ":|." |
    \break \set Score.repeatCommands = #'((volta #f) (volta "2.")) b''4.. a''16 g''2 \bar "||" |
    \set Score.repeatCommands = #'((volta #f)) \tempo "Andante" 4 = 76 \mark \markup { \box \bold "B" } \time 3/4 \key ees \major \voiceOne g''2\p^\markup { \italic "dolce" }( f''4) |
    ees''4( d''8 c''8 bes'4) |
    f''4\< g''8( aes''8) bes''4~ |
    \break bes''2.\fermata\!\mf \bar "||" |
    \tempo "Vivace" 4. = 116 \mark \markup { \box \bold "C" } \time 6/8 \key e \major \oneVoice \ottava #1 e'''8-.\ff fis'''8-. gis'''8-. a'''4.-^ \ottava #0 |
    gis''8( fisis''8 gis''8) b''4. |
    fis''?8 e''8 d''8 e''4 r8 |
    e''4.\> r4.\! \textEndMark \markup { \bold "Fine" } \bar "|." |
    \break \tempo "Tempo I" \mark \markup { \box \bold "D" } \defaultTimeSignature \time 2/2 \key aes \major \tuplet 6/4 { aes16-1\mp^\markup { \italic "leggiero" }( c'16 ees'16 aes'16 c''16 ees''16) } aes''4-! \tuplet 5/4 { g''16( f''16 ees''16 des''16 c''16) } bes'4 \breathe |
    c''8.\sfz beses'32 aes'32 g'4-- f'8( ees'16 des'16) c'4 |
    \break \tuplet 3/2 { bes'?4\<( c''4 des''4) } ees''2-^\! |
    c'''64( des'''64 c'''64 bes''64 aes''8.) r8 r16 ees''16 <c'' ees'' aes''>2\fermata\arpeggio\pp |
    R1 \textEndMark \markup { \italic "D.C. al Fine" } \bar "|." |
          }
          \new Voice = "vPx2" {
    \oneVoice s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    \voiceTwo ees''8 bes'8 ees''8 bes'8 d''8 bes'8 |
    aes'2 g'4 |
    d''2 d''4 |
    <ees'' g''>2. |
    \oneVoice s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
          }
        >>
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \key g \major <g,-5 d-2 g-1>4 r8 d8-. g8-. d8-. <g, b,>4-- |
    g,8 d8 b,8 d8 g,8 d8 b,8 d8 |
    c8 g8 e8 g8 d8 a8 fis8 a8 |
    <g, d>2 g,,2\fermata |
    <d a>4 <d c'>4 <g, d b>2 |
    \key ees \major ees,4\sustainOn <g bes>4 <g bes>4 |
    aes,4\sustainOff\sustainOn <c' ees'>4 <c' ees'>4 |
    bes,,4\sustainOff\sustainOn <aes d'>4 <aes d'>4 |
    <ees, bes,>2.\sustainOff\sustainOn |
    \key e \major \clef "treble" e'8\sustainOff gis'8 b'8 e''4. |
    \clef "bass" e,8 b,8 e8 gis,4. |
    a,8 e8 a8 b,4. |
    <e, b, gis>2. |
    \key aes \major \ottava #-1 aes,,4 ees,,4 \ottava #0 aes,2:32 |
    <aes, ees>4 <bes, des f>4 <c ees aes>4 <des f aes>4 |
    <ees, ees>2 r2 |
    aes,,2.\sustainOn r4\sustainOff |
    <aes,, ees, aes,>1\fermata |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
