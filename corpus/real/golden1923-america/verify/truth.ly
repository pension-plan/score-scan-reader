\version "2.24.3"
% automatically converted by musicxml2ly from golden1923-america/truth.musicxml
\pointAndClickOff

\header {
    title =  America
    subtitle =  "America (My Country, 'Tis of Thee)"
    copyright =  "Public domain (published 1923, USA)"
    composer =  "Henry Carey (?)"
    poet =  "Samuel Francis Smith"
    encodingsoftware = 
    "hand transcription; compiled by corpus/real/tools/mkxml.py"
    encodingdate =  "2026-11-08"
    source = 
    "The Golden Book of Favorite Songs, rev. ed., Chicago: Hall & McCreary, 1923, p. 3 (Internet Archive goldenbookoffavo00beat_0, leaf n2)"
    }

PartPOneVoiceOne =  \relative g' {
    \clef "treble" \time 3/4 \key g \major | % 1
    g4 g4 a4 | % 2
    fis4. g8 a4 | % 3
    b4 b4 c4 | % 4
    b4. a8 g4 | % 5
    a4 g4 fis4 | % 6
    g2. | % 7
    d'4 d4 d4 \break | % 8
    d4. c8 b4 | % 9
    c4 c4 c4 | \barNumberCheck #10
    c4. b8 a4 | % 11
    b4 c8 b8 a8 g8 | % 12
    b4. c8 d4 | % 13
    e8 c8 b4 a4 | % 14
    g2. \bar "|."
    }

PartPOneVoiceOneLyricsOne =  \lyricmode {\set ignoreMelismata = ##t My
    coun -- "try," "'tis" of "thee," Sweet land of lib -- er -- "ty," Of
    thee I "sing." Land where my fa -- thers "died!" Land of the Pil --
    "grim's" "pride!" From ev -- \skip1 "'ry" \skip1 moun -- tain
    "side," Let\skip1 free -- dom "ring!"
    }

PartPOneVoiceOneLyricsTwo =  \lyricmode {\set ignoreMelismata = ##t My
    na -- tive coun -- "try," "thee," Land of the no -- ble "free," Thy
    name I "love." I love thy rocks and "rills," Thy woods and tem --
    pled "hills;" My heart\skip1 with\skip1 rap -- ture thrills
    Like\skip1 that a -- "bove."
    }

PartPOneVoiceOneLyricsThree =  \lyricmode {\set ignoreMelismata = ##t
    Let mu -- sic swell the "breeze," And ring from all the trees Sweet
    free -- "dom's" "song." Let mor -- tal tongues a -- "wake;" Let all
    that breathe par -- "take;" Let rocks\skip1 their\skip1 si -- lence
    "break," The\skip1 sound pro -- "long."
    }

PartPOneVoiceOneLyricsFour =  \lyricmode {\set ignoreMelismata = ##t Our
    fa -- "thers'" "God," to "Thee," Au -- thor of lib -- er -- "ty," To
    Thee we "sing." Long may our land be bright With free -- "dom's" ho
    -- ly "light;" Pro -- tect\skip1 us\skip1 by Thy "might,"
    Great\skip1 "God," our "King!"
    }

PartPTwoVoiceOne =  \relative d' {
    \clef "treble" \time 3/4 \key g \major | % 1
    d4 d4 e4 | % 2
    d4. e8 fis4 | % 3
    g4 g4 g4 | % 4
    g4. fis8 e4 | % 5
    e4 d4 d4 | % 6
    d2. | % 7
    b'4 b4 b4 \break | % 8
    b4. a8 g4 | % 9
    a4 a4 a4 | \barNumberCheck #10
    a4. g8 fis4 | % 11
    g4 g4 g4 | % 12
    g4. fis8 g4 | % 13
    g4 g4 fis4 | % 14
    g2. \bar "|."
    }

PartPThreeVoiceOne =  \relative b {
    \clef "bass" \time 3/4 \key g \major | % 1
    b4 b4 c4 | % 2
    a4. a8 d4 | % 3
    d4 e4 e4 | % 4
    d4. c8 b4 | % 5
    c4 b4 a4 | % 6
    b2. | % 7
    d4 d4 d4 \break | % 8
    d4. d8 d4 | % 9
    d4 d4 d4 | \barNumberCheck #10
    d4. d8 d4 | % 11
    d4 e8 d8 c8 b8 | % 12
    d4. d8 d4 | % 13
    c8 e8 d4 c4 | % 14
    b2. \bar "|."
    }

PartPFourVoiceOne =  \relative g {
    \clef "bass" \time 3/4 \key g \major | % 1
    g4 g4 c,4 | % 2
    d4. d8 d4 | % 3
    g4 e4 c4 | % 4
    d4. d8 e4 | % 5
    c4 d4 d4 | % 6
    g2. | % 7
    g4 b4 d4 \break | % 8
    g,4. g8 g4 | % 9
    d4 fis4 a4 | \barNumberCheck #10
    d,4. d8 d4 | % 11
    g4 g4 g4 | % 12
    g4. a8 b4 | % 13
    c4 d4 d,4 | % 14
    g2. \bar "|."
    }


% The score definition
\score {
    <<
        
        \new Staff
        <<
            \set Staff.instrumentName = "Soprano"
            
            \context Staff << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPOneVoiceOne" {  \PartPOneVoiceOne }
                \new Lyrics \lyricsto "PartPOneVoiceOne" { \set stanza = "1." \PartPOneVoiceOneLyricsOne }
                \new Lyrics \lyricsto "PartPOneVoiceOne" { \set stanza = "2." \PartPOneVoiceOneLyricsTwo }
                \new Lyrics \lyricsto "PartPOneVoiceOne" { \set stanza = "3." \PartPOneVoiceOneLyricsThree }
                \new Lyrics \lyricsto "PartPOneVoiceOne" { \set stanza = "4." \PartPOneVoiceOneLyricsFour }
                >>
            >>
        \new Staff
        <<
            \set Staff.instrumentName = "Alto"
            
            \context Staff << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPTwoVoiceOne" {  \PartPTwoVoiceOne }
                >>
            >>
        \new Staff
        <<
            \set Staff.instrumentName = "Tenor"
            
            \context Staff << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPThreeVoiceOne" {  \PartPThreeVoiceOne }
                >>
            >>
        \new Staff
        <<
            \set Staff.instrumentName = "Bass"
            
            \context Staff << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPFourVoiceOne" {  \PartPFourVoiceOne }
                >>
            >>
        
        >>
    \layout {}
    % To create MIDI output, uncomment the following line:
    %  \midi {\tempo 4 = 100 }
    }

