%% Tag grobs in LilyPond's SVG output so symbol boxes can be read back (OpenCV spike).
%%   lilypond -dbackend=svg -dno-point-and-click -dinclude-settings=svgtag.ly -o out engraving.ly
%% Every grob of the listed types gets output-attributes: class = grob name, plus data-* detail.
#(define svgtag-names
   '(Rest MultiMeasureRest Accidental AccidentalCautionary Clef CueClef KeySignature KeyCancellation TimeSignature
     Script DynamicText Flag Dots NoteHead Stem Beam BarLine TupletNumber MultiMeasureRestNumber))
#(define (svgtag-val g key default)
   (let ((v (ly:grob-property g key default))) (format #f "~a" v)))
#(define (svgtag-acknowledge engraver grob source-engraver)
   (let* ((nm (grob::name grob)))
     (if (memq nm svgtag-names)
       ;; a callback: read when the SVG is written (after layout), never during engraving
       (ly:grob-set-property! grob 'output-attributes
        (lambda (grob) (list (cons 'class (symbol->string nm))
               (cons 'data-dlog (svgtag-val grob 'duration-log ""))
               (cons 'data-glyph (svgtag-val grob 'glyph-name ""))
               (cons 'data-glyph2 (svgtag-val grob 'glyph ""))
               (cons 'data-frac (svgtag-val grob 'fraction ""))
               (cons 'data-style (svgtag-val grob 'style ""))
               (cons 'data-text (let ((t (ly:grob-property grob 'text #f))) (if (markup? t) (markup->string t) "")))
               (cons 'data-script (let ((s (ly:grob-property grob 'script-stencil #f))) (format #f "~a" (if (pair? s) (cdr s) ""))))
               (cons 'data-dots (svgtag-val grob 'dot-count ""))
               (cons 'data-dir (svgtag-val grob 'direction ""))))))))
#(define (svgtag-engraver context)
   (make-engraver (acknowledgers ((grob-interface engraver grob source-engraver) (svgtag-acknowledge engraver grob source-engraver)))))
\layout { \context { \Score \consists #svgtag-engraver } }
