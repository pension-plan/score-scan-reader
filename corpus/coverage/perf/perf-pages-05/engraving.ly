\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Forty Variations"
  subtitle = "for piano - 5 pages"
  composer = "coverage corpus (CC0)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  top-margin = 10\mm
  bottom-margin = 10\mm
  left-margin = 14\mm
  right-margin = 14\mm
  ragged-last-bottom = ##f
  print-page-number = ##t
  print-first-page-number = ##f
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
        <<
          \new Voice = "vPx1" {
    \autoLineBreaksOff \autoPageBreaksOff \mark \markup { \box \bold "1" } \tempo "Var. 1  Maestoso" 4 = 66 \defaultTimeSignature \time 4/4 \key c \major \oneVoice <c'' e'' g''>4--\mf <c'' e'' g''>4 <c'' e'' g''>2 |
    <d'' fis'' a''>4-- <d'' fis'' a''>4 <d'' fis'' a''>2 |
    <g' b' d''>4-- <g'' b'' d'''>4 <g' b' d''>2 |
    <c'' e'' g''>1\fermata |
    \break <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <e'' g'' b''>4-- <e'' g'' b''>4 <e'' g'' b''>2 |
    <f'' a'' c'''>4-- <f'' a'' c'''>4 <f'' a'' c'''>2 |
    <g' b' d''>1\fermata |
    \break <d'' f'' a''>4-- <d'' f'' a''>4 <d'' f'' a''>2 |
    <g' b' d''>4-- <g'' b'' d'''>4 <g' b' d''>2 |
    <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <c'' e'' g''>1\fermata |
    \break <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <a' cis'' e''>4-- <a' cis'' e''>4 <a' cis'' e''>2 |
    <g' b' d''>4-- <g'' b'' d'''>4 <g' b' d''>2 |
    <c'' e'' g''>1\fermata \bar "||" |
    \pageBreak \mark \markup { \box \bold "2" } \tempo "Var. 2  Allegretto" 4 = 108 \numericTimeSignature \time 4/4 \key aes \major ees''4\f( c''8 aes'8) c''4-. aes''4-. |
    c'''4( a''8 f''8) a''4-. f'''4-. |
    f''4( des''8 bes'8) des''4-. bes''4-. |
    ees''2 g''4-. r4 |
    \break aes''4( f''8 des''8) f''4-. des'''4-. |
    bes''4( g''8 ees''8) g''4-. ees'''4-. |
    c'''4( aes''8 f''8) aes''4-. f'''4-. |
    bes'2 d''4-. r4 |
    \break ees''4( c''8 aes'8) c''4-. aes''4-. |
    bes''4( g''8 ees''8) g''4-. ees'''4-. |
    c'''4( aes''8 f''8) aes''4-. f'''4-. |
    des''2 f''4-. r4 |
    \break ees''4( c''8 aes'8) c''4-. aes''4-. |
    aes''4( f''8 des''8) f''4-. des'''4-. |
    bes''4( g''8 ees''8) g''4-. ees'''4-. |
    aes'2 c''4-. r4 |
    \break ees''4( c''8 aes'8) c''4-. aes''4-. |
    c'''4( aes''8 f''8) aes''4-. f'''4-. |
    bes''4( g''8 ees''8) g''4-. ees'''4-. |
    aes'2 c''4-. r4 \bar "||" |
    \pageBreak \mark \markup { \box \bold "3" } \tempo "Var. 3  Presto" 4 = 152 \time 2/4 \key fis \major fis''16->\mp ais''16 cis'''16 fis'''16 fis'''16 cis'''16 ais''16 fis''16 |
    b'16-> dis''16 fis''16 b''16 b''16 fis''16 dis''16 b'16 |
    cis''16-> eis''16 gis''16 cis'''16 cis'''16 gis''16 eis''16 cis''16 |
    fis''16-> ais''16 cis'''16 fis'''16 fis'''16 cis'''16 ais''16 fis''16 |
    \break fis''16-> ais''16 cis'''16 fis'''16 fis'''16 cis'''16 ais''16 fis''16 |
    dis''16-> fis''16 ais''16 dis'''16 dis'''16 ais''16 fis''16 dis''16 |
    gis'16-> b'16 dis''16 gis''16 gis''16 dis''16 b'16 gis'16 |
    cis''16-> eis''16 gis''16 cis'''16 cis'''16 gis''16 eis''16 cis''16 |
    \break fis''16-> ais''16 cis'''16 fis'''16 fis'''16 cis'''16 ais''16 fis''16 |
    b'16-> dis''16 fis''16 b''16 b''16 fis''16 dis''16 b'16 |
    cis''16-> eis''16 gis''16 cis'''16 cis'''16 gis''16 eis''16 cis''16 |
    fis''16-> ais''16 cis'''16 fis'''16 fis'''16 cis'''16 ais''16 fis''16 |
    \break dis''16-> fis''16 ais''16 dis'''16 dis'''16 ais''16 fis''16 dis''16 |
    b'16-> dis''16 fis''16 b''16 b''16 fis''16 dis''16 b'16 |
    fis''16-> ais''16 cis'''16 fis'''16 fis'''16 cis'''16 ais''16 fis''16 |
    cis''16-> eis''16 gis''16 cis'''16 cis'''16 gis''16 eis''16 cis''16 |
    \break fis''16-> ais''16 cis'''16 fis'''16 fis'''16 cis'''16 ais''16 fis''16 |
    gis'16-> bis'16 dis''16 gis''16 gis''16 dis''16 bis'16 gis'16 |
    cis''16-> eis''16 gis''16 cis'''16 cis'''16 gis''16 eis''16 cis''16 |
    fis''16-> ais''16 cis'''16 fis'''16 fis'''16 cis'''16 ais''16 fis''16 \bar "||" |
    \pageBreak \mark \markup { \box \bold "4" } \tempo "Var. 4  Tempo di valse" 4 = 160 \time 3/4 \key fis \minor \slashedGrace { gis''8 } fis''2\pp a''4 |
    fis''2 b'4 |
    \slashedGrace { b''8 } a''2 cis'''4 |
    cis''2.\trill |
    \break \slashedGrace { b''8 } a''2 cis'''4 |
    dis'''2 gis''4 |
    \slashedGrace { fis''8 } eis''2 gis''4 |
    fis''2.\trill |
    \break \slashedGrace { b''8 } a''2 cis'''4 |
    e''2 a'4 |
    \slashedGrace { e''8 } d''2 fis''4 |
    cis''2.\trill |
    \break \slashedGrace { cis'''8 } b''2 d'''4 |
    gis''2 cis''4 |
    \slashedGrace { b''8 } a''2 cis'''4 |
    fis''2.\trill |
    \break \slashedGrace { b''8 } a''2 cis'''4 |
    ais''2 dis''4 |
    \slashedGrace { fis''8 } eis''2 gis''4 |
    fis''2.\trill \bar "||" |
    \pageBreak \mark \markup { \box \bold "5" } \tempo "Var. 5  Andante" 4. = 54 \time 6/8 \key aes \minor des''4.\ff\<( fes''4 bes'8) |
    g''4.( bes''4 ees''8\!) |
    ces''4.\>( ees''4 aes'8) |
    ces''4.( ees''4 aes'8\!) |
    \break ces''4.\<( ees''4 aes'8) |
    a''4.( c'''4 f''8\!) |
    des''4.\>( fes''?4 bes'8) |
    g''4.( bes''4 ees''8\!) |
    \break fes''4.\<( aes''4 des''8) |
    g''4.( bes''4 ees''8\!) |
    aes''4.\>( ces'''4 fes''8) |
    d''4.( f''4 bes'8\!) |
    \break ces''4.\<( ees''4 aes'8) |
    g''4.( bes''4 ees''8\!) |
    aes''4.\>( ces'''4 fes''8) |
    fes''4.( aes''4 des''8\!) |
    \break c''4.\<( ees''4 aes'8) |
    fes''4.( aes''4 des''8\!) |
    g''4.\>( bes''4 ees''8) |
    ces''4.( ees''4 aes'8\!) \bar "|." |
          }
          \new Voice = "vPx2" {
    \oneVoice s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*1/2 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
    s1*3/4 |
          }
        >>
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \key c \major <c, c>2 g,2 |
    <d, d>2 a,2 |
    <g, g>2 d2 |
    <c, c>1\fermata |
    <c, c>2 g,2 |
    <e, e>2 b,2 |
    <f, f>2 c2 |
    <g, g>1\fermata |
    <d, d>2 a,2 |
    <g, g>2 d2 |
    <c, c>2 g,2 |
    <c, c>1\fermata |
    <c, c>2 g,2 |
    <a, a>2 e2 |
    <g, g>2 d2 |
    <c, c>1\fermata |
    \key aes \major aes,8 ees8 c'8 ees8 aes,8 ees8 c'8 ees8 |
    f8 c8 a8 c8 f8 c8 a8 c8 |
    bes,8 f8 des'8 f8 bes,8 f8 des'8 f8 |
    ees8 bes,8 g8 bes,8 ees8 bes,8 g8 bes,8 |
    des8 aes8 f8 aes8 des8 aes8 f8 aes8 |
    ees8 bes,8 g8 bes,8 ees8 bes,8 g8 bes,8 |
    f8 c8 aes8 c8 f8 c8 aes8 c8 |
    bes,8 f8 d8 f8 bes,8 f8 d8 f8 |
    aes,8 ees8 c'8 ees8 aes,8 ees8 c'8 ees8 |
    ees8 bes,8 g8 bes,8 ees8 bes,8 g8 bes,8 |
    f8 c8 aes8 c8 f8 c8 aes8 c8 |
    des8 aes8 f8 aes8 des8 aes8 f8 aes8 |
    aes,8 ees8 c'8 ees8 aes,8 ees8 c'8 ees8 |
    des8 aes8 f8 aes8 des8 aes8 f8 aes8 |
    ees8 bes,8 g8 bes,8 ees8 bes,8 g8 bes,8 |
    aes,8 ees8 c'8 ees8 aes,8 ees8 c'8 ees8 |
    aes,8 ees8 c'8 ees8 aes,8 ees8 c'8 ees8 |
    f8 c8 aes8 c8 f8 c8 aes8 c8 |
    ees8 bes,8 g8 bes,8 ees8 bes,8 g8 bes,8 |
    aes,8 ees8 c'8 ees8 aes,8 ees8 c'8 ees8 |
    \key fis \major <fis ais>8-. <fis ais>8-. <fis ais>8-. <fis ais>8-. |
    <b dis'>8-. <b dis'>8-. <b dis'>8-. <b dis'>8-. |
    <cis eis>8-. <cis eis>8-. <cis eis>8-. <cis eis>8-. |
    <fis ais>8-. <fis ais>8-. <fis ais>8-. <fis ais>8-. |
    <fis ais>8-. <fis ais>8-. <fis ais>8-. <fis ais>8-. |
    <dis fis>8-. <dis fis>8-. <dis fis>8-. <dis fis>8-. |
    <gis b>8-. <gis b>8-. <gis b>8-. <gis b>8-. |
    <cis eis>8-. <cis eis>8-. <cis eis>8-. <cis eis>8-. |
    <fis ais>8-. <fis ais>8-. <fis ais>8-. <fis ais>8-. |
    <b dis'>8-. <b dis'>8-. <b dis'>8-. <b dis'>8-. |
    <cis eis>8-. <cis eis>8-. <cis eis>8-. <cis eis>8-. |
    <fis ais>8-. <fis ais>8-. <fis ais>8-. <fis ais>8-. |
    <dis fis>8-. <dis fis>8-. <dis fis>8-. <dis fis>8-. |
    <b dis'>8-. <b dis'>8-. <b dis'>8-. <b dis'>8-. |
    <fis ais>8-. <fis ais>8-. <fis ais>8-. <fis ais>8-. |
    <cis eis>8-. <cis eis>8-. <cis eis>8-. <cis eis>8-. |
    <fis ais>8-. <fis ais>8-. <fis ais>8-. <fis ais>8-. |
    <gis bis>8-. <gis bis>8-. <gis bis>8-. <gis bis>8-. |
    <cis eis>8-. <cis eis>8-. <cis eis>8-. <cis eis>8-. |
    <fis ais>8-. <fis ais>8-. <fis ais>8-. <fis ais>8-. |
    \key fis \minor d,4\sustainOn <fis a>4-. <fis a>4-.\sustainOff |
    b,4\sustainOn <d' fis'>4-. <d' fis'>4-.\sustainOff |
    fis,4\sustainOn <a cis'>4-. <a cis'>4-.\sustainOff |
    cis4\sustainOn <eis gis>4-. <eis gis>4-.\sustainOff |
    fis,4\sustainOn <a cis'>4-. <a cis'>4-.\sustainOff |
    gis,4\sustainOn <bis dis'>4-. <bis dis'>4-.\sustainOff |
    cis4\sustainOn <eis gis>4-. <eis gis>4-.\sustainOff |
    fis,4\sustainOn <a cis'>4-. <a cis'>4-.\sustainOff |
    fis,4\sustainOn <a cis'>4-. <a cis'>4-.\sustainOff |
    a,4\sustainOn <cis' e'>4-. <cis' e'>4-.\sustainOff |
    b,4\sustainOn <d' fis'>4-. <d' fis'>4-.\sustainOff |
    cis4\sustainOn <eis gis>4-. <eis gis>4-.\sustainOff |
    gis,4\sustainOn <b d'>4-. <b d'>4-.\sustainOff |
    cis4\sustainOn <eis gis>4-. <eis gis>4-.\sustainOff |
    fis,4\sustainOn <a cis'>4-. <a cis'>4-.\sustainOff |
    fis,4\sustainOn <a cis'>4-. <a cis'>4-.\sustainOff |
    fis,4\sustainOn <a cis'>4-. <a cis'>4-.\sustainOff |
    dis,4\sustainOn <fisis ais>4-. <fisis ais>4-.\sustainOff |
    cis4\sustainOn <eis gis>4-. <eis gis>4-.\sustainOff |
    fis,4\sustainOn <a cis'>4-. <a cis'>4-.\sustainOff |
    \key aes \minor bes,8\sustainOn bes8 des'8 fes'8 des'8 bes8\sustainOff |
    ees,8\sustainOn ees8 g8 bes8 g8 ees8\sustainOff |
    aes,8\sustainOn aes8 ces'8 ees'8 ces'8 aes8\sustainOff |
    aes,8\sustainOn aes8 ces'8 ees'8 ces'8 aes8\sustainOff |
    aes,8\sustainOn aes8 ces'8 ees'8 ces'8 aes8\sustainOff |
    f,8\sustainOn f8 a8 c'8 a8 f8\sustainOff |
    bes,8\sustainOn bes8 des'8 fes'8 des'8 bes8\sustainOff |
    ees,8\sustainOn ees8 g8 bes8 g8 ees8\sustainOff |
    des,8\sustainOn des8 fes8 aes8 fes8 des8\sustainOff |
    ees,8\sustainOn ees8 g8 bes8 g8 ees8\sustainOff |
    fes,8\sustainOn fes8 aes8 ces'8 aes8 fes8\sustainOff |
    bes,8\sustainOn bes8 d'8 f'8 d'8 bes8\sustainOff |
    aes,8\sustainOn aes8 ces'8 ees'8 ces'8 aes8\sustainOff |
    ees,8\sustainOn ees8 g8 bes8 g8 ees8\sustainOff |
    fes,8\sustainOn fes8 aes8 ces'8 aes8 fes8\sustainOff |
    des,8\sustainOn des8 fes8 aes8 fes8 des8\sustainOff |
    aes,8\sustainOn aes8 c'8 ees'8 c'8 aes8\sustainOff |
    des,8\sustainOn des8 fes8 aes8 fes8 des8\sustainOff |
    ees,8\sustainOn ees8 g8 bes8 g8 ees8\sustainOff |
    aes,8\sustainOn aes8 ces'8 ees'8 ces'8 aes8\sustainOff |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
