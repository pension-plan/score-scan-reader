%% Verification-only render: every system starts with a tagged bar number "QQ<n>QQ" that
%% pdftotext can read per page (forced breaks make the system layout identical to engraving.ly).
\layout { \context { \Score
  barNumberFormatter = #(lambda (barnum measure-pos alt-number context) (make-simple-markup (format #f "QQ~aQQ" barnum)))
  \override BarNumber.break-visibility = ##(#f #f #t)
  barNumberVisibility = #all-bar-numbers-visible
} }
