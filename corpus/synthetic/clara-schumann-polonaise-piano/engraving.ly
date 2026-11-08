\version "2.24.3"
#(set-global-staff-size 20)
% automatically converted by musicxml2ly from /Users/d.sloane/music/corpus/synthetic/clara-schumann-polonaise-piano/truth.musicxml
\pointAndClickOff



\header {
    title =  "Polonaise Op. 1 No. 1"
    composer =  "Clara Wieck-Schumann (1831)"
    encodingsoftware =  "synthetic-scan corpus builder"
    encodingdate =  "2026-11-08"
    }

\header {
  tagline = ##f
  subtitle = "Op. 1, No. 1"
  title = "Polonaise"
  composer = "Clara Wieck"
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Pagella"
}
\layout {
    \context { \Score
        autoBeaming = ##t
        }
    }
PartPVoiceOne =  \relative g' {
    \repeat volta 2 {
        \clef "treble" \time 3/4 \key es \major | % 1
        r8 <g bes>16 _\mf <g bes>16 <g bes>8 r8 r4 | % 2
        \stemUp g'4 ( \stemUp f8 ) r8 r4 | % 3
        r8 <g, es'>16 <g es'>16 <g es'>8 r8 r4 | % 4
        \stemUp f'4 ( \stemUp es8 ) r8 r4 | % 5
        d4. _\f \times 2/3 {
            bes16 d16 f16 }
        \times 2/3  {
            bes16 d16 f16 }
        \times 2/3  {
            as16 g16 f16 }
        | % 6
        es4. \times 2/3 {
            es,16 g16 bes16 }
        \times 2/3  {
            es16 g16 bes16 }
        \times 2/3  {
            es16 d16 c16 }
        | % 7
        bes4. \times 2/3 {
            bes,,16 d16 f16 }
        \times 2/3  {
            bes16 d16 f16 }
        \times 2/3  {
            as16 g16 f16 }
        | % 8
        es8 \times 2/3 {
            as16 ( g16 f16 }
        es,8 ) -. \times 2/3 {
            as16 ( _\p g16 f16 }
        es8 ) -. r8 }
    | % 9
    <f, as>4. _\mf g16 as16 d16 as16 c16 bes16 | \barNumberCheck #10
    fis8 g8 ~ -> g16 bes16 es16 g16 bes16 es16 d16 c16 | % 11
    bes8 a8 ~ -> a16 c16 es16 e16 g16 f16 es16 c16 | % 12
    bes16 ( a16 as16 g16 f16 es16 d16 c16 ) bes16 -. as16 -. g16 -. f16
    -. | % 13
    r8 <g bes>16 _\mf <g bes>16 <g bes>8 r8 r4 | % 14
    \stemUp g'4 \stemUp f8 r8 r4 | % 15
    r8 <g, es'>16 <g es'>16 <g es'>8 r8 r4 | % 16
    \stemUp f'4 \stemUp es8 r8 r4 \bar "|."
    }

PartPVoiceTwo =  \relative as' {
    \repeat volta 2 {
        \clef "treble" \time 3/4 \key es \major s2. | % 2
        \stemDown as4. r8 r4 s2. | % 4
        \stemDown as4. r8 r4 s1*3 }
    s4*15 | % 14
    \stemDown as4. r8 r4 s2. | % 16
    \stemDown as4. r8 r4 \bar "|."
    }

PartPVoiceFive =  \relative es {
    \repeat volta 2 {
        \clef "bass" \time 3/4 \key es \major | % 1
        <es es'>8 <bes bes'>8 <es es'>8 <bes bes'>8 <es es'>8 <bes bes'>8
        | % 2
        <d d'>8 <bes bes'>8 <d d'>8 <bes bes'>8 <d d'>8 <bes bes'>8 | % 3
        <des des'>8 <es es'>8 <des des'>8 <es es'>8 <des des'>8 <es es'>8
        | % 4
        <c c'>8 <es es'>8 <c c'>8 <es es'>8 <ces ces'>8 <es es'>8 | % 5
        bes8 \clef "treble" <bes' f' as>16 <bes f' as>16 <bes f' as>8
        <bes f' as>8 <bes f' as>8 <bes f' as>8 \clef "bass" | % 6
        \clef "bass" es,8 \clef "treble^8" <bes'' es g>16 <bes es g>16
        <bes es g>8 <bes es g>8 <bes es g>8 <bes es g>8 \clef "bass" | % 7
        bes,,8 \clef "treble" <bes' f' as>16 <bes f' as>16 <bes f' as>8
        <bes f' as>8 <bes f' as>8 <bes f' as>8 | % 8
        <es g>8 <bes d f as>8 ( <es g>8 ) -. <bes d f as>8 ( <es g>8 )
        -. r8 \clef "bass" }
    | % 9
    \stemUp d,8 \stemUp <f bes d>16 \stemUp <f bes d>16 \stemUp <f bes
        d>8 \stemUp <f bes d>8 \stemUp <f bes d>8 \stemUp <f bes d>8 |
    \barNumberCheck #10
    \stemUp es8 \stemUp <g bes es>8 \stemUp <g bes es>8 \stemUp <g bes
        es>8 \stemUp <g bes es>8 \stemUp <g bes es>8 | % 11
    \stemUp f8 \stemUp <c' es>8 \stemUp <c es>8 \stemUp <c es>8 \stemUp
    f,8 \stemUp <a c es>8 | % 12
    <bes d>8 r8 r4 r4 | % 13
    <es, es'>8 <bes bes'>8 <es es'>8 <bes bes'>8 <es es'>8 <bes bes'>8 | % 14
    <d d'>8 <bes bes'>8 <d d'>8 <bes bes'>8 <d d'>8 <bes bes'>8 | % 15
    <des des'>8 <es es'>8 <des des'>8 <es es'>8 <des des'>8 <es es'>8 | % 16
    <c c'>8 <es es'>8 <c c'>8 <es es'>8 <ces ces'>8 <es es'>8 \bar "|."
    }

PartPVoiceSix =  \relative d {
    \repeat volta 2 {
        \clef "bass" \time 3/4 \key es \major s8*25 \clef "treble" s8*5
        \clef "bass" | % 6
        \clef "bass" s8 \clef "treble^8" s8*5 \clef "bass" s8 \clef
        "treble" s8*11 \clef "bass" }
    | % 9
    \stemDown d2. | \barNumberCheck #10
    \stemDown es2. | % 11
    \stemDown f2 \stemDown f4 s4*15 \bar "|."
    }


% The score definition
\score {
    <<
        
        \new PianoStaff
        <<
            \set PianoStaff.instrumentName = "Piano"
            \set PianoStaff.shortInstrumentName = "Pno."
            
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
        
        \new PianoStaff
        <<
            \set PianoStaff.instrumentName = "Piano"
            \set PianoStaff.shortInstrumentName = "Pno."
            
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

