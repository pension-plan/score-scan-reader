"""Build one synthetic-scan corpus item: truth.musicxml, engraving (LilyPond),
validation (MIDI attack multiset == truth, lyric text present in vector PDF),
rasterise + degrade -> scan.pdf (image only) and clean.pdf (undegraded raster)."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import traceback

import numpy as np

from . import degrade as D
from .lily import LilyWriter, default_layout
from .midicheck import compare
from .model import check, compute_extenders, fix_unbalanced_slurs, lyric_verses, sanitize_ties, voices_with_lyrics
from .mxl import write_musicxml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))   # corpus/synthetic


def run(cmd, cwd=None, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def lilypond(ly_path, workdir):
    base = os.path.splitext(os.path.basename(ly_path))[0]
    rc, out, err = run(['lilypond', '-dno-point-and-click', '-ddelete-intermediate-files', '-o', base,
                        os.path.basename(ly_path)], cwd=workdir)
    warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
    return rc, warns, os.path.join(workdir, base + '.pdf'), _find_midi(workdir, base)


def _find_midi(workdir, base):
    for ext in ('.midi', '.mid'):
        p = os.path.join(workdir, base + ext)
        if os.path.exists(p):
            return p
    return None


def musicxml2ly_engrave(truth, workdir, opts, single_verse):
    ly = os.path.join(workdir, 'engraving.ly')
    rc, out, err = run(['musicxml2ly', '-m', '--npl', '-o', ly, truth])
    if rc != 0:
        raise RuntimeError('musicxml2ly failed: ' + err[-500:])
    src = open(ly, encoding='utf-8').read()
    src = src.replace('\\include "articulate.ly"', '')
    k = src.find('\\unfoldRepeats \\articulate {')
    if k >= 0:
        # musicxml2ly wraps the MIDI score in a *sequential* block; make it
        # simultaneous and drop repeat unfolding/articulation (truth is notated order)
        j = k + len('\\unfoldRepeats \\articulate {')
        depth = 1
        while depth and j < len(src):
            if src[j] == '{':
                depth += 1
            elif src[j] == '}':
                depth -= 1
            j += 1
        src = src[:k] + '<<' + src[k + len('\\unfoldRepeats \\articulate {'):j - 1] + '>>' + src[j:]
    src = re.sub(r'\\midi\s*\{[^{}]*\}', lambda m: '\\midi { \\tempo 4 = 100 \\context { \\Staff \\remove "Staff_performer" } '
                 '\\context { \\Voice \\consists "Staff_performer" } }', src)
    if single_verse:
        src = src.replace('\\set stanza = "1." ', '')
    # truth carries no <beam> elements: let LilyPond beam automatically
    src = src.replace('autoBeaming = ##f', 'autoBeaming = ##t')
    pre = []
    if opts.get('staff_size'):
        pre.append(f'#(set-global-staff-size {opts["staff_size"]})')
    paper = ['\\paper {', f'  #(set-paper-size "{opts.get("paper", "a4")}")']
    if opts.get('font'):
        paper.append(f'  property-defaults.fonts.serif = "{opts["font"]}"')
    paper += ['  ' + x for x in opts.get('paper_extra', [])]
    paper.append('}')
    hdr = opts.get('header', {})
    hextra = ['  tagline = ##f']
    for k in ('subtitle', 'poet', 'arranger', 'meter', 'opus', 'title', 'composer'):
        if hdr.get(k):
            v = hdr[k].replace('"', '\\"')
            hextra.append(f'  {k} = "{v}"')
    src = re.sub(r'(\\version "[^"]+")', lambda m: m.group(1) + '\n' + '\n'.join(pre), src, count=1)
    # our header/paper after musicxml2ly's header (later blocks override)
    idx = src.find('\\layout {')
    block = '\\header {\n' + '\n'.join(hextra) + '\n}\n' + '\n'.join(paper) + '\n'
    if idx < 0:
        idx = src.find('% The score definition')
    src = src[:idx] + block + src[idx:]
    for a, b in opts.get('m2l_replace', []):
        src = src.replace(a, b)
    open(ly, 'w', encoding='utf-8').write(src)
    return ly


def lyric_text_check(score, pdf):
    """fraction of truth syllables (all verses) found as substrings in pdftotext output"""
    rc, out, err = run(['pdftotext', '-layout', pdf, '-'])
    text = re.sub(r'\s+', ' ', out)
    flat = text.replace('-', '').replace(' ', '')
    syls = []
    for pid, vk, vs in voices_with_lyrics(score):
        p = score.part(pid)
        for m in p.measures:
            for ev in m.get(vk, []):
                for ly in ev.lyrics.values():
                    syls.append(ly.text)
    if not syls:
        return None
    found = 0
    for s_ in syls:
        core = re.sub(r'[\W_]+', '', s_)
        if not core or core in flat or s_ in text:
            found += 1
    return round(found / len(syls), 4)


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
        truth = os.path.join(outdir, 'truth.musicxml')
        write_musicxml(score, truth)
        # sanity: music21 can parse the truth
        engraver = item.get('engraver', 'lily')
        single_verse = all(len(vs) <= 1 for _, _, vs in voices_with_lyrics(score))
        tried = []
        result = None
        for eng in ([engraver] + (['lily'] if engraver != 'lily' else [])):
            if eng == 'musicxml2ly':
                ly = musicxml2ly_engrave(truth, workdir, opts, single_verse)
            else:
                lay = layout or default_layout(score)
                ly = os.path.join(workdir, 'engraving.ly')
                open(ly, 'w', encoding='utf-8').write(LilyWriter(score, lay, opts).document())
            rc, warns, pdf, mid = lilypond(ly, workdir)
            cmp_ = compare(score, mid) if (rc == 0 and mid) else {'ok': False, 'error': 'no midi'}
            bad_warn = [w for w in warns if 'barcheck' in w or 'error' in w]
            tried.append({'engraver': eng, 'rc': rc, 'midi': cmp_, 'warnings': warns[:20]})
            if rc == 0 and cmp_.get('ok') and not bad_warn:
                result = (eng, ly, pdf)
                break
        log['engrave_attempts'] = tried
        if result is None:
            raise RuntimeError(f'engraving validation failed: {json.dumps(tried, default=str)[:3000]}')
        eng, ly, pdf = result
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        log['engraver'] = 'musicxml2ly+lilypond' if eng == 'musicxml2ly' else 'model->lilypond (custom writer)'
        log['lyric_text_found'] = lyric_text_check(score, pdf)
        rc, out, err = run(['pdfinfo', pdf])
        pages_vec = int(re.search(r'Pages:\s+(\d+)', out).group(1))
        # raster + degrade
        P = dict(item['degrade'])
        dpi = P['dpi']
        pages = D.render_pages(pdf, dpi, workdir)
        rng = np.random.default_rng(item.get('seed', abs(hash(iid)) % 2 ** 32))
        imgs = [D.degrade(pg, P, rng) for pg in pages]
        fmt = P.get('format', 'jpeg')
        scan = os.path.join(outdir, 'scan.pdf')
        D.save_pdf(imgs, dpi, scan, fmt='png' if fmt in ('png', 'png1') else 'jpeg',
                   quality=P.get('jpeg', 75), jpeg_passes=P.get('jpeg_passes', 1))
        from PIL import Image
        clean_imgs = [Image.fromarray(pg) for pg in pages]
        D.save_pdf(clean_imgs, dpi, os.path.join(outdir, 'clean.pdf'), fmt='png')
        # verify image-only
        rc, fonts, _ = run(['pdffonts', scan])
        font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
        rc, imgl, _ = run(['pdfimages', '-list', scan])
        n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
        rc, txt, _ = run(['pdftotext', scan, '-'])
        log.update({
            'pages': len(pages), 'vector_pages': pages_vec, 'image_only': not font_lines and n_imgs == len(pages)
            and not txt.strip(), 'n_images': n_imgs, 'fonts': font_lines,
            'scan_bytes': os.path.getsize(scan), 'pixel_size': [int(pages[0].shape[1]), int(pages[0].shape[0])],
        })
        # metadata
        parts = [p.name for p in score.parts]
        lyr = []
        for pid, vk, vs in voices_with_lyrics(score):
            lyr.append({'part': score.part(pid).name, 'verses': len(vs)})
        meta = {
            'id': iid, 'title': item['title'],
            'expected_parts': parts,
            'lyrics': lyr,
            'shared_staves': item.get('shared_staves', []),
            'layout': item.get('layout_desc', ''),
            'degradation_params': P,
            'degradations': D.describe(P),
            'engraver': log['engraver'],
            'validation': {
                'midi_attacks_match_truth': True,
                'attacks': tried[-1]['midi']['expected_attacks'],
                'lyric_text_found_in_engraving': log['lyric_text_found'],
                'image_only': log['image_only'],
            },
            'pages': len(pages),
            'measures': len(score.measures),
        }
        with open(os.path.join(outdir, 'meta.json'), 'w') as f:
            json.dump(meta, f, indent=2, default=str)
        with open(os.path.join(outdir, 'ATTRIBUTION.txt'), 'w') as f:
            f.write(item['attribution'].strip() + '\n')
        entry = {
            'id': iid, 'title': item['title'], 'source_url': item['source_url'], 'license': item['license'],
            'origin': 'synthetic-scan', 'dpi': dpi, 'degradations': D.describe(P),
            'has_ground_truth': True, 'features': item['features'], 'expected_parts': parts,
            'shared_staves': item.get('shared_staves', []),
            'lyrics_parts': lyr,
            'pages': len(pages), 'measures': len(score.measures),
            'engraver': log['engraver'],
            'scan': f'synthetic/{iid}/scan.pdf', 'truth': f'synthetic/{iid}/truth.musicxml',
            'clean': f'synthetic/{iid}/clean.pdf', 'engraving': f'synthetic/{iid}/engraving.ly',
            'attribution': f'synthetic/{iid}/ATTRIBUTION.txt',
            'notes': item.get('notes', ''),
        }
        log['ok'] = True
        log['entry'] = entry
    except Exception as e:
        log['ok'] = False
        log['error'] = repr(e)
        log['trace'] = traceback.format_exc()[-4000:]
    log['seconds'] = round(time.time() - t0, 1)
    if not keep_work and log.get('ok'):
        shutil.rmtree(workdir, ignore_errors=True)
    return log
