\version "2.24.3"
#(set-global-staff-size 20)
% automatically converted by musicxml2ly from /Users/d.sloane/music/corpus/synthetic/schumann-dichterliebe2-voice-piano/truth.musicxml
\pointAndClickOff



\header {
    title =  "Aus meinen Tränen sprießen"
    composer =  "Robert Schumann (1840)"
    encodingsoftware =  "synthetic-scan corpus builder"
    encodingdate =  "2026-11-08"
    }

\header {
  tagline = ##f
  subtitle = "Dichterliebe, Op. 48, No. 2"
  poet = "Heinrich Heine"
  title = "Aus meinen Tränen sprießen"
  composer = "Robert Schumann"
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
}
\layout {
    \context { \Score
        autoBeaming = ##t
        }
    }
PartVVoiceOne =  \relative cis'' {
    \clef "treble" \time 2/4 \key a \major \partial 8 cis8 _\p | % 1
    cis8. cis16 cis8 cis8 | % 2
    d4 cis8 r16 cis16 | % 3
    b8 b16 cis16 a8 a16 cis16 | % 4
    b8 r8 r8 cis8 | % 5
    cis8. cis16 cis8 cis8 | % 6
    d4 cis8 r16 cis16 | % 7
    b8. cis16 a8. cis16 | % 8
    b8 r8 r8 b8 | % 9
    b8 b16 b16 b8 b8 | \barNumberCheck #10
    cis4 cis4 | % 11
    fis,16 fis16 fis16 fis16 b8. b16 | % 12
    gis4 r8 cis16 cis16 | % 13
    cis8. cis16 \times 2/3 {
        cis8 b8 cis8 }
    | % 14
    d4 cis8 r16 cis16 | % 15
    b8. cis16 a8. cis16 | % 16
    b4. ^\fermata r8 | % 17
    r4 \bar "|."
    }

PartVVoiceOneLyricsOne =  \lyricmode {\set ignoreMelismata = ##t Aus mei
    -- nen Trä -- nen sprie -- ßen viel blü -- hen -- de Blu -- men her
    -- "vor," und mei -- ne Seuf -- zer wer -- den ein Nach -- ti -- gal
    -- len -- "chor." Und wenn du mich lieb "hast," Kind -- "chen,"
    "schenk'" ich dir die Blu -- men "all," und vor dei -- nem Fen --
    ster soll klin -- gen das Lied der Nach -- ti -- "gall."
    }

PartPVoiceOne =  \relative a' {
    \clef "treble" \time 2/4 \key a \major \partial 8 <a cis>8 ~ ~ _\p | % 1
    <a cis>8 <a cis>8 ( -. <a cis>8 -. <a cis>8 ) -. | % 2
    <fis a d>4 ( -> <e a cis>8 ) r8 | % 3
    <d gis b>8. -> cis'16 ( <cis, a'>4 ) | % 4
    <d gis b>8. ^\fermata _\pp cis'16 ( <cis, a'>8 ) <a' cis>8 ~ ~ _\p | % 5
    <a cis>8 <a cis>8 ( -. <a cis>8 -. <a cis>8 ) -. | % 6
    <fis a d>4 ( -> <e a cis>8 ) r8 | % 7
    <d gis b>8. -> cis'16 ( <cis, a'>4 ) | % 8
    <d gis b>8. ^\fermata _\pp cis'16 ( <cis, a'>8 ) <e gis b>8 ~ ~ ~
    _\p | % 9
    <e gis b>2 ~ | \barNumberCheck #10
    \stemUp <e cis'>2 | % 11
    <d fis>8 r8 <fis b>8 -. r8 | % 12
    <eis gis>8 -. r16 <fis b>16 ( <eis gis>8 ) <e g a cis>16 -. _\pp <e
        g a cis>16 -. | % 13
    <e g a cis>8. <e g a cis>16 <e g a cis>8. <e g a cis>16 | % 14
    \stemUp <a d>4 ~ \stemUp <a cis>8 r8 | % 15
    <d, gis b>8. -> cis'16 ( <cis, a'>4 ) | % 16
    <d gis b>4 ~ ^\fermata ~ ~ _\pp <d gis b>8. cis'16 ( | % 17
    <cis, a'>4 ) \bar "|."
    }

PartPVoiceTwo =  \relative gis' {
    \clef "treble" \time 2/4 \key a \major \partial 8 s8*37 |
    \barNumberCheck #10
    \stemDown gis8 \stemDown g8 \stemDown fis8 \stemDown e8 s1. | % 14
    \stemDown fis8 \stemDown f8 \stemDown e8 s8*11 \bar "|."
    }

PartPVoiceFive =  \relative a' {
    \clef "bass" \time 2/4 \key a \major \partial 8 \clef "treble" a8 (
    ~ | % 1
    a8 gis8 -. fis8 -. e8 -. | % 2
    d4 a8 ) r8 | % 3
    \stemUp e'8. \stemUp e,16 \stemUp a4 | % 4
    \stemUp e'8. ^\fermata \stemUp e,16 \stemUp <a a'>8 \stemUp a'8 ( ~
    -> | % 5
    a8 gis8 fis8 e8 ) | % 6
    d4 ( a8 ) r8 | % 7
    \stemUp e'8. \stemUp e,16 \stemUp a4 | % 8
    \stemUp e'8. ^\fermata \stemUp e,16 \stemUp <a a'>8 \stemUp e'8 ( ~
    | % 9
    e8 dis8 cis8 b8 | \barNumberCheck #10
    \clef "bass" ais2 | % 11
    b8 ) r8 <gis d'>8 -. r8 | % 12
    cis8 -. r16 <gis d'>16 ( cis8 ) a16 -. a16 -. | % 13
    a8. a16 a8. a16 | % 14
    \stemUp d,4 ( \stemUp a'8 ) r8 | % 15
    \stemUp e'8. \stemUp e,16 \stemUp a4 | % 16
    \stemUp e'4 ~ ^\fermata \stemUp e8. \stemUp e,16 | % 17
    \stemUp a4 \bar "|."
    }

PartPVoiceSix =  \relative e' {
    \clef "bass" \time 2/4 \key a \major \partial 8 \clef "treble" s8*9
    | % 3
    \stemDown e4 ~ \stemDown e4 | % 4
    \stemDown e4 ~ \stemDown <a, e'>8 s8*9 | % 7
    \stemDown e'4 ~ \stemDown e4 | % 8
    \stemDown e4 ~ \stemDown <a, e'>8 s8*5 | \barNumberCheck #10
    \clef "bass" s1*2 | % 14
    \stemDown a4 ~ \stemDown a8 s8 | % 15
    \stemDown e'4 ~ \stemDown e4 | % 16
    \stemDown e2 ~ | % 17
    \stemDown e4 \bar "|."
    }


% The score definition
\score {
    <<
        
        \new Staff
        <<
            \set Staff.instrumentName = "Voice"
            
            \context Staff << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartVVoiceOne" {  \PartVVoiceOne }
                \new Lyrics \lyricsto "PartVVoiceOne" { \PartVVoiceOneLyricsOne }
                >>
            >>
        \new PianoStaff
        <<
            \set PianoStaff.instrumentName = "Piano"
            
            \context Staff = "1" << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPVoiceOne" {  \voiceOne \PartPVoiceOne }
                \context Voice = "PartPVoiceTwo" {  \voiceTwo \PartPVoiceTwo }
                >> \context Staff = "2" <<
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPVoiceFive" {  \voiceOne \PartPVoiceFive }
                \context Voice = "PartPVoiceSix" {  \voiceTwo \PartPVoiceSix }
                >>
            >>
        
        >>
    \layout {}
    }
\score {
    <<
        
        \new Staff
        <<
            \set Staff.instrumentName = "Voice"
            
            \context Staff << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartVVoiceOne" {  \PartVVoiceOne }
                \new Lyrics \lyricsto "PartVVoiceOne" { \PartVVoiceOneLyricsOne }
                >>
            >>
        \new PianoStaff
        <<
            \set PianoStaff.instrumentName = "Piano"
            
            \context Staff = "1" << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPVoiceOne" {  \voiceOne \PartPVoiceOne }
                \context Voice = "PartPVoiceTwo" {  \voiceTwo \PartPVoiceTwo }
                >> \context Staff = "2" <<
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPVoiceFive" {  \voiceOne \PartPVoiceFive }
                \context Voice = "PartPVoiceSix" {  \voiceTwo \PartPVoiceSix }
                >>
            >>
        
        >>
    \midi { \tempo 4 = 100 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
    }

