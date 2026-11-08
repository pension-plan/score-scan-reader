\version "2.24.3"
#(set-global-staff-size 19)
% automatically converted by musicxml2ly from /Users/d.sloane/music/corpus/synthetic/joplin-maple-leaf-piano/truth.musicxml
\pointAndClickOff



\header {
    title =  "Maple Leaf Rag"
    composer =  "Scott Joplin (1899)"
    encodingsoftware =  "synthetic-scan corpus builder"
    encodingdate =  "2026-11-08"
    }

\header {
  tagline = ##f
  title = "Maple Leaf Rag"
  composer = "Scott Joplin"
}
\paper {
  #(set-paper-size "letter")
  property-defaults.fonts.serif = "C059"
}
\layout {
    \context { \Score
        skipBars = ##t
        autoBeaming = ##t
        }
    }
PartPVoiceOne =  \relative as' {
    \clef "treble" \time 2/4 \key as \major \partial 8 r8 \repeat volta
    2 {
        | % 1
        r16 as16 <es es'>16 as16 c16 <es, es'>8 g16 | % 2
        <es es'>16 g16 bes16 <es, es'>16 ~ ~ <es es'>4 | % 3
        r16 as16 <es es'>16 as16 c16 <es, es'>8 g16 | % 4
        <es es'>16 g16 bes16 <es, es'>16 ~ ~ <es es'>8 r16 <es es'>16 | % 5
        r16 as16 ces16 <fes, fes'>16 r16 <es es'>16 r16 <es es'>16 | % 6
        r16 as16 ces16 <fes, fes'>16 r16 <es es'>16 r8 | % 7
        R2 | % 8
        r16 as16 ( ces16 ) as'16 r16 as16 ( ces16 ) as'16 | % 9
        <as, as'>8 _\f <as as'>8 <as as'>8 <as as'>16 <as as'>16 ~ ~ |
        \barNumberCheck #10
        <as as'>16 es'16 f16 c16 es16 <as, f'>8 <fes as>16 ~ ~ | % 11
        <fes as>16 bes16 <fes ces'>16 as16 bes16 <es, c'>8 as16 | % 12
        <es c'>16 as16 <es bes'>8 <es as>8 r16 <as, as'>16 ~ ~ | % 13
        <as as'>8 <as as'>8 <as as'>8 <as as'>16 <as as'>16 ~ ~ | % 14
        <as as'>16 es'16 <as, f'>16 c16 es16 <as, f'>8 <fes as>16 ~ ~ | % 15
        <fes as>16 bes16 <fes ces'>16 as16 bes16 <es, c'>8 as16 | % 16
        <es c'>16 as16 <es bes'>8 <es as>8 r8 }
    | % 17
    <es c'>16 as16 <es bes'>8 <es as>8 r8 | % 18
    r16 g'16 <es es'>16 g16 bes16 <d, d'>8 g16 | % 19
    <des des'>16 g16 bes16 <c, c'>16 <c c'>16 es16 <bes bes'>16 es16
    \bar "|."
    }

PartPVoiceFive =  \relative es, {
    \clef "bass" \time 2/4 \key as \major \partial 8 <es es'>8 \repeat
    volta 2 {
        | % 1
        <as as'>8 <es' as c>8 <es as c>8 <a, a'>8 | % 2
        <bes bes'>8 <es g des'>8 <es g des'>8 <es, es'>8 | % 3
        <as as'>8 <es' as c>8 <es as c>8 <a, a'>8 | % 4
        <bes bes'>8 <es g des'>8 <es g des'>8 <es, es'>8 | % 5
        <fes fes'>4 <es es'>8 <es es'>8 | % 6
        <fes fes'>4 <es es'>8 r8 | % 7
        r16 \stemUp as16 ( \stemUp ces16 ) \stemUp as'16 r16 \stemUp as16
        ( \stemUp ces16 ) \stemUp as'16 | % 8
        as,8 r8 as'8 r8 | % 9
        \clef "treble" <d, f as b>8 <d f as b>8 <d f as b>8 <d f as b>8
        | \barNumberCheck #10
        <es as c>8 <es as c>8 <es as c>8 <es as c>8 | % 11
        <fes as ces>8 <fes as ces>8 <es as c>8 <es as c>8 | % 12
        <es as c>8 <es g des'>8 <as c>8 r8 | % 13
        \clef "bass" <d,, f as b>8 <d f as b>8 <d f as b>8 <d f as b>8 | % 14
        <es as c>8 <es as c>8 <es as c>8 <es as c>8 | % 15
        <fes as ces>8 <fes as ces>8 <es as c>8 <es as c>8 | % 16
        <es g c>8 <es g des'>8 <as c>8 <es, es'>8 }
    | % 17
    <es' as c>8 <es g des'>8 <as c>8 <a, a'>8 | % 18
    <bes bes'>16 r16 <es g des'>8 <es, es'>8 <es' g des'>8 | % 19
    <bes bes'>8 <es g des'>8 <es, es'>8 <g g'>8 \bar "|."
    }

PartPVoiceSix =  \relative as,, {
    \clef "bass" \time 2/4 \key as \major \partial 8 s8 \repeat volta 2
    {
        s1*3 | % 7
        \stemDown as8 _\mf r8 \stemDown as'8 r8 s2 | % 9
        \clef "treble" s1*2 | % 13
        \clef "bass" s1*2 }
    s1. \bar "|."
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
                \context Voice = "PartPVoiceOne" {  \PartPVoiceOne }
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
                \context Voice = "PartPVoiceOne" {  \PartPVoiceOne }
                >> \context Staff = "2" <<
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPVoiceFive" {  \voiceOne \PartPVoiceFive }
                \context Voice = "PartPVoiceSix" {  \voiceTwo \PartPVoiceSix }
                >>
            >>
        
        >>
    \midi { \tempo 4 = 100 \context { \Staff \remove "Staff_performer" } \context { \Voice \consists "Staff_performer" } }
    }

