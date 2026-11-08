"""Build one challenge/voices item.

  truth.musicxml  <- model (mxl.py, MusicXML 4.0 partwise), XSD-validated with xmllint
  engraving.ly    <- model + staff layout (lily.py, closed score / shared staves)
  validation      : LilyPond MIDI, one track per Voice, must equal the printed attacks of the
                    corresponding truth voice exactly (onset, pitch); notes engraved as
                    spacers (a2 / unis.) must be duplicated by a printed carrier on the same
                    staff; every lyric line's MIDI lyric events == truth (onset, syllable);
                    truth.musicxml re-parsed with music21 == model (attacks + lyrics per part);
                    no LilyPond warnings
  clean.pdf       : undamaged raster (300 dpi, PNG, image only)
  scan*.pdf       : damaged rasters (degrade2.py), image only (pdffonts / pdfimages / pdftotext)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import traceback
from collections import Counter
from fractions import Fraction as F

from . import degrade2 as D
from .lily import LilyWriter, vname
from .midicheck import check_hidden_carriers, compare_detailed, lyricsto_expected, voice_attacks
from .model import check, compute_extenders, fix_unbalanced_slurs, sanitize_ties, voice_events
from .mxl import write_musicxml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))   # corpus/challenge/voices
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
CC0_NOTE = ('Engraving, rasterisation and damage simulation produced by the challenge/voices generator '
            '(corpus/challenge/voices/_tools); all derived files are dedicated to the public domain (CC0 1.0).')


def run(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def lilypond(ly_path, workdir):
    base = os.path.splitext(os.path.basename(ly_path))[0]
    rc, out, err = run(['lilypond', '-dno-point-and-click', '-o', base, os.path.basename(ly_path)], cwd=workdir)
    warns = [l for l in err.splitlines() if re.search(r'(warning|error):', l)]
    mid = None
    for ext in ('.midi', '.mid'):
        if os.path.exists(os.path.join(workdir, base + ext)):
            mid = os.path.join(workdir, base + ext)
    return rc, warns, os.path.join(workdir, base + '.pdf'), mid, err


def xsd_check(path):
    rc, out, err = run(['xmllint', '--noout', '--nonet', '--schema', XSD, path])
    return rc == 0, (err.strip().splitlines() or [''])[-1]


def truth_roundtrip(score, path):
    """music21 parse of the written truth == model (per part attacks incl. hidden, lyrics)."""
    from music21 import converter
    s = converter.parse(path)
    exp_att = {}
    for (pid, vk), c in voice_attacks(score, include_hidden=True).items():
        exp_att.setdefault(pid, Counter()).update(c)
    errors = []
    # music21 splits a multi-staff part into PartStaff objects ("<id>-Staff<n>"): regroup them
    groups = []
    for pm in s.parts:
        base = pm.id.rsplit('-Staff', 1)[0] if type(pm).__name__ == 'PartStaff' else None
        if base is not None and groups and groups[-1][0] == base:
            groups[-1][1].append(pm)
        else:
            groups.append((base, [pm]))
    if len(groups) != len(score.parts):
        return {'ok': False, 'errors': [f'{len(groups)} parts parsed, {len(score.parts)} expected']}
    for (_, pms), p in zip(groups, score.parts):
        if p.staves != len(pms):
            errors.append(f'{p.id}: {len(pms)} staves parsed, {p.staves} expected')
        got = Counter()
        lyr = Counter()
        for n in (n for pm in pms for n in pm.flatten().notes):
            off = F(n.offset).limit_denominator(10000)
            subs = list(n.notes) if n.isChord else [n]
            for x in subs:
                tie = x.tie if x.tie is not None else (n.tie if n.isChord else None)
                if tie is not None and tie.type in ('stop', 'continue'):
                    continue
                got[(off, x.pitch.midi)] += 1
            for l in n.lyrics:
                lyr[(off, int(l.number), l.text)] += 1
        exp_l = Counter()
        for v in p.voices:
            for i, t, ev in voice_events(score, p, v.key):
                if ev.kind == 'note':
                    for num, ly in ev.lyrics.items():
                        exp_l[(F(t), num, ly.text)] += 1
        if got != exp_att[p.id]:
            errors.append(f'{p.id}: attacks differ missing={list((exp_att[p.id]-got).elements())[:4]} '
                          f'extra={list((got-exp_att[p.id]).elements())[:4]}')
        if lyr != exp_l:
            errors.append(f'{p.id}: lyrics differ missing={list((exp_l-lyr).elements())[:4]} '
                          f'extra={list((lyr-exp_l).elements())[:4]}')
    return {'ok': not errors, 'errors': errors,
            'attacks': sum(sum(c.values()) for c in exp_att.values())}


def lyric_text_check(score, pdf):
    rc, out, err = run(['pdftotext', '-layout', pdf, '-'])
    flat = re.sub(r'[\s\-]+', '', out)
    syls = []
    for p in score.parts:
        for v in p.voices:
            for i, t, ev in voice_events(score, p, v.key):
                if ev.kind == 'note' and not ev.hidden:
                    syls += [ly.text for ly in ev.lyrics.values()]
    if not syls:
        return None
    found = sum(1 for s_ in syls if (re.sub(r'[\W_]+', '', s_) or '#') in re.sub(r'[\W_]+', '', flat)
                or not re.sub(r'[\W_]+', '', s_))
    return round(found / len(syls), 4)


def staff_map(layout):
    m = {}
    for g in layout['groups']:
        for st in g['staves']:
            for pv in st['voices']:
                m[tuple(pv)] = st['id']
    return m


def image_only(pdf, n_expected):
    rc, fonts, _ = run(['pdffonts', pdf])
    font_lines = [l for l in fonts.splitlines()[2:] if l.strip()]
    rc, imgl, _ = run(['pdfimages', '-list', pdf])
    n_imgs = len([l for l in imgl.splitlines()[2:] if l.strip()])
    rc, txt, _ = run(['pdftotext', pdf, '-'])
    rc, info, _ = run(['pdfinfo', pdf])
    pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
    return {'image_only': not font_lines and n_imgs == pages and not txt.strip(), 'fonts': font_lines,
            'images': n_imgs, 'pages': pages}


def build_item(item: dict, keep_work=False, only_scans=None):
    t0 = time.time()
    iid = item['id']
    outdir = os.path.join(ROOT, iid)
    workdir = os.path.join(ROOT, '_work', iid)
    shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)
    log = {'id': iid}
    try:
        score, layout, opts = item['make']()
        sanitize_ties(score)
        fix_unbalanced_slurs(score)
        compute_extenders(score)
        check(score)
        truth = os.path.join(workdir, 'truth.musicxml')
        write_musicxml(score, truth)
        ok_xsd, xsd_msg = xsd_check(truth)
        log['xsd'] = xsd_msg
        if not ok_xsd:
            raise RuntimeError('XSD validation failed: ' + xsd_msg)
        rt = truth_roundtrip(score, truth)
        log['truth_roundtrip'] = rt
        if not rt['ok']:
            raise RuntimeError('truth roundtrip failed: ' + '; '.join(rt['errors']))
        ly = os.path.join(workdir, 'engraving.ly')
        lw = LilyWriter(score, layout, opts)
        open(ly, 'w', encoding='utf-8').write(lw.document())
        rc, warns, pdf, mid, err = lilypond(ly, workdir)
        log['lily_warnings'] = warns
        if rc != 0 or not mid:
            raise RuntimeError('lilypond failed: ' + err[-2500:])
        allowed = item.get('allowed_warnings', [])
        bad = [w for w in warns if not any(a in w for a in allowed)]
        if bad:
            raise RuntimeError('lilypond warnings: ' + ' | '.join(bad[:10]))
        lines = []
        for ln in lw.lyric_lines:
            if ln['kind'] == 'lyricsto':
                ln = dict(ln, expected=lyricsto_expected(score, ln['voice'][0], ln['voice'][1], ln['verse']))
            lines.append(ln)
        cmpd = compare_detailed(score, mid, lines, vname)
        log['midi_check'] = cmpd
        if not cmpd['ok']:
            raise RuntimeError('MIDI/lyric check failed: ' + ' | '.join(cmpd['errors'])[:3000])
        # every truth syllable must be printed in some lyric line
        printed = Counter()
        for ln in lines:
            printed.update(ln['expected'])
        truth_syl = Counter()
        for p in score.parts:
            for v in p.voices:
                for i, t, ev in voice_events(score, p, v.key):
                    if ev.kind == 'note':
                        for ly_ in ev.lyrics.values():
                            truth_syl[(F(t), ly_.text)] += 1
        unprinted = truth_syl - printed
        # identical syllables at the same onset in two voices printed once are allowed only if declared
        if unprinted and not item.get('shared_lyric_ok'):
            raise RuntimeError(f'truth syllables not printed: {list(unprinted.elements())[:6]}')
        hid = check_hidden_carriers(score, staff_map(layout))
        log['hidden_check'] = hid
        if not hid['ok']:
            raise RuntimeError('hidden carrier check failed: ' + '; '.join(hid['errors'][:5]))
        log['lyric_text_found_in_vector_pdf'] = lyric_text_check(score, pdf)
        rc, out, _ = run(['pdfinfo', pdf])
        vec_pages = int(re.search(r'Pages:\s+(\d+)', out).group(1))
        if item.get('pages') and vec_pages != item['pages']:
            raise RuntimeError(f'expected {item["pages"]} pages, engraved {vec_pages}')
        # ---- outputs
        for f in os.listdir(outdir):
            if only_scans is None or f.startswith('scan'):
                os.remove(os.path.join(outdir, f))
        shutil.copy(truth, os.path.join(outdir, 'truth.musicxml'))
        shutil.copy(ly, os.path.join(outdir, 'engraving.ly'))
        # clean raster
        clean_pages = D.render_pages(pdf, 300, workdir, tag='c')
        from PIL import Image
        D.save_pdf([Image.fromarray(p) for p in clean_pages], 300, os.path.join(outdir, 'clean.pdf'), fmt='png')
        anchors_px = {}
        degr_meta = {}
        file_checks = {}
        for name, R in item['scans'].items():
            if only_scans and name not in only_scans:
                continue
            dpi = R['dpi']
            pages = D.render_pages(pdf, dpi, workdir, tag=f'p{dpi}_')
            if dpi not in anchors_px:
                anchors_px[dpi] = D.svg_anchors(ly, workdir, [(p.shape[1], p.shape[0]) for p in pages])
            ext = [D.staff_extent(p) for p in pages]
            imgs, out_dpi, dlog = D.degrade_document(pages, R, R['seed'], dpi, anchors_px[dpi], ext)
            outp = os.path.join(outdir, name + '.pdf')
            fmt = R.get('format', 'jpeg')
            D.save_pdf(imgs, out_dpi, outp, fmt=fmt, quality=R.get('quality', 60),
                       jpeg_passes=R.get('jpeg_passes', 1))
            chk = image_only(outp, len(imgs))
            file_checks[name] = chk
            if not chk['image_only']:
                raise RuntimeError(f'{name}.pdf is not image-only: {chk}')
            degr_meta[name + '.pdf'] = {
                'seed': R['seed'], 'render_dpi': dpi, 'output_dpi': round(out_dpi, 2), 'mode': R.get('mode', 'rgb'),
                'format': fmt, 'jpeg_quality': R.get('quality') if fmt == 'jpeg' else None,
                'jpeg_passes': R.get('jpeg_passes', 1) if fmt == 'jpeg' else None,
                'binarize': R.get('binarize') if R.get('mode') == 'bilevel' else None,
                'spread_2up': R.get('spread'),
                'ops': R['ops'], 'summary': R.get('summary', ''),
                'pdf_pages': chk['pages'], 'events': dlog,
            }
        log['files'] = file_checks
        if only_scans:
            old = json.load(open(os.path.join(outdir, 'meta.json')))
            old['degradations'].update(degr_meta)
            degr_meta = old['degradations']
        meta = {
            'id': iid, 'category': 'voices', 'title': item['title'],
            'edge_cases': item['edge_cases'],
            'expected': item['expected'],
            'degradations': degr_meta,
            'dpi': degr_meta['scan.pdf']['output_dpi'],
            'dpi_note': 'output resolution of scan.pdf (render_dpi / output_dpi per file under degradations)',
            'license': item['license'],
            'source': item['source'],
            'files': {'truth': 'truth.musicxml', 'engraving': 'engraving.ly', 'clean': 'clean.pdf',
                      'scans': sorted(k + '.pdf' for k in item['scans'])},
            'pages_engraved': vec_pages, 'measures': len(score.measures),
            'parts_truth': [{'id': p.id, 'name': p.name, 'voices': len(p.voices), 'staves': p.staves}
                            for p in score.parts],
            'lyric_lines_printed': [{k: (list(v) if isinstance(v, tuple) else v) for k, v in ln.items()
                                     if k != 'expected'} | {'syllables': len(ln['expected'])} for ln in lines],
            'validation': {
                'xsd': xsd_msg,
                'truth_reparsed_music21_matches_model': True,
                'midi_per_voice_matches_printed_truth': True,
                'midi_lyrics_match_truth': True,
                'attacks_truth': rt['attacks'],
                'attacks_hidden_in_engraving_carried_by_other_voice': hid['hidden_events'],
                'lyric_text_found_in_vector_pdf': log['lyric_text_found_in_vector_pdf'],
                'lilypond_warnings': warns,
                'scan_files_image_only': {k: v['image_only'] for k, v in file_checks.items()},
            },
            'truth_limitations': item.get('truth_limitations', []),
        }
        with open(os.path.join(outdir, 'meta.json'), 'w') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False, default=str)
        with open(os.path.join(outdir, 'ATTRIBUTION.txt'), 'w') as f:
            f.write(item['attribution'].strip() + '\n\n' + CC0_NOTE + '\n')
        log['ok'] = True
        log['meta'] = meta
    except Exception as e:
        log['ok'] = False
        log['error'] = repr(e)[:4000]
        log['trace'] = traceback.format_exc()[-4000:]
    log['seconds'] = round(time.time() - t0, 1)
    if not keep_work and log.get('ok'):
        shutil.rmtree(workdir, ignore_errors=True)
    return log
