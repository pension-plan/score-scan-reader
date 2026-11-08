"""Build one lyrics-challenge item.

  model (items.py) -> truth.musicxml (MusicXML 4.0, XSD-validated with xmllint)
                   -> engraving.ly (custom writer) -> LilyPond vector PDF + MIDI
  validation:  * MIDI (one track per Voice) reproduces the truth (onset, pitch) multiset
               * MIDI lyric tracks reproduce every truth lyric line exactly:
                 same (onset, syllable) sequence, elisions joined with U+203F
               * every syllable / text-block line found in the vector PDF text
               * no bar-check warnings, LilyPond rc 0
  raster:      pdftoppm -gray at each recipe dpi -> scan.py damage ->
               scan.pdf / scan-mild.pdf / scan-severe.pdf (image only, verified with
               pdffonts / pdfimages / pdftotext), clean.pdf (undamaged 300 dpi raster)
"""
from __future__ import annotations

import copy
import glob
import json
import os
import re
import shutil
import subprocess
import time
import traceback
import unicodedata

import numpy as np
from PIL import Image

import scan as S
from synth.lily import LilyWriter, default_layout
from synth.midicheck import compare, compare_lyrics
from synth.model import check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voices_with_lyrics
from synth.mxl import write_musicxml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))   # corpus/challenge/lyrics
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
CATEGORY = 'lyrics'


def run(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def lilypond(ly_path, workdir):
    base = os.path.splitext(os.path.basename(ly_path))[0]
    rc, out, err = run(['lilypond', '-dno-point-and-click', '-o', base, os.path.basename(ly_path)], cwd=workdir,
                       timeout=600)
    warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
    midi = None
    for ext in ('.midi', '.mid'):
        if os.path.exists(os.path.join(workdir, base + ext)):
            midi = os.path.join(workdir, base + ext)
    return rc, warns, os.path.join(workdir, base + '.pdf'), midi, err


def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'\s+', ' ', s)


def pdf_text_pages(pdf):
    rc, out, _ = run(['pdfinfo', pdf])
    n = int(re.search(r'Pages:\s+(\d+)', out).group(1))
    pages = []
    for k in range(1, n + 1):
        rc, t, _ = run(['pdftotext', '-f', str(k), '-l', str(k), '-raw', pdf, '-'])
        pages.append(norm(t))
    return pages


def text_check(score, pages_text, layout_labels):
    """syllables (each elided part separately) + text-block lines + stanza labels"""
    full = ' '.join(pages_text)
    flat = re.sub(r'[\s\-‿]', '', full)
    miss = []
    n = 0
    for pid, vk, vs in voices_with_lyrics(score):
        p = score.part(pid)
        for m in p.measures:
            for ev in m.get(vk, []):
                for ly in ev.lyrics.values():
                    for t in [ly.text] + [x for _, x in ly.elided]:
                        n += 1
                        core = re.sub(r'\s', '', norm(t))
                        if core not in flat:
                            miss.append(t)
    stanza_found = []
    for st in score.text_stanzas:
        for line in st['lines']:
            n += 1
            if re.sub(r'\s', '', norm(line)) not in flat:
                miss.append(line)
        pg = [k + 1 for k, t in enumerate(pages_text)
              if re.sub(r'\s', '', norm(st['lines'][0])) in re.sub(r'[\s\-]', '', t)]
        stanza_found.append(pg[0] if pg else None)
    labels_missing = [lab for lab in layout_labels if lab and lab not in full]
    return {'checked': n, 'missing': miss[:20], 'n_missing': len(miss), 'stanza_pages': stanza_found,
            'labels_missing': labels_missing}


def render_gray(pdf, dpi, workdir):
    prefix = os.path.join(workdir, f'r{dpi}')
    files = sorted(glob.glob(prefix + '-*.pgm'))
    if not files:
        subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-aa', 'yes', '-aaVector', 'yes', pdf, prefix],
                       check=True, timeout=600)
        files = sorted(glob.glob(prefix + '-*.pgm'))
    return [np.array(Image.open(f), dtype=np.uint8) for f in files]


def image_only(pdf):
    rc, fonts, _ = run(['pdffonts', pdf])
    font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
    rc, imgl, _ = run(['pdfimages', '-list', pdf])
    n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
    rc, txt, _ = run(['pdftotext', pdf, '-'])
    rc, info, _ = run(['pdfinfo', pdf])
    pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    return {'image_only': not font_lines and n_imgs == pages and not txt.strip(), 'fonts': font_lines,
            'images': n_imgs, 'pages': pages}


def xsd_validate(path):
    rc, out, err = run(['xmllint', '--noout', '--schema', XSD, path], timeout=300)
    return rc == 0, (err or out).strip()[-500:]


def layout_labels(layout):
    labs = []
    for g in layout['groups']:
        for st in g['staves']:
            for l in st.get('lyrics', []):
                for vn in l['verses']:
                    lab = l.get('labels', {}).get(vn, f'{vn}.' if l.get('stanza', len(l['verses']) > 1) else '')
                    labs.append(lab)
    return labs


def build_item(item: dict, keep_work=False):
    t0 = time.time()
    iid = item['id']
    outdir = os.path.join(ROOT, iid)
    workdir = os.path.join(ROOT, '_work', iid)
    shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        os.remove(os.path.join(outdir, f))
    log = {'id': iid}
    try:
        score, layout, opts = item['make']()
        sanitize_ties(score)
        fix_unbalanced_slurs(score)
        compute_extenders(score)
        check(score)
        layout = layout or default_layout(score)
        truth = os.path.join(outdir, 'truth.musicxml')
        # ---- engrave + verify
        ly = os.path.join(workdir, 'engraving.ly')
        open(ly, 'w', encoding='utf-8').write(LilyWriter(score, layout, opts).document())
        rc, warns, pdf, mid, err = lilypond(ly, workdir)
        if rc != 0 or not mid:
            raise RuntimeError('lilypond failed: ' + err[-2000:])
        bad = [w for w in warns if 'barcheck' in w or 'error' in w]
        notes = compare(score, mid)
        lyr = compare_lyrics(score, mid)
        pages_text = pdf_text_pages(pdf)
        txt = text_check(score, pages_text, layout_labels(layout))
        log.update({'warnings': warns[:30], 'midi_notes': notes, 'midi_lyrics': lyr, 'pdf_text': txt})
        if bad or not notes['ok'] or not lyr['ok'] or txt['n_missing'] or txt['labels_missing']:
            raise RuntimeError('validation failed: ' + json.dumps(
                {'bad_warn': bad, 'notes': notes, 'lyrics': lyr, 'text': txt}, default=str)[:4000])
        # text-block stanzas: record the page they were printed on
        for st, pg in zip(score.text_stanzas, txt['stanza_pages']):
            st['page'] = pg or 1
        write_musicxml(score, truth)
        ok, msg = xsd_validate(truth)
        if not ok:
            raise RuntimeError('XSD validation failed: ' + msg)
        log['xsd'] = msg
        for alt_name, alt_fn in item.get('alt_truths', {}).items():
            sc2 = alt_fn(copy.deepcopy(score))
            p2 = os.path.join(outdir, alt_name)
            write_musicxml(sc2, p2)
            ok2, msg2 = xsd_validate(p2)
            if not ok2:
                raise RuntimeError(f'XSD validation failed for {alt_name}: {msg2}')
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        n_vec_pages = len(pages_text)
        # ---- clean raster
        clean_pages = render_gray(pdf, 300, workdir)
        S.save_pdf([Image.fromarray(p, 'L') for p in clean_pages], 300, os.path.join(outdir, 'clean.pdf'))
        # ---- damaged scans
        deg_meta = {}
        checks = {}
        for fname, recipe in item['scans'].items():
            pages = render_gray(pdf, recipe['dpi'], workdir)
            imgs, plog = S.damage_pages(pages, recipe)
            out_pdf = os.path.join(outdir, fname)
            S.save_pdf(imgs, recipe['dpi'], out_pdf, jpeg=recipe.get('jpeg'), jpeg_passes=recipe.get('jpeg_passes', 1))
            chk = image_only(out_pdf)
            if not chk['image_only']:
                raise RuntimeError(f'{fname} is not image-only: {chk}')
            checks[fname] = chk
            deg_meta[fname] = {
                'seed': recipe['seed'], 'dpi': recipe['dpi'], 'mode': recipe.get('mode', 'gray'),
                'jpeg_quality': recipe.get('jpeg'), 'jpeg_passes': recipe.get('jpeg_passes', 1),
                'binarize': recipe.get('binarize'),
                'page_ops': recipe.get('page_ops', []), 'ops': recipe['ops'],
                'tags': S.tags_for(recipe), 'output_pages': len(imgs),
                'page_pixels': [pl['size_px'] for pl in plog],
                'annotations': [pl['events'] for pl in plog if pl['events']],
                'bytes': os.path.getsize(out_pdf),
            }
        # ---- meta
        parts = [p.name for p in score.parts]
        lyric_lines = []
        for pid, vk, vs in voices_with_lyrics(score):
            p = score.part(pid)
            for vn in vs:
                nsyl = sum(1 for m in p.measures for ev in m.get(vk, []) if vn in ev.lyrics)
                nel = sum(len(ev.lyrics[vn].elided) for m in p.measures for ev in m.get(vk, []) if vn in ev.lyrics)
                ne = sum(1 for m in p.measures for ev in m.get(vk, []) if vn in ev.lyrics and ev.lyrics[vn].extend)
                la = score.lyric_line_attrs.get(vn, {})
                lyric_lines.append({'part': p.name, 'lyric_number': vn, 'syllables': nsyl, 'elisions': nel,
                                    'extenders': ne, **({'italic': True} if la.get('italic') else {}),
                                    **({'name': la['name']} if la.get('name') else {})})
        exp = dict(item['expected'])
        exp.setdefault('parts', parts)
        assert exp['parts'] == parts, (exp['parts'], parts)
        meta = {
            'id': iid, 'category': CATEGORY, 'title': item['title'],
            'edge_cases': item['edge_cases'],
            'expected': exp,
            'lyric_lines': lyric_lines,
            'text_block_stanzas': [{'label': st.get('label'), 'lines': st['lines'], 'page': st.get('page')}
                                   for st in score.text_stanzas],
            'degradations': deg_meta,
            'dpi': item['scans']['scan.pdf']['dpi'],
            'license': item['license'],
            'source': item['source'],
            'files': sorted(os.listdir(outdir)) + ['meta.json', 'ATTRIBUTION.txt'],
            'measures': len(score.measures),
            'engraved_pages': n_vec_pages,
            'validation': {
                'truth_xsd_valid': True,
                'midi_attacks_match_truth': notes['ok'], 'attacks': notes['expected_attacks'],
                'midi_lyrics_match_truth': lyr['ok'], 'lyric_lines_checked': lyr['lines_expected'],
                'syllables_checked': lyr['syllables'],
                'pdf_text_items_checked': txt['checked'], 'pdf_text_missing': txt['n_missing'],
                'scans_image_only': {k: v['image_only'] for k, v in checks.items()},
                'lilypond_warnings': warns[:10],
            },
            'engraver': 'model -> LilyPond 2.24 (custom writer, corpus/challenge/lyrics/_tools)',
        }
        with open(os.path.join(outdir, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False, default=str)
        with open(os.path.join(outdir, 'ATTRIBUTION.txt'), 'w', encoding='utf-8') as f:
            f.write(item['attribution'].strip() + '\n')
        meta['files'] = sorted(os.listdir(outdir))
        with open(os.path.join(outdir, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False, default=str)
        log['ok'] = True
        log['meta'] = meta
    except Exception as e:
        log['ok'] = False
        log['error'] = repr(e)[:6000]
        log['trace'] = traceback.format_exc()[-4000:]
    log['seconds'] = round(time.time() - t0, 1)
    if not keep_work and log.get('ok'):
        shutil.rmtree(workdir, ignore_errors=True)
    return log
