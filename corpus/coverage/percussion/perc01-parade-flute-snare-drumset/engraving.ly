\version "2.24.0"
#(set-global-staff-size 20)
\header {
  title = "Village Parade"
  composer = "Coverage suite (2026)"
  tagline = ##f
}
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  top-margin = 14\mm
  bottom-margin = 14\mm
  left-margin = 18\mm
  right-margin = 16\mm
  ragged-bottom = ##t
  ragged-last-bottom = ##t
  system-system-spacing.basic-distance = #16
}
#(define snare-line-style (alist->hash-table '((snare () #f 0))))
\score {
  <<
    \new Staff = "fl" \with { instrumentName = "Flute" shortInstrumentName = "Fl." midiInstrument = "flute" } {
      \autoBeamOff \tempo "Marziale" 4 = 112 \numericTimeSignature \time 4/4 \key g \major \clef treble
      \stemDown d''4\mf \stemDown b'8[ \stemDown c''8] \stemDown d''4 \stemUp g'4 |
      \stemDown a'8[ \stemDown b'8 \stemDown c''8 \stemDown a'8] \stemDown b'2 |
      \stemDown c''4 \stemUp a'8[ \stemUp b'8] \stemDown c''4 \stemUp fis'4 |
      \stemUp g'2 r2 |
      \break \stemDown b'8[\< \stemDown c''8 \stemDown d''8 \stemDown b'8] \stemDown c''4 \stemUp a'4\! |
      \stemDown d''4\f \stemDown c''8[ \stemDown b'8] \stemUp a'2 |
      \stemUp b'8[ \stemUp a'8 \stemUp g'8 \stemUp a'8] \stemDown b'4 \stemUp a'4 |
      \stemUp g'2. r4 \bar "|." |
    }
    \new DrumStaff = "sd" \with { instrumentName = "Snare Drum" shortInstrumentName = "S.D." drumStyleTable = #snare-line-style \override StaffSymbol.line-count = #1 } <<
      \new DrumVoice = "sdv1" \drummode { \autoBeamOff \numericTimeSignature \time 4/4
      \stemUp sn8[\f \stemUp sn8] \stemUp sn16[ \stemUp sn16 \stemUp sn16 \stemUp sn16] \stemUp sn4-> \stemUp sn4 |
      \stemUp sn4 \stemUp sn8[ \stemUp sn8] \stemUp sn4 r4 |
      \stemUp sn8[ \stemUp sn8] \stemUp sn16[ \stemUp sn16 \stemUp sn8] \stemUp sn4-> r4 |
      \stemUp sn16[ \stemUp sn16 \stemUp sn16 \stemUp sn16] \stemUp sn16[ \stemUp sn16 \stemUp sn16 \stemUp sn16] \stemUp sn4-> r4 |
      \break \stemUp sn8[ \stemUp sn8] \stemUp sn16[ \stemUp sn16 \stemUp sn16 \stemUp sn16] \stemUp sn4-> \stemUp sn4 |
      \stemUp sn4 \stemUp sn8[ \stemUp sn8] \stemUp sn4 r4 |
      \stemUp sn8[ \stemUp sn8] \stemUp sn16[ \stemUp sn16 \stemUp sn8] \stemUp sn4-> r4 |
      \stemUp sn4-> \stemUp sn4 \stemUp sn2-> \bar "|." |
      }
    >>
    \new DrumStaff = "ds" \with { instrumentName = "Drum Set" shortInstrumentName = "D.S." drumStyleTable = #drums-style } <<
      \new DrumVoice = "dsv1" \drummode { \voiceOne \autoBeamOff \numericTimeSignature \time 4/4
      \stemUp hh8[\mp \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] |
      \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] |
      \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] |
      \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] \stemUp <hh sn>4 r4 |
      \break \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] |
      \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] |
      \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] |
      \stemUp hh8[ \stemUp hh8 \stemUp <hh sn>8 \stemUp hh8] \stemUp <hh sn>2-> \bar "|." |
      }
      \new DrumVoice = "dsv2" \drummode { \voiceTwo \autoBeamOff \numericTimeSignature \time 4/4
      \stemDown bd4 r4 \stemDown bd4 r4 |
      \stemDown bd4 r4 \stemDown bd4 r4 |
      \stemDown bd4 r4 \stemDown bd4 r4 |
      \stemDown bd4 \stemDown bd4 \stemDown bd4 r4 |
      \break \stemDown bd4 r4 \stemDown bd4 r4 |
      \stemDown bd4 r4 \stemDown bd4 r4 |
      \stemDown bd4 r4 \stemDown bd4 r4 |
      \stemDown bd4 r4 \stemDown bd2 \bar "|." |
      }
    >>
  >>
  \layout { \context { \Score \remove "Bar_number_engraver" } }
  \midi { }
}
