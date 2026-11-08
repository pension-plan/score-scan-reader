%% Closed-score SATB hymn: tune composed for this test (CC0); text Charles Wesley,
%% "Love divine, all loves excelling" (1747, public domain).
global = { \key g \major \time 4/4 }
sop = { \omrVoice "S" \global
  d'4 g' a' b' | c''4 b' a' a' | b'4 d'' c'' b' | a'4 a' g'2 |
  b'4 b' c'' d'' | e''4 d'' c''8( b') a'4 | g'4 a' b' c'' | b'4. a'8 g'2 | \break
  d''4 b' e'' d'' | c''4 b' a' b' | c''4 b' a' g' | fis'4 fis' g'2 |
  g'4 a' b' g' | c''4 b' a'8( g') fis'4 | g'4 b' d'' c'' | b'4 a' g'2 \bar "|." }
alt = { \omrVoice "A" \global
  b4 d' fis' g' | e'4 d' d' c' | d'4 g' e' d' | e'4 d' d'2 |
  g'4 g' g' fis' | g'4 g' e' fis' | d'4 fis' g' e' | d'4. c'8 b2 |
  g'4 g' g' g' | g'4 g' fis' d' | e'4 d' c' b | d'4 d' g'2 |
  d'4 fis' g' e' | e'4 d' e' d' | d'4 d' g' e' | d'4 c' b2 }
ten = { \omrVoice "T" \global
  g4 b d' d' | g4 g fis fis | g4 b c'8 b g4 | c'4 c' b2 |
  d'4 d' c' a | c'4 b c' d' | b4 d' d' c' | g4 fis g2 |
  b4 d' c' b | c'4 d' d' d' | g4 g fis g | a4 a b2 |
  b4 d' d' b | c'4 d' c' a | b4 b b c' | g4 fis g2 }
bas = { \omrVoice "B" \global
  g,4 g, d g | c4 g, d d | g4 g a, b, | c4 d g,2 |
  g4 g e d | c4 b, a, d | g,4 d8 e g4 c | d4 d g,2 |
  g4 g c g | a,4 g, d g | c4 g, d e | d4 d g,2 |
  g4 d g e | a,4 b, c d | g,4 g b, a, | d4 d g,2 }
vI = \lyricmode { \set stanza = "1."
  Love di -- vine, all loves ex -- cel -- ling, joy of heav'n to earth come down;
  fix in us thy hum -- ble dwel -- ling; all thy faith -- ful mer -- cies crown!
  Je -- sus, thou art all com -- pas -- sion, pure, un -- bound -- ed love thou art;
  vis -- it us with thy sal -- va -- tion; en -- ter ev -- ery trem -- bling heart. }
vII = \lyricmode { \set stanza = "2."
  Breathe, O breathe thy lov -- ing Spi -- rit in -- to ev -- ery trou -- bled breast!
  Let us all in thee in -- her -- it; let us find that sec -- ond rest.
  Take a -- way our bent to sin -- ning; Al -- pha and O -- me -- ga be;
  end of faith, as its be -- gin -- ning, set our hearts at lib -- er -- ty. }
vIII = \lyricmode { \set stanza = "3."
  Come, Al -- might -- y to de -- li -- ver, let us all thy life re -- ceive;
  sud -- den -- ly re -- turn and ne -- ver, ne -- ver more thy tem -- ples leave.
  Thee we would be al -- ways bless -- ing, serve thee as thy hosts a -- bove,
  pray and praise thee with -- out ceas -- ing, glo -- ry in thy per -- fect love. }
vIV = \lyricmode { \set stanza = "4."
  Fin -- ish, then, thy new cre -- a -- tion; pure and spot -- less let us be.
  Let us see thy great sal -- va -- tion per -- fect -- ly re -- stored in thee;
  changed from glo -- ry in -- to glo -- ry, till in heav'n we take our place,
  till we cast our crowns be -- fore thee, lost in won -- der, love, and praise. }
\header { title = "Love Divine" composer = "Test tune (CC0)" poet = "Charles Wesley, 1747" tagline = ##f }
\score {
  \new ChoirStaff <<
    \new Staff = "women" <<
      \new Voice = "sop" { \voiceOne \sop }
      \new Voice = "alt" { \voiceTwo \alt }
    >>
    \new Lyrics \lyricsto "sop" \vI
    \new Lyrics \lyricsto "sop" \vII
    \new Lyrics \lyricsto "sop" \vIII
    \new Lyrics \lyricsto "sop" \vIV
    \new Staff = "men" <<
      \clef bass
      \new Voice = "ten" { \voiceOne \ten }
      \new Voice = "bas" { \voiceTwo \bas }
    >>
  >>
  \layout { }
}
