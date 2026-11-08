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
%% [coverage/rests] post-layout records: vertical position of every Rest / MultiMeasureRest
%% (staff-position and Y extent relative to the staff symbol, in staff spaces) and the
%% direction of every Stem.  The moment / bar / position are captured when the grob is
%% created; the values are written from an after-line-breaking callback (chained with any
%% existing callback), i.e. after collisions and beams are resolved.
#(define (tc-num x) (if (number? x) (exact->inexact x) "?"))
#(define (tc-out-at ctx-name ctx-id mom bn mp . vals)
   (if (not tc-port)
       (set! tc-port (open-file (string-append (ly:parser-output-name) ".events") "w")))
   (display (string-join
             (append (list ctx-name ctx-id (tc-str (ly:moment-main mom)) (tc-str (ly:moment-grace mom))
                           (tc-str bn) (tc-str (if (ly:moment? mp) (ly:moment-main mp) "?")))
                     (map tc-str vals))
             "\t")
            tc-port)
   (newline tc-port)
   (force-output tc-port))
#(define (tc-ystaff grob)
   (let* ((ss (ly:grob-object grob 'staff-symbol)))
     (if (ly:grob? ss)
         (let* ((com (ly:grob-common-refpoint grob ss Y))
                (ext (ly:grob-extent grob com Y))
                (sy (ly:grob-relative-coordinate ss com Y)))
           (list (tc-num (- (car ext) sy)) (tc-num (- (cdr ext) sy))))
         (list "?" "?"))))
#(define (tc-chain grob proc)
   (let ((old (ly:grob-property grob 'after-line-breaking)))
     (ly:grob-set-property! grob 'after-line-breaking
       (lambda (g) (if (procedure? old) (old g)) (proc g)))))
#(define (tc-layout-capture ctx grob kind)
   (let ((cn (tc-str (ly:context-name ctx))) (ci (tc-str (ly:context-id ctx)))
         (mom (ly:context-current-moment ctx))
         (bn (ly:context-property ctx 'currentBarNumber))
         (mp (ly:context-property ctx 'measurePosition)))
     (tc-chain grob
       (lambda (g)
         (cond
          ((eq? kind 'rest)
           (apply tc-out-at cn ci mom bn mp "restpos" (tc-num (ly:grob-property g 'duration-log))
                  (tc-num (ly:grob-property g 'staff-position)) (tc-ystaff g)))
          ((eq? kind 'mmrest)
           (apply tc-out-at cn ci mom bn mp "mmrestpos" (tc-num (ly:grob-property g 'staff-position))
                  (tc-ystaff g)))
          ((eq? kind 'stem)
           (tc-out-at cn ci mom bn mp "stem" (tc-num (ly:grob-property g 'duration-log))
                      (tc-num (ly:grob-property g 'direction)))))))))
#(define (tc-voice-engraver ctx)
   (make-engraver
    (acknowledgers
     ((rest-interface engraver grob source-engraver)
      (tc-layout-capture ctx grob (if (grob::has-interface grob 'multi-measure-rest-interface) 'mmrest 'rest)))
     ((stem-interface engraver grob source-engraver) (tc-layout-capture ctx grob 'stem)))
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
