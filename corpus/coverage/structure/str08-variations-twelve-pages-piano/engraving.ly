\version "2.24.0"
#(set-global-staff-size 23)
\header {
  title = "Theme and Variations in A"
  subtitle = "for piano"
  composer = "Coverage corpus (2026)"
  copyright = "CC0 1.0"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  indent = 12\mm
  ragged-bottom = ##t
  system-system-spacing.basic-distance = #22
  oddHeaderMarkup = \markup \fill-line { "" \unless \on-first-page \italic "Theme and Variations in A" \if \should-print-page-number \fromproperty #'page:page-number-string }
  evenHeaderMarkup = \markup \fill-line { \if \should-print-page-number \fromproperty #'page:page-number-string \unless \on-first-page \italic "Theme and Variations in A" "" }
}
\score {
  <<
    \new PianoStaff \with { instrumentName = "Piano" } <<
      \new Staff = "rh" { \clef "treble"
          \new Voice = "vPx1" {
    \autoBeamOff
    \autoLineBreaksOff \autoPageBreaksOff \tempo "Andante" 4 = 69 \textMark \markup { \bold "Thema" } \time 2/4 \key a \major \stemDown cis''4\p e''4 |
    fis''4 d''4 |
    e''4 cis''8[ a'8] |
    b'2 |
    \break cis''4 e''4 |
    fis''4 a''4 |
    gis''4 d''4 |
    a''2 \textEndMark \markup { \line {  \italic "To Coda"  \hspace #0.5 \raise #0.6 \musicglyph "scripts.coda" } } \bar ":|.|:" |
    \break fis''4 cis''4 |
    d''4 b'4 |
    e''4 \stemUp gis'4 |
    a'2 |
    \pageBreak \stemDown fis''4 a''4 |
    e''4 cis''4 |
    d''4 b'4 |
    \stemUp a'2 \bar ":|.|:" |
    \break \textMark \markup { \bold "Var. I" } \stemDown cis''8\mf[ a'8] e''8[ cis''8] |
    fis''8[ d''8] d''8[ a'8] |
    e''8[ cis''8] cis''8[ a'8] |
    \stemUp b'8[ gis'8] b'8[ gis'8] |
    \break \stemDown cis''8[ a'8] e''8[ cis''8] |
    fis''8[ d''8] a''8[ fis''8] |
    gis''8[ e''8] d''8[ b'8] |
    a''4 r4 \bar ":|.|:" |
    \pageBreak fis''8[ cis''8] cis''8[ a'8] |
    d''8[ b'8] \stemUp b'8[ fis'8] |
    \stemDown e''8[ b'8] \stemUp gis'8[ e'8] |
    a'8[ e'8] a'8[ e'8] |
    \break \stemDown fis''8[ d''8] a''8[ fis''8] |
    e''8[ cis''8] cis''8[ a'8] |
    d''8[ b'8] \stemUp b'8[ gis'8] |
    a'4 r4 \bar ":|.|:" |
    \break \textMark \markup { \bold "Var. II" } \stemDown cis''16\f[ d''16 cis''16 a'16] e''16[ fis''16 e''16 cis''16] |
    fis''16[ gis''16 fis''16 d''16] d''16[ e''16 d''16 a'16] |
    e''16[ fis''16 e''16 cis''16] cis''16[ d''16 cis''16 a'16] |
    \stemUp b'16[ cis''16 b'16 gis'16] b'16[ cis''16 b'16 gis'16] |
    \pageBreak \stemDown cis''16[ d''16 cis''16 a'16] e''16[ fis''16 e''16 cis''16] |
    fis''16[ gis''16 fis''16 d''16] a''16[ b''16 a''16 fis''16] |
    gis''16[ a''16 gis''16 e''16] d''16[ e''16 d''16 b'16] |
    \set Score.repeatCommands = #'((volta "1.")) \stemUp b'16[ cis''16 b'16 gis'16] \stemDown d''16[ e''16 d''16 b'16] \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) a''4 r4 \bar ".|:-||" |
    \break \set Score.repeatCommands = #'((volta #f)) fis''16[ gis''16 fis''16 cis''16] cis''16[ d''16 cis''16 a'16] |
    d''16[ e''16 d''16 b'16] \stemUp b'16[ cis''16 b'16 fis'16] |
    \stemDown e''16[ fis''16 e''16 b'16] \stemUp gis'16[ a'16 gis'16 e'16] |
    a'16[ b'16 a'16 e'16] a'16[ b'16 a'16 e'16] |
    \break \stemDown fis''16[ gis''16 fis''16 d''16] a''16[ b''16 a''16 fis''16] |
    e''16[ fis''16 e''16 cis''16] cis''16[ d''16 cis''16 a'16] |
    d''16[ e''16 d''16 b'16] \stemUp b'16[ cis''16 b'16 gis'16] |
    a'4 r4 \bar ":|.|:" |
    \pageBreak \textMark \markup { \bold "Var. III" } r8 <e' a' cis''>8\mp r8 <e' a' cis''>8 |
    r8 <d' fis' a'>8 r8 <d' fis' a'>8 |
    r8 <e' a' cis''>8 r8 <e' a' cis''>8 |
    r8 <e' gis' b'>8 r8 <e' gis' b'>8 |
    \break r8 <e' a' cis''>8 r8 <e' a' cis''>8 |
    r8 <d' fis' a'>8 r8 <d' fis' a'>8 |
    r8 <d' e' gis' b'>8 r8 <d' e' gis' b'>8 |
    r8 <e' a' cis''>8 r8 <e' a' cis''>8 \bar ":|.|:" |
    \break r8 <cis' fis' a'>8 r8 <cis' fis' a'>8 |
    r8 <d' fis' b'>8 r8 <d' fis' b'>8 |
    r8 <e' gis' b'>8 r8 <e' gis' b'>8 |
    r8 <e' a' cis''>8 r8 <e' a' cis''>8 |
    \pageBreak r8 <d' fis' a'>8 r8 <d' fis' a'>8 |
    r8 <e' a' cis''>8 r8 <e' a' cis''>8 |
    r8 <d' e' gis' b'>8 r8 <d' e' gis' b'>8 |
    r8 <e' a' cis''>8 r8 <e' a' cis''>8 \bar ":|.|:" |
    \break \tempo "Adagio" 4 = 50 \textMark \markup { \bold "Var. IV - Minore" } \key a \minor <e' a' c''>4\p \stemDown <a' c'' e''>4 |
    <a' d'' f''>4 \stemUp <f' a' d''>4 |
    \stemDown <a' c'' e''>4 \stemUp <e' a' c''>4 |
    <e' gis' b'>2 |
    \break <e' a' c''>4 \stemDown <a' c'' e''>4 |
    <a' d'' f''>4 <d'' f'' a''>4 |
    <d'' e'' gis''>4 <gis' b' d''>4 |
    <c'' e'' a''>2 \bar ":|.|:" |
    \pageBreak <a' c'' f''>4 \stemUp <f' a' c''>4 |
    <f' a' d''>4 <d' f' a'>4 |
    \stemDown <gis' b' e''>4 \stemUp <b e' gis'>4 |
    <c' e' a'>2 |
    \break \stemDown <a' d'' f''>4 <d'' f'' a''>4 |
    <a' c'' e''>4 \stemUp <e' a' c''>4 |
    \stemDown <gis' b' d''>4 \stemUp <e' gis' b'>4 |
    <c' e' a'>2 \bar ":|.|:" |
    \break \tempo "Tempo I" \textMark \markup { \bold "Var. V - Maggiore" } \key a \major \tuplet 3/2 { cis''8\f[ a'8 e'8] } \stemDown \tuplet 3/2 { e''8[ cis''8 a'8] } |
    \tuplet 3/2 { fis''8[ d''8 a'8] } \stemUp \tuplet 3/2 { d''8[ a'8 fis'8] } |
    \stemDown \tuplet 3/2 { e''8[ cis''8 a'8] } \stemUp \tuplet 3/2 { cis''8[ a'8 e'8] } |
    \tuplet 3/2 { b'8[ gis'8 e'8] } \tuplet 3/2 { b'8[ gis'8 e'8] } |
    \pageBreak \tuplet 3/2 { cis''8[ a'8 e'8] } \stemDown \tuplet 3/2 { e''8[ cis''8 a'8] } |
    \tuplet 3/2 { fis''8[ d''8 a'8] } \tuplet 3/2 { a''8[ fis''8 d''8] } |
    \tuplet 3/2 { gis''8[ e''8 d''8] } \tuplet 3/2 { d''8[ b'8 gis'8] } |
    a''4 r4 \bar ":|.|:" |
    \break \tuplet 3/2 { fis''8[ cis''8 a'8] } \stemUp \tuplet 3/2 { cis''8[ a'8 fis'8] } |
    \tuplet 3/2 { d''8[ b'8 fis'8] } \tuplet 3/2 { b'8[ fis'8 d'8] } |
    \stemDown \tuplet 3/2 { e''8[ b'8 gis'8] } \stemUp \tuplet 3/2 { gis'8[ e'8 b8] } |
    \tuplet 3/2 { a'8[ e'8 cis'8] } \tuplet 3/2 { a'8[ e'8 cis'8] } |
    \break \stemDown \tuplet 3/2 { fis''8[ d''8 a'8] } \tuplet 3/2 { a''8[ fis''8 d''8] } |
    \tuplet 3/2 { e''8[ cis''8 a'8] } \stemUp \tuplet 3/2 { cis''8[ a'8 e'8] } |
    \stemDown \tuplet 3/2 { d''8[ b'8 gis'8] } \stemUp \tuplet 3/2 { b'8[ gis'8 e'8] } |
    \set Score.repeatCommands = #'((volta "1.")) \tuplet 3/2 { gis'8[ e'8 d'8] } \tuplet 3/2 { b'8[ gis'8 e'8] } \bar ":|." |
    \set Score.repeatCommands = #'((volta #f) (volta "2.")) a'4 r4 \bar ".|:-||" |
    \pageBreak \set Score.repeatCommands = #'((volta #f)) \textMark \markup { \bold "Var. VI" } \stemDown cis''8.\mf[ d''16] e''8.[ cis''16] |
    fis''8.[ gis''16] d''8.[ a'16] |
    e''8.[ fis''16] cis''8.[ a'16] |
    b'8.[ cis''16] \stemUp b'8.[ gis'16] |
    \break \stemDown cis''8.[ d''16] e''8.[ cis''16] |
    fis''8.[ gis''16] a''8.[ fis''16] |
    gis''8.[ a''16] d''8.[ b'16] |
    a''4 r4 \bar ":|.|:" |
    \break fis''8.[ gis''16] cis''8.[ a'16] |
    d''8.[ e''16] \stemUp b'8.[ fis'16] |
    \stemDown e''8.[ fis''16] \stemUp gis'8.[ e'16] |
    a'8.[ b'16] a'8.[ e'16] |
    \pageBreak \stemDown fis''8.[ gis''16] a''8.[ fis''16] |
    e''8.[ fis''16] cis''8.[ a'16] |
    d''8.[ e''16] \stemUp b'8.[ gis'16] |
    a'4 r4 \bar ":|.|:" |
    \break \textMark \markup { \bold "Var. VII" } \stemDown <cis'' cis'''>4\ff <e'' e'''>4 |
    <fis'' fis'''>4 <d'' d'''>4 |
    <e'' e'''>4 <cis'' cis'''>4 |
    <b' b''>2 |
    \break <cis'' cis'''>4 <e'' e'''>4 |
    <fis'' fis'''>4 <a'' a'''>4 |
    <gis'' gis'''>4 <d'' d'''>4 |
    <a'' a'''>2 \bar ":|." |
    \pageBreak <fis'' fis'''>4 <cis'' cis'''>4 |
    <d'' d'''>4 <b' b''>4 |
    <e'' e'''>4 <gis' gis''>4 |
    <a' a''>2 |
    \break <fis'' fis'''>4 <a'' a'''>4 |
    <e'' e'''>4 <cis'' cis'''>4 |
    <d'' d'''>4 <b' b''>4 |
    <a' a''>2 \textEndMark \markup { \bold \italic "D.C. al Coda" } \bar "||" |
    \break \codaMark 1 \tempo "Più mosso" \textMark \markup { \bold "Coda" } fis''8\f[ cis''8] cis''8[ a'8] |
    d''8[ b'8] \stemUp b'8[ fis'8] |
    \stemDown e''8[ b'8] \stemUp gis'8[ e'8] |
    a'8[ e'8] a'8[ e'8] |
    \pageBreak \stemDown fis''8[ d''8] a''8[ fis''8] |
    e''8[ cis''8] cis''8[ a'8] |
    d''8[ b'8] \stemUp b'8[ gis'8] |
    a'4 r4 |
    \break \stemDown <a' cis'' e''>4 <a' cis'' e''>4 |
    <a' d'' fis''>4 <a' d'' fis''>4 |
    <gis' b' d''>4 <gis' b' d''>4 |
    \stemUp <e' a' cis''>4 <e' a' cis''>4 |
    \break <fis' a' cis''>4 <fis' a' cis''>4 |
    <fis' a' d''>4 <fis' a' d''>4 |
    <e' gis' b'>4 <e' gis' b'>4 |
    <cis' e' a'>2 \bar "|." |
          }
      }
      \new Staff = "lh" { \clef "bass"
          \new Voice = "vPx5" {
    \autoBeamOff
    \key a \major \stemUp a,4 \stemDown <e a cis'>4 |
    d4 <fis a d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    e4 <e gis b>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    d4 <fis a d'>4 |
    e4 <e gis b d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    fis4 <fis a cis'>4 |
    \stemUp b,4 \stemDown <d fis b>4 |
    e4 <e gis b>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    d4 <fis a d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    e4 <e gis b d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    \stemUp a,4 \stemDown e4 |
    d4 a4 |
    \stemUp a,4 \stemDown e4 |
    e4 b4 |
    \stemUp a,4 \stemDown e4 |
    d4 a4 |
    e4 b4 |
    \stemUp a,4 r4 |
    \stemDown fis4 cis'4 |
    \stemUp b,4 \stemDown fis4 |
    e4 b4 |
    \stemUp a,4 \stemDown e4 |
    d4 a4 |
    \stemUp a,4 \stemDown e4 |
    e4 b4 |
    \stemUp a,4 r4 |
    \stemDown a,8[ cis'8] a8[ cis'8] |
    d8[ d'8] a8[ d'8] |
    a,8[ cis'8] a8[ cis'8] |
    e8[ b8] gis8[ b8] |
    a,8[ cis'8] a8[ cis'8] |
    d8[ d'8] a8[ d'8] |
    e8[ d'8] b8[ d'8] |
    e8[ d'8] b8[ d'8] |
    \stemUp a,8[ e8] a,4 |
    \stemDown fis8[ cis'8] a8[ cis'8] |
    b,8[ b8] fis8[ b8] |
    e8[ b8] gis8[ b8] |
    a,8[ cis'8] a8[ cis'8] |
    d8[ d'8] a8[ d'8] |
    a,8[ cis'8] a8[ cis'8] |
    e8[ d'8] b8[ d'8] |
    \stemUp a,8[ e8] a,4 |
    cis4 \stemDown e4 |
    fis4 d4 |
    e4 \stemUp cis4 |
    b,2 |
    cis4 \stemDown e4 |
    fis4 a4 |
    gis4 d4 |
    a2 |
    fis4 \stemUp cis4 |
    \stemDown d4 \stemUp b,4 |
    \stemDown e4 \stemUp gis,4 |
    a,2 |
    \stemDown fis4 a4 |
    e4 \stemUp cis4 |
    \stemDown d4 \stemUp b,4 |
    a,2 |
    \key a \minor a,2 |
    \stemDown d2 |
    \stemUp a,2 |
    \stemDown e2 |
    \stemUp a,2 |
    \stemDown d2 |
    e2 |
    \stemUp a,2 |
    \stemDown f2 |
    d2 |
    e2 |
    \stemUp a,2 |
    \stemDown d2 |
    \stemUp a,2 |
    \stemDown e2 |
    \stemUp a,2 |
    \key a \major a,4 \stemDown e4 |
    d4 a4 |
    \stemUp a,4 \stemDown e4 |
    e4 b4 |
    \stemUp a,4 \stemDown e4 |
    d4 a4 |
    e4 b4 |
    \stemUp a,4 r4 |
    \stemDown fis4 cis'4 |
    \stemUp b,4 \stemDown fis4 |
    e4 b4 |
    \stemUp a,4 \stemDown e4 |
    d4 a4 |
    \stemUp a,4 \stemDown e4 |
    e4 b4 |
    e4 b4 |
    \stemUp a,4 r4 |
    a,4 \stemDown <e a cis'>4 |
    d4 <fis a d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    e4 <e gis b>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    d4 <fis a d'>4 |
    e4 <e gis b d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    fis4 <fis a cis'>4 |
    \stemUp b,4 \stemDown <d fis b>4 |
    e4 <e gis b>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    d4 <fis a d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    e4 <e gis b d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    a,16[ e16 a16 e16] a,16[ e16 a16 e16] |
    \stemUp d,16[ a,16 d16 a,16] d,16[ a,16 d16 a,16] |
    \stemDown a,16[ e16 a16 e16] a,16[ e16 a16 e16] |
    \stemUp e,16[ b,16 e16 b,16] e,16[ b,16 e16 b,16] |
    \stemDown a,16[ e16 a16 e16] a,16[ e16 a16 e16] |
    \stemUp d,16[ a,16 d16 a,16] d,16[ a,16 d16 a,16] |
    e,16[ b,16 e16 b,16] e,16[ b,16 e16 b,16] |
    \stemDown a,16[ e16 a16 e16] a,16[ e16 a16 e16] |
    \stemUp fis,16[ cis16 fis16 cis16] fis,16[ cis16 fis16 cis16] |
    \stemDown b,16[ fis16 b16 fis16] b,16[ fis16 b16 fis16] |
    \stemUp e,16[ b,16 e16 b,16] e,16[ b,16 e16 b,16] |
    \stemDown a,16[ e16 a16 e16] a,16[ e16 a16 e16] |
    \stemUp d,16[ a,16 d16 a,16] d,16[ a,16 d16 a,16] |
    \stemDown a,16[ e16 a16 e16] a,16[ e16 a16 e16] |
    \stemUp e,16[ b,16 e16 b,16] e,16[ b,16 e16 b,16] |
    \stemDown a,16[ e16 a16 e16] a,16[ e16 a16 e16] |
    fis4 cis'4 |
    \stemUp b,4 \stemDown fis4 |
    e4 b4 |
    \stemUp a,4 \stemDown e4 |
    d4 a4 |
    \stemUp a,4 \stemDown e4 |
    e4 b4 |
    \stemUp a,4 r4 |
    a,4 \stemDown <e a cis'>4 |
    d4 <fis a d'>4 |
    e4 <e gis b d'>4 |
    \stemUp a,4 \stemDown <e a cis'>4 |
    fis4 <fis a cis'>4 |
    d4 <fis a d'>4 |
    e4 <e gis b d'>4 |
    \stemUp <a,, a,>2 |
          }
      }
    >>
  >>
  \layout {
    \context { \Score \override CodaMark.break-visibility = ##(#f #t #t) \override SegnoMark.break-visibility = ##(#f #t #t) }
  }
  \midi { \tempo 4 = 90 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
}
