"""coverage/perf build pipeline.

Stage 1  engrave(key)        one engraving per (piece, paper size / page count):
           model -> instrumented twin .ly -> LilyPond (grob log) -> harvest + verify every note/rest
           -> truth.musicxml (stems, beams, accidentals as engraved) -> xmllint XSD -> music21 parse
           -> clean engraving.ly -> LilyPond PDF + MIDI -> twin/clean raster identical
           -> MIDI attacks + lyric syllables == truth (validate.py logic) -> accidental cross-check
           (per-part simulation == printed) -> symbol counts (symcount.py on the truth) cross-checked
           with the engraved grob counts -> page count == plan, no LilyPond warnings
Stage 2  render(key, dpi)    pdftoppm -gray pages (PGM) at the item dpi
Stage 3  page tasks          clean PNG + damaged scan pages (cov/degrade2.py, seeded per page)
Stage 4  assemble(item)      clean.pdf / scan.pdf / scan-severe.pdf (img2pdf, image-only check),
                             meta.json, ATTRIBUTION.txt, engraving.ly, truth.musicxml
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from collections import Counter

import numpy as np
from PIL import Image

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)

from cov import degrade2 as D  # noqa: E402
from cov import harvest as H  # noqa: E402
from cov.acc import GLYPH, simulate  # noqa: E402
from cov.lily import LilyWriter  # noqa: E402
from cov.model import check, compute_extenders, sanitize_ties  # noqa: E402
from cov.mxl import write_musicxml  # noqa: E402
from cov import validate_lib as V  # noqa: E402
import symcount  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(TOOLS)                       # corpus/coverage/perf
WORK = os.path.join(ROOT, '_work')
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
PY = '/Users/d.sloane/music/.venv/bin/python'
FAMILY = 'perf'


def run(cmd, cwd=None, timeout=1800):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def lilypond(ly, cwd, timeout=3600):
    rc, out, err = run(['lilypond', '-dno-point-and-click', '-ddelete-intermediate-files', '-o',
                        os.path.splitext(os.path.basename(ly))[0], os.path.basename(ly)], cwd=cwd, timeout=timeout)
    return rc, err


def pdf_pages(pdf):
    rc, info, _ = run(['pdfinfo', pdf])
    return int(re.search(r'Pages:\s+(\d+)', info).group(1))


def raster_digest(pdf, workdir, tag):
    pre = os.path.join(workdir, f'cmp-{tag}')
    for f in glob.glob(pre + '*'):
        os.remove(f)
    subprocess.run(['pdftoppm', '-gray', '-r', '40', pdf, pre], check=True, timeout=1800)
    h = hashlib.sha1()
    for f in sorted(glob.glob(pre + '*.pgm')):
        h.update(open(f, 'rb').read())
        os.remove(f)
    return h.hexdigest()


# --------------------------------------------------------------------------- symbol cross-check

def cross_check(counts, eng):
    """truth symbol counts vs engraved grob counts; returns (rows, failures)"""
    def s(*keys):
        return sum(eng.get(k, 0) for k in keys)
    acc_total = sum(v for k, v in counts.items() if k.startswith('acc-') and k != 'acc-courtesy')
    pairs = {
        'tie': (counts.get('tie', 0), s('tie')),
        'tie-across-system': (counts.get('tie-across-system', 0), s('tie-across-system')),
        'slur': (counts.get('slur', 0), s('slur')),
        'beam': (counts.get('beam', 0), s('beam')),
        'flag': (counts.get('flag', 0), s('flag')),
        'staccato': (counts.get('staccato', 0), s('script:staccato')),
        'staccatissimo': (counts.get('staccatissimo', 0), s('script:staccatissimo')),
        'accent': (counts.get('accent', 0), s('script:accent')),
        'tenuto': (counts.get('tenuto', 0), s('script:tenuto')),
        'marcato': (counts.get('marcato', 0), s('script:marcato')),
        'fermata': (counts.get('fermata', 0), s('script:fermata')),
        'trill': (counts.get('trill', 0), s('script:trill')),
        'mordent': (counts.get('mordent', 0), s('script:mordent', 'script:prall')),
        'turn': (counts.get('turn', 0), s('script:turn')),
        'fingering': (counts.get('fingering', 0), s('fingering')),
        'arpeggio': (counts.get('arpeggio', 0), s('arpeggio')),
        'tremolo': (counts.get('tremolo', 0), s('tremolo')),
        'breath': (counts.get('breath', 0), s('breath')),
        'hairpin-cresc': (counts.get('hairpin-cresc', 0), s('hairpin:cresc')),
        'hairpin-dim': (counts.get('hairpin-dim', 0), s('hairpin:dim')),
        'pedal': (counts.get('pedal', 0), s('pedal-mark:-1')),
        'accidentals(all)': (acc_total, s(*[k for k in eng if k.startswith('acc:')])),
        'acc-courtesy': (counts.get('acc-courtesy', 0), s(*[k for k in eng if k.startswith('acc:') and k.endswith(':paren')])),
        'ottava-8va': (counts.get('ottava-8va', 0), s('ottava:1')),
        'ottava-8vb': (counts.get('ottava-8vb', 0), s('ottava:-1')),
        'ottava-15ma': (counts.get('ottava-15ma', 0), s('ottava:2')),
        'ledger-above': (counts.get('ledger-above', 0), s('ledger-above')),
        'ledger-below': (counts.get('ledger-below', 0), s('ledger-below')),
        'lyrics': (counts.get('lyrics', 0), s('lyric')),
        'rehearsal-mark': (counts.get('rehearsal-mark', 0), s('rehearsal')),
        'tempo-mark': (counts.get('tempo-mark', 0), s('metronome-mark')),
        'volta': (counts.get('volta-1', 0) + counts.get('volta-2', 0), s('volta')),
        'rest-whole-bar': (counts.get('rest-whole-bar', 0), s('mmrest')),
        'clef-change': (counts.get('clef-change', 0), s('clef-change-grob')),
    }
    for dyn in ('pp', 'p', 'mp', 'mf', 'f', 'ff', 'sfz'):
        pairs['dyn-' + dyn] = (counts.get('dyn-' + dyn, 0), s('dyn:' + dyn))
    for k in [k for k in counts if k.startswith('tuplet-') and k[7:].isdigit()]:
        n = k[7:]
        pairs[k] = (counts[k], s(*[e for e in eng if e.startswith(f'tuplet:{n}/')]))
    rows = {k: {'truth': a, 'engraved': b, 'ok': a == b} for k, (a, b) in pairs.items()}
    fails = [k for k, r in rows.items() if not r['ok']]
    return rows, fails


# --------------------------------------------------------------------------- stage 1

def engrave(key, make, expect_pages):
    """Build + verify one engraving into _work/eng/<key>/ ; returns the result dict (also saved)."""
    t0 = time.time()
    wd = os.path.join(WORK, 'eng', key)
    shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    res = {'key': key, 'ok': False}
    try:
        score, layout, opts, info = make()
        sanitize_ties(score)
        compute_extenders(score)
        check(score)
        H.assign_ids(score)
        staff_name = {}
        for g in layout['groups']:
            for st in g['staves']:
                for pid, vk in st['voices']:
                    staff_name.setdefault((pid, score.part(pid).voice(vk).staff), st['id'])
                for ps in st.get('part_staves', []):
                    staff_name[tuple(ps)] = st['id']
        score._staff_name = staff_name
        # ---- instrumented twin
        twin = os.path.join(wd, 'twin.ly')
        open(twin, 'w', encoding='utf-8').write(LilyWriter(score, layout, opts, instrument=True).document())
        rc, err = lilypond(twin, wd)
        if rc != 0:
            raise RuntimeError('lilypond (twin) failed: ' + err[-3000:])
        rows = H.parse_log(err)
        heads, rests = H.harvest(rows)
        ver = H.verify(score, rows, heads, rests)
        res['verify_notes'] = {k: ver[k] for k in ('ok', 'checked', 'n_problems', 'problems')}
        if not ver['ok']:
            raise RuntimeError('engraving != model: ' + json.dumps(ver['problems'][:20]))
        H.merge(score, heads)
        beams = H.beam_values(score, heads)
        # tuplet bracket visibility per tuplet-start note id
        tup = {}
        idx = H.event_index(score)
        tb = {}
        for r in rows:
            if r['tag'] == 'TupletBracket' and r['when']:
                tb[(r['staff'], r['when'][0])] = bool(r['data'][2])
        for nid, (p, vk, i, t, g, ev, pit) in idx.items():
            if ev.tuplet and ev.tuplet_start and nid == ev.ids[0]:
                sn = staff_name[(p.id, ev.staff or p.voice(vk).staff)]
                tup[nid] = tb.get((sn, t))
        # key cancellations printed by LilyPond
        offs = score.measure_offsets()
        kc_t = {r['when'][0] for r in rows if r['tag'] == 'KeyCancellation' and r['when']}
        key_cancel = {i for i, o in enumerate(offs) if o in kc_t and score.measures[i].key}
        truth = os.path.join(wd, 'truth.musicxml')
        write_musicxml(score, truth, beams=beams, tuplet_vis=tup, key_cancel=key_cancel)
        rc, out, err2 = run(['xmllint', '--noout', '--schema', XSD, truth])
        if rc != 0:
            raise RuntimeError('XSD validation failed: ' + err2[-1500:])
        res['xsd_valid'] = True
        rc, out, err2 = run([PY, '-c', 'import sys,music21;s=music21.converter.parse(sys.argv[1]);'
                             'print(len(s.parts), len(s.recurse().notes), len(s.recurse().getElementsByClass("Rest")))',
                             truth], timeout=3600)
        if rc != 0:
            raise RuntimeError('music21 parse failed: ' + err2[-800:])
        res['music21'] = out.strip()
        # ---- accidental cross-check: printed (harvest) vs per-part simulation
        ls = H.line_starts(rows)
        lsm = [i for i, o in enumerate(offs) if o in set(ls)]
        staves = []
        for p in score.parts:
            for sn in range(1, p.staves + 1):
                staves.append((f'{p.id}/{sn}', [(p.id, v.key, sn) for v in p.voices]))
        sim = simulate(score, staves, lsm)
        printed = {}
        for p in score.parts:
            for m in p.measures:
                for evs in m.values():
                    for ev in evs:
                        if ev.kind == 'note':
                            for nid, pit in zip(ev.ids, ev.pitches):
                                h = heads[nid]
                                if h['acc']:
                                    printed[(id(ev), pit)] = (GLYPH[h['acc']['glyph']], h['acc']['restore_first'],
                                                              h['acc']['paren'])
        simd = {k: (v['alter'], v['restore_first'], v['paren']) for k, v in sim.items()}
        acc_diff = [str(k[1]) for k in set(simd) ^ set(printed)] + \
                   [str(k[1]) for k in set(simd) & set(printed) if simd[k] != printed[k]]
        res['accidentals'] = {'printed': len(printed), 'simulated_per_part': len(simd), 'differences': acc_diff[:20]}
        if acc_diff:
            raise RuntimeError('printed accidentals differ from per-part notation: ' + ', '.join(acc_diff[:10]))
        # ---- clean engraving
        ly = os.path.join(wd, 'engraving.ly')
        open(ly, 'w', encoding='utf-8').write(LilyWriter(score, layout, opts, instrument=False).document())
        rc, err = lilypond(ly, wd)
        warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
        res['lilypond_warnings'] = warns[:30]
        if rc != 0:
            raise RuntimeError('lilypond failed: ' + err[-3000:])
        if warns:
            raise RuntimeError('lilypond warnings: ' + '\n'.join(warns[:10]))
        pdf = os.path.join(wd, 'engraving.pdf')
        npages = pdf_pages(pdf)
        res['pages'] = npages
        if npages != expect_pages:
            raise RuntimeError(f'{npages} pages, planned {expect_pages}')
        if pdf_pages(os.path.join(wd, 'twin.pdf')) != npages or \
                raster_digest(pdf, wd, 'a') != raster_digest(os.path.join(wd, 'twin.pdf'), wd, 'b'):
            raise RuntimeError('instrumented twin layout differs from the clean engraving')
        res['twin_identical'] = True
        # ---- MIDI vs truth (independent truth reader from corpus/challenge/_validate/validate.py)
        mid = os.path.join(wd, 'engraving.midi')
        te = V.truth_events(truth)
        mc = V.midi_check(te, [mid])
        res['midi'] = {k: mc[k] for k in ('truth_attacks', 'midi_attacks', 'grace_extras', 'missing', 'extra',
                                          'notes_exact', 'truth_syllables', 'midi_syllables', 'lyrics_ok',
                                          'missing_sample', 'extra_sample', 'lyr_missing_sample')}
        if not (mc['notes_exact'] and mc['lyrics_ok']):
            raise RuntimeError('MIDI vs truth mismatch: ' + json.dumps(res['midi']))
        if te['parts'] != info['parts']:
            raise RuntimeError(f'part names {te["parts"]} != expected {info["parts"]}')
        # ---- symbol counts
        counts = symcount.count(truth)
        eng = H.engraved_counts(rows, heads)
        rows_x, fails = cross_check(counts, eng)
        res['cross_check'] = rows_x
        if fails:
            raise RuntimeError('truth vs engraved symbol counts differ: ' +
                               json.dumps({k: rows_x[k] for k in fails}))
        if eng.get('stanza'):
            counts['stanza-text'] = eng['stanza']
        res['counts'] = dict(sorted(counts.items()))
        res['engraved_counts'] = dict(sorted(eng.items()))
        res['systems'] = len(ls)
        res['measures'] = len(score.measures)
        res['notes_in_truth'] = te['n_notes']
        res['rests_in_truth'] = te['n_rests']
        res['staff_size'] = opts.get('staff_size')
        res['paper'] = score.page
        info = dict(info)
        res['info'] = info
        res['ok'] = True
    except Exception as e:
        res['error'] = repr(e)[:6000]
        res['trace'] = traceback.format_exc()[-4000:]
    res['seconds'] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(wd, 'result.json'), 'w'), indent=1, default=str)
    return res


# --------------------------------------------------------------------------- stage 2/3

def render(key, dpi):
    wd = os.path.join(WORK, 'eng', key)
    out = os.path.join(wd, f'r{dpi}')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes',
                    os.path.join(wd, 'engraving.pdf'), os.path.join(out, 'p')], check=True, timeout=7200)
    return sorted(glob.glob(os.path.join(out, 'p-*.pgm')))


def page_task(args):
    """(item_id, file_name, page_index, n_pages, key, dpi, plan) -> page image saved under _work/items"""
    iid, fname, k, n, key, dpi, plan = args
    t0 = time.time()
    src = sorted(glob.glob(os.path.join(WORK, 'eng', key, f'r{dpi}', 'p-*.pgm')))
    page = np.array(Image.open(src[k]), dtype=np.uint8)
    od = os.path.join(WORK, 'items', iid, fname)
    os.makedirs(od, exist_ok=True)
    if fname == 'clean.pdf':
        fn = os.path.join(od, f'p{k:03d}.png')
        Image.fromarray(page).save(fn, 'PNG', dpi=(dpi, dpi), optimize=False, compress_level=6)
        return {'item': iid, 'file': fname, 'page': k, 'path': fn, 'size': list(page.shape[::-1]), 'ops': [],
                'seconds': round(time.time() - t0, 2)}
    P = dict(plan['params'])
    P['dpi'] = dpi
    back = np.array(Image.open(src[k + 1 if k + 1 < n else max(0, k - 1)]), dtype=np.uint8) if P.get('bleed') else page
    seed = plan['seed'] * 1000 + k
    rng = np.random.default_rng(seed)
    sc = dpi / 300.0
    rgb, r1 = D.stage_a(page, back, P, rng, sc, 'left' if k % 2 else 'right')
    img, r2 = D.stage_b(rgb, P, rng, sc, k)
    rec = r1 + r2
    img = D.finish(img, P, k, rec)
    fmt = P.get('format', 'jpeg')
    if fmt == 'jpeg' and img.mode != '1':
        fn = os.path.join(od, f'p{k:03d}.jpg')
        img.save(fn, 'JPEG', quality=P.get('jpeg', 75), dpi=(dpi, dpi), optimize=True)
    else:
        fn = os.path.join(od, f'p{k:03d}.png')
        img.save(fn, 'PNG', dpi=(dpi, dpi), optimize=True)
    return {'item': iid, 'file': fname, 'page': k, 'path': fn, 'size': list(img.size), 'seed': seed,
            'ops': rec, 'mode': img.mode, 'seconds': round(time.time() - t0, 2)}


def image_only(pdf, n_expected):
    rc, fonts, _ = run(['pdffonts', pdf])
    font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
    rc, imgl, _ = run(['pdfimages', '-list', pdf])
    n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
    rc, txt, _ = run(['pdftotext', pdf, '-'])
    pages = pdf_pages(pdf)
    return {'fonts': len(font_lines), 'images': n_imgs, 'pages': pages, 'text_chars': len(txt.strip()),
            'image_only': not font_lines and n_imgs == pages == n_expected and not txt.strip()}
