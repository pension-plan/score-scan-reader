#!/usr/bin/env python3
"""Generate test "scans" + ground truth for the ML OMR spike.

pieces.py -> LilyPond (.ly) -> PDF + SVG (same layout) -> pdftoppm 200/300 dpi gray PNG
          -> degraded variants (rotation / noise / blur / JPEG / photocopy)
Ground truth:
  gt/<piece>.musicxml       MusicXML 4.0 partwise, one <part> per voice, lyrics w/ syllabic+extend
  gt/<piece>.json           per-voice note list (step/alter/octave/midi/dur/measure/lyrics)
  scans/<piece>_<dpi>_<variant>.png + .boxes.json   notehead boxes (px) labelled voice/note index,
                            taken from LilyPond SVG output-attributes + textedit line:col,
                            transformed with the same affine as the degradation.
Usage: .venv/bin/python src/make_scans.py
"""
import json, os, re, subprocess, sys, math
import numpy as np
import cv2
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from pieces import PIECES  # noqa: E402

LY_DIR = os.path.join(ROOT, "scans", "ly")
GT_DIR = os.path.join(ROOT, "scans", "gt")
IMG_DIR = os.path.join(ROOT, "scans")
STEPS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
TYPES = {1: "whole", 2: "half", 4: "quarter", 8: "eighth", 16: "16th"}
DIV = 4  # divisions per quarter


def parse_tok(tok):
    m = re.fullmatch(r"([A-Gr])([#b]?)(\d?):(\d+)(\.?)([()]?)", tok)
    if not m:
        raise ValueError(tok)
    step, acc, octv, dur, dot, slur = m.groups()
    d = {"rest": step == "r", "dur": int(dur), "dots": 1 if dot else 0, "slur": slur or None}
    if not d["rest"]:
        d.update(step=step, alter={"#": 1, "b": -1, "": 0}[acc], octave=int(octv))
        d["midi"] = 12 * (d["octave"] + 1) + STEPS[step] + d["alter"]
    q = 4.0 / d["dur"] * (1.5 if d["dots"] else 1.0)
    d["quarters"] = q
    return d


def parse_voice(s):
    measures = [m.split() for m in s.split("|")]
    notes = []
    for mi, toks in enumerate(measures):
        for t in toks:
            n = parse_tok(t)
            n["measure"] = mi
            notes.append(n)
    return notes


def ly_pitch(n):
    if n["rest"]:
        return "r"
    name = n["step"].lower() + {1: "is", -1: "es", 0: ""}[n["alter"]]
    o = n["octave"] - 3
    return name + ("'" * o if o > 0 else "," * (-o))


def ly_tok(n):
    s = ly_pitch(n) + str(n["dur"]) + ("." if n["dots"] else "")
    if n["slur"]:
        s += n["slur"]
    return s


def lyric_syllables(text):
    """'A -- maz -- ing __ grace' -> [(syl, syllabic, extend)]"""
    toks = text.split()
    out = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in ("--", "__"):
            i += 1
            continue
        hyph_after = i + 1 < len(toks) and toks[i + 1] == "--"
        ext_after = i + 1 < len(toks) and toks[i + 1] == "__"
        hyph_before = i - 1 >= 0 and toks[i - 1] == "--"
        if hyph_before and hyph_after:
            syl = "middle"
        elif hyph_before:
            syl = "end"
        elif hyph_after:
            syl = "begin"
        else:
            syl = "single"
        out.append((t, syl, ext_after))
        i += 1
    return out


def attach_lyrics(notes, text, verse):
    syls = lyric_syllables(text)
    k = 0
    in_slur = False
    for n in notes:
        if n["rest"]:
            continue
        cont = in_slur  # note inside a melisma (after the first slurred note)
        if n["slur"] == "(":
            in_slur = True
        if n["slur"] == ")":
            in_slur = False
        if cont:
            continue
        if k < len(syls):
            t, syl, ext = syls[k]
            n.setdefault("lyrics", {})[str(verse)] = {"text": t, "syllabic": syl, "extend": ext}
            k += 1
    if k != len(syls):
        raise ValueError(f"lyric count mismatch {k} vs {len(syls)}")


def build(piece_id):
    P = PIECES[piece_id]
    voices = {}
    for st in P["staves"]:
        for vid, music, _ in st["voices"]:
            voices[vid] = parse_voice(music)
    for vi, (vid, text, _) in enumerate(P["lyrics"]):
        verse = 1 + sum(1 for (v2, _, _) in P["lyrics"][:vi] if v2 == vid)
        attach_lyrics(voices[vid], text, verse)
    for vid in P.get("lyrics_apply_to", []):
        if vid == P["lyrics"][0][0]:
            continue
        src = voices[P["lyrics"][0][0]]
        # homorhythmic copy (same note count, no melismas in these settings)
        for a, b in zip(src, voices[vid]):
            if "lyrics" in a:
                b["lyrics"] = json.loads(json.dumps(a["lyrics"]))
                b["lyrics_inherited"] = True
    return P, voices


def write_ly(piece_id, P, voices):
    """Each voice's music is on its own line so textedit line:col -> (voice, note index)."""
    lines = ['\\version "2.24.0"',
             '\\header { title = "%s" tagline = ##f }' % P["title"],
             '\\paper { #(set-paper-size "a4") indent = 0 }', '\\pointAndClickTypes #\'note-event',
             '\\layout { \\context { \\Voice \\override NoteHead.output-attributes = #\'((class . "nh")) } }']
    colmap = {}  # (line, col) -> (vid, idx)
    tsig = "\\time %d/%d" % P["time"]
    for st in P["staves"]:
        for vid, _, vcmd in st["voices"]:
            prefix = "%s = { \\key %s %s %s " % (vid + "Music", P["key"], tsig,
                                                ("\\partial %d " % P["partial"]) if P["partial"] else "")
            if vcmd:
                prefix = prefix.replace("{ ", "{ %s " % vcmd, 1)
            body = prefix
            lineno = len(lines) + 1
            for i, n in enumerate(voices[vid]):
                if i > 0 and n["measure"] != voices[vid][i - 1]["measure"]:
                    body += "| "
                col = len(body)
                colmap[(lineno, col)] = (vid, i)
                body += ly_tok(n) + " "
            body += '\\bar "|." }'
            lines.append(body)
    verse_names = []
    for vi, (vid, text, _) in enumerate(P["lyrics"]):
        nm = "lyr" + "ABCDEFGH"[vi]
        lines.append('%s = \\lyricmode { %s }' % (nm, text))
        verse_names.append(nm)
    staff_blocks = []
    for si, st in enumerate(P["staves"]):
        vs = " ".join('\\new Voice = "%s" \\%sMusic' % (vid, vid) for vid, _, _ in st["voices"])
        clef = st["clef"]
        sb = '\\new Staff << \\clef "%s" %s >>' % (clef, vs)
        for vi, (vid, text, place) in enumerate(P["lyrics"]):
            if place == si:
                sb += ' \\new Lyrics \\lyricsto "%s" \\%s' % (vid, verse_names[vi])
        staff_blocks.append(sb)
    grp = "ChoirStaff" if len(P["staves"]) > 1 else "StaffGroup"
    lines.append("\\score { \\new %s << %s >> \\layout { } }" % (grp, " ".join(staff_blocks)))
    ly = "\n".join(lines) + "\n"
    path = os.path.join(LY_DIR, piece_id + ".ly")
    with open(path, "w") as f:
        f.write(ly)
    return path, colmap


def svg_path_bbox(d):
    toks = re.findall(r"[MmLlHhVvCcSsQqTtZz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    x = y = 0.0
    sx = sy = 0.0
    xs, ys = [], []
    i = 0
    cmd = None
    nargs = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "Z": 0}
    while i < len(toks):
        t = toks[i]
        if re.fullmatch(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                x, y = sx, sy
                continue
        k = nargs[cmd.upper()]
        args = [float(a) for a in toks[i:i + k]]
        i += k
        rel = cmd.islower()
        U = cmd.upper()
        if U == "H":
            x = x + args[0] if rel else args[0]
        elif U == "V":
            y = y + args[0] if rel else args[0]
        else:
            pts = [(args[j], args[j + 1]) for j in range(0, k, 2)]
            for px, py in pts:
                ax, ay = (x + px, y + py) if rel else (px, py)
                xs.append(ax)
                ys.append(ay)
            ex, ey = pts[-1]
            x, y = (x + ex, y + ey) if rel else (ex, ey)
            if U == "M":
                sx, sy = x, y
                cmd = "l" if rel else "L"
        xs.append(x)
        ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def svg_noteheads(svg_path, colmap):
    s = open(svg_path).read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    heads = []
    for m in re.finditer(r'<g class="nh">\s*<a[^>]*textedit://[^"]*?:(\d+):(\d+):\d+">\s*'
                         r'<g transform="translate\(([-\d.]+), ([-\d.]+)\)">\s*'
                         r'<path transform="scale\(([-\d.]+), ([-\d.]+)\)" d="([^"]+)"', s):
        line, col, tx, ty, scx, scy, d = m.groups()
        line, col = int(line), int(col) - 1  # textedit col is 1-based? normalise below
        key = None
        for dc in (0, 1, -1, 2):
            if (line, col + dc) in colmap:
                key = colmap[(line, col + dc)]
                break
        x0, y0, x1, y1 = svg_path_bbox(d)
        scx, scy, tx, ty = float(scx), float(scy), float(tx), float(ty)
        X = sorted([tx + x0 * scx, tx + x1 * scx])
        Y = sorted([ty + y0 * scy, ty + y1 * scy])
        heads.append({"voice": key[0] if key else None, "idx": key[1] if key else None,
                      "x0": X[0], "x1": X[1], "y0": Y[0], "y1": Y[1]})
    return vb, heads


def pdf_noteheads(pdf_path, colmap):
    """Notehead boxes from LilyPond point-and-click link annotations (PDF points, y down)."""
    from pypdf import PdfReader
    r = PdfReader(pdf_path)
    if len(r.pages) != 1:
        raise SystemExit("expected one page: " + pdf_path)
    pg = r.pages[0]
    W, H = float(pg.mediabox.width), float(pg.mediabox.height)
    cand = {}
    for a in pg.get("/Annots") or []:
        o = a.get_object()
        uri = o.get("/A", {}).get("/URI", "")
        m = re.search(r":(\d+):(\d+):\d+$", uri)
        if not m:
            continue
        line, col = int(m.group(1)), int(m.group(2))
        key = colmap.get((line, col)) or colmap.get((line, col - 1))
        if key is None:
            continue
        x0, y0, x1, y1 = [float(v) for v in o["/Rect"]]
        cand.setdefault(key, []).append((x0, H - y1, x1, H - y0))
    hs = sorted((b[3] - b[1]) for v in cand.values() for b in v)
    med = hs[len(hs) // 2]
    heads = []
    for key, bs in cand.items():
        b = min(bs, key=lambda b: abs((b[3] - b[1]) - med) + 0.01 * abs((b[2] - b[0]) - 1.2 * med))
        heads.append({"voice": key[0], "idx": key[1], "x0": b[0], "y0": b[1], "x1": b[2], "y1": b[3]})
    return [0, 0, W, H], heads


def write_musicxml(piece_id, P, voices):
    beats, beat_type = P["time"]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
           '"http://www.musicxml.org/dtds/partwise.dtd">',
           '<score-partwise version="4.0">',
           '<work><work-title>%s</work-title></work>' % P["title"], '<part-list>']
    vids = [vid for st in P["staves"] for vid, _, _ in st["voices"]]
    clefs = {vid: st["clef"] for st in P["staves"] for vid, _, _ in st["voices"]}
    for i, vid in enumerate(vids):
        out.append('<score-part id="P%d"><part-name>%s</part-name></score-part>' % (i + 1, vid.capitalize()))
    out.append('</part-list>')
    for i, vid in enumerate(vids):
        out.append('<part id="P%d">' % (i + 1))
        notes = voices[vid]
        nmeas = max(n["measure"] for n in notes) + 1
        for mi in range(nmeas):
            out.append('<measure number="%d"%s>' % (mi + (0 if P["partial"] else 1),
                                                   ' implicit="yes"' if (P["partial"] and mi == 0) else ""))
            if mi == 0:
                c = clefs[vid]
                sign, line, oct_ch = {"treble": ("G", 2, 0), "bass": ("F", 4, 0), "treble_8": ("G", 2, -1)}[c]
                out.append('<attributes><divisions>%d</divisions><key><fifths>%d</fifths></key>'
                           '<time><beats>%d</beats><beat-type>%d</beat-type></time>'
                           '<clef><sign>%s</sign><line>%d</line>%s</clef></attributes>'
                           % (DIV, P["fifths"], beats, beat_type, sign, line,
                              "<clef-octave-change>-1</clef-octave-change>" if oct_ch else ""))
            for n in [n for n in notes if n["measure"] == mi]:
                dur = int(round(n["quarters"] * DIV))
                x = "<note>"
                if n["rest"]:
                    x += "<rest/>"
                else:
                    x += "<pitch><step>%s</step>%s<octave>%d</octave></pitch>" % (
                        n["step"], ("<alter>%d</alter>" % n["alter"]) if n["alter"] else "", n["octave"])
                x += "<duration>%d</duration><type>%s</type>%s" % (dur, TYPES[n["dur"]], "<dot/>" * n["dots"])
                if n["slur"]:
                    x += '<notations><slur type="%s"/></notations>' % ("start" if n["slur"] == "(" else "stop")
                for v, L in sorted(n.get("lyrics", {}).items()):
                    x += '<lyric number="%s"><syllabic>%s</syllabic><text>%s</text>%s</lyric>' % (
                        v, L["syllabic"], L["text"].replace("&", "&amp;").replace("'", "&apos;"),
                        "<extend/>" if L["extend"] else "")
                x += "</note>"
                out.append(x)
            if mi == nmeas - 1:
                out.append('<barline location="right"><bar-style>light-heavy</bar-style></barline>')
            out.append('</measure>')
        out.append('</part>')
    out.append('</score-partwise>')
    with open(os.path.join(GT_DIR, piece_id + ".musicxml"), "w") as f:
        f.write("\n".join(out) + "\n")


# ---------------------------------------------------------------- degradation
VARIANTS = ["clean", "rot", "noiseblur", "jpeg", "scan", "photocopy"]


def degrade(img, variant, dpi, seed):
    rng = np.random.default_rng(seed)
    h, w = img.shape
    M = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float64)
    out = img.astype(np.float32)
    k = dpi / 300.0
    if variant == "clean":
        pass
    elif variant == "rot":
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 1.3, 1.0)
        out = cv2.warpAffine(out, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=255)
    elif variant == "noiseblur":
        out = cv2.GaussianBlur(out, (0, 0), 1.1 * k)
        out = out + rng.normal(0, 14, out.shape)
    elif variant == "jpeg":
        pass  # applied at save time (q=30)
    elif variant == "scan":
        M = cv2.getRotationMatrix2D((w / 2, h / 2), -0.8, 1.0)
        M[0, 2] += 9 * k
        M[1, 2] += -14 * k
        out = cv2.warpAffine(out, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=255)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        illum = 0.86 + 0.08 * (xx / w) + 0.05 * np.sin(yy / h * math.pi)  # uneven lighting
        paper = 255 * illum
        ink = 35.0
        out = ink + (out / 255.0) * (paper - ink)
        out = cv2.GaussianBlur(out, (0, 0), 0.8 * k)
        out = out + rng.normal(0, 9, out.shape)
    elif variant == "photocopy":
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0.5, 1.0)
        out = cv2.warpAffine(out, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=255)
        out = cv2.GaussianBlur(out, (0, 0), 1.3 * k)
        out = out + rng.normal(0, 25, out.shape)
        out = np.where(out < 150, 20.0, 245.0)  # hard threshold -> broken/thickened strokes
        sp = rng.random(out.shape)
        out[sp < 0.0015] = 20.0  # speckle
        out = cv2.medianBlur(out.astype(np.uint8), 3).astype(np.float32)
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out, M


def render_variant(args):
    piece_id, dpi, variant, heads_px = args
    src = os.path.join(IMG_DIR, "raw", "%s_%d.png" % (piece_id, dpi))
    img = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
    out, M = degrade(img, variant, dpi, seed=hash((piece_id, dpi, variant)) & 0xFFFF)
    base = os.path.join(IMG_DIR, "%s_%d_%s" % (piece_id, dpi, variant))
    if variant in ("jpeg", "scan"):
        q = 30 if variant == "jpeg" else 55
        ok, buf = cv2.imencode(".jpg", out, [cv2.IMWRITE_JPEG_QUALITY, q])
        out = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)
        with open(base + ".jpg", "wb") as f:
            f.write(buf.tobytes())
    cv2.imwrite(base + ".png", out)
    boxes = []
    for hd in heads_px:
        cx, cy = (hd["x0"] + hd["x1"]) / 2, (hd["y0"] + hd["y1"]) / 2
        nx = M[0, 0] * cx + M[0, 1] * cy + M[0, 2]
        ny = M[1, 0] * cx + M[1, 1] * cy + M[1, 2]
        boxes.append({**{k: hd[k] for k in ("voice", "idx")}, "cx": round(nx, 2), "cy": round(ny, 2),
                      "w": round(hd["x1"] - hd["x0"], 2), "h": round(hd["y1"] - hd["y0"], 2)})
    with open(base + ".boxes.json", "w") as f:
        json.dump({"image": os.path.basename(base) + ".png", "dpi": dpi, "variant": variant,
                   "width": int(out.shape[1]), "height": int(out.shape[0]), "noteheads": boxes}, f)
    return base


def main():
    for d in (LY_DIR, GT_DIR, os.path.join(IMG_DIR, "raw")):
        os.makedirs(d, exist_ok=True)
    jobs = []
    for pid in PIECES:
        P, voices = build(pid)
        ly, colmap = write_ly(pid, P, voices)
        write_musicxml(pid, P, voices)
        with open(os.path.join(GT_DIR, pid + ".json"), "w") as f:
            json.dump({"piece": pid, "title": P["title"], "time": P["time"], "fifths": P["fifths"],
                       "staves": [[v for v, _, _ in st["voices"]] for st in P["staves"]],
                       "voices": voices}, f, indent=1)
        for args in (["--pdf"],):
            r = subprocess.run(["lilypond", *args, "-o", os.path.join(LY_DIR, pid), ly],
                               capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stderr)
                raise SystemExit(1)
        vb, heads = pdf_noteheads(os.path.join(LY_DIR, pid + ".pdf"), colmap)
        nmiss = sum(1 for h in heads if h["voice"] is None)
        nnotes = sum(1 for v in voices.values() for n in v if not n["rest"])
        print(f"{pid}: {len(heads)} noteheads in svg ({nmiss} unmapped), {nnotes} notes in source")
        for dpi in (200, 300):
            raw = os.path.join(IMG_DIR, "raw", "%s_%d" % (pid, dpi))
            subprocess.run(["pdftoppm", "-r", str(dpi), "-gray", "-png", "-singlefile",
                            os.path.join(LY_DIR, pid + ".pdf"), raw], check=True)
            img = cv2.imread(raw + ".png", cv2.IMREAD_GRAYSCALE)
            sx = img.shape[1] / vb[2]
            sy = img.shape[0] / vb[3]
            heads_px = [{**h, "x0": h["x0"] * sx, "x1": h["x1"] * sx, "y0": h["y0"] * sy, "y1": h["y1"] * sy}
                        for h in heads]
            for v in VARIANTS:
                jobs.append((pid, dpi, v, heads_px))
    with ProcessPoolExecutor(max_workers=min(32, len(jobs))) as ex:
        for b in ex.map(render_variant, jobs):
            print("wrote", os.path.relpath(b, ROOT))


if __name__ == "__main__":
    main()
