\version "2.24.0"
#(set-global-staff-size 18)
\header {
  title = "Forty Variations"
  subtitle = "for piano - 10 pages"
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
    d''32 e''32 fis''32 g''32 a''32 b''32 cis'''32 d'''32 d'''4-. a'4-. d''4 \bar "|." |
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
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
