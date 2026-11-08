#!/usr/bin/env python3
"""Independent end-to-end check of the published files (not the build model):

  * truth.musicxml (and any truth-*.musicxml) validates against the MusicXML 4.0 XSD
  * engraving.ly is re-rendered by LilyPond; its MIDI (onset, pitch) multiset equals
    the one computed straight from truth.musicxml (ElementTree, backup/forward/chord aware)
  * every lyric line of truth.musicxml (part, lyric number) equals one MIDI lyric track
    ((onset, text) sequence; elided parts joined with U+203F)
  * every scan*.pdf is image-only (no fonts, one image per page, no extractable text)

usage: /Users/d.sloane/music/.venv/bin/python corpus/challenge/lyrics/_tools/verify.py
"""
import glob
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from synth.midicheck import read_midi  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))
XSD = '/Users/d.sloane/music/mvp/work/schema/musicxml.xsd'
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def truth_events(path):
    root = ET.parse(path).getroot()
    notes = Counter()
    lyrics = {}
    for part in root.findall('part'):
        pid = part.get('id')
        div = 1
        t = F(0)
        for meas in part.findall('measure'):
            last_onset = t
            for el in meas:
                if el.tag == 'attributes' and el.find('divisions') is not None:
                    div = int(el.find('divisions').text)
                elif el.tag == 'backup':
                    t -= F(int(el.find('duration').text), div)
                elif el.tag == 'forward':
                    t += F(int(el.find('duration').text), div)
                elif el.tag == 'note':
                    d = F(int(el.find('duration').text), div)
                    chord = el.find('chord') is not None
                    on = last_onset if chord else t
                    if not chord:
                        last_onset = t
                        t += d
                    p = el.find('pitch')
                    if p is not None:
                        tied_stop = any(x.get('type') == 'stop' for x in el.findall('tie'))
                        if not tied_stop:
                            m = 12 * (int(p.find('octave').text) + 1) + STEP[p.find('step').text] + \
                                int(p.find('alter').text if p.find('alter') is not None else 0)
                            notes[(on, m)] += 1
                    v = el.find('voice').text
                    for ly in el.findall('lyric'):
                        txt = '‿'.join(x.text or '' for x in ly.findall('text'))
                        lyrics.setdefault((pid, v, ly.get('number')), []).append((on, txt))
    return notes, {k: tuple(v) for k, v in lyrics.items()}


def midi_events(midi):
    div, tracks = read_midi(midi)
    notes = Counter()
    lines = []
    for tr in tracks:
        for t, p in tr['notes']:
            notes[(F(t, div), p)] += 1
        seq = tuple((F(t, div), x) for t, x in tr['lyr5'] if x.strip())
        if seq:
            lines.append(seq)
    return notes, lines


def image_only(pdf):
    fonts = subprocess.run(['pdffonts', pdf], capture_output=True, text=True).stdout.splitlines()[2:]
    imgs = subprocess.run(['pdfimages', '-list', pdf], capture_output=True, text=True).stdout.splitlines()[2:]
    txt = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
    info = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
    pages = int([l for l in info.splitlines() if l.startswith('Pages:')][0].split()[1])
    return not [l for l in fonts if l.strip()] and len([l for l in imgs if l.strip()]) == pages and not txt.strip()


def main():
    report = {}
    ok_all = True
    for d in sorted(glob.glob(os.path.join(ROOT, 'lyr*'))):
        iid = os.path.basename(d)
        r = {}
        for tx in sorted(glob.glob(os.path.join(d, 'truth*.musicxml'))):
            rc = subprocess.run(['xmllint', '--noout', '--schema', XSD, tx], capture_output=True, text=True,
                                timeout=300)
            r['xsd:' + os.path.basename(tx)] = rc.returncode == 0
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(['cp', os.path.join(d, 'engraving.ly'), td])
            subprocess.run(['lilypond', '-dno-point-and-click', '-o', 'e', 'engraving.ly'], cwd=td,
                           capture_output=True, timeout=600)
            mid = os.path.join(td, 'e.midi') if os.path.exists(os.path.join(td, 'e.midi')) else os.path.join(td, 'e.mid')
            mn, ml = midi_events(mid)
        tn, tl = truth_events(os.path.join(d, 'truth.musicxml'))
        r['notes_match'] = mn == tn
        r['notes'] = sum(tn.values())
        remaining = list(ml)
        miss = []
        for k, seq in tl.items():
            if seq in remaining:
                remaining.remove(seq)
            else:
                miss.append(k)
        r['lyric_lines'] = len(tl)
        r['lyrics_match'] = not miss and not remaining
        if miss:
            r['lyric_lines_missing'] = [list(k) for k in miss]
        r['scans_image_only'] = {os.path.basename(p): image_only(p) for p in sorted(glob.glob(os.path.join(d, 'scan*.pdf')))}
        good = all(v for k, v in r.items() if k.startswith('xsd:')) and r['notes_match'] and r['lyrics_match'] and \
            all(r['scans_image_only'].values())
        r['ok'] = good
        ok_all &= good
        report[iid] = r
        print(('OK  ' if good else 'FAIL'), iid, json.dumps(r, default=str, ensure_ascii=False))
    print('ALL OK' if ok_all else 'FAILURES')
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
