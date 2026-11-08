%% omrtruth.ily -- ground-truth instrumentation for the OMR spike.
%%
%% When the environment variable OMR_TRUTH=1 is set, every grob class that
%% matters for OMR is drawn in a unique colour:  R = class code, (G,B) = a
%% 16-bit object id.  Rendered without anti-aliasing (pdftoppm -aa no
%% -aaVector no) the colour of each pixel tells which grob painted it, so the
%% pixel-exact position of every notehead / stem / barline / staff line is
%% known at any DPI.  Semantic data (pitch, duration, staff-position, stem
%% direction, voice) for each id is written to $OMR_TRUTH_LOG.
%% Colour does not influence layout, so the clean render (OMR_TRUTH unset)
%% has an identical layout.
%%
%% Class codes (R channel):
%%  10 StaffSymbol      20 LedgerLineSpanner  30 BarLine      31 SpanBar
%%  40 Stem up          41 Stem down          42 Stem (no dir)
%%  50 NoteHead filled  51 NoteHead half      52 NoteHead whole  53 breve+
%%  60 Rest             70 Beam               71 Flag
%%  80 Accidental       81 KeySignature       82 Clef         83 TimeSignature
%%  84 KeyCancellation  90 Dots               91 Tie          92 Slur/PhrasingSlur
%% 100 LyricText       101 LyricHyphen       102 LyricExtender 103 StanzaNumber
%% 110 Dynamics        111 TextScript/markup 112 MetronomeMark
%% 120 SystemStart{Bar,Bracket,Brace}       121 Arpeggio/other

#(define omr-truth?
   (let ((v (getenv "OMR_TRUTH"))) (and v (not (string=? v "")) (not (string=? v "0")))))
#(define omr-id-counter 0)
#(define omr-log-port #f)
#(define (omr-log . items)
   (if (not omr-log-port)
       (set! omr-log-port
             (open-output-file (or (getenv "OMR_TRUTH_LOG") "omr-truth-log.txt"))))
   (display (string-join (map (lambda (x) (format #f "~a" x)) items) "\t") omr-log-port)
   (newline omr-log-port)
   (force-output omr-log-port))
#(define (omr-next-id) (set! omr-id-counter (1+ omr-id-counter)) omr-id-counter)
#(define (omr-rgb cls id)
   (list (/ cls 255.0) (/ (quotient id 256) 255.0) (/ (remainder id 256) 255.0)))

%% plain class colour with a fresh id (no semantic log beyond class)
#(define (omr-class-color cls name)
   (lambda (grob)
     (let ((id (omr-next-id)))
       (omr-log "obj" id cls name)
       (omr-rgb cls id))))

#(define (omr-pitch-str p)
   (if (ly:pitch? p)
       (format #f "~a:~a:~a" (ly:pitch-notename p) (ly:pitch-alteration p) (ly:pitch-octave p))
       "-"))

#(define (omr-head-color voice)
   (lambda (grob)
     (let* ((id (omr-next-id))
            (dl (ly:grob-property grob 'duration-log 2))
            (cls (cond ((>= dl 2) 50) ((= dl 1) 51) ((= dl 0) 52) (else 53)))
            (cause (ly:grob-property grob 'cause))
            (ev? (ly:stream-event? cause))
            (pitch (and ev? (ly:event-property cause 'pitch #f)))
            (dur (and ev? (ly:event-property cause 'duration #f)))
            (dots (if (ly:duration? dur) (ly:duration-dot-count dur) 0))
            (stem (ly:grob-object grob 'stem))
            (sdir (if (ly:grob? stem) (ly:grob-property stem 'direction 0) 0))
            (spos (ly:grob-property grob 'staff-position 0)))
       (omr-log "head" id cls voice dl dots spos sdir (omr-pitch-str pitch))
       (omr-rgb cls id))))

#(define (omr-stem-color grob)
   (let* ((id (omr-next-id))
          (dir (ly:grob-property grob 'direction 0))
          (cls (cond ((eqv? dir UP) 40) ((eqv? dir DOWN) 41) (else 42))))
     (omr-log "stem" id cls dir)
     (omr-rgb cls id)))

#(define (omr-barline-color grob)
   (let* ((id (omr-next-id))
          (glyph (ly:grob-property grob 'glyph-name "")))
     (omr-log "bar" id 30 (if (string? glyph) glyph "?"))
     (omr-rgb 30 id)))

#(define (omr-lyric-color grob)
   (let* ((id (omr-next-id))
          (txt (ly:grob-property grob 'text "")))
     (omr-log "lyric" id 100 (if (string? txt) txt (markup->string txt)))
     (omr-rgb 100 id)))

%% \omrVoice "sop"  -- tag a voice so its noteheads are logged with that name.
omrVoice =
#(define-music-function (name) (string?)
   (if omr-truth?
       #{ \override NoteHead.color = #(omr-head-color name) #}
       (make-music 'SequentialMusic 'elements '())))

#(if omr-truth?
     (ly:parser-include-string "
\\layout {
  \\context { \\Score
    \\override StaffSymbol.color = #(omr-class-color 10 \"staff\")
    \\override LedgerLineSpanner.color = #(omr-class-color 20 \"ledger\")
    \\override BarLine.color = #omr-barline-color
    \\override SpanBar.color = #(omr-class-color 31 \"spanbar\")
    \\override Stem.color = #omr-stem-color
    \\override NoteHead.color = #(omr-head-color \"?\")
    \\override Rest.color = #(omr-class-color 60 \"rest\")
    \\override MultiMeasureRest.color = #(omr-class-color 60 \"mmrest\")
    \\override Beam.color = #(omr-class-color 70 \"beam\")
    \\override Flag.color = #(omr-class-color 71 \"flag\")
    \\override Accidental.color = #(omr-class-color 80 \"accidental\")
    \\override KeySignature.color = #(omr-class-color 81 \"key\")
    \\override KeyCancellation.color = #(omr-class-color 84 \"keycancel\")
    \\override Clef.color = #(omr-class-color 82 \"clef\")
    \\override TimeSignature.color = #(omr-class-color 83 \"time\")
    \\override Dots.color = #(omr-class-color 90 \"dots\")
    \\override Tie.color = #(omr-class-color 91 \"tie\")
    \\override Slur.color = #(omr-class-color 92 \"slur\")
    \\override PhrasingSlur.color = #(omr-class-color 92 \"pslur\")
    \\override LyricText.color = #omr-lyric-color
    \\override LyricHyphen.color = #(omr-class-color 101 \"hyphen\")
    \\override LyricExtender.color = #(omr-class-color 102 \"extender\")
    \\override StanzaNumber.color = #(omr-class-color 103 \"stanza\")
    \\override DynamicText.color = #(omr-class-color 110 \"dynamic\")
    \\override Hairpin.color = #(omr-class-color 110 \"hairpin\")
    \\override TextScript.color = #(omr-class-color 111 \"text\")
    \\override MetronomeMark.color = #(omr-class-color 112 \"tempo\")
    \\override SystemStartBar.color = #(omr-class-color 120 \"startbar\")
    \\override SystemStartBracket.color = #(omr-class-color 120 \"bracket\")
    \\override SystemStartBrace.color = #(omr-class-color 120 \"brace\")
    \\override Arpeggio.color = #(omr-class-color 121 \"arpeggio\")
    \\override Script.color = #(omr-class-color 121 \"script\")
    \\override Fingering.color = #(omr-class-color 121 \"fingering\")
    \\override InstrumentName.color = #(omr-class-color 111 \"instrname\")
  }
}
"))
