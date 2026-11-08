%% Event + grob dump for truth-vs-engraving verification (coverage/marks corpus).
%% Extends corpus/challenge/rhythm/_tools/rsynth/dump.ly.
%% Included with  lilypond -dinclude-settings=dump.ly ; writes <output>.events with one
%% tab-separated line per record:
%%   ctxtype ctxid moment-main moment-grace currentBarNumber measurePosition kind args...
%% Voice: every music event (notes with the fingerings inside chords, rests, ties, beams,
%%   slurs, articulations/ornaments/fermatas, dynamics, hairpins, pedal, fingering, text
%%   scripts, arpeggios, breath marks) and, at the end, every Stem, Script (articulation, ornament,
%%   fermata) and Fingering grob with its final direction.
%% ChordNames: the pitches of every chord.  Score: tempo and mark events, and one 'G' line per
%%   grob created anywhere in the score (name, creating context id, text / script glyph).
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
#(define (tc-mk x) (if (markup? x) (markup->string x) (tc-str x)))
#(define (tc-inner ev)
   (string-join
    (map (lambda (a)
           (format #f "~a:~a:~a" (car (ly:event-property a 'class))
                   (ly:event-property a 'digit) (ly:event-property a 'direction)))
         (ly:event-property ev 'articulations))
    ","))
#(define (tc-voice-engraver ctx)
   (let ((stems '()) (scripts '()) (fingers '()))
     (make-engraver
      (listeners
       ((note-event engraver ev)
        (let ((p (ly:event-property ev 'pitch)))
          (tc-out ctx "note" (+ 60 (ly:pitch-semitones p)) (tc-dur (ly:event-property ev 'duration))
                  (tc-inner ev))))
       ((rest-event engraver ev)
        (tc-out ctx "rest" (tc-dur (ly:event-property ev 'duration))))
       ((multi-measure-rest-event engraver ev)
        (tc-out ctx "mmrest" (tc-dur (ly:event-property ev 'duration))))
       ((tie-event engraver ev) (tc-out ctx "tie"))
       ((beam-event engraver ev) (tc-out ctx "beam" (ly:event-property ev 'span-direction)))
       ((slur-event engraver ev) (tc-out ctx "slur" (ly:event-property ev 'span-direction)))
       ((articulation-event engraver ev)
        (tc-out ctx "artic" (ly:event-property ev 'articulation-type) (ly:event-property ev 'direction)))
       ((absolute-dynamic-event engraver ev) (tc-out ctx "dyn" (ly:event-property ev 'text)))
       ((crescendo-event engraver ev) (tc-out ctx "cresc" (ly:event-property ev 'span-direction)))
       ((decrescendo-event engraver ev) (tc-out ctx "decresc" (ly:event-property ev 'span-direction)))
       ((sustain-event engraver ev) (tc-out ctx "sustain" (ly:event-property ev 'span-direction)))
       ((fingering-event engraver ev)
        (tc-out ctx "finger" (ly:event-property ev 'digit) (ly:event-property ev 'direction)))
       ((text-script-event engraver ev)
        (tc-out ctx "text" (tc-mk (ly:event-property ev 'text)) (ly:event-property ev 'direction)))
       ((arpeggio-event engraver ev) (tc-out ctx "arpeggio"))
       ((breathing-event engraver ev) (tc-out ctx "breathe")))
      (acknowledgers
       ((stem-interface engraver grob source-engraver)
        (set! stems (cons (cons grob (ly:moment-main (ly:context-current-moment ctx))) stems)))
       ((script-interface engraver grob source-engraver)
        (if (eq? (grob::name grob) 'Script)
            (set! scripts (cons (cons grob (ly:moment-main (ly:context-current-moment ctx))) scripts))))
       ((finger-interface engraver grob source-engraver)
        (set! fingers (cons (cons grob (ly:moment-main (ly:context-current-moment ctx))) fingers))))
      ((finalize engraver)
       (for-each
        (lambda (sm)
          (let ((c (event-cause (car sm))))
            (tc-out ctx "scriptdir" (cdr sm) (ly:event-property c 'articulation-type)
                    (ly:grob-property (car sm) 'direction))))
        (reverse scripts))
       (for-each
        (lambda (sm)
          (let ((c (event-cause (car sm))))
            (tc-out ctx "fingerdir" (cdr sm) (ly:event-property c 'digit) (ly:grob-property (car sm) 'direction))))
        (reverse fingers))
       (for-each
        (lambda (sm)
          (let* ((st (car sm))
                 (heads (ly:grob-object st 'note-heads))
                 (ps (if (ly:grob-array? heads)
                         (map (lambda (h) (+ 60 (ly:pitch-semitones (ly:event-property (event-cause h) 'pitch))))
                              (ly:grob-array->list heads))
                         '())))
            (tc-out ctx "stem" (cdr sm) (ly:grob-property st 'duration-log) (ly:grob-property st 'direction)
                    (string-join (map tc-str ps) " "))))
        (reverse stems))))))
#(define (tc-chord-engraver ctx)
   (make-engraver
    (listeners
     ((note-event engraver ev)
      (tc-out ctx "cnote" (+ 60 (ly:pitch-semitones (ly:event-property ev 'pitch))))))))
#(define (tc-score-engraver ctx)
   (make-engraver
    (listeners
     ((tempo-change-event engraver ev)
      (tc-out ctx "tempo" (tc-mk (ly:event-property ev 'text))
              (let ((u (ly:event-property ev 'tempo-unit))) (if (ly:duration? u) (tc-dur u) "-"))
              (ly:event-property ev 'metronome-count)))
     ((mark-event engraver ev) (tc-out ctx "mark" (ly:event-property ev 'label))))
    (acknowledgers
     ((grob-interface engraver grob source-engraver)
      (let ((nm (grob::name grob))
            (cid (ly:context-id (ly:translator-context source-engraver))))
        (cond
         ((eq? nm 'Script)
          (tc-out ctx "G" nm cid (cdr (ly:grob-property grob 'script-stencil))))
         ((eq? nm 'Accidental)
          (let ((c (event-cause grob)))
            (tc-out ctx "G" nm cid
                    (if (ly:stream-event? c) (+ 60 (ly:pitch-semitones (ly:event-property c 'pitch))) "?")
                    (ly:grob-property grob 'alteration))))
         ((memq nm '(DynamicText TextScript ChordName Fingering MetronomeMark RehearsalMark SustainPedal))
          (tc-out ctx "G" nm cid (tc-mk (ly:grob-property grob 'text))))
         (else (tc-out ctx "G" nm cid))))))))
\layout {
  \context { \Voice \consists #tc-voice-engraver }
  \context { \ChordNames \consists #tc-chord-engraver }
  \context { \Score \consists #tc-score-engraver }
}
