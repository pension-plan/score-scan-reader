#!/usr/bin/env python3
"""Generate varied LilyPond scores with multi-verse lyrics + a meta JSON (logical syllables per verse).
Usage: make_ly.py OUTDIR [NDOCS]"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from texts import TEXTS

FONTS = ["TeX Gyre Schola", "TeX Gyre Termes", "TeX Gyre Bonum", "TeX Gyre Pagella", "C059", "P052",
         "Nimbus Roman", "Liberation Serif", "DejaVu Serif", "Bitstream Charter", "TeX Gyre Heros", "Latin Modern Roman"]
NOTE_NAMES = ["c", "d", "e", "f", "g", "a", "b"]
KEYS = [("c", "major", 0, {}), ("g", "major", 4, {"f": "fis"}), ("f", "major", 3, {"b": "bes"}),
        ("d", "major", 1, {"f": "fis", "c": "cis"}), ("bes", "major", 6, {"b": "bes", "e": "ees"}),
        ("ees", "major", 2, {"b": "bes", "e": "ees", "a": "aes"})]
PHRASE_END = set(",;:.!?")

def parse_verse(v):
    syls = []
    for tok in v.split():
        parts = tok.split("-")
        for j, p in enumerate(parts):
            syls.append(dict(t=p, hyph=j < len(parts) - 1))
    return syls

def lily_pitch(deg, key):
    """deg: diatonic step index from C4=0 (absolute). Returns lilypond absolute pitch."""
    tonic_idx = key[2]
    # scale degrees are relative to key tonic; deg is diatonic index relative to C4 already shifted by tonic
    d = deg + tonic_idx
    name = NOTE_NAMES[d % 7]
    octv = d // 7  # 0 => octave of middle C (c')
    acc = key[3].get(name, name)
    marks = octv + 1  # c' == middle C
    return acc + ("'" * marks if marks > 0 else "," * (-marks))

def quote(s):
    return '"' + s.replace('\\', '').replace('"', '') + '"'

def build(doc_id, cfg, rng):
    text = cfg["text"]
    verses = [parse_verse(v) for v in text["verses"]][: cfg["nverses"]]
    n = len(verses[0])
    key = cfg["key"]
    three = cfg["time"] == "3/4"
    # melody: groups of notes per syllable
    groups = []
    deg = rng.randint(2, 5)
    mel_p = cfg["mel_p"]
    for i, s in enumerate(verses[0]):
        end = s["t"][-1] in PHRASE_END
        m = 1
        if rng.random() < mel_p and i < n - 1:
            m = rng.choice([2, 2, 3])
        notes = []
        for k in range(m):
            deg = max(-1, min(9, deg + rng.choice([-2, -1, -1, 0, 1, 1, 2])))
            notes.append(deg)
        if m == 1:
            durs = ["2." if (end and three) else ("2" if end else "4")]
        else:
            durs = ["8"] * m
            if end:
                durs[-1] = "4"
        groups.append((notes, durs))
    def voice_str(shift, lo, slurs, gr=groups):
        out = []
        for notes, durs in gr:
            for k, (d, du) in enumerate(zip(notes, durs)):
                dd = max(lo, d + shift)
                tok = lily_pitch(dd, key) + du
                if slurs and len(notes) > 1:
                    if k == 0: tok += "("
                    if k == len(notes) - 1: tok += ")"
                out.append(tok)
        return " ".join(out)
    sop = voice_str(0, -3, True)
    alto = voice_str(-rng.choice([2, 2, 3, 4]), -5, False)
    ten = voice_str(-7 + rng.choice([0, 2]), -10, False)
    bas = voice_str(-11 + rng.choice([0, 0, -2]), -15, False)
    keystr = f"\\key {key[0]} \\{key[1]} \\time {cfg['time']}"
    # lyrics with mapping
    def lyr(vi, syls, stanza):
        toks = []
        if stanza: toks.append(f'\\set stanza = "{vi+1}."')
        for i in range(n):
            if i >= len(syls):
                toks.append("\\skip 1")
                continue
            s = syls[i]
            toks.append(quote(s["t"]))
            mel = len(groups[i][0]) > 1
            if s["hyph"]:
                toks.append("--")
            elif mel:
                toks.append("__")
        return "{ " + " ".join(toks) + " }"
    font = cfg["font"]
    lyrfont = f'\\override LyricText.font-name = #"{font}"'
    def lyrics_ctx(vi, voice, above=None):
        it = ""
        if cfg["italic_even"] and vi % 2 == 1:
            it = f'\\override LyricText.font-name = #"{font} Italic"'
        w = f"\\with {{ {it} }}" if it else ""
        return f'\\new Lyrics {w} \\lyricsto "{voice}" {lyr(vi, verses[vi], cfg["stanza"])}'
    layout = cfg["layout"]
    nv = len(verses)
    if layout == "melody":
        music = f"""<<
  \\new Staff \\new Voice = "sop" {{ {keystr} {sop} \\bar "|." }}
  {' '.join(lyrics_ctx(v, 'sop') for v in range(nv))}
>>"""
    elif layout == "closed":
        music = f"""\\new ChoirStaff <<
  \\new Staff = "upper" << \\new Voice = "sop" {{ \\voiceOne {keystr} {sop} \\bar "|." }} \\new Voice = "alto" {{ \\voiceTwo {keystr} {alto} }} >>
  {' '.join(lyrics_ctx(v, 'sop') for v in range(nv))}
  \\new Staff = "lower" << \\clef bass \\new Voice = "ten" {{ \\voiceOne {keystr} {ten} }} \\new Voice = "bas" {{ \\voiceTwo {keystr} {bas} }} >>
>>"""
    elif layout == "open":
        nv = min(nv, 2)
        parts = []
        for nm, mus, clef in [("sop", sop, "treble"), ("alto", alto, "treble"), ("ten", ten, "treble_8"), ("bas", bas, "bass")]:
            parts.append(f'\\new Staff \\new Voice = "{nm}" {{ \\clef "{clef}" {keystr} {mus} \\bar "|." }}')
            parts.append(' '.join(lyrics_ctx(v, nm) for v in range(nv)))
        music = "\\new ChoirStaff <<\n" + "\n".join(parts) + "\n>>"
    else:  # voice + piano
        music = f"""<<
  \\new Staff \\new Voice = "sop" {{ {keystr} {sop} \\bar "|." }}
  {' '.join(lyrics_ctx(v, 'sop') for v in range(nv))}
  \\new PianoStaff <<
    \\new Staff << \\new Voice {{ \\voiceOne {keystr} {sop} }} \\new Voice {{ \\voiceTwo {keystr} {alto} }} >>
    \\new Staff << \\clef bass \\new Voice {{ \\voiceOne {keystr} {ten} }} \\new Voice {{ \\voiceTwo {keystr} {bas} }} >>
  >>
>>"""
    ly = f"""\\version "2.24.0"
#(set-global-staff-size {cfg['staff']})
\\paper {{ #(set-paper-size "{cfg['paper']}") ragged-last-bottom = ##t indent = {cfg['indent']}\\mm }}
\\header {{ title = "{text['title']}" poet = "Words: {text['poet']}" composer = "Tune: spike {doc_id}" tagline = ##f }}
\\layout {{
  \\context {{ \\Voice \\remove Note_heads_engraver \\consists Completion_heads_engraver }}
  \\context {{ \\Lyrics {lyrfont} \\override LyricText.font-size = #{cfg['fsize']} }}
}}
\\score {{
{music}
}}
"""
    meta = dict(id=doc_id, text_id=text["id"], lang=text["lang"], layout=layout, font=font, italic_even=cfg["italic_even"],
                stanza=cfg["stanza"], staff=cfg["staff"], fsize=cfg["fsize"], paper=cfg["paper"], nverses=nv,
                melisma_groups=[i for i, g in enumerate(groups) if len(g[0]) > 1],
                verses=[[dict(t=s["t"], hyph=s["hyph"], mel=len(groups[i][0]) > 1) for i, s in enumerate(v[:n])] for v in verses[:nv]],
                lyrics_voices={"melody": ["sop"], "closed": ["sop"], "open": ["sop", "alto", "ten", "bas"], "piano": ["sop"]}[layout])
    return ly, meta

def main():
    out = sys.argv[1]
    ndocs = int(sys.argv[2]) if len(sys.argv) > 2 else 28
    os.makedirs(out, exist_ok=True)
    layouts = ["closed", "melody", "closed", "open", "piano", "melody", "closed"]
    for d in range(ndocs):
        rng = random.Random(1000 + d)
        text = TEXTS[d % len(TEXTS)]
        cfg = dict(text=text, nverses=rng.choice([2, 3, 3]), key=rng.choice(KEYS), time=rng.choice(["4/4", "4/4", "3/4"]),
                   mel_p=(rng.uniform(0.15, 0.35) if text["melismatic"] else rng.uniform(0.0, 0.08)),
                   layout=layouts[d % len(layouts)], font=FONTS[d % len(FONTS)], italic_even=rng.random() < 0.3,
                   stanza=rng.random() < 0.7, staff=rng.choice([16, 17, 18, 19, 20]), fsize=rng.choice([-1, -0.5, 0, 0, 0.5, 1]),
                   paper=rng.choice(["a4", "letter"]), indent=rng.choice([0, 5, 10]))
        if cfg["font"] in ("TeX Gyre Heros",):
            cfg["italic_even"] = False
        did = f"d{d:02d}_{text['lang']}_{text['id']}_{cfg['layout']}"
        ly, meta = build(did, cfg, rng)
        with open(os.path.join(out, did + ".ly"), "w") as f: f.write(ly)
        with open(os.path.join(out, did + ".meta.json"), "w") as f: json.dump(meta, f, ensure_ascii=False, indent=1)
        print(did)

if __name__ == "__main__":
    main()
