%% Event dump for truth-vs-engraving verification (rhythm challenge corpus).
%% Included with  lilypond -dinclude-settings=dump.ly  ; writes <output>.events
%% One tab-separated line per music event heard by a Voice / Lyrics context and per
%% time signature grob created in a Staff:
%%   ctxtype ctxid moment-main moment-grace currentBarNumber measurePosition kind ...
#(define tc-port #f)
#(define (tc-str x) (format #f "~a" x))
#(define (tc-out ctx . vals)
   (if (not tc-port)
       (set! tc-port (open-file (string-append (ly:parser-output-name) ".events") "w")))
   (let* ((m (ly:context-current-moment ctx))
          (mp (ly:context-property ctx 'measurePosition))
          (bn (ly:context-property ctx 'currentBarNumber)))
     (display (string-join
               (append (list (tc-str (ly:context-name ctx)) (tc-str (ly:context-id ctx))
                             (tc-str (ly:moment-main m)) (tc-str (ly:moment-grace m))
                             (tc-str bn) (tc-str (if (ly:moment? mp) (ly:moment-main mp) "?")))
                       (map tc-str vals))
               "\t")
              tc-port)
     (newline tc-port)
     (force-output tc-port)))
#(define (tc-dur d)
   (format #f "~a ~a ~a" (ly:duration-log d) (ly:duration-dot-count d) (ly:duration-scale d)))
#(define (tc-voice-engraver ctx)
   (make-engraver
    (listeners
     ((note-event engraver ev)
      (let ((p (ly:event-property ev 'pitch)))
        (tc-out ctx "note" (+ 60 (ly:pitch-semitones p)) (tc-dur (ly:event-property ev 'duration)))
        ;; coverage/time: a tie written inside a chord (<c'~ e'>) is an articulation of the note
        ;; event and is not heard as a separate tie-event
        (for-each (lambda (a)
                    (if (ly:in-event-class? a 'tie-event)
                        (tc-out ctx "notetie" (+ 60 (ly:pitch-semitones p)))))
                  (ly:event-property ev 'articulations '()))))
     ((rest-event engraver ev)
      (tc-out ctx "rest" (tc-dur (ly:event-property ev 'duration))))
     ((multi-measure-rest-event engraver ev)
      (tc-out ctx "mmrest" (tc-dur (ly:event-property ev 'duration))))
     ((multi-measure-articulation-event engraver ev)
      (tc-out ctx "mmartic" (ly:event-property ev 'articulation-type)))
     ((tie-event engraver ev) (tc-out ctx "tie"))
     ((beam-event engraver ev) (tc-out ctx "beam" (ly:event-property ev 'span-direction)))
     ((slur-event engraver ev) (tc-out ctx "slur" (ly:event-property ev 'span-direction)))
     ((articulation-event engraver ev) (tc-out ctx "artic" (ly:event-property ev 'articulation-type)))
     ((lyric-event engraver ev) (tc-out ctx "lyric" (ly:event-property ev 'text)))
     ((hyphen-event engraver ev) (tc-out ctx "hyphen"))
     ((extender-event engraver ev) (tc-out ctx "extender")))))
#(define (tc-staff-engraver ctx)
   (make-engraver
    (acknowledgers
     ((time-signature-interface engraver grob source-engraver)
      (let ((fr (ly:grob-property grob 'fraction)))
        (tc-out ctx "timesig" (car fr) (cdr fr) (ly:grob-property grob 'style)))))))
%% coverage/time: every printed TupletBracket (stencil callback wraps the default print):
%%   Grob tuplets <moment-main of left bound> <grace> 0 ? bracket <numerator> <denominator> <visible 0/1>
#(define (tc-raw . vals)
   (if (not tc-port)
       (set! tc-port (open-file (string-append (ly:parser-output-name) ".events") "w")))
   (display (string-join (map tc-str vals) "\t") tc-port)
   (newline tc-port)
   (force-output tc-port))
#(define (tc-bracket-print grob)
   (let* ((st (ly:tuplet-bracket::print grob))
          (ev (event-cause grob))
          (lb (ly:spanner-bound grob LEFT))
          (col (and (ly:grob? lb) (ly:item? lb) (ly:item-get-column lb)))
          (w (and col (ly:grob-property col 'when #f))))
     (tc-raw "Grob" "tuplets"
             (if (ly:moment? w) (ly:moment-main w) "?")
             (if (ly:moment? w) (ly:moment-grace w) "?")
             0 "?" "bracket"
             (if ev (ly:event-property ev 'numerator) "?")
             (if ev (ly:event-property ev 'denominator) "?")
             (if (and (ly:stencil? st) (not (ly:stencil-empty? st))) 1 0))
     st))
\layout {
  \context { \Voice \consists #tc-voice-engraver \override TupletBracket.stencil = #tc-bracket-print }
  \context { \Lyrics \consists #tc-voice-engraver }
  \context { \Staff \consists #tc-staff-engraver }
}
