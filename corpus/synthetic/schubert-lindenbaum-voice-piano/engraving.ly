\version "2.24.3"
#(set-global-staff-size 18)
% automatically converted by musicxml2ly from /Users/d.sloane/music/corpus/synthetic/schubert-lindenbaum-voice-piano/truth.musicxml
\pointAndClickOff



\header {
    title =  "Der Lindenbaum"
    composer =  "Franz Schubert (1827)"
    encodingsoftware =  "synthetic-scan corpus builder"
    encodingdate =  "2026-11-08"
    }

\header {
  tagline = ##f
  subtitle = "Winterreise, D. 911, No. 5"
  poet = "Wilhelm Müller"
  title = "Der Lindenbaum"
  composer = "Franz Schubert"
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "C059"
}
\layout {
    \context { \Score
        skipBars = ##t
        autoBeaming = ##t
        }
    }
PartVVoiceOne =  \relative b' {
    \clef "treble" \time 3/4 \key e \major | % 1
    R2.*7 | % 8
    r2 r8 b8 | % 9
    b4. gis8 gis8 gis8 | \barNumberCheck #10
    gis4 e4 r8 e8 | % 11
    fis4. gis8 \times 2/3 {
        a8 gis8 fis8 }
    | % 12
    e2 r8 b'8 | % 13
    b4. gis8 gis8 gis8 | % 14
    gis4 e4 r8 e8 | % 15
    fis4. gis8 \times 2/3 {
        a8 gis8 fis8 }
    | % 16
    e2 r8 e8 | % 17
    fis4. fis8 fis8 fis8 | % 18
    gis8. a16 b4. b8 | % 19
    cis4. b8 gis8 e8 | \barNumberCheck #20
    fis2 r8 fis8 | % 21
    fis4. fis8 fis8 fis8 | % 22
    gis8. a16 b4 r8 b8 | % 23
    e4 b8 gis8 a8. fis16 | % 24
    e2 r4 \bar "|."
    }

PartVVoiceOneLyricsOne =  \lyricmode {\set ignoreMelismata = ##t Am Bru
    -- nnen vor dem Tho -- re da steht ein "Lin " __\skip1 den --
    "baum;" ich "traumt'" in sei -- nem Scha -- tten so man -- chen
    "su " __\skip1 ssen "Traum." Ich schnitt in sei -- ne "Rin "
    __\skip1 de so man -- ches lie -- be "Wort;" es zog in "Freud'" und
    "Lei " __\skip1 de zu "ihm " __\skip1 mich i -- mmer "fort."
    }

PartPVoiceOne =  \relative gis {
    \clef "treble" \time 3/4 \key e \major | % 1
    \times 2/3  {
        gis16 ( _\pp e'16 gis,16 }
    \times 2/3  {
        fis16 dis'16 fis,16 }
    \times 2/3  {
        gis16 e'16 gis,16 }
    \times 2/3  {
        b16 gis'16 b,16 }
    \times 2/3  {
        a16 fis'16 a,16 }
    \times 2/3  {
        gis16 e'16 gis,16 }
    | % 2
    <fis b>8. cis''16 b2 ) -> | % 3
    \times 2/3  {
        gis16 e'16 gis,16 }
    \times 2/3  {
        fis16 dis'16 fis,16 }
    \times 2/3  {
        gis16 e'16 gis,16 }
    \times 2/3  {
        b16 gis'16 b,16 }
    \times 2/3  {
        a16 fis'16 a,16 }
    \times 2/3  {
        gis16 e'16 gis,16 }
    | % 4
    \times 2/3  {
        fis16 dis'16 fis,16 }
    \times 2/3  {
        e16 cis'16 e,16 }
    \times 2/3  {
        dis16 b'16 dis,16 }
    \times 2/3  {
        cis16 a'16 cis,16 }
    \times 2/3  {
        b16 gis'16 b,16 }
    \times 2/3  {
        a16 fis'16 a,16 }
    | % 5
    \times 2/3  {
        gis16 e'16 gis,16 }
    \times 2/3  {
        a16 fis'16 a,16 }
    \times 2/3  {
        gis16 e'16 gis,16 }
    \times 2/3  {
        a16 fis'16 a,16 }
    \times 2/3  {
        gis16 e'16 gis,16 }
    \times 2/3  {
        d'16 eis16 d16 }
    | % 6
    \times 2/3  {
        cis16 fis16 cis16 }
    \times 2/3  {
        <eis gis>16 cis16 <eis gis>16 }
    <fis a>8 <cis fis a>8 <dis fis a>8 <e fis a>8 | % 7
    <fis a>8. ( _\fp <e gis>32 <b fis'>32 ) <b fis'>2 | % 8
    <fis' a>8. ( _\ppp <e gis>32 <b fis'>32 ) <b fis'>4. <b gis' b>8 _\p
    | % 9
    <b gis' b>4. <b e gis>8 ( <b e gis>8 <b e gis>8 ) | \barNumberCheck
    #10
    <b e gis>4 ( <gis b e>4 ) r8 <b e>8 | % 11
    <b e fis>2 <b dis fis>4 | % 12
    <gis b e>8 <gis' b>8 ( <e gis>8 <gis b>8 <fis a>8 <b, fis'>8 ) | % 13
    <gis e'>8 <b gis' b>4 <b e gis>8 ( <b e gis>8 <b e gis>8 ) | % 14
    <b e gis>4 ( <gis b e>4 ) r8 <b e>8 | % 15
    <b e fis>2 <b dis fis>4 | % 16
    <gis b e>8 <gis' b>8 ( <e gis>8 <gis b>8 <fis a>8 <e gis>8 ) | % 17
    <cis e fis>4. <cis e fis>8 ( <b dis fis>8 <b dis fis>8 ) | % 18
    \stemUp <e gis>8. ( \stemUp <fis a>16 \stemUp <gis b>4. ) \stemUp
    <gis b>8 | % 19
    <a cis>4. _\fp <gis b>8 <e gis>8 <b e>8 | \barNumberCheck #20
    <b dis fis>8. b'32 _\pp cis32 b8. <e, gis>16 <dis b'>4 | % 21
    <cis e fis>4. <cis e fis>8 ( <b dis fis>8 <b dis fis>8 ) | % 22
    \stemUp <e gis>8. \stemUp <fis a>16 \stemUp <gis b>4. \stemUp <gis
        b>8 | % 23
    <gis e'>4 <gis b>8 <e gis>8 <fis a>8. <b, fis'>16 | % 24
    <gis e'>8. gis'32 cis32 b8. <fis dis'>16 <e e'>4 \bar "|."
    }

PartPVoiceTwo =  \relative b {
    \clef "treble" \time 3/4 \key e \major s4*51 | % 18
    \stemDown b4 \stemDown b4. s8*19 | % 22
    \stemDown b4 \stemDown b4. s8*13 \bar "|."
    }

PartPVoiceFive =  \relative e, {
    \clef "bass" \time 3/4 \key e \major | % 1
    <e b'>2. ~ | % 2
    <b b'>8 r8 r4 r4 | % 3
    <e' b'>2. ~ | % 4
    <b b'>8 r16 cis16 b4. bis8 | % 5
    cis8 bis8 cis8 bis8 cis8 b8 | % 6
    a8 gis8 fis8 e8 dis8 cis8 | % 7
    b2. | % 8
    b2 ~ b8 <e e'>8 | % 9
    <e e'>4. e8 gis8 b8 | \barNumberCheck #10
    e2 r8 gis,8 | % 11
    b2 b4 | % 12
    e,8 <gis' b>8 <e gis>8 <gis b>8 <fis a>8 <b, dis>8 | % 13
    <e, gis e'>8 e'4 e,8 gis8 b8 | % 14
    e2 r8 gis,8 | % 15
    b2 b4 | % 16
    e,8 <gis' b>8 <e gis>8 <gis b>8 <fis a>8 <e gis>8 | % 17
    <ais, fis'>4. <ais gis'>8 <a b fis'>8 <a b fis'>8 | % 18
    \stemUp <b e>4 \stemUp <b e>4. \stemUp <gis' b>8 | % 19
    <a cis>4. <gis b>8 <e gis>8 <gis, e'>8 | \barNumberCheck #20
    <b fis'>8. b'32 cis32 b8. <e, gis>16 <b fis'>4 | % 21
    <ais fis'>4. <ais fis'>8 <a b fis'>8 <a b fis'>8 | % 22
    \stemUp <b e>4 \stemUp <b e>4. \stemUp <gis' b>8 | % 23
    <gis e'>4 <gis b>8 <e gis>8 <fis a>8. <b, fis'>16 | % 24
    <e, gis e'>8. gis'32 cis32 b8. <b, a'>16 <e gis>4 \bar "|."
    }

PartPVoiceSix =  \relative gis, {
    \clef "bass" \time 3/4 \key e \major s4*51 | % 18
    \stemDown gis8. \stemDown fis16 \stemDown e4. s8*19 | % 22
    \stemDown gis8. \stemDown fis16 \stemDown e4. s8*13 \bar "|."
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

