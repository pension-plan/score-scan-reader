\version "2.24.0"
\include "omrtruth.ily"
#(set-global-staff-size 20)
\paper { #(set-paper-size "a4") }
%% Melody composed for this test (CC0); text Ben Jonson, "Song: To Celia" (1616, public domain).
\header { title = "To Celia" composer = "Test tune (CC0)" poet = "Ben Jonson" tagline = ##f }
melody = { \omrVoice "M" \clef treble \key g \major \time 3/4
  d'4 d' d' | g'2 a'4 | b'4( c'') b' | a'2. |
  g'4 a' b' | c''2( e''4) | d''2( b'4) | a'2 r4 |
  d''4 d'' cis'' | b'2 a'4 | g'4( fis') g' | e'2. |
  c'4 e' g' | c''2( b'4) | a'2( fis'4) | g'2. |
  b'4 b' b' | e''2 d''4 | c''4( b') a' | b'2. |
  g'8( a') b'4 c'' | d''2( fis''4) | a''2( d''4) | b'2 r4 |
  d''4 e'' d'' | c''2 b'4 | a'4( b') c'' | d''2. |
  g'4 a' b' | d''2( c''4) | b'2( a'4) | g'2.~ | g'2. \bar "|." }
wI = \lyricmode { \set stanza = "1."
  Drink to me on -- ly with thine eyes, and I will pledge __ with __ mine;
  or leave a kiss but in __ the cup, and I'll not look __ for __ wine.
  The thirst that from the soul __ doth rise doth __ ask a drink __ di __ -- vine;
  but might I of Jove's nec __ -- tar sup, I would not change __ for __ thine. __ }
wII = \lyricmode { \set stanza = "2."
  I sent thee late a ro -- sy wreath, not so much hon -- 'ring thee
  as giv -- ing it a hope, that there it could not with -- ered be.
  But thou there -- on didst on -- ly breathe, and sent'st it back to me;
  since when it grows, and smells, I swear, not of it -- self, but thee. }
\score {
  <<
    \new Staff \new Voice = "mel" \melody
    \new Lyrics \lyricsto "mel" \wI
    \new Lyrics \lyricsto "mel" \wII
  >>
  \layout { }
}
