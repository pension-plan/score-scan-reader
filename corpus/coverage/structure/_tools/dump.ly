%% Event + grob dump for truth-vs-engraving verification (coverage corpus, structure family).
%% Based on corpus/challenge/rhythm/_tools/rsynth/dump.ly, extended with structure grobs.
%% Included with  lilypond -dinclude-settings=dump.ly ; writes <output>.events
%% One tab-separated line per record:
%%   ctxtype ctxid moment-main moment-grace currentBarNumber measurePosition kind args...
#(define tc-port #f)
#(define (tc-str x) (format #f "~a" x))
#(define (tc-text x) (if (markup? x) (markup->string x) (tc-str x)))
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
     ((tie-event engraver ev) (tc-out ctx "tie"))
     ((beam-event engraver ev) (tc-out ctx "beam" (ly:event-property ev 'span-direction)))
     ((slur-event engraver ev) (tc-out ctx "slur" (ly:event-property ev 'span-direction)))
     ((articulation-event engraver ev) (tc-out ctx "artic" (ly:event-property ev 'articulation-type)))
     ((absolute-dynamic-event engraver ev) (tc-out ctx "dyn" (ly:event-property ev 'text)))
     ((crescendo-event engraver ev) (tc-out ctx "cresc" (ly:event-property ev 'span-direction)))
     ((decrescendo-event engraver ev) (tc-out ctx "decresc" (ly:event-property ev 'span-direction)))
     ((sustain-event engraver ev) (tc-out ctx "sustain" (ly:event-property ev 'span-direction)))
     ((text-script-event engraver ev) (tc-out ctx "textscript" (tc-text (ly:event-property ev 'text))))
     ((lyric-event engraver ev) (tc-out ctx "lyric" (ly:event-property ev 'text)))
     ((hyphen-event engraver ev) (tc-out ctx "hyphen"))
     ((extender-event engraver ev) (tc-out ctx "extender")))))
#(define (tc-staff-engraver ctx)
   (make-engraver
    (acknowledgers
     ((time-signature-interface engraver grob source-engraver)
      (let ((fr (ly:grob-property grob 'fraction)))
        (tc-out ctx "timesig" (car fr) (cdr fr) (ly:grob-property grob 'style))))
     ((clef-interface engraver grob source-engraver)
      (if (and (eq? (grob::name grob) 'Clef) (eq? #t (ly:grob-property-data grob 'non-default)))
          (tc-out ctx "clef" (ly:context-property ctx 'clefGlyph) (ly:context-property ctx 'clefPosition)
                  (ly:context-property ctx 'clefTransposition))))
     ((key-signature-interface engraver grob source-engraver)
      (if (and (eq? (grob::name grob) 'KeySignature) (eq? #t (ly:grob-property-data grob 'non-default)))
          (let ((alist (ly:grob-property grob 'alteration-alist)))
            (tc-out ctx "key"
                    (apply + (map (lambda (x) (let ((a (cdr x))) (if (> a 0) 1 (if (< a 0) -1 0)))) alist)))))))))
#(define (tc-score-engraver ctx)
   (define voltas '())
   (make-engraver
    ((finalize engraver)
     (for-each (lambda (g)
                 (let ((l (ly:spanner-bound g LEFT)) (r (ly:spanner-bound g RIGHT)))
                   (tc-out ctx "voltaspan" (tc-text (ly:grob-property-data g 'text))
                           (ly:moment-main (ly:grob-property (ly:item-get-column l) 'when))
                           (ly:moment-main (ly:grob-property (ly:item-get-column r) 'when)))))
               (reverse voltas)))
    (acknowledgers
     ((grob-interface engraver grob source-engraver)
      (let* ((name (grob::name grob))
             (sid (tc-str (ly:context-id (ly:translator-context source-engraver)))))
        (cond
         ((eq? name 'BarLine) (tc-out ctx "barline" sid (ly:grob-property-data grob 'glyph)))
         ((eq? name 'VoltaBracket)
          (set! voltas (cons grob voltas))
          (tc-out ctx "volta" (tc-text (ly:grob-property-data grob 'text))))
         ((memq name '(SegnoMark CodaMark)) (tc-out ctx (tc-str name)))
         ((memq name '(TextMark RehearsalMark))
          (let ((ev (event-cause grob)))
            (tc-out ctx (tc-str name) (tc-text (ly:event-property ev 'text))
                    (ly:event-property ev 'horizontal-direction))))
         ((eq? name 'MetronomeMark)
          (let ((ev (event-cause grob)))
            (tc-out ctx "MetronomeMark" (tc-text (ly:event-property ev 'text))
                    (ly:event-property ev 'metronome-count))))
         ((eq? name 'Stem)
          (let ((d (ly:grob-property-data grob 'direction)))
            (if (number? d) (tc-out ctx "stem" sid d))))
         (else #f)))))
    (listeners
     ((line-break-event engraver ev) (tc-out ctx "break" (ly:event-property ev 'break-permission)))
     ((page-break-event engraver ev) (tc-out ctx "pagebreak" (ly:event-property ev 'break-permission))))))
\layout {
  \context { \Voice \consists #tc-voice-engraver }
  \context { \Lyrics \consists #tc-voice-engraver }
  \context { \Staff \consists #tc-staff-engraver }
  \context { \Score \consists #tc-score-engraver }
}
