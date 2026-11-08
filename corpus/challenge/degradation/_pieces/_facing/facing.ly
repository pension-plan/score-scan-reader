\version "2.24.0"
% Facing (verso) page for the 2-up spread variants of single-page pieces.
% Text only - NO music.  Original text written for this corpus, CC0-1.0.
\paper {
  #(set-paper-size "a4")
  property-defaults.fonts.serif = "TeX Gyre Schola"
  top-margin = 25\mm
  left-margin = 22\mm
  right-margin = 22\mm
  markup-markup-spacing.basic-distance = #4
}
\header { tagline = ##f }
\markup \fill-line { \fontsize #4 \bold "Notes on the Music" }
\markup \vspace #1.5
\markup \justify {
  The pieces collected in this little book are intended for singing and playing at home, in
  school and in small congregations. Most of them can be learned in a single evening, and none
  requires more than an ordinary voice or a modest technique at the keyboard. Where a tune is
  traditional, the setting printed here has been made new; where a text is old, its spelling has
  been left as the poet wrote it.
}
\markup \vspace #1
\markup \justify {
  Singers reading from a closed score should remember that two parts share each staff: the upper
  part has its stems pointing up and the lower part has its stems pointing down. When the two
  parts meet on the same note, a single note head serves for both. Words are printed between the
  staves and belong to every part unless they are marked otherwise.
}
\markup \vspace #1
\markup \justify {
  Pianists will find that the pieces lie comfortably under the hands. The pedal may be used
  freely to join the harmonies, but it should be changed with every new chord, and never so
  heavily that the melody is lost. A slow practice tempo is recommended at first; the marked
  dynamics are suggestions rather than commands.
}
\markup \vspace #1
\markup \justify {
  Teachers are welcome to copy these pages for their own students. The editor would be glad to
  hear of any misprints, which will be corrected in a later printing.
}
\markup \vspace #3
\markup \fill-line { \italic "Contents" }
\markup \vspace #0.5
\markup \fill-line { \column {
  \line { "Amazing Grace" \hspace #30 "13" }
  \line { "Who Has Seen the Wind?" \hspace #22 "14" }
  \line { "Andantino" \hspace #38 "15" }
  \line { "Theme and Variation" \hspace #26 "16" }
} }
\markup \vspace #6
\markup \fill-line { "- 12 -" }
