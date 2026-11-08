%% Event + grob dump for truth-vs-engraving verification (coverage/notes corpus).
%% Copied from corpus/challenge/rhythm/_tools/rsynth/dump.ly and extended with:
%%   * tremolo-event / tremolo-span-event listeners
%%   * a Stem / NoteHead after-line-breaking logger (final layout: stem direction, beam
%%     counts left/right, flag, stem-tremolo strokes, head count, staff position, font size)
%%     attributed to the Voice that created the grob (acknowledger + hash table)
%%   * a Staff acknowledger for printed accidentals (pitch of the cause event, alteration)
%% Included with  lilypond -dinclude-settings=dump.ly  ; writes <output>.events
#(define tc-port #f)
#(define tc-grob-voice (make-hash-table 4096))
#(define (tc-str x) (format #f "~a" x))
#(define (tc-port-get)
   (if (not tc-port)
       (set! tc-port (open-file (string-append (ly:parser-output-name) ".events") "w")))
   tc-port)
#(define (tc-line vals)
   (let ((p (tc-port-get)))
     (display (string-join (map tc-str vals) "\t") p)
     (newline p)
     (force-output p)))
#(define (tc-out ctx . vals)
   (let* ((m (ly:context-current-moment ctx))
          (mp (ly:context-property ctx 'measurePosition))
          (bn (ly:context-property ctx 'currentBarNumber)))
     (tc-line (append (list (ly:context-name ctx) (ly:context-id ctx)
                            (ly:moment-main m) (ly:moment-grace m)
                            bn (if (ly:moment? mp) (ly:moment-main mp) "?"))
                      vals))))
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
     ((tremolo-event engraver ev) (tc-out ctx "tremolo" (ly:event-property ev 'tremolo-type)))
     ((tremolo-span-event engraver ev) (tc-out ctx "tremspan" (ly:event-property ev 'span-direction)))
     ((lyric-event engraver ev) (tc-out ctx "lyric" (ly:event-property ev 'text)))
     ((hyphen-event engraver ev) (tc-out ctx "hyphen"))
     ((extender-event engraver ev) (tc-out ctx "extender")))
    (acknowledgers
     ((stem-interface engraver grob source-engraver)
      (hashq-set! tc-grob-voice grob (ly:context-id ctx)))
     ((note-head-interface engraver grob source-engraver)
      (hashq-set! tc-grob-voice grob (ly:context-id ctx))))))
#(define (tc-staff-engraver ctx)
   (make-engraver
    (acknowledgers
     ((time-signature-interface engraver grob source-engraver)
      (let ((fr (ly:grob-property grob 'fraction)))
        (tc-out ctx "timesig" (car fr) (cdr fr) (ly:grob-property grob 'style))))
     ((accidental-interface engraver grob source-engraver)
      (let* ((ev (event-cause grob))
             (p (and ev (ly:event-property ev 'pitch #f))))
        (tc-out ctx "accidental" (if p (+ 60 (ly:pitch-semitones p)) "?")
                (if p (ly:pitch-steps p) "?")
                (ly:grob-property grob 'alteration)
                (grob::name grob)))))))
#(define (tc-beam-counts g)
   (let ((b (ly:grob-property g 'beaming)))
     (if (pair? b)
         (list (if (list? (car b)) (length (car b)) 0) (if (list? (cdr b)) (length (cdr b)) 0))
         (list 0 0))))
#(define (tc-grob-log g)
   (let* ((w (grob::when g))
          (nm (grob::name g))
          (vid (hashq-ref tc-grob-voice g "?")))
     (cond
      ((eq? nm 'Stem)
       (let* ((heads (ly:grob-object g 'note-heads))
              (nh (if (ly:grob-array? heads) (ly:grob-array-length heads) 0))
              (tf (ly:grob-object g 'tremolo-flag))
              (bc (tc-beam-counts g)))
         (tc-line (list "GROB" vid (ly:moment-main w) (ly:moment-grace w) "stem"
                        (ly:grob-property g 'direction)
                        (ly:grob-property g 'duration-log)
                        (if (ly:grob? (ly:grob-object g 'beam)) 1 0)
                        (car bc) (cadr bc)
                        (if (ly:grob? tf) (ly:grob-property tf 'flag-count) 0)
                        nh))))
      ((eq? nm 'NoteHead)
       (let ((fs (ly:grob-property g 'font-size)))
         (tc-line (list "GROB" vid (ly:moment-main w) (ly:moment-grace w) "head"
                        (ly:grob-property g 'staff-position)
                        (ly:grob-property g 'duration-log)
                        (if (number? fs) fs 0))))))))
\layout {
  \context { \Voice \consists #tc-voice-engraver
    \override Stem.after-line-breaking = #tc-grob-log
    \override NoteHead.after-line-breaking = #tc-grob-log }
  \context { \CueVoice \consists #tc-voice-engraver
    \override Stem.after-line-breaking = #tc-grob-log
    \override NoteHead.after-line-breaking = #tc-grob-log }
  \context { \Lyrics \consists #tc-voice-engraver }
  \context { \Staff \consists #tc-staff-engraver }
}
