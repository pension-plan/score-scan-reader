\version "2.24.0"
#(set-global-staff-size 19)
\header {
  title = "Variations on \"Ah! vous dirai-je, maman\""
  subtitle = "Theme and eight variations for piano"
  composer = "Theme: French folk melody (1761)"
  arranger = "Variations: layout-challenge corpus (2026)"
  copyright = "Dedicated to the public domain (CC0 1.0) - page 1 of 12"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  indent = 12\mm
  ragged-last = ##f
  ragged-bottom = ##f
  print-first-page-number = ##f
  oddHeaderMarkup = \markup \fill-line { \null \unless \on-first-page \italic "Variations on \"Ah! vous dirai-je, maman\"" \unless \on-first-page \bold \fromproperty #'page:page-number-string }
  evenHeaderMarkup = \markup \fill-line { \unless \on-first-page \bold \fromproperty #'page:page-number-string \unless \on-first-page \italic "Theme and eight variations for piano" \null }
  oddFooterMarkup = \markup \fill-line { \if \on-first-page \fromproperty #'header:copyright }
  evenFooterMarkup = ##f
  system-system-spacing.basic-distance = #13
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vPx1" {
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante" 4 = 76 \textMark \markup { \bold "Thema" } \time 2/4 \key c \major c''4\p c''4 |
    g''4 g''4 |
    a''4 a''4 |
    g''2 |
    \break f''4 f''4 |
    e''4 e''4 |
    d''4 d''4 |
    c''2 \bar ":|.|:" |
    \break g''4 g''4 |
    f''4 f''4 |
    e''4 e''4 |
    d''2 |
    \break g''4 g''4 |
    f''4 f''4 |
    e''4 e''4 |
    d''2 |
    \pageBreak c''4 c''4 |
    g''4 g''4 |
    a''4 a''4 |
    g''2 |
    \break f''4 f''4 |
    e''4 e''4 |
    d''4 d''4 |
    c''2 \bar ":|.|:" |
    \break \tempo "Poco più mosso" \textMark \markup { \bold "Var. I" } c''16\mf[ d''16 c''16 b'16] c''16[ d''16 c''16 b'16] |
    g''16[ a''16 g''16 f''16] g''16[ a''16 g''16 f''16] |
    a''16[ b''16 a''16 g''16] a''16[ b''16 a''16 g''16] |
    g''16[ a''16 g''16 f''16] g''4 |
    \break f''16[ g''16 f''16 e''16] f''16[ g''16 f''16 e''16] |
    e''16[ f''16 e''16 d''16] e''16[ f''16 e''16 d''16] |
    d''16[ e''16 d''16 c''16] d''16[ e''16 d''16 c''16] |
    c''16[ d''16 c''16 b'16] c''4 \bar ":|.|:" |
    \break g''16[ a''16 g''16 f''16] g''16[ a''16 g''16 f''16] |
    f''16[ g''16 f''16 e''16] f''16[ g''16 f''16 e''16] |
    e''16[ f''16 e''16 d''16] e''16[ f''16 e''16 d''16] |
    d''16[ e''16 d''16 c''16] d''4 |
    \pageBreak g''16[ a''16 g''16 f''16] g''16[ a''16 g''16 f''16] |
    f''16[ g''16 f''16 e''16] f''16[ g''16 f''16 e''16] |
    e''16[ f''16 e''16 d''16] e''16[ f''16 e''16 d''16] |
    d''16[ e''16 d''16 c''16] d''4 |
    \break c''16[ d''16 c''16 b'16] c''16[ d''16 c''16 b'16] |
    g''16[ a''16 g''16 f''16] g''16[ a''16 g''16 f''16] |
    a''16[ b''16 a''16 g''16] a''16[ b''16 a''16 g''16] |
    g''16[ a''16 g''16 f''16] g''4 |
    \break f''16[ g''16 f''16 e''16] f''16[ g''16 f''16 e''16] |
    e''16[ f''16 e''16 d''16] e''16[ f''16 e''16 d''16] |
    d''16[ e''16 d''16 c''16] d''16[ e''16 d''16 c''16] |
    c''16[ d''16 c''16 b'16] c''4 \bar ":|.|:" |
    \break \textMark \markup { \bold "Var. II" } <g' c''>4\p <g' c''>4 |
    <e'' g''>4 <e'' g''>4 |
    <f'' a''>4 <f'' a''>4 |
    <e'' g''>2 |
    \break <d'' f''>4 <d'' f''>4 |
    <c'' e''>4 <c'' e''>4 |
    <a' d''>4 <b' d''>4 |
    \set Score.repeatCommands = #'((volta "1.")) <g' c''>4 <f' g'>4 \bar ":|." |
    \pageBreak \set Score.repeatCommands = #'((volta #f) (volta "2.")) <g' c''>2 \bar ".|:" |
    \set Score.repeatCommands = #'((volta #f)) <e'' g''>4 <e'' g''>4 |
    <d'' f''>4 <d'' f''>4 |
    <c'' e''>4 <c'' e''>4 |
    \break <b' d''>2 |
    <e'' g''>4 <e'' g''>4 |
    <d'' f''>4 <d'' f''>4 |
    <c'' e''>4 <c'' e''>4 |
    \break <b' d''>2 |
    <g' c''>4 <g' c''>4 |
    <e'' g''>4 <e'' g''>4 |
    <f'' a''>4 <f'' a''>4 |
    \break <e'' g''>2 |
    <d'' f''>4 <d'' f''>4 |
    <c'' e''>4 <c'' e''>4 |
    <a' d''>4 <b' d''>4 |
    \break \set Score.repeatCommands = #'((volta "1.")) <g' c''>4 <f' g'>4 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) <g' c''>2 \bar ".|:" |
    \pageBreak \set Score.repeatCommands = #'((volta #f)) \tempo "Leggiero" \textMark \markup { \bold "Var. III" } \tuplet 3/2 { c''8\mp[ g'8 e'8] } \tuplet 3/2 { c''8[ g'8 e'8] } |
    \tuplet 3/2 { g''8[ e''8 c''8] } \tuplet 3/2 { g''8[ e''8 c''8] } |
    \tuplet 3/2 { a''8[ f''8 c''8] } \tuplet 3/2 { a''8[ f''8 c''8] } |
    \tuplet 3/2 { g''8[ e''8 c''8] } g''4 |
    \break \tuplet 3/2 { f''8[ d''8 b'8] } \tuplet 3/2 { f''8[ d''8 b'8] } |
    \tuplet 3/2 { e''8[ c''8 g'8] } \tuplet 3/2 { e''8[ c''8 g'8] } |
    \tuplet 3/2 { d''8[ a'8 f'8] } \tuplet 3/2 { d''8[ b'8 g'8] } |
    \tuplet 3/2 { c''8[ g'8 e'8] } c''4 \bar ":|.|:" |
    \break \tuplet 3/2 { g''8[ e''8 c''8] } \tuplet 3/2 { g''8[ e''8 c''8] } |
    \tuplet 3/2 { f''8[ d''8 b'8] } \tuplet 3/2 { f''8[ d''8 b'8] } |
    \tuplet 3/2 { e''8[ c''8 g'8] } \tuplet 3/2 { e''8[ c''8 g'8] } |
    \tuplet 3/2 { d''8[ b'8 g'8] } d''4 |
    \break \tuplet 3/2 { g''8[ e''8 c''8] } \tuplet 3/2 { g''8[ e''8 c''8] } |
    \tuplet 3/2 { f''8[ d''8 a'8] } \tuplet 3/2 { f''8[ d''8 b'8] } |
    \tuplet 3/2 { e''8[ c''8 g'8] } \tuplet 3/2 { e''8[ c''8 a'8] } |
    \tuplet 3/2 { d''8[ b'8 g'8] } d''4 |
    \break \tuplet 3/2 { c''8[ g'8 e'8] } \tuplet 3/2 { c''8[ g'8 e'8] } |
    \tuplet 3/2 { g''8[ e''8 c''8] } \tuplet 3/2 { g''8[ e''8 c''8] } |
    \tuplet 3/2 { a''8[ f''8 c''8] } \tuplet 3/2 { a''8[ f''8 c''8] } |
    \tuplet 3/2 { g''8[ e''8 c''8] } g''4 |
    \pageBreak \tuplet 3/2 { f''8[ d''8 b'8] } \tuplet 3/2 { f''8[ d''8 b'8] } |
    \tuplet 3/2 { e''8[ c''8 g'8] } \tuplet 3/2 { e''8[ c''8 g'8] } |
    \tuplet 3/2 { d''8[ a'8 f'8] } \tuplet 3/2 { d''8[ b'8 g'8] } |
    \tuplet 3/2 { c''8[ g'8 e'8] } c''4 \bar ":|.|:" |
    \break \tempo "Energico" \textMark \markup { \bold "Var. IV" } <c' c''>4\f <c' c''>4 |
    <g' g''>4 <g' g''>4 |
    <a' a''>4 <a' a''>4 |
    <g' g''>2 |
    \break <f' f''>4 <f' f''>4 |
    <e' e''>4 <e' e''>4 |
    <d' d''>4 <d' d''>4 |
    \set Score.repeatCommands = #'((volta "1.")) <c' c''>4 <g g'>4 \bar ":|." |
    \break \set Score.repeatCommands = #'((volta #f) (volta "2.")) <c' c''>2 \bar ".|:" |
    \set Score.repeatCommands = #'((volta #f)) <g' g''>4 <g' g''>4 |
    <f' f''>4 <f' f''>4 |
    <e' e''>4 <e' e''>4 |
    \break <d' d''>2 |
    <g' g''>4 <g' g''>4 |
    <f' f''>4 <f' f''>4 |
    <e' e''>4 <e' e''>4 |
    \pageBreak <d' d''>2 |
    <c' c''>4 <c' c''>4 |
    <g' g''>4 <g' g''>4 |
    <a' a''>4 <a' a''>4 |
    \break <g' g''>2 |
    <f' f''>4 <f' f''>4 |
    <e' e''>4 <e' e''>4 |
    <d' d''>4 <d' d''>4 |
    \break \set Score.repeatCommands = #'((volta "1.")) <c' c''>4 <g g'>4 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) <c' c''>2 \bar ".|:" |
    \break \set Score.repeatCommands = #'((volta #f)) \tempo "Andante espressivo" 4 = 66 \textMark \markup { \bold "Var. V - Minore" } \key c \minor c''8.\p[ d''16] c''8.[ d''16] |
    g''8.[ aes''16] g''8.[ aes''16] |
    aes''8.[ bes''16] aes''8.[ bes''16] |
    g''8.[ aes''16] g''4 |
    \break f''8.[ g''16] f''8.[ g''16] |
    ees''8.[ f''16] ees''8.[ f''16] |
    d''8.[ ees''16] d''8.[ ees''16] |
    c''8.[ d''16] c''4 \bar ":|.|:" |
    \pageBreak g''8.\<[ aes''16] g''8.[ aes''16] |
    f''8.[ g''16] f''8.[ g''16] |
    ees''8.\![ f''16] ees''8.[ f''16] |
    d''8.[ ees''16] d''4 |
    \break g''8.[ aes''16] g''8.[ aes''16] |
    f''8.[ g''16] f''8.[ g''16] |
    ees''8.[ f''16] ees''8.[ f''16] |
    d''8.[ ees''16] d''4 |
    \break c''8.[ d''16] c''8.[ d''16] |
    g''8.[ aes''16] g''8.[ aes''16] |
    aes''8.[ bes''16] aes''8.[ bes''16] |
    g''8.[ aes''16] g''4 |
    \break f''8.[ g''16] f''8.[ g''16] |
    ees''8.[ f''16] ees''8.[ f''16] |
    d''8.[ ees''16] d''8.[ ees''16] |
    c''8.[ d''16] c''4 \bar ":|.|:" |
    \break \tempo "Allegretto" 4 = 96 \textMark \markup { \bold "Var. VI - Maggiore" } \key c \major <e' g' c''>4\f <e' g' c''>4 |
    <c'' e'' g''>4 <c'' e'' g''>4 |
    <c'' f'' a''>4 <c'' f'' a''>4 |
    <c'' e'' g''>2 |
    \pageBreak <b' d'' f''>4 <b' d'' f''>4 |
    <g' c'' e''>4 <g' c'' e''>4 |
    <f' a' d''>4 <g' b' d''>4 |
    \set Score.repeatCommands = #'((volta "1.")) <e' g' c''>4 <d' f' g'>4 \bar ":|." |
    \break \set Score.repeatCommands = #'((volta #f) (volta "2.")) <e' g' c''>2 \bar ".|:" |
    \set Score.repeatCommands = #'((volta #f)) <c'' e'' g''>4 <c'' e'' g''>4 |
    <b' d'' f''>4 <b' d'' f''>4 |
    <g' c'' e''>4 <g' c'' e''>4 |
    \break <g' b' d''>2 |
    <c'' e'' g''>4 <c'' e'' g''>4 |
    <a' d'' f''>4 <b' d'' f''>4 |
    <g' c'' e''>4 <a' c'' e''>4 |
    \break <g' b' d''>2 |
    <e' g' c''>4 <e' g' c''>4 |
    <c'' e'' g''>4 <c'' e'' g''>4 |
    <c'' f'' a''>4 <c'' f'' a''>4 |
    \break <c'' e'' g''>2 |
    <b' d'' f''>4 <b' d'' f''>4 |
    <g' c'' e''>4 <g' c'' e''>4 |
    <f' a' d''>4 <g' b' d''>4 |
    \pageBreak \set Score.repeatCommands = #'((volta "1.")) <e' g' c''>4 <d' f' g'>4 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) <e' g' c''>2 \bar ".|:" |
    \break \set Score.repeatCommands = #'((volta #f)) \tempo "Adagio cantabile" 4 = 50 \textMark \markup { \bold "Var. VII" } c''8\pp[ d''16 c''16] c''8[ d''16 c''16] |
    g''8[ a''16 g''16] g''8[ a''16 g''16] |
    a''8[ b''16 a''16] a''8[ b''16 a''16] |
    g''8[ a''16 g''16] g''4 |
    \break f''8[ g''16 f''16] f''8[ g''16 f''16] |
    e''8[ f''16 e''16] e''8[ f''16 e''16] |
    d''8[ e''16 d''16] d''8[ e''16 d''16] |
    c''8[ d''16 c''16] c''4 \bar ":|.|:" |
    \break g''8[ a''16 g''16] g''8[ a''16 g''16] |
    f''8[ g''16 f''16] f''8[ g''16 f''16] |
    e''8[ f''16 e''16] e''8[ f''16 e''16] |
    d''8[ e''16 d''16] d''4 |
    \break g''8[ a''16 g''16] g''8[ a''16 g''16] |
    f''8[ g''16 f''16] f''8[ g''16 f''16] |
    e''8[ f''16 e''16] e''8[ f''16 e''16] |
    d''8[ e''16 d''16] d''4 |
    \pageBreak c''8[ d''16 c''16] c''8[ d''16 c''16] |
    g''8[ a''16 g''16] g''8[ a''16 g''16] |
    a''8[ b''16 a''16] a''8[ b''16 a''16] |
    g''8[ a''16 g''16] g''4 |
    \break f''8[ g''16 f''16] f''8[ g''16 f''16] |
    e''8[ f''16 e''16] e''8[ f''16 e''16] |
    d''8[ e''16 d''16] d''8[ e''16 d''16] |
    c''8[ d''16 c''16] c''4\fermata \bar ":|.|:" |
    \break \tempo "Allegro" 4. = 112 \textMark \markup { \bold "Var. VIII - Finale" } \time 6/8 c''4\f e'8 c''4 e'8 |
    g''4 c''8 g''4 c''8 |
    a''4 c''8 a''4 c''8 |
    g''4 c''8 g''4. |
    \break f''4 b'8 f''4 b'8 |
    e''4 g'8 e''4 g'8 |
    d''4 f'8 d''4 g'8 |
    \set Score.repeatCommands = #'((volta "1.")) c''4 e'8 g'4 d'8 \bar ":|." |
    \break \set Score.repeatCommands = #'((volta #f) (volta "2.")) c''4 e'8 c''4. \bar ".|:" |
    \set Score.repeatCommands = #'((volta #f)) g''4 c''8 g''4 c''8 |
    f''4 b'8 f''4 b'8 |
    e''4 g'8 e''4 g'8 |
    \pageBreak d''4 g'8 d''4. |
    g''4 c''8 g''4 c''8 |
    f''4 a'8 f''4 b'8 |
    e''4 g'8 e''4 a'8 |
    \break d''4 g'8 d''4. |
    c''4 e'8 c''4 e'8 |
    g''4 c''8 g''4 c''8 |
    a''4 c''8 a''4 c''8 |
    \break g''4 c''8 g''4. |
    f''4 b'8 f''4 b'8 |
    e''4 g'8 e''4 g'8 |
    d''4 f'8 d''4 g'8 |
    \break \set Score.repeatCommands = #'((volta "1.")) c''4 e'8 g'4 d'8 \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) c''4 e'8 c''4. \bar "||" |
    \break \set Score.repeatCommands = #'((volta #f)) \tempo "Più allegro" \textMark \markup { \bold "Coda" } <e' g' c''>4. <f' a' c''>4. |
    <d' f' b'>4. <e' g' c''>4. |
    <c'' e'' g''>4.^\markup { \italic "cresc." } <c'' f'' a''>4. |
    <b' d'' g''>4. <b' d'' f''>4. |
    <c'' e'' g'' c'''>4.\ff r4. |
    <f' a' c'' f''>4.^\markup { \italic "rit." } <g' b' d'' g''>4. |
    <e' g' c'' e''>2. |
    <e' g' c'' e''>2.\fermata \bar "|." |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \key c \major <c e g>4 <c e g>4 |
    <c e g>4 <c e g>4 |
    <c f a>4 <c f a>4 |
    <c e g>2 |
    <d f g>4 <d f g>4 |
    <c e g>4 <c e g>4 |
    <d f a>4 <d f g>4 |
    <c e g>2 |
    <c e g>4 <c e g>4 |
    <d f g>4 <d f g>4 |
    <c e g>4 <c e g>4 |
    <b, d g>2 |
    <c e g>4 <c e g>4 |
    <d f a>4 <d f g>4 |
    <c e g>4 <c e a>4 |
    <b, d g>2 |
    <c e g>4 <c e g>4 |
    <c e g>4 <c e g>4 |
    <c f a>4 <c f a>4 |
    <c e g>2 |
    <d f g>4 <d f g>4 |
    <c e g>4 <c e g>4 |
    <d f a>4 <d f g>4 |
    <c e g>2 |
    c4 <g c'>4 |
    c4 <g c'>4 |
    f4 <a c'>4 |
    c4 <g c'>4 |
    g,4 <g b>4 |
    c4 <g c'>4 |
    d4 <g b>4 |
    c4 <g c'>4 |
    c4 <g c'>4 |
    g,4 <g b>4 |
    c4 <g c'>4 |
    g,4 <b d'>4 |
    c4_\markup { \italic "cresc." } <g c'>4 |
    d4 <g b>4 |
    c4 <a c'>4 |
    g,4 <g b>4 |
    c4 <g c'>4 |
    c4 <g c'>4 |
    f4 <a c'>4 |
    c4 <g c'>4 |
    g,4 <g b>4 |
    c4 <g c'>4 |
    d4 <g b>4 |
    c4 <g c'>4 |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    f,16[ c16 a,16 c16] f,16[ c16 a,16 c16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    g,16[ d16 b,16 d16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    d16[ a16 f16 a16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    g,16[ d16 b,16 d16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    g,16[ d16 b,16 d16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    d16[ a16 f16 a16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] a,16[ e16 c16 e16] |
    g,16[ d16 b,16 d16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    f,16[ c16 a,16 c16] f,16[ c16 a,16 c16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    g,16[ d16 b,16 d16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    d16[ a16 f16 a16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] g,16[ d16 b,16 d16] |
    c16[ g16 e16 g16] c16[ g16 e16 g16] |
    c,4 c,4 |
    c,4 c,4 |
    f,4 f,4 |
    c,4 c,4 |
    g,4 g,4 |
    c,4 c,4 |
    d,4 g,4 |
    c,4 c,4 |
    c,4 c,4 |
    g,4 g,4 |
    c,4 c,4 |
    g,4 g,4 |
    c,4 c,4 |
    d,4 g,4 |
    c,4 a,,4 |
    g,4 g,4 |
    c,4 c,4 |
    c,4 c,4 |
    f,4 f,4 |
    c,4 c,4 |
    g,4 g,4 |
    c,4 c,4 |
    d,4 g,4 |
    c,4 c,4 |
    \tuplet 3/2 { c,8\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { f,8\sustainOff\sustainOn[ a,8 c8] } \tuplet 3/2 { f,8[ a,8 c8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { g,8\sustainOff\sustainOn[ b,8 d8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { d,8\sustainOff\sustainOn[ f,8 a,8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { g,8\sustainOff\sustainOn[ b,8 d8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { g,8\sustainOff\sustainOn[ b,8 d8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { d,8\sustainOff\sustainOn[ f,8 a,8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { a,8[ c8 e8] } |
    \tuplet 3/2 { g,8\sustainOff\sustainOn[ b,8 d8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { f,8\sustainOff\sustainOn[ a,8 c8] } \tuplet 3/2 { f,8[ a,8 c8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { g,8\sustainOff\sustainOn[ b,8 d8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8] } |
    \tuplet 3/2 { d,8\sustainOff\sustainOn[ f,8 a,8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { g,8[ b,8 d8] } |
    \tuplet 3/2 { c,8\sustainOff\sustainOn[ e,8 g,8] } \tuplet 3/2 { c,8[ e,8 g,8\sustainOff] } |
    \key c \minor c,8[ <g c'>8] c,8[ <g c'>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    f,8[ <aes c'>8] f,8[ <aes c'>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    g,8[ <g b>8] g,8[ <g b>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    d,8[ <f aes>8] g,8[ <g b>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    g,8[ <g b>8] g,8[ <g b>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    g,8[ <g b>8] g,8[ <g b>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    d,8[ <f aes>8] g,8[ <g b>8] |
    c,8[ <g c'>8] aes,8[ <aes c'>8] |
    g,8[ <g b>8] g,8[ <g b>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    f,8[ <aes c'>8] f,8[ <aes c'>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    g,8[ <g b>8] g,8[ <g b>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    d,8[ <f aes>8] g,8[ <g b>8] |
    c,8[ <g c'>8] c,8[ <g c'>8] |
    \key c \major c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    f,16[ g,16 a,16 b,16] f,16[ g,16 a,16 b,16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    g,16[ a,16 b,16 c16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    d,16[ e,16 f,16 g,16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    g,16[ a,16 b,16 c16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    g,16[ a,16 b,16 c16] g,16[ a,16 b,16 c16] |
    c,16_\markup { \italic "cresc." }[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    d,16[ e,16 f,16 g,16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] a,16[ b,16 c16 d16] |
    g,16[ a,16 b,16 c16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    f,16[ g,16 a,16 b,16] f,16[ g,16 a,16 b,16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    g,16[ a,16 b,16 c16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    d,16[ e,16 f,16 g,16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] g,16[ a,16 b,16 c16] |
    c,16[ d,16 e,16 f,16] c,16[ d,16 e,16 f,16] |
    c,8\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    f,8\sustainOff\sustainOn[ <a c'>8] f,8[ <a c'>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    g,8\sustainOff\sustainOn[ <g b>8] g,8[ <g b>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    d,8\sustainOff\sustainOn[ <f a>8] g,8[ <g b>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    g,8\sustainOff\sustainOn[ <g b>8] g,8[ <g b>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    g,8\sustainOff\sustainOn[ <g b>8] g,8[ <g b>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    d,8\sustainOff\sustainOn[ <f a>8] g,8[ <g b>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] a,8[ <a c'>8] |
    g,8\sustainOff\sustainOn[ <g b>8] g,8[ <g b>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    f,8\sustainOff\sustainOn[ <a c'>8] f,8[ <a c'>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    g,8\sustainOff\sustainOn[ <g b>8] g,8[ <g b>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8] |
    d,8\sustainOff\sustainOn[ <f a>8] g,8[ <g b>8] |
    c,8\sustainOff\sustainOn[ <g c'>8] c,8[ <g c'>8\fermata\sustainOff] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    f,8[ <a c'>8 <a c'>8] f,8[ <a c'>8 <a c'>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    g,8[ <g b>8 <g b>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    d,8[ <f a>8 <f a>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    g,8[ <g b>8 <g b>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    g,8[ <g b>8 <g b>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    d,8[ <f a>8 <f a>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] a,8[ <a c'>8 <a c'>8] |
    g,8[ <g b>8 <g b>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    f,8[ <a c'>8 <a c'>8] f,8[ <a c'>8 <a c'>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    g,8[ <g b>8 <g b>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    d,8[ <f a>8 <f a>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] g,8[ <g b>8 <g b>8] |
    c,8[ <g c'>8 <g c'>8] c,8[ <g c'>8 <g c'>8] |
    c8[ <e g>8 <e g>8] f,8[ <f a>8 <f a>8] |
    g,8[ <f g b>8 <f g b>8] c8[ <e g>8 <e g>8] |
    c8[ <e g>8 <e g>8] f8[ <a c'>8 <a c'>8] |
    g8[ <b d'>8 <b d'>8] g,8[ <b, d f>8 <b, d f>8] |
    <c, c>4. r4. |
    <f, f>4. <g, g>4. |
    <c, c>2. |
    <c, g, c>2.\fermata |
          }
      }
    >>
  >>
  \layout {
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
