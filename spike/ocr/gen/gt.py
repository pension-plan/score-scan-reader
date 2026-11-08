#!/usr/bin/env python3
"""Extract lyric-line ground truth (boxes, syllables, printed hyphens/extenders) from a LilyPond PDF.
Renders each page at DPI (gray PNG) and writes <out>/<doc>_p<N>.png + .gt.json (pixel coords).
Usage: gt.py PDF META_JSON OUTDIR [DPI]"""
import json, os, re, subprocess, sys, unicodedata
import numpy as np
from PIL import Image
import pdfplumber

def letters(s):
    return "".join(ch for ch in unicodedata.normalize("NFKC", s) if ch.isalnum())

def main():
    pdf_path, meta_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    meta = json.load(open(meta_path))
    os.makedirs(out, exist_ok=True)
    doc = meta["id"]
    sc = dpi / 72.0
    # verse letter strings with letter->syllable index maps
    vinfo = []
    for vi, syls in enumerate(meta["verses"]):
        s, idx, starts = "", [], []
        for si, sy in enumerate(syls):
            l = letters(sy["t"])
            starts.append(len(s))
            s += l
            idx += [si] * len(l)
        vinfo.append(dict(s=s, idx=idx, starts=starts))
    cursor = {}  # (verse, column-key) -> letter pos consumed
    pdf = pdfplumber.open(pdf_path)
    for pno, page in enumerate(pdf.pages):
        base = f"{out}/{doc}_p{pno+1}"
        subprocess.run(["pdftoppm", "-r", str(dpi), "-gray", "-png", "-f", str(pno+1), "-l", str(pno+1), "-singlefile", pdf_path, base], check=True)
        img = np.array(Image.open(base + ".png").convert("L"))
        H, W = img.shape
        chars = [c for c in page.chars if "Emmentaler" not in c["fontname"] and c["text"].strip()]
        for c in chars:  # fonts without ToUnicode for Latin-1 glyphs
            m_ = re.fullmatch(r"\(cid:(\d+)\)", c["text"])
            if m_ and 160 <= int(m_.group(1)) <= 255: c["text"] = chr(int(m_.group(1)))
        from collections import Counter
        lyr_size = Counter(round(c["size"], 1) for c in chars).most_common(1)[0][0] if chars else 0
        chars = [c for c in chars if abs(c["size"] - lyr_size) <= 0.12 * lyr_size]
        # group by baseline (matrix y) and size
        chars.sort(key=lambda c: (round(page.height - c["matrix"][5], 0), c["x0"]))
        lines = []
        for c in chars:
            bl = page.height - c["matrix"][5]
            for L in lines:
                if abs(L["bl"] - bl) < 1.2 and abs(L["size"] - c["size"]) < 3.0:
                    L["chars"].append(c); break
            else:
                lines.append(dict(bl=bl, size=c["size"], chars=[c]))
        lines.sort(key=lambda L: L["bl"])
        def _msize(L):
            return Counter(round(c["size"], 1) for c in L["chars"]).most_common(1)[0][0]
        lines = [L for L in lines if abs(_msize(L) - lyr_size) <= 0.1 * lyr_size]
        for L in lines: L["size"] = _msize(L)
        gt_lines = []
        for L in lines:
            cs = sorted(L["chars"], key=lambda c: c["x0"])
            # words by gap
            words, cur = [], [cs[0]]
            for a, b in zip(cs, cs[1:]):
                if b["x0"] - a["x1"] > 0.18 * a["size"]:
                    words.append(cur); cur = [b]
                else:
                    cur.append(b)
            words.append(cur)
            wtext = ["".join(c["text"] for c in w) for w in words]
            stanza = None
            if wtext and re.fullmatch(r"\d+\.", wtext[0]) and "Bold" in words[0][0]["fontname"]:
                stanza = wtext[0]; words = words[1:]; wtext = wtext[1:]
            if not words: continue
            ls = letters("".join(wtext))
            if len(ls) < 2: continue
            best = None
            for vi, v in enumerate(vinfo):
                start = 0
                while True:
                    k = v["s"].find(ls, start)
                    if k < 0: break
                    a, b = k, k + len(ls)
                    if a in v["starts"] and (b == len(v["s"]) or b in v["starts"]):
                        # prefer occurrence after the cursor for this verse
                        key = vi
                        score = (0 if k >= cursor.get(key, 0) else 1, k)
                        if best is None or score < best[0]:
                            best = (score, vi, a, b)
                    start = k + 1
            if best is None: continue
            _, vi, a, b = best
            cursor[vi] = b
            v = vinfo[vi]
            s0, s1 = v["idx"][a], v["idx"][b - 1]
            syls = meta["verses"][vi][s0:s1 + 1]
            # assign chars to syllables sequentially by letter count
            flat = [c for w in words for c in w]
            sylboxes, ci = [], 0
            for sy in syls:
                need = len(letters(sy["t"]))
                got, mine = 0, []
                while ci < len(flat) and (got < need or not letters(flat[ci]["text"])):
                    if got >= need and letters(flat[ci]["text"]): break
                    mine.append(flat[ci]); got += len(letters(flat[ci]["text"])); ci += 1
                # trailing punctuation
                while ci < len(flat) and not letters(flat[ci]["text"]) and (ci + 1 >= len(flat) or flat[ci+1]["x0"] - flat[ci]["x1"] < 0.18 * flat[ci]["size"] or True):
                    if mine and flat[ci]["x0"] - mine[-1]["x1"] < 0.18 * flat[ci]["size"]:
                        mine.append(flat[ci]); ci += 1
                    else: break
                x0 = min(c["x0"] for c in mine); x1 = max(c["x1"] for c in mine)
                sylboxes.append([x0 * sc, x1 * sc])
            size_px = L["size"] * sc
            bl_px = L["bl"] * sc
            top_px = bl_px - 0.80 * size_px
            bot_px = bl_px + 0.25 * size_px
            # printed hyphen / extender detection on clean raster between syllables
            out_syls = []
            for i, (sy, (x0, x1)) in enumerate(zip(syls, sylboxes)):
                nx0 = sylboxes[i + 1][0] if i + 1 < len(syls) else min(W - 1, x1 + 6 * size_px)
                gx0, gx1 = int(x1 + 0.5), int(nx0 - 0.5)
                hy = ext = False
                if gx1 - gx0 >= 2:
                    band_h = img[int(bl_px - 0.45 * size_px):int(bl_px - 0.12 * size_px), gx0:gx1] < 128
                    band_e = img[int(bl_px - 0.06 * size_px):int(bl_px + 0.10 * size_px), gx0:gx1] < 128
                    colh = band_h.any(axis=0).sum(); cole = band_e.any(axis=0).sum()
                    if sy["hyph"] and colh >= 0.12 * size_px: hy = True
                    if (not sy["hyph"]) and cole >= 0.8 * size_px: ext = True
                out_syls.append(dict(t=sy["t"], hyph=sy["hyph"], hyph_printed=bool(hy), mel=sy["mel"], ext_printed=bool(ext), x0=round(x0, 1), x1=round(x1, 1)))
            # ink bbox within font box
            lx0 = int(min(s[0] for s in sylboxes)) - 1; lx1 = int(max(s[1] for s in sylboxes)) + 1
            if stanza:
                lx0 = int(words[0][0]["x0"] * sc) - 1 if False else int(min(c["x0"] for c in L["chars"]) * sc) - 1
            reg = img[int(top_px):int(bot_px), max(0, lx0):min(W, lx1)] < 128
            rows = np.where(reg.any(axis=1))[0]
            iy0 = int(top_px) + (rows[0] if len(rows) else 0); iy1 = int(top_px) + (rows[-1] + 1 if len(rows) else int(bot_px - top_px))
            # leading hyphen (word continued from previous system, LilyPond may repeat the hyphen)
            lead_pr = False
            if s0 > 0 and meta["verses"][vi][s0 - 1]["hyph"]:
                fx0 = sylboxes[0][0]
                band = img[int(bl_px - 0.45 * size_px):int(bl_px - 0.12 * size_px), max(0, int(fx0 - 3 * size_px)):int(fx0 - 1)] < 128
                lead_pr = bool(band.size) and band.any(axis=0).sum() >= 0.12 * size_px
            printed = (stanza + " " if stanza else "") + ("- " if lead_pr else "")
            for i, s in enumerate(out_syls):
                printed += s["t"]
                if i < len(out_syls) - 1:
                    printed += " - " if s["hyph"] else " "
                elif s["hyph_printed"]:
                    printed += " -"
            words_gt, curw = [], ""
            for s in out_syls:
                curw += s["t"]
                if not s["hyph"]:
                    words_gt.append(curw); curw = ""
            if curw: words_gt.append(curw + "-")  # word continues on next line
            gt_lines.append(dict(verse=vi + 1, stanza=stanza, font=words[0][0]["fontname"].split("+")[-1], size_px=round(size_px, 2),
                                 baseline=round(bl_px, 1), bbox=[lx0, int(iy0), lx1, int(iy1)], fontbox=[lx0, int(top_px), lx1, int(bot_px)],
                                 text=printed, words=words_gt, syllables=out_syls,
                                 lead_hyphen=bool(lead_pr), cont_from_prev=bool(s0 > 0 and meta["verses"][vi][s0 - 1]["hyph"])))
        json.dump(dict(doc=doc, page=pno + 1, dpi=dpi, width=W, height=H, lang=meta["lang"], layout=meta["layout"], font=meta["font"],
                       lines=gt_lines), open(base + ".gt.json", "w"), ensure_ascii=False, indent=1)
        print(base, len(gt_lines), "lines")

if __name__ == "__main__":
    main()
