\version "2.24.3"
% automatically converted by musicxml2ly from ./truth.musicxml
\pointAndClickOff

\header {
    title =  Melodie
    subtitle =  "Melodie (Album fuer die Jugend, Op. 68 No. 1)"
    copyright =  "Public domain"
    composer =  "Robert Schumann"
    arranger =  "Karl Klauser (editor)"
    encodingsoftware = 
    "hand transcription; compiled by corpus/real/tools/mkxml.py"
    encodingdate =  "2026-11-08"
    source = 
    "Erstes Album fuer die Jugend Op. 68, Leipzig: J. Schuberth & Co. [1867], p. 1 (Internet Archive b26976821, leaf n2; Gaylord Music Library, Washington University in St. Louis)"
    }

PartPOneVoiceOne =  \relative e'' {
    \repeat volta 2 {
        \clef "treble" \time 4/4 \key c \major | % 1
        e4 d4 c4 b4 | % 2
        a8 c8 b8 d8 c4 g4 | % 3
        g'4 f4 e4 c4 | % 4
        b4 <fis a>4 g4 r4 }
    \break | % 5
    d'4 c4 b4 r4 | % 6
    f'4 e4 d4 r4 | % 7
    a'4 g4 f4 e4 | % 8
    d8 f8 e8 g8 f4. d8 | % 9
    <c e>4 d4 c4 b4 \break | \barNumberCheck #10
    a8 c8 b8 d8 c4 g4 | % 11
    a'4 g4 <b, f'>4 <c e>4 | % 12
    d8 f8 b,8 d8 c4 r4 | % 13
    d4 c4 b4 r4 | % 14
    f'4 e4 d4 r4 \break | % 15
    a'4 g4 f4 e4 | % 16
    d8 f8 e8 g8 f4. d8 | % 17
    <c e>4 d4 c4 b4 | % 18
    a8 c8 b8 d8 c4 g4 | % 19
    a'4 g4 <b, f'>4 <c e>4 | \barNumberCheck #20
    d8 f8 b,8 d8 c4 r4 \bar "|."
    }

PartPOneVoiceThree =  \relative c' {
    \repeat volta 2 {
        \clef "bass" \time 4/4 \key c \major | % 1
        \clef "treble" c8 g'8 f8 g8 e8 g8 c,8 e8 | % 2
        f8 d8 g8 f8 e8 f8 e8 d8 | % 3
        e8 g8 d8 g8 c,8 g'8 e8 g8 | % 4
        d8 g8 c,8 d8 b8 d8 g,4 }
    \break | % 5
    f'8 g8 e8 g8 d8 g8 fis8 g8 | % 6
    d8 g8 c,8 g'8 b,8 g'8 fis8 g8 | % 7
    f8 g8 e8 g8 d8 g8 c,8 g'8 | % 8
    b,8 g'8 c,8 cis8 d4 g4 | % 9
    c,8 g'8 f8 g8 e8 g8 c,8 e8 \break | \barNumberCheck #10
    f8 d8 g8 f8 e8 f8 e8 c8 | % 11
    f8 c'8 e,8 c'8 d,8 g8 c,8 g'8 | % 12
    f8 a8 g8 f8 e8 g8 c,8 e8 | % 13
    f8 g8 e8 g8 d8 g8 fis8 g8 | % 14
    d8 g8 c,8 g'8 b,8 g'8 fis8 g8 \break | % 15
    f8 g8 e8 g8 d8 g8 c,8 g'8 | % 16
    b,8 g'8 c,8 cis8 d4 g4 | % 17
    c,8 g'8 f8 g8 e8 g8 c,8 e8 | % 18
    f8 d8 g8 f8 e8 f8 e8 c8 | % 19
    f8 c'8 e,8 c'8 d,8 g8 c,8 g'8 | \barNumberCheck #20
    f8 a8 g8 f8 e8 g8 c,4 \bar "|."
    }

PartPOneVoiceTwo =  \relative a' {
    \repeat volta 2 {
        \clef "treble" \time 4/4 \key c \major s1*4 }
    \break s2*7 a8 c8 b8 d8 s1 \break s1*5 \break s1. a8 c8 b8 d8 s1*4
    \bar "|."
    }


% The score definition
\score {
    <<
        
        \new PianoStaff
        <<
            \set PianoStaff.instrumentName = "Piano"
            
            \context Staff = "1" << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPOneVoiceOne" {  \voiceOne \PartPOneVoiceOne }
                \context Voice = "PartPOneVoiceTwo" {  \voiceTwo \PartPOneVoiceTwo }
                >> \context Staff = "2" <<
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPOneVoiceThree" {  \PartPOneVoiceThree }
                >>
            >>
        
        >>
    \layout {}
    % To create MIDI output, uncomment the following line:
    %  \midi {\tempo 4 = 100 }
    }

