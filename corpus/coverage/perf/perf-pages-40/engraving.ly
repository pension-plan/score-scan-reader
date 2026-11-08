\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Forty Variations"
  subtitle = "for piano - 40 pages"
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
    ces''4.( ees''4 aes'8\!) \bar "||" |
    \pageBreak \mark \markup { \box \bold "6" } \tempo "Var. 6  Moderato" 4 = 88 \numericTimeSignature \time 4/4 \key a \major \tuplet 3/2 { a'8\p\< cis''8 e''8 } \tuplet 3/2 { a''8 cis'''8 e'''8 } \tuplet 3/2 { e'''8 cis'''8 a''8 } \tuplet 3/2 { e''8 cis''8 a'8 } |
    \tuplet 3/2 { e'8 gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8\! } |
    \tuplet 3/2 { fis'8\> a'8 cis''8 } \tuplet 3/2 { fis''8 a''8 cis'''8 } \tuplet 3/2 { cis'''8 a''8 fis''8 } \tuplet 3/2 { cis''8 a'8 fis'8 } |
    \tuplet 3/2 { d'8 fis'8 a'8 } \tuplet 3/2 { d''8 fis''8 a''8 } \tuplet 3/2 { a''8 fis''8 d''8 } \tuplet 3/2 { a'8 fis'8 d'8\! } |
    \break \tuplet 3/2 { a'8\< cis''8 e''8 } \tuplet 3/2 { a''8 cis'''8 e'''8 } \tuplet 3/2 { e'''8 cis'''8 a''8 } \tuplet 3/2 { e''8 cis''8 a'8 } |
    \tuplet 3/2 { d'8 fis'8 a'8 } \tuplet 3/2 { d''8 fis''8 a''8 } \tuplet 3/2 { a''8 fis''8 d''8 } \tuplet 3/2 { a'8 fis'8 d'8\! } |
    \tuplet 3/2 { e'8\> gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8 } |
    \tuplet 3/2 { a'8 cis''8 e''8 } \tuplet 3/2 { a''8 cis'''8 e'''8 } \tuplet 3/2 { e'''8 cis'''8 a''8 } \tuplet 3/2 { e''8 cis''8 a'8\! } |
    \break \tuplet 3/2 { a'8\< cis''8 e''8 } \tuplet 3/2 { a''8 cis'''8 e'''8 } \tuplet 3/2 { e'''8 cis'''8 a''8 } \tuplet 3/2 { e''8 cis''8 a'8 } |
    \tuplet 3/2 { fis'8 a'8 cis''8 } \tuplet 3/2 { fis''8 a''8 cis'''8 } \tuplet 3/2 { cis'''8 a''8 fis''8 } \tuplet 3/2 { cis''8 a'8 fis'8\! } |
    \tuplet 3/2 { b'8\> d''8 fis''8 } \tuplet 3/2 { b''8 d'''8 fis'''8 } \tuplet 3/2 { fis'''8 d'''8 b''8 } \tuplet 3/2 { fis''8 d''8 b'8 } |
    \tuplet 3/2 { e'8 gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8\! } |
    \break \tuplet 3/2 { a'8\< cis''8 e''8 } \tuplet 3/2 { a''8 cis'''8 e'''8 } \tuplet 3/2 { e'''8 cis'''8 a''8 } \tuplet 3/2 { e''8 cis''8 a'8 } |
    \tuplet 3/2 { d'8 fis'8 a'8 } \tuplet 3/2 { d''8 fis''8 a''8 } \tuplet 3/2 { a''8 fis''8 d''8 } \tuplet 3/2 { a'8 fis'8 d'8\! } |
    \tuplet 3/2 { e'8\> gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8 } |
    \tuplet 3/2 { a'8 cis''8 e''8 } \tuplet 3/2 { a''8 cis'''8 e'''8 } \tuplet 3/2 { e'''8 cis'''8 a''8 } \tuplet 3/2 { e''8 cis''8 a'8\! } |
    \break \tuplet 3/2 { fis'8\< a'8 cis''8 } \tuplet 3/2 { fis''8 a''8 cis'''8 } \tuplet 3/2 { cis'''8 a''8 fis''8 } \tuplet 3/2 { cis''8 a'8 fis'8 } |
    \tuplet 3/2 { d'8 fis'8 a'8 } \tuplet 3/2 { d''8 fis''8 a''8 } \tuplet 3/2 { a''8 fis''8 d''8 } \tuplet 3/2 { a'8 fis'8 d'8\! } |
    \tuplet 3/2 { e'8\> gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8 } |
    \tuplet 3/2 { a'8 cis''8 e''8 } \tuplet 3/2 { a''8 cis'''8 e'''8 } \tuplet 3/2 { e'''8 cis'''8 a''8 } \tuplet 3/2 { e''8 cis''8 a'8\! } \bar "||" |
    \pageBreak \mark \markup { \box \bold "7" } \tempo "Var. 7  Con fuoco" 4 = 120 \key e \minor \ottava #1 <e''' e''''>4->\mf <g''' g''''>4 <b''' b''''>4-^ <g''' g''''>4 |
    <a'' a'''>4-> <c''' c''''>4 <e''' e''''>4-^ <c''' c''''>4 \ottava #0 |
    <b' b''>4-> <dis'' dis'''>4 <fis'' fis'''>4-^ <dis'' dis'''>4 |
    <e'' e'''>4-> <g'' g'''>4 <b'' b'''>4-^ <g'' g'''>4 |
    \break <c'' c'''>4-> <e'' e'''>4 <g'' g'''>4-^ <e'' e'''>4 |
    <a' a''>4-> <c'' c'''>4 <e'' e'''>4-^ <c'' c'''>4 |
    <e'' e'''>4-> <g'' g'''>4 <b'' b'''>4-^ <g'' g'''>4 |
    <b' b''>4-> <dis'' dis'''>4 <fis'' fis'''>4-^ <dis'' dis'''>4 |
    \break \ottava #1 <e''' e''''>4-> <g''' g''''>4 <b''' b''''>4-^ <g''' g''''>4 |
    <fis''' fis''''>4-> <ais''' ais''''>4 <cis'''' cis'''''>4-^ <ais''' ais''''>4 \ottava #0 |
    <b' b''>4-> <dis'' dis'''>4 <fis'' fis'''>4-^ <dis'' dis'''>4 |
    <e'' e'''>4-> <g'' g'''>4 <b'' b'''>4-^ <g'' g'''>4 |
    \break <e'' e'''>4-> <g'' g'''>4 <b'' b'''>4-^ <g'' g'''>4 |
    <g' g''>4-> <b' b''>4 <d'' d'''>4-^ <b' b''>4 |
    <a' a''>4-> <c'' c'''>4 <e'' e'''>4-^ <c'' c'''>4 |
    <b' b''>4-> <dis'' dis'''>4 <fis'' fis'''>4-^ <dis'' dis'''>4 |
    \break \ottava #1 <fis''' fis''''>4-> <a''' a''''>4 <c'''' c'''''>4-^ <a''' a''''>4 |
    <b'' b'''>4-> <dis''' dis''''>4 <fis''' fis''''>4-^ <dis''' dis''''>4 \ottava #0 |
    <b' b''>4-> <dis'' dis'''>4 <fis'' fis'''>4-^ <dis'' dis'''>4 |
    <e'' e'''>4-> <g'' g'''>4 <b'' b'''>4-^ <g'' g'''>4 \bar "||" |
    \pageBreak \mark \markup { \box \bold "8" } \tempo "Var. 8  Cantabile" 4 = 72 \key cis \major \voiceOne eis''2\f( cis''4 gis''4) |
    gis''2( eis''4 bis''4) |
    ais''2( fis''4 cis'''4) |
    gis''1 |
    \break fis''2( dis''4 ais''4) |
    bis''2( gis''4 dis'''4) |
    eis''2( cis''4 gis''4) |
    cis''1 |
    \break eis''2( cis''4 gis''4) |
    cisis''2( ais'4 eis''4) |
    fis''2( dis''4 ais''4) |
    gis''1 |
    \break ais''2( fis''4 cis'''4) |
    bis''2( gis''4 dis'''4) |
    cis''2( ais'4 eis''4) |
    dis''1 |
    \break eis''2( cis''4 gis''4) |
    bis''2( gis''4 dis'''4) |
    bis''2( gis''4 dis'''4) |
    cis''1 \bar "||" |
    \pageBreak \mark \markup { \box \bold "9" } \tempo "Var. 9  Grave" 2 = 48 \time 3/2 \key ees \minor \oneVoice ces''2.\mordent\mp ees''4 aes'2 |
    d''2.\turn f''4 bes'2 |
    ees''2.\mordent ges''4 ces''2 |
    f''1.\fermata |
    \break ges''2.\mordent bes''4 ees''2 |
    d''2.\turn f''4 bes'2 |
    ees''2.\mordent ges''4 ces''2 |
    aes'1.\fermata |
    \break g''2.\mordent bes''4 ees''2 |
    ces''2.\turn ees''4 aes'2 |
    d''2.\mordent f''4 bes'2 |
    ees''1.\fermata |
    \break ges''2.\mordent bes''4 ees''2 |
    ees''2.\turn ges''4 ces''2 |
    aes''2.\mordent ces'''4 f''2 |
    bes'1.\fermata |
    \break ges''2.\mordent bes''4 ees''2 |
    ces''2.\turn ees''4 aes'2 |
    d''2.\mordent f''4 bes'2 |
    ees''1.\fermata \bar "||" |
    \pageBreak \mark \markup { \box \bold "10" } \tempo "Var. 10  Allegro" 4 = 116 \numericTimeSignature \time 4/4 \key d \major d''32\pp e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 |
    b'32 cis''32 d''32 e''32 fis''32 g''32 a''32 b''32 b''4-. fis''4-. b''4 |
    e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 e'''32 e'''4-. b'4-. e''4 |
    a'32 b'32 cis''32 d''32 e''32 fis''32 g''32 a''32 a''4-. e''4-. a''4 |
    \break d''32 e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 |
    g'32 a'32 b'32 cis''32 d''32 e''32 fis''32 g''32 g''4-. d''4-. g''4 |
    a'32 b'32 cis''32 d''32 e''32 fis''32 g''32 a''32 a''4-. e''4-. a''4 |
    d''32 e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 |
    \break b'32 cis''32 d''32 e''32 fis''32 g''32 a''32 b''32 b''4-. fis''4-. b''4 |
    g'32 a'32 b'32 cis''32 d''32 e''32 fis''32 g''32 g''4-. d''4-. g''4 |
    d''32 e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 |
    a'32 b'32 cis''32 d''32 e''32 fis''32 g''32 a''32 a''4-. e''4-. a''4 |
    \break d''32 e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 |
    e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 e'''32 e'''4-. b'4-. e''4 |
    a'32 b'32 cis''32 d''32 e''32 fis''32 g''32 a''32 a''4-. e''4-. a''4 |
    d''32 e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 |
    \break d''32 e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 |
    fis''32 g''32 a''32 b''32 cis'''32 d'''32 e'''32 fis'''32 fis'''4-. cis''4-. fis''4 |
    a'32 b'32 cis''32 d''32 e''32 fis''32 g''32 a''32 a''4-. e''4-. a''4 |
    d''32 e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 \bar "||" |
    \pageBreak \mark \markup { \box \bold "11" } \tempo "Var. 11  Pastorale" 4. = 60 \time 12/8 \key bes \major d''4\ff bes'8 f''8( d''8 bes'8) d''4 bes'8 bes'4. |
    e''4 c''8 g''8( e''8 c''8) e''4 c''8 c''4. |
    a''4 f''8 c'''8( a''8 f''8) a''4 f''8 f''4. |
    d''4 bes'8 f''8( d''8 bes'8) d''4 bes'8 bes'4. |
    \break d''4 bes'8 f''8( d''8 bes'8) d''4 bes'8 bes'4. |
    f''4 d''8 a''8( f''8 d''8) f''4 d''8 d''4. |
    g''4 ees''8 bes''8( g''8 ees''8) g''4 ees''8 ees''4. |
    a''4 f''8 c'''8( a''8 f''8) a''4 f''8 f''4. |
    \break ees''4 c''8 g''8( ees''8 c''8) ees''4 c''8 c''4. |
    a''4 f''8 c'''8( a''8 f''8) a''4 f''8 f''4. |
    d''4 bes'8 f''8( d''8 bes'8) d''4 bes'8 bes'4. |
    d''4 bes'8 f''8( d''8 bes'8) d''4 bes'8 bes'4. |
    \break d''4 bes'8 f''8( d''8 bes'8) d''4 bes'8 bes'4. |
    b'4 g'8 d''8( b'8 g'8) b'4 g'8 g'4. |
    ees''4 c''8 g''8( ees''8 c''8) ees''4 c''8 c''4. |
    a''4 f''8 c'''8( a''8 f''8) a''4 f''8 f''4. |
    \break g''4 ees''8 bes''8( g''8 ees''8) g''4 ees''8 ees''4. |
    a''4 f''8 c'''8( a''8 f''8) a''4 f''8 f''4. |
    a''4 f''8 c'''8( a''8 f''8) a''4 f''8 f''4. |
    d''4 bes'8 f''8( d''8 bes'8) d''4 bes'8 bes'4. \bar "||" |
    \pageBreak \mark \markup { \box \bold "12" } \tempo "Var. 12  Alla marcia" 2 = 60 \defaultTimeSignature \time 2/2 \key b \minor b'8.\p( d''16) fis''4-. d''4-. b'4-- |
    gis'8.( bis'16) dis''4-. bis'4-. gis'4-- |
    cis''8.( e''16) g''4-. e''4-. cis''4-- |
    fis''2-> r2 |
    \break e''8.( g''16) b''4-. g''4-. e''4-- |
    fis''8.( ais''16) cis'''4-. ais''4-. fis''4-- |
    g'8.( b'16) d''4-. b'4-. g'4-- |
    cis''2-> r2 |
    \break b'8.( d''16) fis''4-. d''4-. b'4-- |
    fis''8.( ais''16) cis'''4-. ais''4-. fis''4-- |
    g'8.( b'16) d''4-. b'4-. g'4-- |
    e''2-> r2 |
    \break b'8.( dis''16) fis''4-. dis''4-. b'4-- |
    e''8.( g''16) b''4-. g''4-. e''4-- |
    fis''8.( ais''16) cis'''4-. ais''4-. fis''4-- |
    b'2-> r2 |
    \break b'8.( d''16) fis''4-. d''4-. b'4-- |
    g'8.( b'16) d''4-. b'4-. g'4-- |
    fis''8.( ais''16) cis'''4-. ais''4-. fis''4-- |
    b'2-> r2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "13" } \tempo "Var. 13  Siciliano" 4. = 50 \time 9/8 \key bes \minor d''4.\mf f''8.( d''16 bes'8) bes'4. |
    ges''4. bes''8.( ges''16 ees''8) ees''4. |
    a''4. c'''8.( a''16 f''8) f''4. |
    des''4. f''8.( des''16 bes'8) bes'4. |
    \break des''4. f''8.( des''16 bes'8) bes'4. |
    bes''4. des'''8.( bes''16 ges''8) ges''4. |
    ees''4. ges''8.( ees''16 c''8) c''4. |
    a''4. c'''8.( a''16 f''8) f''4. |
    \break des''4. f''8.( des''16 bes'8) bes'4. |
    ges''4. bes''8.( ges''16 ees''8) ees''4. |
    a''4. c'''8.( a''16 f''8) f''4. |
    des''4. f''8.( des''16 bes'8) bes'4. |
    \break bes''4. des'''8.( bes''16 ges''8) ges''4. |
    ges''4. bes''8.( ges''16 ees''8) ees''4. |
    des''4. f''8.( des''16 bes'8) bes'4. |
    a''4. c'''8.( a''16 f''8) f''4. |
    \break des''4. f''8.( des''16 bes'8) bes'4. |
    e''4. g''8.( e''16 c''8) c''4. |
    a''4. c'''8.( a''16 f''8) f''4. |
    des''4. f''8.( des''16 bes'8) bes'4. \bar "||" |
    \pageBreak \mark \markup { \box \bold "14" } \tempo "Var. 14  Inquieto" 4 = 132 \time 5/4 \key g \major e''4\f g''4 b''4 g''2 |
    c''4 e''4 g''4 e''2 |
    g'4 b'4 d''4 b'2 |
    d''4 fis''4 a''4 fis''2 |
    \break g'4 b'4 d''4 b'2 |
    a'4 cis''4 e''4 cis''2 |
    d''4 fis''4 a''4 fis''2 |
    g'4 b'4 d''4 b'2 |
    \break g'4 b'4 d''4 b'2 |
    b'4 d''4 fis''4 d''2 |
    c''4 e''4 g''4 e''2 |
    d''4 fis''4 a''4 fis''2 |
    \break a'4 c''4 e''4 c''2 |
    d''4 fis''4 a''4 fis''2 |
    g'4 b'4 d''4 b'2 |
    g'4 b'4 d''4 b'2 |
    \break g'4 b'4 d''4 b'2 |
    e''4 gis''4 b''4 gis''2 |
    d''4 fis''4 a''4 fis''2 |
    g'4 b'4 d''4 b'2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "15" } \tempo "Var. 15  Danza" 8 = 220 \time 7/8 \key e \major fis''8\mp[ a''8] cis'''8[ a''8] fis''8[ cis'''8 fis'''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    e''8[ gis''8] b''8[ gis''8] e''8[ b''8 e'''8] |
    e''8[ gis''8] b''8[ gis''8] e''8[ b''8 e'''8] |
    \break e''8[ gis''8] b''8[ gis''8] e''8[ b''8 e'''8] |
    cis''8[ eis''8] gis''8[ eis''8] cis''8[ gis''8 cis'''8] |
    fis''8[ a''8] cis'''8[ a''8] fis''8[ cis'''8 fis'''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    \break a'8[ cis''8] e''8[ cis''8] a'8[ e''8 a''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    cis''8[ e''8] gis''8[ e''8] cis''8[ gis''8 cis'''8] |
    fis''8[ ais''8] cis'''8[ ais''8] fis''8[ cis'''8 fis'''8] |
    \break e''8[ gis''8] b''8[ gis''8] e''8[ b''8 e'''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    cis''8[ e''8] gis''8[ e''8] cis''8[ gis''8 cis'''8] |
    a'8[ cis''8] e''8[ cis''8] a'8[ e''8 a''8] |
    \break e''8[ gis''8] b''8[ gis''8] e''8[ b''8 e'''8] |
    a'8[ cis''8] e''8[ cis''8] a'8[ e''8 a''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    e''8[ gis''8] b''8[ gis''8] e''8[ b''8 e'''8] \bar "||" |
    \pageBreak \mark \markup { \box \bold "16" } \tempo "Var. 16  Misterioso" 4 = 60 \numericTimeSignature \time 4/4 \key d \minor <d'' f'' a''>2\pp <d'' f'' a''>2 |
    <a' cis'' e''>2 <a' cis'' e''>2 |
    <bes' d'' f''>2 <bes' d'' f''>2 |
    <g'' bes'' d'''>2 <g'' bes'' d'''>2 |
    \break <d'' fis'' a''>2 <d'' fis'' a''>2 |
    <g'' bes'' d'''>2 <g'' bes'' d'''>2 |
    <a' cis'' e''>2 <a' cis'' e''>2 |
    <d'' f'' a''>2 <d'' f'' a''>2 |
    \break <d'' f'' a''>2 <d'' f'' a''>2 |
    <bes' d'' f''>2 <bes' d'' f''>2 |
    <e'' g'' bes''>2 <e'' g'' bes''>2 |
    <a' cis'' e''>2 <a' cis'' e''>2 |
    \break <d'' f'' a''>2 <d'' f'' a''>2 |
    <g'' bes'' d'''>2 <g'' bes'' d'''>2 |
    <a' cis'' e''>2 <a' cis'' e''>2 |
    <d'' f'' a''>2 <d'' f'' a''>2 |
    \break <bes' d'' f''>2 <bes' d'' f''>2 |
    <g'' bes'' d'''>2 <g'' bes'' d'''>2 |
    <a' cis'' e''>2 <a' cis'' e''>2 |
    <d'' f'' a''>2 <d'' f'' a''>2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "17" } \tempo "Var. 17  Comodo" 4 = 96 \key ces \major ces''4\ff ees''4 ges''2 |
    fes''4 aes''4 ces'''2 |
    ges''4 bes''4 des'''2 |
    ces''4 ees''4 ges''2 |
    \break aes''4 ces'''4 ees'''2 |
    fes''4 aes''4 ces'''2 |
    ces''4 ees''4 ges''2 |
    ges''4 bes''4 des'''2 |
    \break ces''4 ees''4 ges''2 |
    des''4 f''4 aes''2 |
    ges''4 bes''4 des'''2 |
    ces''4 ees''4 ges''2 |
    \break ces''4 ees''4 ges''2 |
    ees''4 ges''4 bes''2 |
    fes''4 aes''4 ces'''2 |
    ges''4 bes''4 des'''2 |
    \break des''4 fes''4 aes''2 |
    ges''4 bes''4 des'''2 |
    ges''4 bes''4 des'''2 |
    ces''4 ees''4 ges''2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "18" } \tempo "Var. 18  Fluido" 4 = 69 \key ais \minor \tuplet 6/4 { ais'16\p cis''16 eis''16 ais''16 cis'''16 eis'''16 } eis'''4 \tuplet 6/4 { eis'''16 cis'''16 ais''16 eis''16 cis''16 ais'16 } ais'4 |
    \tuplet 6/4 { cis'16 eis'16 gis'16 cis''16 eis''16 gis''16 } gis''4 \tuplet 6/4 { gis''16 eis''16 cis''16 gis'16 eis'16 cis'16 } cis'4 |
    \tuplet 6/4 { dis'16 fis'16 ais'16 dis''16 fis''16 ais''16 } ais''4 \tuplet 6/4 { ais''16 fis''16 dis''16 ais'16 fis'16 dis'16 } dis'4 |
    \tuplet 6/4 { eis'16 gisis'16 bis'16 eis''16 gisis''16 bis''16 } bis''4 \tuplet 6/4 { bis''16 gisis''16 eis''16 bis'16 gisis'16 eis'16 } eis'4 |
    \break \tuplet 6/4 { bis16 dis'16 fis'16 bis'16 dis''16 fis''16 } fis''4 \tuplet 6/4 { fis''16 dis''16 bis'16 fis'16 dis'16 bis16 } bis4 |
    \tuplet 6/4 { eis'16 gisis'16 bis'16 eis''16 gisis''16 bis''16 } bis''4 \tuplet 6/4 { bis''16 gisis''16 eis''16 bis'16 gisis'16 eis'16 } eis'4 |
    \tuplet 6/4 { ais'16 cis''16 eis''16 ais''16 cis'''16 eis'''16 } eis'''4 \tuplet 6/4 { eis'''16 cis'''16 ais''16 eis''16 cis''16 ais'16 } ais'4 |
    \tuplet 6/4 { ais'16 cis''16 eis''16 ais''16 cis'''16 eis'''16 } eis'''4 \tuplet 6/4 { eis'''16 cis'''16 ais''16 eis''16 cis''16 ais'16 } ais'4 |
    \break \tuplet 6/4 { ais'16 cis''16 eis''16 ais''16 cis'''16 eis'''16 } eis'''4 \tuplet 6/4 { eis'''16 cis'''16 ais''16 eis''16 cis''16 ais'16 } ais'4 |
    \tuplet 6/4 { fisis'16 aisis'16 cisis''16 fisis''16 aisis''16 cisis'''16 } cisis'''4 \tuplet 6/4 { cisis'''16 aisis''16 fisis''16 cisis''16 aisis'16 fisis'16 } fisis'4 |
    \tuplet 6/4 { bis16 dis'16 fis'?16 bis'16 dis''16 fis''?16 } fis''4 \tuplet 6/4 { fis''16 dis''16 bis'16 fis'16 dis'16 bis16 } bis4 |
    \tuplet 6/4 { eis'16 gisis'16 bis'16 eis''16 gisis''16 bis''16 } bis''4 \tuplet 6/4 { bis''16 gisis''16 eis''16 bis'16 gisis'16 eis'16 } eis'4 |
    \break \tuplet 6/4 { dis'16 fis'16 ais'16 dis''16 fis''16 ais''16 } ais''4 \tuplet 6/4 { ais''16 fis''16 dis''16 ais'16 fis'16 dis'16 } dis'4 |
    \tuplet 6/4 { eis'16 gisis'16 bis'16 eis''16 gisis''16 bis''16 } bis''4 \tuplet 6/4 { bis''16 gisis''16 eis''16 bis'16 gisis'16 eis'16 } eis'4 |
    \tuplet 6/4 { fis'16 ais'16 cis''16 fis''16 ais''16 cis'''16 } cis'''4 \tuplet 6/4 { cis'''16 ais''16 fis''16 cis''16 ais'16 fis'16 } fis'4 |
    \tuplet 6/4 { bis16 disis'16 fisis'16 bis'16 disis''16 fisis''16 } fisis''4 \tuplet 6/4 { fisis''16 disis''16 bis'16 fisis'16 disis'16 bis16 } bis4 |
    \break \tuplet 6/4 { ais'16 cis''16 eis''16 ais''16 cis'''16 eis'''16 } eis'''4 \tuplet 6/4 { eis'''16 cis'''16 ais''16 eis''16 cis''16 ais'16 } ais'4 |
    \tuplet 6/4 { eis'16 gisis'16 bis'16 eis''16 gisis''16 bis''16 } bis''4 \tuplet 6/4 { bis''16 gisis''16 eis''16 bis'16 gisis'16 eis'16 } eis'4 |
    \tuplet 6/4 { eis'16 gisis'16 bis'16 eis''16 gisis''16 bis''16 } bis''4 \tuplet 6/4 { bis''16 gisis''16 eis''16 bis'16 gisis'16 eis'16 } eis'4 |
    \tuplet 6/4 { ais'16 cis''16 eis''16 ais''16 cis'''16 eis'''16 } eis'''4 \tuplet 6/4 { eis'''16 cis'''16 ais''16 eis''16 cis''16 ais'16 } ais'4 \bar "||" |
    \pageBreak \mark \markup { \box \bold "19" } \tempo "Var. 19  Capriccioso" 4 = 76 \key g \minor \tuplet 5/4 { c''16\mf ees''16 g''16 c'''16 ees'''16 } ees'''8 c'''8 g''2 |
    \tuplet 5/4 { d'16 fis'16 a'16 d''16 fis''16 } fis''8 d''8 a'2 |
    \tuplet 5/4 { ees'16 g'16 bes'16 ees''16 g''16 } g''8 ees''8 bes'2 |
    \tuplet 5/4 { a'16 cis''16 e''16 a''16 cis'''16 } cis'''8 a''8 e''2 |
    \break \tuplet 5/4 { g'16 bes'16 d''16 g''16 bes''16 } bes''8 g''8 d''2 |
    \tuplet 5/4 { d'16 fis'16 a'16 d''16 fis''16 } fis''8 d''8 a'2 |
    \tuplet 5/4 { ees'16 g'16 bes'16 ees''16 g''16 } g''8 ees''8 bes'2 |
    \tuplet 5/4 { c''16 ees''16 g''16 c'''16 ees'''16 } ees'''8 c'''8 g''2 |
    \break \tuplet 5/4 { g'16 b'16 d''16 g''16 b''16 } b''8 g''8 d''2 |
    \tuplet 5/4 { c''16 ees''16 g''16 c'''16 ees'''16 } ees'''8 c'''8 g''2 |
    \tuplet 5/4 { d'16 fis'16 a'16 d''16 fis''16 } fis''8 d''8 a'2 |
    \tuplet 5/4 { g'16 bes'16 d''16 g''16 bes''16 } bes''8 g''8 d''2 |
    \break \tuplet 5/4 { g'16 bes'16 d''16 g''16 bes''16 } bes''8 g''8 d''2 |
    \tuplet 5/4 { ees'16 g'16 bes'16 ees''16 g''16 } g''8 ees''8 bes'2 |
    \tuplet 5/4 { a'16 c''16 ees''16 a''16 c'''16 } c'''8 a''8 ees''2 |
    \tuplet 5/4 { d'16 fis'16 a'16 d''16 fis''16 } fis''8 d''8 a'2 |
    \break \tuplet 5/4 { g'16 bes'16 d''16 g''16 bes''16 } bes''8 g''8 d''2 |
    \tuplet 5/4 { c''16 ees''16 g''16 c'''16 ees'''16 } ees'''8 c'''8 g''2 |
    \tuplet 5/4 { d'16 fis'16 a'16 d''16 fis''16 } fis''8 d''8 a'2 |
    \tuplet 5/4 { g'16 bes'16 d''16 g''16 bes''16 } bes''8 g''8 d''2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "20" } \tempo "Var. 20  Scherzando" 4 = 100 \time 2/4 \key des \major \grace { des'''16 f'''16 } des''8\f f''8 \slashedGrace { f'''8 } aes''8 f''8 |
    \grace { bes''16 des'''16 } bes'8 des''8 \slashedGrace { des'''8 } f''8 des''8 |
    \grace { ees'''16 ges'''16 } ees''8 ges''8 \slashedGrace { ges'''8 } bes''8 ges''8 |
    \grace { aes''16 c'''16 } aes'8 c''8 \slashedGrace { c'''8 } ees''8 c''8 |
    \break \grace { des'''16 f'''16 } des''8 f''8 \slashedGrace { f'''8 } aes''8 f''8 |
    \grace { ges'''16 bes'''16 } ges''8 bes''8 \slashedGrace { bes'''8 } des'''8 bes''8 |
    \grace { aes''16 c'''16 } aes'8 c''8 \slashedGrace { c'''8 } ees''8 c''8 |
    \grace { des'''16 f'''16 } des''8 f''8 \slashedGrace { f'''8 } aes''8 f''8 |
    \break \grace { bes''16 des'''16 } bes'8 des''8 \slashedGrace { des'''8 } f''8 des''8 |
    \grace { ges'''16 bes'''16 } ges''8 bes''8 \slashedGrace { bes'''8 } des'''8 bes''8 |
    \grace { des'''16 f'''16 } des''8 f''8 \slashedGrace { f'''8 } aes''8 f''8 |
    \grace { aes''16 c'''16 } aes'8 c''8 \slashedGrace { c'''8 } ees''8 c''8 |
    \break \grace { des'''16 f'''16 } des''8 f''8 \slashedGrace { f'''8 } aes''8 f''8 |
    \grace { ees'''16 g'''16 } ees''8 g''8 \slashedGrace { g'''8 } bes''8 g''8 |
    \grace { aes''16 c'''16 } aes'8 c''8 \slashedGrace { c'''8 } ees''8 c''8 |
    \grace { des'''16 f'''16 } des''8 f''8 \slashedGrace { f'''8 } aes''8 f''8 |
    \break \grace { des'''16 f'''16 } des''8 f''8 \slashedGrace { f'''8 } aes''8 f''8 |
    \grace { f'''16 aes'''16 } f''8 aes''8 \slashedGrace { aes'''8 } c'''8 aes''8 |
    \grace { aes''16 c'''16 } aes'8 c''8 \slashedGrace { c'''8 } ees''8 c''8 |
    \grace { des'''16 f'''16 } des''8 f''8 \slashedGrace { f'''8 } aes''8 f''8 \bar "||" |
    \pageBreak \mark \markup { \box \bold "21" } \tempo "Var. 21  Largo" 4 = 50 \numericTimeSignature \time 4/4 \key f \minor <f'-1 aes'-2 c''-3 f''-5>2\arpeggio\mp <f' aes' c'' f''>2\arpeggio |
    <g'-1 b'-2 d''-3 g''-5>2\arpeggio <g' b' d'' g''>2\arpeggio |
    <c''-1 e''-2 g''-3 c'''-5>2\arpeggio <c'' e'' g'' c'''>2\arpeggio |
    <f'-1 aes'-2 c''-3 f''-5>2\arpeggio <f' aes' c'' f''>2\arpeggio |
    \break <f'-1 aes'-2 c''-3 f''-5>2\arpeggio <f' aes' c'' f''>2\arpeggio |
    <aes'-1 c''-2 ees''-3 aes''-5>2\arpeggio <aes' c'' ees'' aes''>2\arpeggio |
    <bes'-1 des''-2 f''-3 bes''-5>2\arpeggio <bes' des'' f'' bes''>2\arpeggio |
    <c''-1 e''-2 g''-3 c'''-5>2\arpeggio <c'' e'' g'' c'''>2\arpeggio |
    \break <g'-1 bes'-2 des''-3 g''-5>2\arpeggio <g' bes' des'' g''>2\arpeggio |
    <c''-1 e''-2 g''-3 c'''-5>2\arpeggio <c'' e'' g'' c'''>2\arpeggio |
    <f'-1 aes'-2 c''-3 f''-5>2\arpeggio <f' aes' c'' f''>2\arpeggio |
    <f'-1 aes'-2 c''-3 f''-5>2\arpeggio <f' aes' c'' f''>2\arpeggio |
    \break <f'-1 aes'-2 c''-3 f''-5>2\arpeggio <f' aes' c'' f''>2\arpeggio |
    <d'-1 fis'-2 a'-3 d''-5>2\arpeggio <d' fis' a' d''>2\arpeggio |
    <g'-1 bes'-2 des''?-3 g''-5>2\arpeggio <g' bes' des'' g''>2\arpeggio |
    <c''-1 e''-2 g''-3 c'''-5>2\arpeggio <c'' e'' g'' c'''>2\arpeggio |
    \break <bes'-1 des''-2 f''-3 bes''-5>2\arpeggio <bes' des'' f'' bes''>2\arpeggio |
    <c''-1 e''-2 g''-3 c'''-5>2\arpeggio <c'' e'' g'' c'''>2\arpeggio |
    <c''-1 e''-2 g''-3 c'''-5>2\arpeggio <c'' e'' g'' c'''>2\arpeggio |
    <f'-1 aes'-2 c''-3 f''-5>2\arpeggio <f' aes' c'' f''>2\arpeggio \bar "||" |
    \pageBreak \mark \markup { \box \bold "22" } \tempo "Var. 22  Semplice" 4 = 80 \time 3/4 \key dis \minor fis''2\pp dis''4 |
    disis''2 bis'4 \breathe |
    gis''2 eis''4 |
    cisis''2 ais'4 \breathe |
    \break b''2 gis''4 |
    cisis''2 ais'4 \breathe |
    dis''2 b'4 |
    gisis''2 eis''4 \breathe |
    \break fis''2 dis''4 |
    cisis''2 ais'4 \breathe |
    dis''2 b'4 |
    b''2 gis''4 \breathe |
    \break fisis''2 dis''4 |
    b''2 gis''4 \breathe |
    cisis''2 ais'4 |
    fis''2 dis''4 \breathe |
    \break fis''2 dis''4 |
    dis''2 b'4 \breathe |
    cisis''2 ais'4 |
    fis''2 dis''4 \breathe \bar "||" |
    \pageBreak \mark \markup { \box \bold "23" } \tempo "Var. 23  Maestoso" 4 = 66 \defaultTimeSignature \time 4/4 \key f \major <f'' a'' c'''>4--\ff <f'' a'' c'''>4 <f'' a'' c'''>2 |
    <bes' d'' f''>4-- <bes' d'' f''>4 <bes' d'' f''>2 |
    <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <f'' a'' c'''>1\fermata |
    \break <f'' a'' c'''>4-- <f'' a'' c'''>4 <f'' a'' c'''>2 |
    <d'' f'' a''>4-- <d'' f'' a''>4 <d'' f'' a''>2 |
    <g' bes' d''>4-- <g'' bes'' d'''>4 <g' bes' d''>2 |
    <c'' e'' g''>1\fermata |
    \break <f'' a'' c'''>4-- <f'' a'' c'''>4 <f'' a'' c'''>2 |
    <bes' d'' f''>4-- <bes' d'' f''>4 <bes' d'' f''>2 |
    <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <f'' a'' c'''>1\fermata |
    \break <d'' f'' a''>4-- <d'' f'' a''>4 <d'' f'' a''>2 |
    <bes' d'' f''>4-- <bes' d'' f''>4 <bes' d'' f''>2 |
    <f'' a'' c'''>4-- <f'' a'' c'''>4 <f'' a'' c'''>2 |
    <c'' e'' g''>1\fermata |
    \break <f'' a'' c'''>4-- <f'' a'' c'''>4 <f'' a'' c'''>2 |
    <g' b' d''>4-- <g'' b'' d'''>4 <g' b' d''>2 |
    <c'' e'' g''>4-- <c'' e'' g''>4 <c'' e'' g''>2 |
    <f'' a'' c'''>1\fermata \bar "||" |
    \pageBreak \mark \markup { \box \bold "24" } \tempo "Var. 24  Allegretto" 4 = 108 \numericTimeSignature \time 4/4 \key b \major dis''4\p( b'8 gis'8) b'4-. gis''4-. |
    b''4( gis''8 e''8) gis''4-. e'''4-. |
    fis''4( dis''8 b'8) dis''4-. b''4-. |
    fis''2 ais''4-. r4 |
    \break fis''4( dis''8 b'8) dis''4-. b''4-. |
    gis''4( eis''8 cis''8) eis''4-. cis'''4-. |
    cis'''4( ais''8 fis''8) ais''4-. fis'''4-. |
    b'2 dis''4-. r4 |
    \break fis''4( dis''8 b'8) dis''4-. b''4-. |
    ais''4( fis''8 dis''8) fis''4-. dis'''4-. |
    b''4( gis''8 e''8) gis''4-. e'''4-. |
    fis''2 ais''4-. r4 |
    \break gis''4( e''8 cis''8) e''4-. cis'''4-. |
    cis'''4( ais''8 fis''8) ais''4-. fis'''4-. |
    fis''4( dis''8 b'8) dis''4-. b''4-. |
    b'2 dis''4-. r4 |
    \break fis''4( dis''8 b'8) dis''4-. b''4-. |
    dis''4( bis'8 gis'8) bis'4-. gis''4-. |
    cis'''4( ais''8 fis''8) ais''4-. fis'''4-. |
    b'2 dis''4-. r4 \bar "||" |
    \pageBreak \mark \markup { \box \bold "25" } \tempo "Var. 25  Presto" 4 = 152 \time 2/4 \key ges \major aes'16->\mf ces''16 ees''16 aes''16 aes''16 ees''16 ces''16 aes'16 |
    des''16-> f''16 aes''16 des'''16 des'''16 aes''16 f''16 des''16 |
    ges''16-> bes''16 des'''16 ges'''16 ges'''16 des'''16 bes''16 ges''16 |
    ges''16-> bes''16 des'''16 ges'''16 ges'''16 des'''16 bes''16 ges''16 |
    \break ges''16-> bes''16 des'''16 ges'''16 ges'''16 des'''16 bes''16 ges''16 |
    ees''16-> g''16 bes''16 ees'''16 ees'''16 bes''16 g''16 ees''16 |
    aes'16-> ces''16 ees''16 aes''16 aes''16 ees''16 ces''16 aes'16 |
    des''16-> f''16 aes''16 des'''16 des'''16 aes''16 f''16 des''16 |
    \break ces''16-> ees''16 ges''16 ces'''16 ces'''16 ges''16 ees''16 ces''16 |
    des''16-> f''16 aes''16 des'''16 des'''16 aes''16 f''16 des''16 |
    ees''16-> ges''16 bes''16 ees'''16 ees'''16 bes''16 ges''16 ees''16 |
    aes'16-> c''16 ees''16 aes''16 aes''16 ees''16 c''16 aes'16 |
    \break ges''16-> bes''16 des'''16 ges'''16 ges'''16 des'''16 bes''16 ges''16 |
    des''16-> f''16 aes''16 des'''16 des'''16 aes''16 f''16 des''16 |
    ees''16-> ges''16 bes''16 ees'''16 ees'''16 bes''16 ges''16 ees''16 |
    ces''16-> ees''16 ges''16 ces'''16 ces'''16 ges''16 ees''16 ces''16 |
    \break ges''16-> bes''16 des'''16 ges'''16 ges'''16 des'''16 bes''16 ges''16 |
    ces''16-> ees''16 ges''16 ces'''16 ces'''16 ges''16 ees''16 ces''16 |
    des''16-> f''16 aes''16 des'''16 des'''16 aes''16 f''16 des''16 |
    ges''16-> bes''16 des'''16 ges'''16 ges'''16 des'''16 bes''16 ges''16 \bar "||" |
    \pageBreak \mark \markup { \box \bold "26" } \tempo "Var. 26  Tempo di valse" 4 = 160 \time 3/4 \key gis \minor \slashedGrace { cis'''8 } b''2\f dis'''4 |
    ais''2 dis''4 |
    \slashedGrace { ais''8 } gis''2 b''4 |
    cis''2.\trill |
    \break \slashedGrace { cis'''8 } bis''2 dis'''4 |
    gis''2 cis''4 |
    \slashedGrace { gis''8 } fisis''2 ais''4 |
    gis''2.\trill |
    \break \slashedGrace { cis'''8 } b''2 dis'''4 |
    b''2 e''4 |
    \slashedGrace { dis''8 } cis''2 e''4 |
    dis''2.\trill |
    \break \slashedGrace { cis'''8 } b''2 dis'''4 |
    gis''2 cis''4 |
    \slashedGrace { gis''8 } fisis''2 ais''4 |
    gis''2.\trill |
    \break \slashedGrace { ais''8 } gis''2 b''4 |
    gis''2 cis''4 |
    \slashedGrace { gis''8 } fisis''2 ais''4 |
    gis''2.\trill \bar "||" |
    \pageBreak \mark \markup { \box \bold "27" } \tempo "Var. 27  Andante" 4. = 54 \time 6/8 \key c \minor ees''4.\mp\<( g''4 c''8) |
    aes''4.( c'''4 f''8\!) |
    b'4.\>( d''4 g'8) |
    ees''4.( g''4 c''8\!) |
    \break c''4.\<( ees''4 aes'8) |
    aes''4.( c'''4 f''8\!) |
    ees''4.\>( g''4 c''8) |
    b'4.( d''4 g'8\!) |
    \break ees''4.\<( g''4 c''8) |
    fis''4.( a''4 d''8\!) |
    b'4.\>( d''4 g'8) |
    ees''4.( g''4 c''8\!) |
    \break ees''4.\<( g''4 c''8) |
    g''4.( bes''4 ees''8\!) |
    aes''4.\>( c'''4 f''8) |
    b'4.( d''4 g'8\!) |
    \break f''4.\<( aes''4 d''8) |
    b'4.( d''4 g'8\!) |
    b'4.\>( d''4 g'8) |
    ees''4.( g''4 c''8\!) \bar "||" |
    \pageBreak \mark \markup { \box \bold "28" } \tempo "Var. 28  Moderato" 4 = 88 \numericTimeSignature \time 4/4 \key a \minor \tuplet 3/2 { a'8\pp\< c''8 e''8 } \tuplet 3/2 { a''8 c'''8 e'''8 } \tuplet 3/2 { e'''8 c'''8 a''8 } \tuplet 3/2 { e''8 c''8 a'8 } |
    \tuplet 3/2 { c'8 e'8 g'8 } \tuplet 3/2 { c''8 e''8 g''8 } \tuplet 3/2 { g''8 e''8 c''8 } \tuplet 3/2 { g'8 e'8 c'8\! } |
    \tuplet 3/2 { d'8\> f'8 a'8 } \tuplet 3/2 { d''8 f''8 a''8 } \tuplet 3/2 { a''8 f''8 d''8 } \tuplet 3/2 { a'8 f'8 d'8 } |
    \tuplet 3/2 { e'8 gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8\! } |
    \break \tuplet 3/2 { b'8\< d''8 f''8 } \tuplet 3/2 { b''8 d'''8 f'''8 } \tuplet 3/2 { f'''8 d'''8 b''8 } \tuplet 3/2 { f''8 d''8 b'8 } |
    \tuplet 3/2 { e'8 gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8\! } |
    \tuplet 3/2 { a'8\> c''8 e''8 } \tuplet 3/2 { a''8 c'''8 e'''8 } \tuplet 3/2 { e'''8 c'''8 a''8 } \tuplet 3/2 { e''8 c''8 a'8 } |
    \tuplet 3/2 { a'8 c''8 e''8 } \tuplet 3/2 { a''8 c'''8 e'''8 } \tuplet 3/2 { e'''8 c'''8 a''8 } \tuplet 3/2 { e''8 c''8 a'8\! } |
    \break \tuplet 3/2 { a'8\< c''8 e''8 } \tuplet 3/2 { a''8 c'''8 e'''8 } \tuplet 3/2 { e'''8 c'''8 a''8 } \tuplet 3/2 { e''8 c''8 a'8 } |
    \tuplet 3/2 { fis'8 ais'8 cis''8 } \tuplet 3/2 { fis''8 ais''8 cis'''8 } \tuplet 3/2 { cis'''8 ais''8 fis''8 } \tuplet 3/2 { cis''8 ais'8 fis'8\! } |
    \tuplet 3/2 { b'8\> d''8 f''?8 } \tuplet 3/2 { b''8 d'''8 f'''8 } \tuplet 3/2 { f'''8 d'''8 b''8 } \tuplet 3/2 { f''8 d''8 b'8 } |
    \tuplet 3/2 { e'8 gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8\! } |
    \break \tuplet 3/2 { d'8\< f'8 a'8 } \tuplet 3/2 { d''8 f''8 a''8 } \tuplet 3/2 { a''8 f''8 d''8 } \tuplet 3/2 { a'8 f'8 d'8 } |
    \tuplet 3/2 { e'8 gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8\! } |
    \tuplet 3/2 { f'8\> a'8 c''8 } \tuplet 3/2 { f''8 a''8 c'''8 } \tuplet 3/2 { c'''8 a''8 f''8 } \tuplet 3/2 { c''8 a'8 f'8 } |
    \tuplet 3/2 { b'8 dis''8 fis''8 } \tuplet 3/2 { b''8 dis'''8 fis'''8 } \tuplet 3/2 { fis'''8 dis'''8 b''8 } \tuplet 3/2 { fis''8 dis''8 b'8\! } |
    \break \tuplet 3/2 { a'8\< c''8 e''8 } \tuplet 3/2 { a''8 c'''8 e'''8 } \tuplet 3/2 { e'''8 c'''8 a''8 } \tuplet 3/2 { e''8 c''8 a'8 } |
    \tuplet 3/2 { e'8 gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8\! } |
    \tuplet 3/2 { e'8\> gis'8 b'8 } \tuplet 3/2 { e''8 gis''8 b''8 } \tuplet 3/2 { b''8 gis''8 e''8 } \tuplet 3/2 { b'8 gis'8 e'8 } |
    \tuplet 3/2 { a'8 c''8 e''8 } \tuplet 3/2 { a''8 c'''8 e'''8 } \tuplet 3/2 { e'''8 c'''8 a''8 } \tuplet 3/2 { e''8 c''8 a'8\! } \bar "||" |
    \pageBreak \mark \markup { \box \bold "29" } \tempo "Var. 29  Con fuoco" 4 = 120 \key ees \major \ottava #1 <aes'' aes'''>4->\ff <c''' c''''>4 <ees''' ees''''>4-^ <c''' c''''>4 |
    <bes'' bes'''>4-> <d''' d''''>4 <f''' f''''>4-^ <d''' d''''>4 \ottava #0 |
    <c'' c'''>4-> <ees'' ees'''>4 <g'' g'''>4-^ <ees'' ees'''>4 |
    <f'' f'''>4-> <a'' a'''>4 <c''' c''''>4-^ <a'' a'''>4 |
    \break <ees'' ees'''>4-> <g'' g'''>4 <bes'' bes'''>4-^ <g'' g'''>4 |
    <bes' bes''>4-> <d'' d'''>4 <f'' f'''>4-^ <d'' d'''>4 |
    <c'' c'''>4-> <ees'' ees'''>4 <g'' g'''>4-^ <ees'' ees'''>4 |
    <aes' aes''>4-> <c'' c'''>4 <ees'' ees'''>4-^ <c'' c'''>4 |
    \break \ottava #1 <ees''' ees''''>4-> <g''' g''''>4 <bes''' bes''''>4-^ <g''' g''''>4 |
    <aes'' aes'''>4-> <c''' c''''>4 <ees''' ees''''>4-^ <c''' c''''>4 \ottava #0 |
    <bes' bes''>4-> <d'' d'''>4 <f'' f'''>4-^ <d'' d'''>4 |
    <ees'' ees'''>4-> <g'' g'''>4 <bes'' bes'''>4-^ <g'' g'''>4 |
    \break <ees'' ees'''>4-> <g'' g'''>4 <bes'' bes'''>4-^ <g'' g'''>4 |
    <c'' c'''>4-> <ees'' ees'''>4 <g'' g'''>4-^ <ees'' ees'''>4 |
    <f'' f'''>4-> <aes'' aes'''>4 <c''' c''''>4-^ <aes'' aes'''>4 |
    <bes' bes''>4-> <d'' d'''>4 <f'' f'''>4-^ <d'' d'''>4 |
    \break \ottava #1 <ees''' ees''''>4-> <g''' g''''>4 <bes''' bes''''>4-^ <g''' g''''>4 |
    <aes'' aes'''>4-> <c''' c''''>4 <ees''' ees''''>4-^ <c''' c''''>4 \ottava #0 |
    <bes' bes''>4-> <d'' d'''>4 <f'' f'''>4-^ <d'' d'''>4 |
    <ees'' ees'''>4-> <g'' g'''>4 <bes'' bes'''>4-^ <g'' g'''>4 \bar "||" |
    \pageBreak \mark \markup { \box \bold "30" } \tempo "Var. 30  Cantabile" 4 = 72 \key cis \minor \voiceOne e''2\p( cis''4 gis''4) |
    cis''2( a'4 e''4) |
    fis''2( dis''4 a''4) |
    gis''1 |
    \break e''2( cis''4 gis''4) |
    a''2( fis''4 cis'''4) |
    bis''2( gis''4 dis'''4) |
    cis''1 |
    \break cis''2( a'4 e''4) |
    a''2( fis''4 cis'''4) |
    e''2( cis''4 gis''4) |
    gis''1 |
    \break e''2( cis''4 gis''4) |
    fisis''2( dis''4 ais''4) |
    bis''2( gis''4 dis'''4) |
    cis''1 |
    \break e''2( cis''4 gis''4) |
    gis''2( e''4 b''4) |
    bis''2( gis''4 dis'''4) |
    cis''1 \bar "||" |
    \pageBreak \mark \markup { \box \bold "31" } \tempo "Var. 31  Grave" 2 = 48 \time 3/2 \key c \major \oneVoice e''2.\mordent\mf g''4 c''2 |
    fis''2.\turn a''4 d''2 |
    b'2.\mordent d''4 g'2 |
    c''1.\fermata |
    \break e''2.\mordent g''4 c''2 |
    g''2.\turn b''4 e''2 |
    a''2.\mordent c'''4 f''2 |
    g'1.\fermata |
    \break f''2.\mordent a''4 d''2 |
    b'2.\turn d''4 g'2 |
    e''2.\mordent g''4 c''2 |
    c''1.\fermata |
    \break e''2.\mordent g''4 c''2 |
    cis''2.\turn e''4 a'2 |
    f''2.\mordent a''4 d''2 |
    g'1.\fermata |
    \break a''2.\mordent c'''4 f''2 |
    b'2.\turn d''4 g'2 |
    b'2.\mordent d''4 g'2 |
    c''1.\fermata \bar "||" |
    \pageBreak \mark \markup { \box \bold "32" } \tempo "Var. 32  Allegro" 4 = 116 \numericTimeSignature \time 4/4 \key aes \major aes'32\f bes'32 c''32 des''32 ees''32 f''32 g''32 aes''32 aes''4-. ees''4-. aes''4 |
    f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 f'''32 f'''4-. c''4-. f''4 |
    bes'32 c''32 des''32 ees''32 f''32 g''32 aes''32 bes''32 bes''4-. f''4-. bes''4 |
    ees''32 f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 ees'''4-. bes'4-. ees''4 |
    \break des''32 ees''32 f''32 g''32 aes''32 bes''32 c'''32 des'''32 des'''4-. aes''4-. des''4 |
    ees''32 f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 ees'''4-. bes'4-. ees''4 |
    f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 f'''32 f'''4-. c''4-. f''4 |
    bes'32 c''32 des''32 ees''32 f''32 g''32 aes''32 bes''32 bes''4-. f''4-. bes''4 |
    \break aes'32 bes'32 c''32 des''32 ees''32 f''32 g''32 aes''32 aes''4-. ees''4-. aes''4 |
    ees''32 f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 ees'''4-. bes'4-. ees''4 |
    f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 f'''32 f'''4-. c''4-. f''4 |
    des''32 ees''32 f''32 g''32 aes''32 bes''32 c'''32 des'''32 des'''4-. aes''4-. des''4 |
    \break aes'32 bes'32 c''32 des''32 ees''32 f''32 g''32 aes''32 aes''4-. ees''4-. aes''4 |
    des''32 ees''32 f''32 g''32 aes''32 bes''32 c'''32 des'''32 des'''4-. aes''4-. des''4 |
    ees''32 f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 ees'''4-. bes'4-. ees''4 |
    aes'32 bes'32 c''32 des''32 ees''32 f''32 g''32 aes''32 aes''4-. ees''4-. aes''4 |
    \break aes'32 bes'32 c''32 des''32 ees''32 f''32 g''32 aes''32 aes''4-. ees''4-. aes''4 |
    f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 f'''32 f'''4-. c''4-. f''4 |
    ees''32 f''32 g''32 aes''32 bes''32 c'''32 des'''32 ees'''32 ees'''4-. bes'4-. ees''4 |
    aes'32 bes'32 c''32 des''32 ees''32 f''32 g''32 aes''32 aes''4-. ees''4-. aes''4 \bar "||" |
    \pageBreak \mark \markup { \box \bold "33" } \tempo "Var. 33  Pastorale" 4. = 60 \time 12/8 \key fis \major ais''4\mp fis''8 cis'''8( ais''8 fis''8) ais''4 fis''8 fis''4. |
    dis''4 b'8 fis''8( dis''8 b'8) dis''4 b'8 b'4. |
    eis''4 cis''8 gis''8( eis''8 cis''8) eis''4 cis''8 cis''4. |
    ais''4 fis''8 cis'''8( ais''8 fis''8) ais''4 fis''8 fis''4. |
    \break ais''4 fis''8 cis'''8( ais''8 fis''8) ais''4 fis''8 fis''4. |
    fis''4 dis''8 ais''8( fis''8 dis''8) fis''4 dis''8 dis''4. |
    b'4 gis'8 dis''8( b'8 gis'8) b'4 gis'8 gis'4. |
    eis''4 cis''8 gis''8( eis''8 cis''8) eis''4 cis''8 cis''4. |
    \break ais''4 fis''8 cis'''8( ais''8 fis''8) ais''4 fis''8 fis''4. |
    dis''4 b'8 fis''8( dis''8 b'8) dis''4 b'8 b'4. |
    eis''4 cis''8 gis''8( eis''8 cis''8) eis''4 cis''8 cis''4. |
    ais''4 fis''8 cis'''8( ais''8 fis''8) ais''4 fis''8 fis''4. |
    \break fis''4 dis''8 ais''8( fis''8 dis''8) fis''4 dis''8 dis''4. |
    dis''4 b'8 fis''8( dis''8 b'8) dis''4 b'8 b'4. |
    ais''4 fis''8 cis'''8( ais''8 fis''8) ais''4 fis''8 fis''4. |
    eis''4 cis''8 gis''8( eis''8 cis''8) eis''4 cis''8 cis''4. |
    \break ais''4 fis''8 cis'''8( ais''8 fis''8) ais''4 fis''8 fis''4. |
    bis'4 gis'8 dis''8( bis'8 gis'8) bis'4 gis'8 gis'4. |
    eis''4 cis''8 gis''8( eis''8 cis''8) eis''4 cis''8 cis''4. |
    ais''4 fis''8 cis'''8( ais''8 fis''8) ais''4 fis''8 fis''4. \bar "||" |
    \pageBreak \mark \markup { \box \bold "34" } \tempo "Var. 34  Alla marcia" 2 = 60 \defaultTimeSignature \time 2/2 \key fis \minor d''8.\pp( fis''16) a''4-. fis''4-. d''4-- |
    b'8.( d''16) fis''4-. d''4-. b'4-- |
    fis''8.( a''16) cis'''4-. a''4-. fis''4-- |
    cis''2-> r2 |
    \break fis''8.( a''16) cis'''4-. a''4-. fis''4-- |
    gis'8.( bis'16) dis''4-. bis'4-. gis'4-- |
    cis''8.( eis''16) gis''4-. eis''4-. cis''4-- |
    fis''2-> r2 |
    \break fis''8.( a''16) cis'''4-. a''4-. fis''4-- |
    a'8.( cis''16) e''4-. cis''4-. a'4-- |
    b'8.( d''16) fis''4-. d''4-. b'4-- |
    cis''2-> r2 |
    \break gis'8.( b'16) d''4-. b'4-. gis'4-- |
    cis''8.( eis''16) gis''4-. eis''4-. cis''4-- |
    fis''8.( a''16) cis'''4-. a''4-. fis''4-- |
    fis''2-> r2 |
    \break fis''8.( a''16) cis'''4-. a''4-. fis''4-- |
    dis''8.( fisis''16) ais''4-. fisis''4-. dis''4-- |
    cis''8.( eis''16) gis''4-. eis''4-. cis''4-- |
    fis''2-> r2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "35" } \tempo "Var. 35  Siciliano" 4. = 50 \time 9/8 \key aes \minor des''4.\ff fes''8.( des''16 bes'8) bes'4. |
    g''4. bes''8.( g''16 ees''8) ees''4. |
    ces''4. ees''8.( ces''16 aes'8) aes'4. |
    ces''4. ees''8.( ces''16 aes'8) aes'4. |
    \break ces''4. ees''8.( ces''16 aes'8) aes'4. |
    a''4. c'''8.( a''16 f''8) f''4. |
    des''4. fes''?8.( des''16 bes'8) bes'4. |
    g''4. bes''8.( g''16 ees''8) ees''4. |
    \break fes''4. aes''8.( fes''16 des''8) des''4. |
    g''4. bes''8.( g''16 ees''8) ees''4. |
    aes''4. ces'''8.( aes''16 fes''8) fes''4. |
    d''4. f''8.( d''16 bes'8) bes'4. |
    \break ces''4. ees''8.( ces''16 aes'8) aes'4. |
    g''4. bes''8.( g''16 ees''8) ees''4. |
    aes''4. ces'''8.( aes''16 fes''8) fes''4. |
    fes''4. aes''8.( fes''16 des''8) des''4. |
    \break c''4. ees''8.( c''16 aes'8) aes'4. |
    fes''4. aes''8.( fes''16 des''8) des''4. |
    g''4. bes''8.( g''16 ees''8) ees''4. |
    ces''4. ees''8.( ces''16 aes'8) aes'4. \bar "||" |
    \pageBreak \mark \markup { \box \bold "36" } \tempo "Var. 36  Inquieto" 4 = 132 \time 5/4 \key a \major a'4\p cis''4 e''4 cis''2 |
    e''4 gis''4 b''4 gis''2 |
    fis''4 a''4 cis'''4 a''2 |
    d''4 fis''4 a''4 fis''2 |
    \break a'4 cis''4 e''4 cis''2 |
    d''4 fis''4 a''4 fis''2 |
    e''4 gis''4 b''4 gis''2 |
    a'4 cis''4 e''4 cis''2 |
    \break a'4 cis''4 e''4 cis''2 |
    fis''4 a''4 cis'''4 a''2 |
    b'4 d''4 fis''4 d''2 |
    e''4 gis''4 b''4 gis''2 |
    \break a'4 cis''4 e''4 cis''2 |
    d''4 fis''4 a''4 fis''2 |
    e''4 gis''4 b''4 gis''2 |
    a'4 cis''4 e''4 cis''2 |
    \break fis''4 a''4 cis'''4 a''2 |
    d''4 fis''4 a''4 fis''2 |
    e''4 gis''4 b''4 gis''2 |
    a'4 cis''4 e''4 cis''2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "37" } \tempo "Var. 37  Danza" 8 = 220 \time 7/8 \key e \minor e''8\mf[ g''8] b''8[ g''8] e''8[ b''8 e'''8] |
    a'8[ c''8] e''8[ c''8] a'8[ e''8 a''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    e''8[ g''8] b''8[ g''8] e''8[ b''8 e'''8] |
    \break c''8[ e''8] g''8[ e''8] c''8[ g''8 c'''8] |
    a'8[ c''8] e''8[ c''8] a'8[ e''8 a''8] |
    e''8[ g''8] b''8[ g''8] e''8[ b''8 e'''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    \break e''8[ g''8] b''8[ g''8] e''8[ b''8 e'''8] |
    fis''8[ ais''8] cis'''8[ ais''8] fis''8[ cis'''8 fis'''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    e''8[ g''8] b''8[ g''8] e''8[ b''8 e'''8] |
    \break e''8[ g''8] b''8[ g''8] e''8[ b''8 e'''8] |
    g''8[ b''8] d'''8[ b''8] g''8[ d'''8 g'''8] |
    a'8[ c''8] e''8[ c''8] a'8[ e''8 a''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    \break fis''8[ a''8] c'''8[ a''8] fis''8[ c'''8 fis'''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    b'8[ dis''8] fis''8[ dis''8] b'8[ fis''8 b''8] |
    e''8[ g''8] b''8[ g''8] e''8[ b''8 e'''8] \bar "||" |
    \pageBreak \mark \markup { \box \bold "38" } \tempo "Var. 38  Misterioso" 4 = 60 \numericTimeSignature \time 4/4 \key cis \major <cis'' eis'' gis''>2\f <cis'' eis'' gis''>2 |
    <eis'' gis'' bis''>2 <eis'' gis'' bis''>2 |
    <fis'' ais'' cis'''>2 <fis'' ais'' cis'''>2 |
    <gis'' bis'' dis'''>2 <gis'' bis'' dis'''>2 |
    \break <dis'' fis'' ais''>2 <dis'' fis'' ais''>2 |
    <gis'' bis'' dis'''>2 <gis'' bis'' dis'''>2 |
    <cis'' eis'' gis''>2 <cis'' eis'' gis''>2 |
    <cis'' eis'' gis''>2 <cis'' eis'' gis''>2 |
    \break <cis'' eis'' gis''>2 <cis'' eis'' gis''>2 |
    <ais' cisis'' eis''>2 <ais' cisis'' eis''>2 |
    <dis'' fis'' ais''>2 <dis'' fis'' ais''>2 |
    <gis'' bis'' dis'''>2 <gis'' bis'' dis'''>2 |
    \break <fis'' ais'' cis'''>2 <fis'' ais'' cis'''>2 |
    <gis'' bis'' dis'''>2 <gis'' bis'' dis'''>2 |
    <ais' cis'' eis''>2 <ais' cis'' eis''>2 |
    <dis'' fisis'' ais''>2 <dis'' fisis'' ais''>2 |
    \break <cis'' eis'' gis''>2 <cis'' eis'' gis''>2 |
    <gis'' bis'' dis'''>2 <gis'' bis'' dis'''>2 |
    <gis'' bis'' dis'''>2 <gis'' bis'' dis'''>2 |
    <cis'' eis'' gis''>2 <cis'' eis'' gis''>2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "39" } \tempo "Var. 39  Comodo" 4 = 96 \key ees \minor aes''4\mp ces'''4 ees'''2 |
    bes'4 d''4 f''2 |
    ces''4 ees''4 ges''2 |
    f''4 a''4 c'''2 |
    \break ees''4 ges''4 bes''2 |
    bes'4 d''4 f''2 |
    ces''4 ees''4 ges''2 |
    aes''4 ces'''4 ees'''2 |
    \break ees''4 g''4 bes''2 |
    aes''4 ces'''4 ees'''2 |
    bes'4 d''4 f''2 |
    ees''4 ges''4 bes''2 |
    \break ees''4 ges''4 bes''2 |
    ces''4 ees''4 ges''2 |
    f''4 aes''4 ces'''2 |
    bes'4 d''4 f''2 |
    \break ees''4 ges''4 bes''2 |
    aes''4 ces'''4 ees'''2 |
    bes'4 d''4 f''2 |
    ees''4 ges''4 bes''2 \bar "||" |
    \pageBreak \mark \markup { \box \bold "40" } \tempo "Var. 40  Fluido" 4 = 69 \key d \major \tuplet 6/4 { d'16\pp fis'16 a'16 d''16 fis''16 a''16 } a''4 \tuplet 6/4 { a''16 fis''16 d''16 a'16 fis'16 d'16 } d'4 |
    \tuplet 6/4 { b'16 d''16 fis''16 b''16 d'''16 fis'''16 } fis'''4 \tuplet 6/4 { fis'''16 d'''16 b''16 fis''16 d''16 b'16 } b'4 |
    \tuplet 6/4 { e'16 g'16 b'16 e''16 g''16 b''16 } b''4 \tuplet 6/4 { b''16 g''16 e''16 b'16 g'16 e'16 } e'4 |
    \tuplet 6/4 { a'16 cis''16 e''16 a''16 cis'''16 e'''16 } e'''4 \tuplet 6/4 { e'''16 cis'''16 a''16 e''16 cis''16 a'16 } a'4 |
    \break \tuplet 6/4 { d'16 fis'16 a'16 d''16 fis''16 a''16 } a''4 \tuplet 6/4 { a''16 fis''16 d''16 a'16 fis'16 d'16 } d'4 |
    \tuplet 6/4 { g'16 b'16 d''16 g''16 b''16 d'''16 } d'''4 \tuplet 6/4 { d'''16 b''16 g''16 d''16 b'16 g'16 } g'4 |
    \tuplet 6/4 { a'16 cis''16 e''16 a''16 cis'''16 e'''16 } e'''4 \tuplet 6/4 { e'''16 cis'''16 a''16 e''16 cis''16 a'16 } a'4 |
    \tuplet 6/4 { d'16 fis'16 a'16 d''16 fis''16 a''16 } a''4 \tuplet 6/4 { a''16 fis''16 d''16 a'16 fis'16 d'16 } d'4 |
    \break \tuplet 6/4 { b'16 d''16 fis''16 b''16 d'''16 fis'''16 } fis'''4 \tuplet 6/4 { fis'''16 d'''16 b''16 fis''16 d''16 b'16 } b'4 |
    \tuplet 6/4 { g'16 b'16 d''16 g''16 b''16 d'''16 } d'''4 \tuplet 6/4 { d'''16 b''16 g''16 d''16 b'16 g'16 } g'4 |
    \tuplet 6/4 { d'16 fis'16 a'16 d''16 fis''16 a''16 } a''4 \tuplet 6/4 { a''16 fis''16 d''16 a'16 fis'16 d'16 } d'4 |
    \tuplet 6/4 { a'16 cis''16 e''16 a''16 cis'''16 e'''16 } e'''4 \tuplet 6/4 { e'''16 cis'''16 a''16 e''16 cis''16 a'16 } a'4 |
    \break \tuplet 6/4 { d'16 fis'16 a'16 d''16 fis''16 a''16 } a''4 \tuplet 6/4 { a''16 fis''16 d''16 a'16 fis'16 d'16 } d'4 |
    \tuplet 6/4 { e'16 gis'16 b'16 e''16 gis''16 b''16 } b''4 \tuplet 6/4 { b''16 gis''16 e''16 b'16 gis'16 e'16 } e'4 |
    \tuplet 6/4 { a'16 cis''16 e''16 a''16 cis'''16 e'''16 } e'''4 \tuplet 6/4 { e'''16 cis'''16 a''16 e''16 cis''16 a'16 } a'4 |
    \tuplet 6/4 { d'16 fis'16 a'16 d''16 fis''16 a''16 } a''4 \tuplet 6/4 { a''16 fis''16 d''16 a'16 fis'16 d'16 } d'4 |
    \break \tuplet 6/4 { d'16 fis'16 a'16 d''16 fis''16 a''16 } a''4 \tuplet 6/4 { a''16 fis''16 d''16 a'16 fis'16 d'16 } d'4 |
    \tuplet 6/4 { fis'16 a'16 cis''16 fis''16 a''16 cis'''16 } cis'''4 \tuplet 6/4 { cis'''16 a''16 fis''16 cis''16 a'16 fis'16 } fis'4 |
    \tuplet 6/4 { a'16 cis''16 e''16 a''16 cis'''16 e'''16 } e'''4 \tuplet 6/4 { e'''16 cis'''16 a''16 e''16 cis''16 a'16 } a'4 |
    \tuplet 6/4 { d'16 fis'16 a'16 d''16 fis''16 a''16 } a''4 \tuplet 6/4 { a''16 fis''16 d''16 a'16 fis'16 d'16 } d'4 \bar "|." |
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
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    \voiceTwo cis''8 eis''8 gis''8 cis'''8 cis'''8 gis''8 eis''8 cis''8 |
    eis'8 gis'8 bis'8 eis''8 eis''8 bis'8 gis'8 eis'8 |
    fis'8 ais'8 cis''8 fis''8 fis''8 cis''8 ais'8 fis'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    dis'8 fis'8 ais'8 dis''8 dis''8 ais'8 fis'8 dis'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    cis''8 eis''8 gis''8 cis'''8 cis'''8 gis''8 eis''8 cis''8 |
    cis''8 eis''8 gis''8 cis'''8 cis'''8 gis''8 eis''8 cis''8 |
    cis''8 eis''8 gis''8 cis'''8 cis'''8 gis''8 eis''8 cis''8 |
    ais'8 cisis''8 eis''8 ais''8 ais''8 eis''8 cisis''8 ais'8 |
    dis'8 fis'8 ais'8 dis''8 dis''8 ais'8 fis'8 dis'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    fis'8 ais'8 cis''8 fis''8 fis''8 cis''8 ais'8 fis'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    ais'8 cis''8 eis''8 ais''8 ais''8 eis''8 cis''8 ais'8 |
    dis'8 fisis'8 ais'8 dis''8 dis''8 ais'8 fisis'8 dis'8 |
    cis''8 eis''8 gis''8 cis'''8 cis'''8 gis''8 eis''8 cis''8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    cis''8 eis''8 gis''8 cis'''8 cis'''8 gis''8 eis''8 cis''8 |
    \oneVoice s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
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
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
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
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
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
    s1 |
    s1 |
    s1 |
    s1 |
    s1 |
    \voiceTwo cis''8 e''8 gis''8 cis'''8 cis'''8 gis''8 e''8 cis''8 |
    a'8 cis''8 e''8 a''8 a''8 e''8 cis''8 a'8 |
    dis'8 fis'8 a'8 dis''8 dis''8 a'8 fis'8 dis'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    cis''8 e''8 gis''8 cis'''8 cis'''8 gis''8 e''8 cis''8 |
    fis'8 a'8 cis''8 fis''8 fis''8 cis''8 a'8 fis'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    cis''8 e''8 gis''8 cis'''8 cis'''8 gis''8 e''8 cis''8 |
    a'8 cis''8 e''8 a''8 a''8 e''8 cis''8 a'8 |
    fis'8 a'8 cis''8 fis''8 fis''8 cis''8 a'8 fis'8 |
    cis''8 e''8 gis''8 cis'''8 cis'''8 gis''8 e''8 cis''8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    cis''8 e''8 gis''8 cis'''8 cis'''8 gis''8 e''8 cis''8 |
    dis'8 fisis'8 ais'8 dis''8 dis''8 ais'8 fisis'8 dis'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    cis''8 e''8 gis''8 cis'''8 cis'''8 gis''8 e''8 cis''8 |
    cis''8 e''8 gis''8 cis'''8 cis'''8 gis''8 e''8 cis''8 |
    e'8 gis'8 b'8 e''8 e''8 b'8 gis'8 e'8 |
    gis'8 bis'8 dis''8 gis''8 gis''8 dis''8 bis'8 gis'8 |
    cis''8 e''8 gis''8 cis'''8 cis'''8 gis''8 e''8 cis''8 |
    \oneVoice s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
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
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
    s1*3/2 |
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
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*9/8 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*5/4 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
    s1*7/8 |
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
    \key a \major a,2 e2 |
    e,2 b,2 |
    fis,2 cis2 |
    d,2 a,2 |
    a,2 e2 |
    d,2 a,2 |
    e,2 b,2 |
    a,2 e2 |
    a,2 e2 |
    fis,2 cis2 |
    b,2 fis2 |
    e,2 b,2 |
    a,2 e2 |
    d,2 a,2 |
    e,2 b,2 |
    a,2 e2 |
    fis,2 cis2 |
    d,2 a,2 |
    e,2 b,2 |
    a,2 e2 |
    \key e \minor <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 |
    <a, a>8 <a, a>8 <a, a>8 <a, a>8 <a, a>8 <a, a>8 <a, a>8 <a, a>8 |
    <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 |
    <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 |
    \ottava #-1 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 |
    <a,, a,>8 <a,, a,>8 <a,, a,>8 <a,, a,>8 <a,, a,>8 <a,, a,>8 <a,, a,>8 <a,, a,>8 \ottava #0 |
    <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 |
    <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 |
    <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 |
    <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 |
    <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 |
    <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 |
    \ottava #-1 <e,, e,>8 <e,, e,>8 <e,, e,>8 <e,, e,>8 <e,, e,>8 <e,, e,>8 <e,, e,>8 <e,, e,>8 |
    <g,, g,>8 <g,, g,>8 <g,, g,>8 <g,, g,>8 <g,, g,>8 <g,, g,>8 <g,, g,>8 <g,, g,>8 \ottava #0 |
    <a, a>8 <a, a>8 <a, a>8 <a, a>8 <a, a>8 <a, a>8 <a, a>8 <a, a>8 |
    <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 |
    <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 <fis, fis>8 |
    <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 |
    <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 <b, b>8 |
    <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 <e, e>8 |
    \key cis \major cis4 gis4 eis,4 gis4 |
    eis,4 bis,4 gis,4 bis,4 |
    fis,4 cis4 ais,4 cis4 |
    gis,4 dis4 bis,4 dis4 |
    dis,4 ais,4 fis,4 ais,4 |
    gis,4 dis4 bis,4 dis4 |
    cis4 gis4 eis,4 gis4 |
    cis4 gis4 eis,4 gis4 |
    cis4 gis4 eis,4 gis4 |
    ais,4 eis4 cisis4 eis4 |
    dis,4 ais,4 fis,4 ais,4 |
    gis,4 dis4 bis,4 dis4 |
    fis,4 cis4 ais,4 cis4 |
    gis,4 dis4 bis,4 dis4 |
    ais,4 eis4 cis4 eis4 |
    dis,4 ais,4 fisis,4 ais,4 |
    cis4 gis4 eis,4 gis4 |
    gis,4 dis4 bis,4 dis4 |
    gis,4 dis4 bis,4 dis4 |
    cis4 gis4 eis,4 gis4 |
    \key ees \minor <aes, ces ees>2 <aes, ces ees>2 <aes, ces ees>2 |
    <bes, d f>2 <bes, d f>2 <bes, d f>2 |
    <ces ees ges>2 <ces ees ges>2 <ces ees ges>2 |
    <f a c'>1.\fermata |
    <ees ges bes>2 <ees ges bes>2 <ees ges bes>2 |
    <bes, d f>2 <bes, d f>2 <bes, d f>2 |
    <ces ees ges>2 <ces ees ges>2 <ces ees ges>2 |
    <aes, ces ees>1.\fermata |
    <ees g bes>2 <ees g bes>2 <ees g bes>2 |
    <aes, ces ees>2 <aes, ces ees>2 <aes, ces ees>2 |
    <bes, d f>2 <bes, d f>2 <bes, d f>2 |
    <ees ges bes>1.\fermata |
    <ees ges bes>2 <ees ges bes>2 <ees ges bes>2 |
    <ces ees ges>2 <ces ees ges>2 <ces ees ges>2 |
    <f aes ces'>2 <f aes ces'>2 <f aes ces'>2 |
    <bes, d f>1.\fermata |
    <ees ges bes>2 <ees ges bes>2 <ees ges bes>2 |
    <aes, ces ees>2 <aes, ces ees>2 <aes, ces ees>2 |
    <bes, d f>2 <bes, d f>2 <bes, d f>2 |
    <ees ges bes>1.\fermata |
    \key d \major <d fis a>4 <d fis a>4 <d fis a>4 <d fis a>4 |
    <b d' fis'>4 <b d' fis'>4 <b d' fis'>4 <b d' fis'>4 |
    <e g b>4 <e g b>4 <e g b>4 <e g b>4 |
    <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 |
    <d fis a>4 <d fis a>4 <d fis a>4 <d fis a>4 |
    <g b d'>4 <g b d'>4 <g b d'>4 <g b d'>4 |
    <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 |
    <d fis a>4 <d fis a>4 <d fis a>4 <d fis a>4 |
    <b d' fis'>4 <b d' fis'>4 <b d' fis'>4 <b d' fis'>4 |
    <g b d'>4 <g b d'>4 <g b d'>4 <g b d'>4 |
    <d fis a>4 <d fis a>4 <d fis a>4 <d fis a>4 |
    <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 |
    <d fis a>4 <d fis a>4 <d fis a>4 <d fis a>4 |
    <e gis b>4 <e gis b>4 <e gis b>4 <e gis b>4 |
    <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 |
    <d fis a>4 <d fis a>4 <d fis a>4 <d fis a>4 |
    <d fis a>4 <d fis a>4 <d fis a>4 <d fis a>4 |
    <fis a cis'>4 <fis a cis'>4 <fis a cis'>4 <fis a cis'>4 |
    <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 <a cis' e'>4 |
    <d fis a>4 <d fis a>4 <d fis a>4 <d fis a>4 |
    \key bes \major <bes, f>4. <bes, f>4. <bes, f>4. <bes, f>4. |
    <c, g,>4. <c, g,>4. <c, g,>4. <c, g,>4. |
    <f, c>4. <f, c>4. <f, c>4. <f, c>4. |
    <bes, f>4. <bes, f>4. <bes, f>4. <bes, f>4. |
    <bes, f>4. <bes, f>4. <bes, f>4. <bes, f>4. |
    <d, a,>4. <d, a,>4. <d, a,>4. <d, a,>4. |
    <ees, bes,>4. <ees, bes,>4. <ees, bes,>4. <ees, bes,>4. |
    <f, c>4. <f, c>4. <f, c>4. <f, c>4. |
    <c, g,>4. <c, g,>4. <c, g,>4. <c, g,>4. |
    <f, c>4. <f, c>4. <f, c>4. <f, c>4. |
    <bes, f>4. <bes, f>4. <bes, f>4. <bes, f>4. |
    <bes, f>4. <bes, f>4. <bes, f>4. <bes, f>4. |
    <bes, f>4. <bes, f>4. <bes, f>4. <bes, f>4. |
    <g, d>4. <g, d>4. <g, d>4. <g, d>4. |
    <c, g,>4. <c, g,>4. <c, g,>4. <c, g,>4. |
    <f, c>4. <f, c>4. <f, c>4. <f, c>4. |
    <ees, bes,>4. <ees, bes,>4. <ees, bes,>4. <ees, bes,>4. |
    <f, c>4. <f, c>4. <f, c>4. <f, c>4. |
    <f, c>4. <f, c>4. <f, c>4. <f, c>4. |
    <bes, f>4. <bes, f>4. <bes, f>4. <bes, f>4. |
    \key b \minor b,4 <d' fis'>4-. fis,4 <d' fis'>4-. |
    gis,4 <bis dis'>4-. dis4 <bis dis'>4-. |
    cis,4 <e' g'>4-. g,?4 <e' g'>4-. |
    fis,4 <ais cis'>4-. cis4 <ais cis'>4-. |
    e,4 <g b>4-. b,4 <g b>4-. |
    fis,4 <ais cis'>4-. cis4 <ais cis'>4-. |
    g,4 <b d'>4-. d4 <b d'>4-. |
    cis,4 <eis gis>4-. gis,4 <eis gis>4-. |
    b,4 <d' fis'>4-. fis,4 <d' fis'>4-. |
    fis,4 <ais cis'>4-. cis4 <ais cis'>4-. |
    g,4 <b d'>4-. d4 <b d'>4-. |
    e,4 <g b>4-. b,4 <g b>4-. |
    b,4 <dis' fis'>4-. fis,4 <dis' fis'>4-. |
    e,4 <g b>4-. b,4 <g b>4-. |
    fis,4 <ais cis'>4-. cis4 <ais cis'>4-. |
    b,4 <d' fis'>4-. fis,4 <d' fis'>4-. |
    b,4 <d' fis'>4-. fis,4 <d' fis'>4-. |
    g,4 <b d'>4-. d4 <b d'>4-. |
    fis,4 <ais cis'>4-. cis4 <ais cis'>4-. |
    b,4 <d' fis'>4-. fis,4 <d' fis'>4-. |
    \key bes \minor <bes d' f'>4. <bes d' f'>4. <bes d' f'>4. |
    <ees ges bes>4. <ees ges bes>4. <ees ges bes>4. |
    <f a c'>4. <f a c'>4. <f a c'>4. |
    <bes des' f'>4. <bes des' f'>4. <bes des' f'>4. |
    <bes des' f'>4. <bes des' f'>4. <bes des' f'>4. |
    <ges bes des'>4. <ges bes des'>4. <ges bes des'>4. |
    <c ees ges>4. <c ees ges>4. <c ees ges>4. |
    <f a c'>4. <f a c'>4. <f a c'>4. |
    <bes des' f'>4. <bes des' f'>4. <bes des' f'>4. |
    <ees ges bes>4. <ees ges bes>4. <ees ges bes>4. |
    <f a c'>4. <f a c'>4. <f a c'>4. |
    <bes des' f'>4. <bes des' f'>4. <bes des' f'>4. |
    <ges bes des'>4. <ges bes des'>4. <ges bes des'>4. |
    <ees ges bes>4. <ees ges bes>4. <ees ges bes>4. |
    <bes des' f'>4. <bes des' f'>4. <bes des' f'>4. |
    <f a c'>4. <f a c'>4. <f a c'>4. |
    <bes des' f'>4. <bes des' f'>4. <bes des' f'>4. |
    <c e g>4. <c e g>4. <c e g>4. |
    <f a c'>4. <f a c'>4. <f a c'>4. |
    <bes des' f'>4. <bes des' f'>4. <bes des' f'>4. |
    \key g \major e,2. <g b>2 |
    c,2. <e g>2 |
    g,2. <b d'>2 |
    d,2. <fis a>2 |
    g,2. <b d'>2 |
    a,2. <cis' e'>2 |
    d,2. <fis a>2 |
    g,2. <b d'>2 |
    g,2. <b d'>2 |
    b,2. <d' fis'>2 |
    c,2. <e g>2 |
    d,2. <fis a>2 |
    a,2. <c' e'>2 |
    d,2. <fis a>2 |
    g,2. <b d'>2 |
    g,2. <b d'>2 |
    g,2. <b d'>2 |
    e,2. <gis b>2 |
    d,2. <fis a>2 |
    g,2. <b d'>2 |
    \key e \major fis,4 <a cis'>4 cis4. |
    b,4 <dis fis>4 fis4. |
    e,4 <gis b>4 b,4. |
    e,4 <gis b>4 b,4. |
    e,4 <gis b>4 b,4. |
    cis4 <eis gis>4 gis4. |
    fis,4 <a cis'>4 cis4. |
    b,4 <dis fis>4 fis4. |
    a,4 <cis' e'>4 e4. |
    b,4 <dis fis>4 fis4. |
    cis4 <e gis>4 gis4. |
    fis,4 <ais cis'>4 cis4. |
    e,4 <gis b>4 b,4. |
    b,4 <dis fis>4 fis4. |
    cis4 <e gis>4 gis4. |
    a,4 <cis' e'>4 e4. |
    e,4 <gis b>4 b,4. |
    a,4 <cis' e'>4 e4. |
    b,4 <dis fis>4 fis4. |
    e,4 <gis b>4 b,4. |
    \key d \minor d,2:32 a,2:32 |
    a,2:32 e2:32 |
    bes,2:32 f2:32 |
    g,2:32 d2:32 |
    d,2:32 a,2:32 |
    g,2:32 d2:32 |
    a,2:32 e2:32 |
    d,2:32 a,2:32 |
    d,2:32 a,2:32 |
    bes,2:32 f2:32 |
    e,2:32 bes,2:32 |
    a,2:32 e2:32 |
    d,2:32 a,2:32 |
    g,2:32 d2:32 |
    a,2:32 e2:32 |
    d,2:32 a,2:32 |
    bes,2:32 f2:32 |
    g,2:32 d2:32 |
    a,2:32 e2:32 |
    d,2:32 a,2:32 |
    \key ces \major ces8 ees8 ges8 ees8 <ces ees ges>2 |
    \clef "treble" fes'8 aes'8 ces''8 aes'8 <fes' aes' ces''>2 |
    \clef "bass" ges,8 bes,8 des8 bes,8 <ges, bes, des>2 |
    ces8 ees8 ges8 ees8 <ces ees ges>2 |
    aes,8 ces8 ees8 ces8 <aes, ces ees>2 |
    \clef "treble" fes'8 aes'8 ces''8 aes'8 <fes' aes' ces''>2 |
    \clef "bass" ces8 ees8 ges8 ees8 <ces ees ges>2 |
    ges,8 bes,8 des8 bes,8 <ges, bes, des>2 |
    ces8 ees8 ges8 ees8 <ces ees ges>2 |
    \clef "treble" des'8 f'8 aes'8 f'8 <des' f' aes'>2 |
    \clef "bass" ges,8 bes,8 des8 bes,8 <ges, bes, des>2 |
    ces8 ees8 ges8 ees8 <ces ees ges>2 |
    ces8 ees8 ges8 ees8 <ces ees ges>2 |
    \clef "treble" ees'8 ges'8 bes'8 ges'8 <ees' ges' bes'>2 |
    \clef "bass" fes8 aes8 ces'8 aes8 <fes aes ces'>2 |
    ges,8 bes,8 des8 bes,8 <ges, bes, des>2 |
    des8 fes8 aes8 fes8 <des fes aes>2 |
    \clef "treble" ges'8 bes'8 des''8 bes'8 <ges' bes' des''>2 |
    \clef "bass" ges,8 bes,8 des8 bes,8 <ges, bes, des>2 |
    ces8 ees8 ges8 ees8 <ces ees ges>2 |
    \key ais \minor ais,8 cis8 ais,8 cis8 ais,8 cis8 ais,8 cis8 |
    cis8 eis8 cis8 eis8 cis8 eis8 cis8 eis8 |
    dis8 fis8 dis8 fis8 dis8 fis8 dis8 fis8 |
    eis8 gisis8 eis8 gisis8 eis8 gisis8 eis8 gisis8 |
    bis,8 dis8 bis,8 dis8 bis,8 dis8 bis,8 dis8 |
    eis8 gisis8 eis8 gisis8 eis8 gisis8 eis8 gisis8 |
    ais,8 cis8 ais,8 cis8 ais,8 cis8 ais,8 cis8 |
    ais,8 cis8 ais,8 cis8 ais,8 cis8 ais,8 cis8 |
    ais,8 cis8 ais,8 cis8 ais,8 cis8 ais,8 cis8 |
    fisis8 aisis8 fisis8 aisis8 fisis8 aisis8 fisis8 aisis8 |
    bis,8 dis8 bis,8 dis8 bis,8 dis8 bis,8 dis8 |
    eis8 gisis8 eis8 gisis8 eis8 gisis8 eis8 gisis8 |
    dis8 fis8 dis8 fis8 dis8 fis8 dis8 fis8 |
    eis8 gisis8 eis8 gisis8 eis8 gisis8 eis8 gisis8 |
    fis8 ais8 fis8 ais8 fis8 ais8 fis8 ais8 |
    bis,8 disis8 bis,8 disis8 bis,8 disis8 bis,8 disis8 |
    ais,8 cis8 ais,8 cis8 ais,8 cis8 ais,8 cis8 |
    eis8 gisis8 eis8 gisis8 eis8 gisis8 eis8 gisis8 |
    eis8 gisis8 eis8 gisis8 eis8 gisis8 eis8 gisis8 |
    ais,8 cis8 ais,8 cis8 ais,8 cis8 ais,8 cis8 |
    \key g \minor <c ees g>4 <c ees g>4 <c ees g>2 |
    <d fis a>4 <d fis a>4 <d fis a>2 |
    <ees g bes>4 <ees g bes>4 <ees g bes>2 |
    <a, cis e>4 <a, cis e>4 <a, cis e>2 |
    <g bes d'>4 <g bes d'>4 <g bes d'>2 |
    <d fis a>4 <d fis a>4 <d fis a>2 |
    <ees g bes>4 <ees g bes>4 <ees g bes>2 |
    <c ees g>4 <c ees g>4 <c ees g>2 |
    <g b d'>4 <g b d'>4 <g b d'>2 |
    <c ees g>4 <c ees g>4 <c ees g>2 |
    <d fis a>4 <d fis a>4 <d fis a>2 |
    <g bes d'>4 <g bes d'>4 <g bes d'>2 |
    <g bes d'>4 <g bes d'>4 <g bes d'>2 |
    <ees g bes>4 <ees g bes>4 <ees g bes>2 |
    <a, c ees>4 <a, c ees>4 <a, c ees>2 |
    <d fis a>4 <d fis a>4 <d fis a>2 |
    <g bes d'>4 <g bes d'>4 <g bes d'>2 |
    <c ees g>4 <c ees g>4 <c ees g>2 |
    <d fis a>4 <d fis a>4 <d fis a>2 |
    <g bes d'>4 <g bes d'>4 <g bes d'>2 |
    \key des \major des8 aes8 f,8 aes8 |
    bes,8 f8 des8 f8 |
    ees,8 bes,8 ges,8 bes,8 |
    aes,8 ees8 c8 ees8 |
    des8 aes8 f,8 aes8 |
    ges,8 des8 bes,8 des8 |
    aes,8 ees8 c8 ees8 |
    des8 aes8 f,8 aes8 |
    bes,8 f8 des8 f8 |
    ges,8 des8 bes,8 des8 |
    des8 aes8 f,8 aes8 |
    aes,8 ees8 c8 ees8 |
    des8 aes8 f,8 aes8 |
    ees,8 bes,8 g,8 bes,8 |
    aes,8 ees8 c8 ees8 |
    des8 aes8 f,8 aes8 |
    des8 aes8 f,8 aes8 |
    f,8 c8 aes,8 c8 |
    aes,8 ees8 c8 ees8 |
    des8 aes8 f,8 aes8 |
    \key f \minor <f,-5 aes,-3 c-1>2\arpeggio <f, aes, c>2 |
    <g,-5 b,-3 d-1>2\arpeggio <g, b, d>2 |
    <c,-5 e,-3 g,-1>2\arpeggio <c, e, g,>2 |
    <f,-5 aes,-3 c-1>2\arpeggio <f, aes, c>2 |
    <f,-5 aes,-3 c-1>2\arpeggio <f, aes, c>2 |
    <aes,-5 c-3 ees-1>2\arpeggio <aes, c ees>2 |
    <bes,-5 des-3 f-1>2\arpeggio <bes, des f>2 |
    <c,-5 e,-3 g,-1>2\arpeggio <c, e, g,>2 |
    <g,-5 bes,-3 des-1>2\arpeggio <g, bes, des>2 |
    <c,-5 e,-3 g,-1>2\arpeggio <c, e, g,>2 |
    <f,-5 aes,-3 c-1>2\arpeggio <f, aes, c>2 |
    <f,-5 aes,-3 c-1>2\arpeggio <f, aes, c>2 |
    <f,-5 aes,-3 c-1>2\arpeggio <f, aes, c>2 |
    <d,-5 fis,-3 a,-1>2\arpeggio <d, fis, a,>2 |
    <g,-5 bes,-3 des-1>2\arpeggio <g, bes, des>2 |
    <c,-5 e,-3 g,-1>2\arpeggio <c, e, g,>2 |
    <bes,-5 des-3 f-1>2\arpeggio <bes, des f>2 |
    <c,-5 e,-3 g,-1>2\arpeggio <c, e, g,>2 |
    <c,-5 e,-3 g,-1>2\arpeggio <c, e, g,>2 |
    <f,-5 aes,-3 c-1>2\arpeggio <f, aes, c>2 |
    \key dis \minor dis,4 <fis ais>2 |
    bis,4 <disis' fisis'>2 |
    eis,4 <gis b>2 |
    ais,4 <cisis' eis'>2 |
    gis,4 <b dis'>2 |
    ais,4 <cisis' eis'>2 |
    b,4 <dis' fis'>2 |
    eis,4 <gisis bis>2 |
    dis,4 <fis ais>2 |
    ais,4 <cisis' eis'>2 |
    b,4 <dis' fis'>2 |
    gis,4 <b dis'>2 |
    dis,4 <fisis ais>2 |
    gis,4 <b dis'>2 |
    ais,4 <cisis' eis'>2 |
    dis,4 <fis ais>2 |
    dis,4 <fis ais>2 |
    b,4 <dis' fis'>2 |
    ais,4 <cisis' eis'>2 |
    dis,4 <fis ais>2 |
    \key f \major <f, f>2 c2 |
    <bes, bes>2 f2 |
    <c, c>2 g,2 |
    <f, f>1\fermata |
    <f, f>2 c2 |
    <d, d>2 a,2 |
    <g, g>2 d2 |
    <c, c>1\fermata |
    <f, f>2 c2 |
    <bes, bes>2 f2 |
    <c, c>2 g,2 |
    <f, f>1\fermata |
    <d, d>2 a,2 |
    <bes, bes>2 f2 |
    <f, f>2 c2 |
    <c, c>1\fermata |
    <f, f>2 c2 |
    <g, g>2 d2 |
    <c, c>2 g,2 |
    <f, f>1\fermata |
    \key b \major gis,8 dis8 b8 dis8 gis,8 dis8 b8 dis8 |
    e8 b,8 gis8 b,8 e8 b,8 gis8 b,8 |
    b,8 fis8 dis8 fis8 b,8 fis8 dis8 fis8 |
    fis8 cis8 ais8 cis8 fis8 cis8 ais8 cis8 |
    b,8 fis8 dis8 fis8 b,8 fis8 dis8 fis8 |
    cis8 gis8 eis8 gis8 cis8 gis8 eis8 gis8 |
    fis8 cis8 ais8 cis8 fis8 cis8 ais8 cis8 |
    b,8 fis8 dis8 fis8 b,8 fis8 dis8 fis8 |
    b,8 fis8 dis8 fis8 b,8 fis8 dis8 fis8 |
    dis8 ais,8 fis8 ais,8 dis8 ais,8 fis8 ais,8 |
    e8 b,8 gis8 b,8 e8 b,8 gis8 b,8 |
    fis8 cis8 ais8 cis8 fis8 cis8 ais8 cis8 |
    cis8 gis8 e8 gis8 cis8 gis8 e8 gis8 |
    fis8 cis8 ais8 cis8 fis8 cis8 ais8 cis8 |
    b,8 fis8 dis8 fis8 b,8 fis8 dis8 fis8 |
    b,8 fis8 dis8 fis8 b,8 fis8 dis8 fis8 |
    b,8 fis8 dis8 fis8 b,8 fis8 dis8 fis8 |
    gis,8 dis8 bis8 dis8 gis,8 dis8 bis8 dis8 |
    fis8 cis8 ais8 cis8 fis8 cis8 ais8 cis8 |
    b,8 fis8 dis8 fis8 b,8 fis8 dis8 fis8 |
    \key ges \major <aes ces'>8-. <aes ces'>8-. <aes ces'>8-. <aes ces'>8-. |
    <des f>8-. <des f>8-. <des f>8-. <des f>8-. |
    <ges bes>8-. <ges bes>8-. <ges bes>8-. <ges bes>8-. |
    <ges bes>8-. <ges bes>8-. <ges bes>8-. <ges bes>8-. |
    <ges bes>8-. <ges bes>8-. <ges bes>8-. <ges bes>8-. |
    <ees g>8-. <ees g>8-. <ees g>8-. <ees g>8-. |
    <aes ces'>8-. <aes ces'>8-. <aes ces'>8-. <aes ces'>8-. |
    <des f>8-. <des f>8-. <des f>8-. <des f>8-. |
    <ces' ees'>8-. <ces' ees'>8-. <ces' ees'>8-. <ces' ees'>8-. |
    <des f>8-. <des f>8-. <des f>8-. <des f>8-. |
    <ees ges>8-. <ees ges>8-. <ees ges>8-. <ees ges>8-. |
    <aes c'>8-. <aes c'>8-. <aes c'>8-. <aes c'>8-. |
    <ges bes>8-. <ges bes>8-. <ges bes>8-. <ges bes>8-. |
    <des f>8-. <des f>8-. <des f>8-. <des f>8-. |
    <ees ges>8-. <ees ges>8-. <ees ges>8-. <ees ges>8-. |
    <ces' ees'>8-. <ces' ees'>8-. <ces' ees'>8-. <ces' ees'>8-. |
    <ges bes>8-. <ges bes>8-. <ges bes>8-. <ges bes>8-. |
    <ces' ees'>8-. <ces' ees'>8-. <ces' ees'>8-. <ces' ees'>8-. |
    <des f>8-. <des f>8-. <des f>8-. <des f>8-. |
    <ges bes>8-. <ges bes>8-. <ges bes>8-. <ges bes>8-. |
    \key gis \minor gis,4\sustainOn <b dis'>4-. <b dis'>4-.\sustainOff |
    dis,4\sustainOn <fisis ais>4-. <fisis ais>4-.\sustainOff |
    e,4\sustainOn <gis b>4-. <gis b>4-.\sustainOff |
    cis4\sustainOn <e' gis'>4-. <e' gis'>4-.\sustainOff |
    gis,4\sustainOn <bis dis'>4-. <bis dis'>4-.\sustainOff |
    cis4\sustainOn <e' gis'>4-. <e' gis'>4-.\sustainOff |
    dis,4\sustainOn <fisis ais>4-. <fisis ais>4-.\sustainOff |
    gis,4\sustainOn <b dis'>4-. <b dis'>4-.\sustainOff |
    gis,4\sustainOn <b dis'>4-. <b dis'>4-.\sustainOff |
    e,4\sustainOn <gis b>4-. <gis b>4-.\sustainOff |
    ais,4\sustainOn <cis' e'>4-. <cis' e'>4-.\sustainOff |
    dis,4\sustainOn <fisis ais>4-. <fisis ais>4-.\sustainOff |
    gis,4\sustainOn <b dis'>4-. <b dis'>4-.\sustainOff |
    cis4\sustainOn <e' gis'>4-. <e' gis'>4-.\sustainOff |
    dis,4\sustainOn <fisis ais>4-. <fisis ais>4-.\sustainOff |
    gis,4\sustainOn <b dis'>4-. <b dis'>4-.\sustainOff |
    e,4\sustainOn <gis b>4-. <gis b>4-.\sustainOff |
    cis4\sustainOn <e' gis'>4-. <e' gis'>4-.\sustainOff |
    dis,4\sustainOn <fisis ais>4-. <fisis ais>4-.\sustainOff |
    gis,4\sustainOn <b dis'>4-. <b dis'>4-.\sustainOff |
    \key c \minor c,8\sustainOn c8 ees8 g8 ees8 c8\sustainOff |
    f,8\sustainOn f8 aes8 c'8 aes8 f8\sustainOff |
    g,8\sustainOn g8 b8 d'8 b8 g8\sustainOff |
    c,8\sustainOn c8 ees8 g8 ees8 c8\sustainOff |
    aes,8\sustainOn aes8 c'8 ees'8 c'8 aes8\sustainOff |
    f,8\sustainOn f8 aes8 c'8 aes8 f8\sustainOff |
    c,8\sustainOn c8 ees8 g8 ees8 c8\sustainOff |
    g,8\sustainOn g8 b8 d'8 b8 g8\sustainOff |
    c,8\sustainOn c8 ees8 g8 ees8 c8\sustainOff |
    d,8\sustainOn d8 fis8 a8 fis8 d8\sustainOff |
    g,8\sustainOn g8 b8 d'8 b8 g8\sustainOff |
    c,8\sustainOn c8 ees8 g8 ees8 c8\sustainOff |
    c,8\sustainOn c8 ees8 g8 ees8 c8\sustainOff |
    ees,8\sustainOn ees8 g8 bes8 g8 ees8\sustainOff |
    f,8\sustainOn f8 aes8 c'8 aes8 f8\sustainOff |
    g,8\sustainOn g8 b8 d'8 b8 g8\sustainOff |
    d,8\sustainOn d8 f8 aes8 f8 d8\sustainOff |
    g,8\sustainOn g8 b8 d'8 b8 g8\sustainOff |
    g,8\sustainOn g8 b8 d'8 b8 g8\sustainOff |
    c,8\sustainOn c8 ees8 g8 ees8 c8\sustainOff |
    \key a \minor a,2 e2 |
    c,2 g,2 |
    d,2 a,2 |
    e,2 b,2 |
    b,2 f2 |
    e,2 b,2 |
    a,2 e2 |
    a,2 e2 |
    a,2 e2 |
    fis,2 cis2 |
    b,2 f2 |
    e,2 b,2 |
    d,2 a,2 |
    e,2 b,2 |
    f,2 c2 |
    b,2 fis2 |
    a,2 e2 |
    e,2 b,2 |
    e,2 b,2 |
    a,2 e2 |
    \key ees \major <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 |
    <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 |
    <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 |
    <f, f>8 <f, f>8 <f, f>8 <f, f>8 <f, f>8 <f, f>8 <f, f>8 <f, f>8 |
    \ottava #-1 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 |
    <bes,, bes,>8 <bes,, bes,>8 <bes,, bes,>8 <bes,, bes,>8 <bes,, bes,>8 <bes,, bes,>8 <bes,, bes,>8 <bes,, bes,>8 \ottava #0 |
    <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 |
    <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 |
    <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 |
    <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 |
    <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 |
    <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 |
    \ottava #-1 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 |
    <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 <c, c>8 \ottava #0 |
    <f, f>8 <f, f>8 <f, f>8 <f, f>8 <f, f>8 <f, f>8 <f, f>8 <f, f>8 |
    <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 |
    <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 |
    <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 <aes, aes>8 |
    <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 <bes, bes>8 |
    <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 <ees, ees>8 |
    \key cis \minor cis4 gis4 e4 gis4 |
    a,4 e4 cis4 e4 |
    dis,4 a,4 fis,4 a,4 |
    gis,4 dis4 bis,4 dis4 |
    cis4 gis4 e4 gis4 |
    fis,4 cis4 a,4 cis4 |
    gis,4 dis4 bis,4 dis4 |
    cis4 gis4 e4 gis4 |
    a,4 e4 cis4 e4 |
    fis,4 cis4 a,4 cis4 |
    cis4 gis4 e4 gis4 |
    gis,4 dis4 bis,4 dis4 |
    cis4 gis4 e4 gis4 |
    dis,4 ais,4 fisis,4 ais,4 |
    gis,4 dis4 bis,4 dis4 |
    cis4 gis4 e4 gis4 |
    cis4 gis4 e4 gis4 |
    e,4 b,4 gis,4 b,4 |
    gis,4 dis4 bis,4 dis4 |
    cis4 gis4 e4 gis4 |
    \key c \major <c e g>2 <c e g>2 <c e g>2 |
    <d fis a>2 <d fis a>2 <d fis a>2 |
    <g, b, d>2 <g, b, d>2 <g, b, d>2 |
    <c e g>1.\fermata |
    <c e g>2 <c e g>2 <c e g>2 |
    <e g b>2 <e g b>2 <e g b>2 |
    <f a c'>2 <f a c'>2 <f a c'>2 |
    <g, b, d>1.\fermata |
    <d f a>2 <d f a>2 <d f a>2 |
    <g, b, d>2 <g, b, d>2 <g, b, d>2 |
    <c e g>2 <c e g>2 <c e g>2 |
    <c e g>1.\fermata |
    <c e g>2 <c e g>2 <c e g>2 |
    <a, cis e>2 <a, cis e>2 <a, cis e>2 |
    <d f a>2 <d f a>2 <d f a>2 |
    <g, b, d>1.\fermata |
    <f a c'>2 <f a c'>2 <f a c'>2 |
    <g, b, d>2 <g, b, d>2 <g, b, d>2 |
    <g, b, d>2 <g, b, d>2 <g, b, d>2 |
    <c e g>1.\fermata |
    \key aes \major <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 |
    <f a c'>4 <f a c'>4 <f a c'>4 <f a c'>4 |
    <bes des' f'>4 <bes des' f'>4 <bes des' f'>4 <bes des' f'>4 |
    <ees g bes>4 <ees g bes>4 <ees g bes>4 <ees g bes>4 |
    <des f aes>4 <des f aes>4 <des f aes>4 <des f aes>4 |
    <ees g bes>4 <ees g bes>4 <ees g bes>4 <ees g bes>4 |
    <f aes c'>4 <f aes c'>4 <f aes c'>4 <f aes c'>4 |
    <bes d' f'>4 <bes d' f'>4 <bes d' f'>4 <bes d' f'>4 |
    <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 |
    <ees g bes>4 <ees g bes>4 <ees g bes>4 <ees g bes>4 |
    <f aes c'>4 <f aes c'>4 <f aes c'>4 <f aes c'>4 |
    <des f aes>4 <des f aes>4 <des f aes>4 <des f aes>4 |
    <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 |
    <des f aes>4 <des f aes>4 <des f aes>4 <des f aes>4 |
    <ees g bes>4 <ees g bes>4 <ees g bes>4 <ees g bes>4 |
    <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 |
    <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 |
    <f aes c'>4 <f aes c'>4 <f aes c'>4 <f aes c'>4 |
    <ees g bes>4 <ees g bes>4 <ees g bes>4 <ees g bes>4 |
    <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 <aes c' ees'>4 |
    \key fis \major <fis, cis>4. <fis, cis>4. <fis, cis>4. <fis, cis>4. |
    <b, fis>4. <b, fis>4. <b, fis>4. <b, fis>4. |
    <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. |
    <fis, cis>4. <fis, cis>4. <fis, cis>4. <fis, cis>4. |
    <fis, cis>4. <fis, cis>4. <fis, cis>4. <fis, cis>4. |
    <dis, ais,>4. <dis, ais,>4. <dis, ais,>4. <dis, ais,>4. |
    <gis, dis>4. <gis, dis>4. <gis, dis>4. <gis, dis>4. |
    <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. |
    <fis, cis>4. <fis, cis>4. <fis, cis>4. <fis, cis>4. |
    <b, fis>4. <b, fis>4. <b, fis>4. <b, fis>4. |
    <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. |
    <fis, cis>4. <fis, cis>4. <fis, cis>4. <fis, cis>4. |
    <dis, ais,>4. <dis, ais,>4. <dis, ais,>4. <dis, ais,>4. |
    <b, fis>4. <b, fis>4. <b, fis>4. <b, fis>4. |
    <fis, cis>4. <fis, cis>4. <fis, cis>4. <fis, cis>4. |
    <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. |
    <fis, cis>4. <fis, cis>4. <fis, cis>4. <fis, cis>4. |
    <gis, dis>4. <gis, dis>4. <gis, dis>4. <gis, dis>4. |
    <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. <cis, gis,>4. |
    <fis, cis>4. <fis, cis>4. <fis, cis>4. <fis, cis>4. |
    \key fis \minor d,4 <fis a>4-. a,4 <fis a>4-. |
    b,4 <d' fis'>4-. fis,4 <d' fis'>4-. |
    fis,4 <a cis'>4-. cis4 <a cis'>4-. |
    cis,4 <eis gis>4-. gis,4 <eis gis>4-. |
    fis,4 <a cis'>4-. cis4 <a cis'>4-. |
    gis,4 <bis dis'>4-. dis4 <bis dis'>4-. |
    cis,4 <eis gis>4-. gis,4 <eis gis>4-. |
    fis,4 <a cis'>4-. cis4 <a cis'>4-. |
    fis,4 <a cis'>4-. cis4 <a cis'>4-. |
    a,4 <cis' e'>4-. e,4 <cis' e'>4-. |
    b,4 <d' fis'>4-. fis,4 <d' fis'>4-. |
    cis,4 <eis gis>4-. gis,4 <eis gis>4-. |
    gis,4 <b d'>4-. d4 <b d'>4-. |
    cis,4 <eis gis>4-. gis,4 <eis gis>4-. |
    fis,4 <a cis'>4-. cis4 <a cis'>4-. |
    fis,4 <a cis'>4-. cis4 <a cis'>4-. |
    fis,4 <a cis'>4-. cis4 <a cis'>4-. |
    dis,4 <fisis ais>4-. ais,4 <fisis ais>4-. |
    cis,4 <eis gis>4-. gis,4 <eis gis>4-. |
    fis,4 <a cis'>4-. cis4 <a cis'>4-. |
    \key aes \minor <bes des' fes'>4. <bes des' fes'>4. <bes des' fes'>4. |
    <ees g bes>4. <ees g bes>4. <ees g bes>4. |
    <aes ces' ees'>4. <aes ces' ees'>4. <aes ces' ees'>4. |
    <aes ces' ees'>4. <aes ces' ees'>4. <aes ces' ees'>4. |
    <aes ces' ees'>4. <aes ces' ees'>4. <aes ces' ees'>4. |
    <f a c'>4. <f a c'>4. <f a c'>4. |
    <bes des' fes'>4. <bes des' fes'>4. <bes des' fes'>4. |
    <ees g bes>4. <ees g bes>4. <ees g bes>4. |
    <des fes aes>4. <des fes aes>4. <des fes aes>4. |
    <ees g bes>4. <ees g bes>4. <ees g bes>4. |
    <fes aes ces'>4. <fes aes ces'>4. <fes aes ces'>4. |
    <bes d' f'>4. <bes d' f'>4. <bes d' f'>4. |
    <aes ces' ees'>4. <aes ces' ees'>4. <aes ces' ees'>4. |
    <ees g bes>4. <ees g bes>4. <ees g bes>4. |
    <fes aes ces'>4. <fes aes ces'>4. <fes aes ces'>4. |
    <des fes aes>4. <des fes aes>4. <des fes aes>4. |
    <aes c' ees'>4. <aes c' ees'>4. <aes c' ees'>4. |
    <des fes aes>4. <des fes aes>4. <des fes aes>4. |
    <ees g bes>4. <ees g bes>4. <ees g bes>4. |
    <aes ces' ees'>4. <aes ces' ees'>4. <aes ces' ees'>4. |
    \key a \major a,2. <cis' e'>2 |
    e,2. <gis b>2 |
    fis,2. <a cis'>2 |
    d,2. <fis a>2 |
    a,2. <cis' e'>2 |
    d,2. <fis a>2 |
    e,2. <gis b>2 |
    a,2. <cis' e'>2 |
    a,2. <cis' e'>2 |
    fis,2. <a cis'>2 |
    b,2. <d' fis'>2 |
    e,2. <gis b>2 |
    a,2. <cis' e'>2 |
    d,2. <fis a>2 |
    e,2. <gis b>2 |
    a,2. <cis' e'>2 |
    fis,2. <a cis'>2 |
    d,2. <fis a>2 |
    e,2. <gis b>2 |
    a,2. <cis' e'>2 |
    \key e \minor e,4 <g b>4 b,4. |
    a,4 <c' e'>4 e4. |
    b,4 <dis fis>4 fis4. |
    e,4 <g b>4 b,4. |
    c4 <e g>4 g4. |
    a,4 <c' e'>4 e4. |
    e,4 <g b>4 b,4. |
    b,4 <dis fis>4 fis4. |
    e,4 <g b>4 b,4. |
    fis,4 <ais cis'>4 cis4. |
    b,4 <dis fis>4 fis4. |
    e,4 <g b>4 b,4. |
    e,4 <g b>4 b,4. |
    g,4 <b d'>4 d4. |
    a,4 <c' e'>4 e4. |
    b,4 <dis fis>4 fis4. |
    fis,4 <a c'>4 c4. |
    b,4 <dis fis>4 fis4. |
    b,4 <dis fis>4 fis4. |
    e,4 <g b>4 b,4. |
    \key cis \major cis,2:32 gis,2:32 |
    eis,2:32 bis,2:32 |
    fis,2:32 cis2:32 |
    gis,2:32 dis2:32 |
    dis,2:32 ais,2:32 |
    gis,2:32 dis2:32 |
    cis,2:32 gis,2:32 |
    cis,2:32 gis,2:32 |
    cis,2:32 gis,2:32 |
    ais,2:32 eis2:32 |
    dis,2:32 ais,2:32 |
    gis,2:32 dis2:32 |
    fis,2:32 cis2:32 |
    gis,2:32 dis2:32 |
    ais,2:32 eis2:32 |
    dis,2:32 ais,2:32 |
    cis,2:32 gis,2:32 |
    gis,2:32 dis2:32 |
    gis,2:32 dis2:32 |
    cis,2:32 gis,2:32 |
    \key ees \minor aes,8 ces8 ees8 ces8 <aes, ces ees>2 |
    \clef "treble" bes'8 d''8 f''8 d''8 <bes' d'' f''>2 |
    \clef "bass" ces8 ees8 ges8 ees8 <ces ees ges>2 |
    f,8 a,8 c8 a,8 <f, a, c>2 |
    ees8 ges8 bes8 ges8 <ees ges bes>2 |
    \clef "treble" bes'8 d''8 f''8 d''8 <bes' d'' f''>2 |
    \clef "bass" ces8 ees8 ges8 ees8 <ces ees ges>2 |
    aes,8 ces8 ees8 ces8 <aes, ces ees>2 |
    ees8 g8 bes8 g8 <ees g bes>2 |
    \clef "treble" aes'8 ces''8 ees''8 ces''8 <aes' ces'' ees''>2 |
    \clef "bass" bes,8 d8 f8 d8 <bes, d f>2 |
    ees8 ges8 bes8 ges8 <ees ges bes>2 |
    ees8 ges8 bes8 ges8 <ees ges bes>2 |
    \clef "treble" ces''8 ees''8 ges''8 ees''8 <ces'' ees'' ges''>2 |
    \clef "bass" f,8 aes,8 ces8 aes,8 <f, aes, ces>2 |
    bes,8 d8 f8 d8 <bes, d f>2 |
    ees8 ges8 bes8 ges8 <ees ges bes>2 |
    \clef "treble" aes'8 ces''8 ees''8 ces''8 <aes' ces'' ees''>2 |
    \clef "bass" bes,8 d8 f8 d8 <bes, d f>2 |
    ees8 ges8 bes8 ges8 <ees ges bes>2 |
    \key d \major d8 fis8 d8 fis8 d8 fis8 d8 fis8 |
    b,8 d8 b,8 d8 b,8 d8 b,8 d8 |
    e8 g8 e8 g8 e8 g8 e8 g8 |
    a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 |
    d8 fis8 d8 fis8 d8 fis8 d8 fis8 |
    g8 b8 g8 b8 g8 b8 g8 b8 |
    a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 |
    d8 fis8 d8 fis8 d8 fis8 d8 fis8 |
    b,8 d8 b,8 d8 b,8 d8 b,8 d8 |
    g8 b8 g8 b8 g8 b8 g8 b8 |
    d8 fis8 d8 fis8 d8 fis8 d8 fis8 |
    a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 |
    d8 fis8 d8 fis8 d8 fis8 d8 fis8 |
    e8 gis8 e8 gis8 e8 gis8 e8 gis8 |
    a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 |
    d8 fis8 d8 fis8 d8 fis8 d8 fis8 |
    d8 fis8 d8 fis8 d8 fis8 d8 fis8 |
    fis8 a8 fis8 a8 fis8 a8 fis8 a8 |
    a,8 cis8 a,8 cis8 a,8 cis8 a,8 cis8 |
    d8 fis8 d8 fis8 d8 fis8 d8 fis8 |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
