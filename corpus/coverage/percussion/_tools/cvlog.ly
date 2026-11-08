%% Grob log for truth-vs-engraving verification (coverage suite; percussion copy of layouts/_tools/csynth/cvlog.ly,
%% adds DrumStaff and logs the NoteHead style).
%% Used as:  lilypond -dinclude-settings=cvlog.ly engraving.ly   -> engraving.cvlog
%% Every live grob of the listed types, after line breaking, is written as one tab-separated line:
%%   name  context-id  when  uid  orig-uid  fields...
%% (context-id = the Staff / Lyrics / ChordNames / group context the grob was acknowledged in;
%%  uid/orig-uid identify broken spanner pieces so they can be counted once.)
#(define cv-port #f)
#(define (cv-str x) (format #f "~a" x))
#(define (cv-out . vals)
   (if (not cv-port)
       (set! cv-port (open-file (string-append (ly:parser-output-name) ".cvlog") "w")))
   (display (string-join (map cv-str vals) "\t") cv-port)
   (newline cv-port)
   (force-output cv-port))
#(define (cv-when g)
   (let* ((it (if (ly:spanner? g) (ly:spanner-bound g LEFT) g))
          (col (and (ly:item? it) (ly:item-get-column it))))
     (if (ly:grob? col) (ly:moment-main (ly:grob-property col 'when)) "?")))
#(define (cv-uid g) (object-address g))
#(define (cv-orig g)
   (let ((o (ly:grob-original g)))
     (if (ly:grob? o) (object-address o) (object-address g))))
#(define (cv-txt m)
   (cond ((string? m) m)
         ((markup? m) (markup->string m))
         (else (cv-str m))))
#(define (cv-pitch g)
   (let* ((ev (event-cause g))
          (p (and ev (ly:event-property ev 'pitch #f))))
     (if (ly:pitch? p) (+ 60 (ly:pitch-semitones p)) "?")))
#(define (cv-dots g)
   (let ((d (ly:grob-object g 'dot)))
     (if (ly:grob? d) (ly:grob-property d 'dot-count 0) 0)))
#(define cv-names
   '(NoteHead Stem Flag Beam Accidental Dots Rest MultiMeasureRest Script Slur Tie DynamicText Hairpin
     TextScript LyricText LyricHyphen LyricExtender ChordName TupletNumber SustainPedal BreathingSign
     Arpeggio Fingering Clef KeySignature KeyCancellation TimeSignature InstrumentName StanzaNumber
     SystemStartBrace SystemStartBracket SystemStartSquare VoltaBracket RehearsalMark SegnoMark CodaMark
     TextMark MetronomeMark BarLine))
#(define (cv-log g nm sid)
   (let ((base (list nm sid (cv-when g) (cv-uid g) (cv-orig g))))
     (apply cv-out
       (append base
         (case nm
           ((NoteHead) (list (cv-pitch g) (ly:grob-property g 'duration-log) (ly:grob-property g 'staff-position)
                             (cv-dots g) (ly:grob-property g 'font-size 0) (cv-str (ly:grob-property g 'style 'default))))
           ((Stem) (let ((nh (ly:grob-object g 'note-heads)))
                     (list (ly:grob-property g 'direction) (ly:grob-property g 'duration-log)
                           (if (ly:grob? (ly:grob-object g 'beam)) 1 0)
                           (if (ly:grob-array? nh) (ly:grob-array-length nh) 0))))
           ((Accidental) (let ((nh (ly:grob-parent g Y)))
                           (list (ly:grob-property g 'glyph-name) (if (ly:grob? nh) (cv-pitch nh) "?")
                                 (ly:grob-property g 'parenthesized #f))))
           ((Dots) (list (ly:grob-property g 'dot-count 0)))
           ((Rest) (list (ly:grob-property g 'duration-log) (cv-dots g)))
           ((Script) (list (cv-str (ly:grob-property g 'script-stencil))))
           ((DynamicText TextScript LyricText ChordName Fingering StanzaNumber TextMark RehearsalMark
             MetronomeMark InstrumentName)
            (list (cv-txt (ly:grob-property g 'text ""))))
           ((Hairpin) (list (ly:grob-property g 'grow-direction)))
           ((SustainPedal) (list (cv-txt (ly:grob-property g 'text ""))))
           ((Clef) (list (ly:grob-property g 'glyph-name) (ly:item-break-dir g) (ly:grob-property g 'non-default #f)))
           ((KeySignature KeyCancellation) (list (length (ly:grob-property g 'alteration-alist '())) (ly:item-break-dir g)))
           ((TimeSignature) (list (cv-str (ly:grob-property g 'fraction)) (ly:item-break-dir g)
                                  (cv-str (ly:grob-property g 'style 'C))))
           ((BarLine) (list (cv-str (ly:grob-property g 'glyph-name)) (ly:item-break-dir g)))
           ((VoltaBracket) (list (cv-txt (ly:grob-property g 'text ""))))
           (else '()))))))
#(define cv-hooked (make-object-property))
#(define (cv-hook grob sid)
   (let ((nm (grob::name grob)))
     (if (and (memq nm cv-names) (not (cv-hooked grob)))
         (set! (cv-hooked grob) #t))
     (if (and (memq nm cv-names) (eq? (cv-hooked grob) #t))
         (let ((orig (ly:grob-property-data grob 'after-line-breaking)))
           (ly:grob-set-property! grob 'after-line-breaking
             (lambda (g)
               (if (procedure? orig) (orig g))
               (if (grob::is-live? g) (cv-log g nm sid))))
           (if (memq nm '(LyricHyphen LyricExtender))
               (let ((ost (ly:grob-property-data grob 'stencil)))
                 (if (procedure? ost)
                     (ly:grob-set-property! grob 'stencil
                       (lambda (g)
                         (let ((st (ost g)))
                           (cv-out (string-append (symbol->string nm) "Ink") sid (cv-when g) (cv-uid g) (cv-orig g)
                                   (if (and (ly:stencil? st) (not (ly:stencil-empty? st))) 1 0))
                           st))))))
           (set! (cv-hooked grob) 'done)))))
#(define (cv-engraver ctx)
   (let ((sid (let ((i (ly:context-id ctx))) (if (and (string? i) (> (string-length i) 0)) i
                                                 (cv-str (ly:context-name ctx))))))
     (make-engraver
      (acknowledgers
       ((grob-interface engraver grob source-engraver)
        (cv-hook grob sid))))))
\layout {
  \context { \Score \consists #cv-engraver }
  \context { \Staff \consists #cv-engraver }
  \context { \DrumStaff \consists #cv-engraver }
  \context { \RhythmicStaff \consists #cv-engraver }
  \context { \Lyrics \consists #cv-engraver }
  \context { \ChordNames \consists #cv-engraver }
  \context { \PianoStaff \consists #cv-engraver }
  \context { \ChoirStaff \consists #cv-engraver }
  \context { \StaffGroup \consists #cv-engraver }
  \context { \GrandStaff \consists #cv-engraver }
}
