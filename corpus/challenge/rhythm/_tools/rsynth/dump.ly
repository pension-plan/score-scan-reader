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
        (tc-out ctx "note" (+ 60 (ly:pitch-semitones p)) (tc-dur (ly:event-property ev 'duration)))))
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
\layout {
  \context { \Voice \consists #tc-voice-engraver }
  \context { \Lyrics \consists #tc-voice-engraver }
  \context { \Staff \consists #tc-staff-engraver }
}
