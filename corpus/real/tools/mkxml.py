#!/usr/bin/env python3
"""
mkxml.py - compile a hand-transcription source (truth.src) into MusicXML 4.0 partwise.

Usage:
  python3 mkxml.py truth.src --layout split   -o truth.musicxml
  python3 mkxml.py truth.src --layout printed -o truth-printed.musicxml
  python3 mkxml.py truth.src --stats            (JSON summary on stdout)

Source format (one directive per line, '#' starts a comment):
  @title  <text>            @subtitle <text>
  @composer <text>          @lyricist <text>        @arranger <text>
  @rights <text>            @source <text>
  @key <fifths> [major|minor]
  @time <beats>/<beat-type>
  @systems <m> <m> ...      measure indices (1-based, counting a pickup as 1) that start a system
  @split   Name=[V1 V2 / V3] Name2=[V4] ...     output parts for --layout split
  @printed Name=[V1 V2] Name2=[V3 V4] ...       output parts for --layout printed (as engraved)
           inside [...]: voices on one staff are space separated, '/' starts the next staff
  @clef <voice> <G|F|C3|C4|G8>   home clef of the staff that voice sits on
  @name <voice> <long name>
  voice <id>                then note lines until the next directive
  lyrics <voice> <verse-number>   then lyric lines until the next directive

Notes use LilyPond-like ABSOLUTE pitch: c' = middle C (C4), c = C3, c'' = C5, c, = C2.
  accidentals: is (sharp) es (flat) isis eses;  a trailing '!' forces a printed accidental
  duration: 1 2 4 8 16 32 with dots, e.g. fis'4.  (omitted -> previous duration)
  chord: <g b d'>4      rest: r4      tie: ~ after the note     fermata: ^F
  spacer: s4 (no printed rest; becomes <forward>; a voice whose measure is all spacers is omitted)
  @timesymbol common|cut   prints C / alla-breve instead of numerals
  barlines: |  (normal)  ||  (double)  |!  (single heavy, e.g. hymnal line-end bar; may split a measure)
            |.  (final)  :|  (end repeat)  |:  (start repeat)
  inline clef change: \\clefG \\clefF (applies to the voice's staff at that point)
Lyrics: syllables separated by spaces; ' -- ' joins syllables of one word;
  '__' after a syllable draws an extender over following '_' skips; '_' skips a note.
  Lyrics attach to the voice's notes, skipping rests and tie-continuation notes.
  Use '~' inside a syllable for a printed space (elision-free), e.g. "a~new".
"""
import sys, re, json, argparse, datetime
from fractions import Fraction
from xml.sax.saxutils import escape

DIV = 24  # divisions per quarter note
STEPS = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
SHARP_ORDER = ['f', 'c', 'g', 'd', 'a', 'e', 'b']
TYPE_BY_DEN = {1: 'whole', 2: 'half', 4: 'quarter', 8: 'eighth', 16: '16th', 32: '32nd'}


def key_alters(fifths):
    alt = {s: 0 for s in STEPS}
    if fifths > 0:
        for s in SHARP_ORDER[:fifths]:
            alt[s] = 1
    elif fifths < 0:
        for s in list(reversed(SHARP_ORDER))[:-fifths]:
            alt[s] = -1
    return alt


class Note:
    __slots__ = ('pitches', 'rest', 'den', 'dots', 'dur', 'tie_start', 'tie_stop', 'fermata',
                 'lyrics', 'clef_change', 'barline_after', 'force_acc', 'spacer')

    def __init__(self):
        self.pitches = []  # list of (step, alter, octave, force)
        self.rest = False
        self.den = 4
        self.dots = 0
        self.dur = Fraction(1, 4)
        self.tie_start = False
        self.tie_stop = False
        self.fermata = False
        self.lyrics = {}  # verse -> dict(text, syllabic, extend)
        self.clef_change = None
        self.spacer = False


PITCH_RE = re.compile(r"^([a-g])((?:isis|eses|is|es|s)?)([',]*)(!?)$")


def parse_pitch(tok):
    m = PITCH_RE.match(tok)
    if not m:
        raise ValueError('bad pitch %r' % tok)
    step, acc, octs, force = m.groups()
    alter = {'': 0, 'is': 1, 'es': -1, 's': -1, 'isis': 2, 'eses': -2}[acc]
    octave = 3 + octs.count("'") - octs.count(',')
    return (step, alter, octave, bool(force))


NOTE_RE = re.compile(r"^(<[^>]*>|r|s|[a-g](?:isis|eses|is|es|s)?[',]*!?)(\d+)?(\.*)((?:~|\^F)*)$")


def parse_voice(text):
    """Return list of measures; each measure = dict(notes=[...], bar=str|None, start_repeat=bool)."""
    measures = [dict(notes=[], bar=None, start_repeat=False)]
    last_den, last_dots = 4, 0
    toks = text.replace('<', ' <').replace('>', '> ').split()
    # re-join chord tokens: "<g", "b", "d'>4" etc. -> handle by scanning
    i = 0
    merged = []
    while i < len(toks):
        t = toks[i]
        if t.startswith('<') and '>' not in t:
            buf = [t]
            i += 1
            while i < len(toks) and '>' not in toks[i]:
                buf.append(toks[i]); i += 1
            buf.append(toks[i])
            t = ' '.join(buf)
            # attach duration that was split off after '>'
            if i + 1 < len(toks) and re.match(r"^\d+\.*(?:~|\^F)*$|^\.+|^(?:~|\^F)+$", toks[i + 1]):
                t += toks[i + 1]; i += 1
        elif t.startswith('<') and t.endswith('>'):
            if i + 1 < len(toks) and re.match(r"^\d+\.*(?:~|\^F)*$|^(?:~|\^F)+$", toks[i + 1]):
                t += toks[i + 1]; i += 1
        merged.append(t)
        i += 1
    pending_clef = None
    for t in merged:
        if t in ('|', '||', '|.', ':|', ':|:', '|!'):
            measures[-1]['bar'] = t
            measures.append(dict(notes=[], bar=None, start_repeat=(t == ':|:')))
            continue
        if t == '|:':
            if measures[-1]['notes']:
                measures[-1]['bar'] = '|'
                measures.append(dict(notes=[], bar=None, start_repeat=True))
            else:
                measures[-1]['start_repeat'] = True
            continue
        if t.startswith('\\clef'):
            pending_clef = t[5:]
            continue
        m = NOTE_RE.match(t.replace(' ', '\x00') if False else t)
        if not m:
            # chords contain spaces; parse manually
            mm = re.match(r"^(<[^>]*>)(\d+)?(\.*)((?:~|\^F)*)$", t)
            if not mm:
                raise ValueError('bad token %r' % t)
            m = mm
        head, den, dots, mods = m.groups()
        n = Note()
        if den:
            last_den = int(den); last_dots = len(dots)
        elif dots:
            last_dots = len(dots)
        n.den, n.dots = last_den, (len(dots) if den else last_dots)
        base = Fraction(1, n.den)
        n.dur = base * (2 - Fraction(1, 2 ** n.dots))
        if head == 'r':
            n.rest = True
        elif head == 's':
            n.rest = True
            n.spacer = True
        elif head.startswith('<'):
            n.pitches = [parse_pitch(p) for p in head[1:-1].split()]
        else:
            n.pitches = [parse_pitch(head)]
        n.tie_start = '~' in mods
        n.fermata = '^F' in mods
        if pending_clef:
            n.clef_change = pending_clef; pending_clef = None
        measures[-1]['notes'].append(n)
    if not measures[-1]['notes']:
        measures.pop()
    # tie stops
    prev = None
    for ms in measures:
        for n in ms['notes']:
            if prev is not None and prev.tie_start and not n.rest:
                n.tie_stop = True
            prev = n
    return measures


def tokenize_lyrics(text):
    toks = text.split()
    out = []  # list of dicts: text / skip, with hyphen_after, extend
    i = 0
    while i < len(toks):
        t = toks[i]
        if t == '--':
            if out:
                out[-1]['hyph'] = True
        elif t == '__':
            if out:
                out[-1]['ext'] = True
        elif t == '_':
            out.append(dict(skip=True))
        else:
            ext = False
            if t.endswith('__') and len(t) > 2:
                t = t[:-2]; ext = True
            out.append(dict(text=t.replace('~', ' '), hyph=False, ext=ext, skip=False))
        i += 1
    return out


def attach_lyrics(measures, verse, text, voice_id):
    notes = [n for ms in measures for n in ms['notes'] if not n.rest and not n.tie_stop]
    toks = tokenize_lyrics(text)
    if len(toks) > len(notes):
        raise ValueError('voice %s verse %s: %d lyric tokens > %d notes' % (voice_id, verse, len(toks), len(notes)))
    in_word = False
    ext_open = None
    for idx, tok in enumerate(toks):
        n = notes[idx]
        if tok.get('skip'):
            if ext_open is not None:
                # extender continues over this note
                n.lyrics[verse] = dict(extend_only='continue')
                ext_open = n
            continue
        if ext_open is not None:
            # close previous extender on last skipped note
            if ext_open.lyrics.get(verse, {}).get('extend_only'):
                ext_open.lyrics[verse]['extend_only'] = 'stop'
            ext_open = None
        hyph = tok['hyph']
        if in_word:
            syl = 'middle' if hyph else 'end'
        else:
            syl = 'begin' if hyph else 'single'
        in_word = hyph
        n.lyrics[verse] = dict(text=tok['text'], syllabic=syl, extend=tok['ext'])
        if tok['ext']:
            ext_open = n
    if ext_open is not None and ext_open.lyrics.get(verse, {}).get('extend_only'):
        ext_open.lyrics[verse]['extend_only'] = 'stop'
    return len(toks)


def parse_src(path):
    meta = dict(title='', subtitle='', composer='', lyricist='', arranger='', rights='', source='',
                fifths=0, mode='major', beats=4, beat_type=4, systems=[1], split=None, printed=None, timesymbol=None,
                clefs={}, names={})
    voices = {}
    voice_order = []
    lyrics = []  # (voice, verse, text)
    cur = None
    buf = []

    def flush():
        nonlocal cur, buf
        if cur is None:
            return
        kind, a, b = cur
        text = ' '.join(buf)
        if kind == 'voice':
            voices[a] = text
            voice_order.append(a)
        else:
            lyrics.append((a, int(b), text))
        cur, buf = None, []

    for raw in open(path, encoding='utf-8'):
        line = raw.split('#', 1)[0].rstrip() if not raw.lstrip().startswith('lyrics') else raw.rstrip('\n')
        if raw.lstrip().startswith('#'):
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith('@'):
            flush()
            k, _, v = s[1:].partition(' ')
            v = v.strip()
            if k in ('title', 'subtitle', 'composer', 'lyricist', 'arranger', 'rights', 'source'):
                meta[k] = v
            elif k == 'key':
                p = v.split(); meta['fifths'] = int(p[0]); meta['mode'] = p[1] if len(p) > 1 else 'major'
            elif k == 'time':
                b, t = v.split('/'); meta['beats'] = int(b); meta['beat_type'] = int(t)
            elif k == 'timesymbol':
                meta['timesymbol'] = v
            elif k == 'systems':
                meta['systems'] = [int(x) for x in v.split()]
            elif k in ('split', 'printed'):
                meta[k] = parse_layout(v)
            elif k == 'clef':
                vid, c = v.split(); meta['clefs'][vid] = c
            elif k == 'name':
                vid, _, nm = v.partition(' '); meta['names'][vid] = nm
            else:
                raise ValueError('unknown directive @' + k)
        elif s.startswith('voice '):
            flush(); cur = ('voice', s.split()[1], None)
        elif s.startswith('lyrics '):
            flush(); p = s.split(); cur = ('lyrics', p[1], p[2])
        else:
            if cur is None:
                raise ValueError('content outside block: ' + s)
            buf.append(s)
    flush()
    parsed = {v: parse_voice(t) for v, t in voices.items()}
    lyr_counts = {}
    for vid, verse, text in lyrics:
        lyr_counts[(vid, verse)] = attach_lyrics(parsed[vid], verse, text, vid)
    return meta, parsed, voice_order, lyrics


def parse_layout(v):
    parts = []
    for m in re.finditer(r"([^\s=\[]+)=\[([^\]]*)\]", v):
        name, body = m.groups()
        staves = [s.split() for s in body.split('/')]
        parts.append((name.replace('_', ' '), staves))
    return parts


CLEF_XML = {
    'G': ('G', 2, 0), 'F': ('F', 4, 0), 'C3': ('C', 3, 0), 'C4': ('C', 4, 0), 'G8': ('G', 2, -1),
}


def clef_xml(c, number=None):
    sign, line, oct_ = CLEF_XML[c]
    attr = ' number="%d"' % number if number else ''
    s = '<clef%s><sign>%s</sign><line>%d</line>' % (attr, sign, line)
    if oct_:
        s += '<clef-octave-change>%d</clef-octave-change>' % oct_
    return s + '</clef>'


def check_measures(meta, parsed):
    full = Fraction(meta['beats'], meta['beat_type'])
    nmeas = None
    report = []
    for vid, ms in parsed.items():
        if nmeas is None:
            nmeas = len(ms)
        elif len(ms) != nmeas:
            raise ValueError('voice %s has %d measures, expected %d' % (vid, len(ms), nmeas))
    lengths = []
    for i in range(nmeas):
        ls = {vid: sum((n.dur for n in ms[i]['notes']), Fraction(0)) for vid, ms in parsed.items()}
        vals = set(ls.values())
        if len(vals) != 1:
            raise ValueError('measure %d: voices disagree on length: %s' % (i + 1, {k: str(v) for k, v in ls.items()}))
        L = vals.pop()
        lengths.append(L)
        if L != full and i not in (0, nmeas - 1):
            # allow mid-piece partial measures only at repeat/section barlines
            SECTION = {':|', '||', '|.', ':|:', '|!'}
            bars = {ms[i]['bar'] for ms in parsed.values()}
            prevbars = {ms[i - 1]['bar'] for ms in parsed.values()}
            nxt = {ms[i + 1]['start_repeat'] for ms in parsed.values()} if i + 1 < nmeas else set()
            if not (bars & SECTION or prevbars & SECTION or True in nxt):
                raise ValueError('measure %d has length %s (expected %s)' % (i + 1, L, full))
            report.append('measure %d partial (%s) at section/repeat barline' % (i + 1, L))
    return nmeas, lengths, full, report


def build(meta, parsed, layout_name):
    layout = meta[layout_name] or meta['split']
    nmeas, lengths, full, _ = check_measures(meta, parsed)
    first_voice = next(iter(parsed))
    pickup = lengths[0] != full
    out = []
    w = out.append
    w('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    w('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">')
    w('<score-partwise version="4.0">')
    w('  <work><work-title>%s</work-title></work>' % escape(meta['title']))
    if meta['subtitle']:
        w('  <movement-title>%s</movement-title>' % escape(meta['title'] + ' (' + meta['subtitle'] + ')'))
    else:
        w('  <movement-title>%s</movement-title>' % escape(meta['title']))
    w('  <identification>')
    for role in ('composer', 'lyricist', 'arranger'):
        if meta[role]:
            w('    <creator type="%s">%s</creator>' % (role, escape(meta[role])))
    if meta['rights']:
        w('    <rights>%s</rights>' % escape(meta['rights']))
    w('    <encoding>')
    w('      <software>hand transcription; compiled by corpus/real/tools/mkxml.py</software>')
    w('      <encoding-date>%s</encoding-date>' % datetime.date.today().isoformat())
    w('      <supports element="accidental" type="yes"/>')
    w('      <supports element="beam" type="no"/>')
    w('      <supports element="stem" type="%s"/>' % ('yes' if layout_name == 'printed' else 'no'))
    w('      <supports element="print" attribute="new-system" type="yes" value="yes"/>')
    w('    </encoding>')
    if meta['source']:
        w('    <source>%s</source>' % escape(meta['source']))
    w('  </identification>')
    w('  <part-list>')
    for pi, (pname, staves) in enumerate(layout, 1):
        w('    <score-part id="P%d"><part-name>%s</part-name></score-part>' % (pi, escape(pname)))
    w('  </part-list>')
    kalt = key_alters(meta['fifths'])
    for pi, (pname, staves) in enumerate(layout, 1):
        w('  <part id="P%d">' % pi)
        nst = len(staves)
        vinfo = []  # (vid, staffno, voiceno, stem)
        vno = 0
        for si, svs in enumerate(staves, 1):
            for k, vid in enumerate(svs):
                vno += 1
                stem = None
                if layout_name == 'printed' and len(svs) > 1:
                    stem = 'up' if k == 0 else 'down'
                vinfo.append((vid, si, vno, stem))
        acc_state = None
        mnum = 0 if pickup else 1
        for mi in range(nmeas):
            attrs = ' implicit="yes"' if (mi == 0 and pickup) or (lengths[mi] != full and mi == nmeas - 1 and pickup) else ''
            w('    <measure number="%d"%s>' % (mnum, attrs))
            mnum += 1
            if (mi + 1) in meta['systems'] and mi > 0:
                w('      <print new-system="yes"/>')
            # start repeat
            if any(parsed[v][mi]['start_repeat'] for v, *_ in vinfo):
                w('      <barline location="left"><bar-style>heavy-light</bar-style><repeat direction="forward"/></barline>')
            if mi == 0:
                w('      <attributes>')
                w('        <divisions>%d</divisions>' % DIV)
                w('        <key><fifths>%d</fifths><mode>%s</mode></key>' % (meta['fifths'], meta['mode']))
                sym = ' symbol="%s"' % meta['timesymbol'] if meta['timesymbol'] else ''
                w('        <time%s><beats>%d</beats><beat-type>%d</beat-type></time>' % (sym, meta['beats'], meta['beat_type']))
                if nst > 1:
                    w('        <staves>%d</staves>' % nst)
                for si, svs in enumerate(staves, 1):
                    w('        ' + clef_xml(meta['clefs'].get(svs[0], 'G'), si if nst > 1 else None))
                w('      </attributes>')
            # accidental state per staff for this measure
            acc_state = {si: {} for si in range(1, nst + 1)}
            first = True
            for vid, si, vno_, stem in vinfo:
                notes = parsed[vid][mi]['notes']
                if notes and all(n.spacer for n in notes) and not first:
                    continue
                if not first:
                    w('      <backup><duration>%d</duration></backup>' % int(lengths[mi] * 4 * DIV))
                first = False
                for n in notes:
                    if n.spacer:
                        w('      <forward><duration>%d</duration><voice>%d</voice>%s</forward>' % (
                            int(n.dur * 4 * DIV), vno_, '<staff>%d</staff>' % si if nst > 1 else ''))
                        continue
                    if n.clef_change:
                        w('      <attributes>%s</attributes>' % clef_xml(n.clef_change, si if nst > 1 else None))
                    dur = int(n.dur * 4 * DIV)
                    heads = [None] if n.rest else n.pitches
                    for hi, p in enumerate(heads):
                        w('      <note>')
                        if hi > 0:
                            w('        <chord/>')
                        if n.rest:
                            w('        <rest/>')
                        else:
                            step, alter, octv, force = p
                            al = '<alter>%d</alter>' % alter if alter else ''
                            w('        <pitch><step>%s</step>%s<octave>%d</octave></pitch>' % (step.upper(), al, octv))
                        w('        <duration>%d</duration>' % dur)
                        if not n.rest:
                            if n.tie_stop:
                                w('        <tie type="stop"/>')
                            if n.tie_start:
                                w('        <tie type="start"/>')
                        w('        <voice>%d</voice>' % vno_)
                        w('        <type>%s</type>' % TYPE_BY_DEN[n.den])
                        for _ in range(n.dots):
                            w('        <dot/>')
                        if not n.rest:
                            step, alter, octv, force = p
                            st = acc_state[si]
                            cur_alt = st.get((step, octv), kalt[step])
                            show = force or (alter != cur_alt and not n.tie_stop)
                            st[(step, octv)] = alter
                            if show:
                                name = {0: 'natural', 1: 'sharp', -1: 'flat', 2: 'double-sharp', -2: 'flat-flat'}[alter]
                                w('        <accidental>%s</accidental>' % name)
                        if stem and not n.rest:
                            w('        <stem>%s</stem>' % stem)
                        if nst > 1:
                            w('        <staff>%d</staff>' % si)
                        nots = []
                        if not n.rest and n.tie_stop:
                            nots.append('<tied type="stop"/>')
                        if not n.rest and n.tie_start:
                            nots.append('<tied type="start"/>')
                        if n.fermata and hi == 0:
                            nots.append('<fermata type="upright"/>')
                        if nots:
                            w('        <notations>%s</notations>' % ''.join(nots))
                        if hi == 0 and n.lyrics:
                            for verse in sorted(n.lyrics):
                                L = n.lyrics[verse]
                                if 'extend_only' in L:
                                    w('        <lyric number="%d"><extend type="%s"/></lyric>' % (verse, L['extend_only']))
                                    continue
                                ext = '<extend type="start"/>' if L['extend'] else ''
                                w('        <lyric number="%d"><syllabic>%s</syllabic><text>%s</text>%s</lyric>' % (
                                    verse, L['syllabic'], escape(L['text']), ext))
                        w('      </note>')
            bar = parsed[first_voice][mi]['bar']
            if mi == nmeas - 1 and bar in (None, '|'):
                bar = '|.'
            if bar == '|.':
                w('      <barline location="right"><bar-style>light-heavy</bar-style></barline>')
            elif bar == '||':
                w('      <barline location="right"><bar-style>light-light</bar-style></barline>')
            elif bar == '|!':
                w('      <barline location="right"><bar-style>heavy</bar-style></barline>')
            elif bar in (':|', ':|:'):
                w('      <barline location="right"><bar-style>light-heavy</bar-style><repeat direction="backward"/></barline>')
            w('    </measure>')
        w('  </part>')
    w('</score-partwise>')
    return '\n'.join(out) + '\n'


def stats(meta, parsed, lyrics):
    nmeas, lengths, full, report = check_measures(meta, parsed)
    res = dict(measures=nmeas, pickup=lengths[0] != full, time='%d/%d' % (meta['beats'], meta['beat_type']),
               fifths=meta['fifths'], mode=meta['mode'], systems=len(meta['systems']),
               voices={}, verses=sorted({v for _, v, _ in lyrics}), notes_total=0, partial_measures=report)
    for vid, ms in parsed.items():
        nn = sum(1 for m in ms for n in m['notes'] if not n.rest)
        heads = sum(len(n.pitches) for m in ms for n in m['notes'] if not n.rest)
        rests = sum(1 for m in ms for n in m['notes'] if n.rest and not n.spacer)
        lyr = {}
        for m in ms:
            for n in m['notes']:
                for verse, L in n.lyrics.items():
                    if 'text' in L:
                        lyr[verse] = lyr.get(verse, 0) + 1
        res['voices'][vid] = dict(notes=nn, noteheads=heads, rests=rests, syllables=lyr)
        res['notes_total'] += heads
    res['split_parts'] = [dict(name=n, staves=s) for n, s in (meta['split'] or [])]
    res['printed_parts'] = [dict(name=n, staves=s) for n, s in (meta['printed'] or [])]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--layout', default='split', choices=['split', 'printed'])
    ap.add_argument('-o', '--out')
    ap.add_argument('--stats', action='store_true')
    a = ap.parse_args()
    meta, parsed, order, lyrics = parse_src(a.src)
    if a.stats:
        print(json.dumps(stats(meta, parsed, lyrics), indent=1))
        return
    xml = build(meta, parsed, a.layout)
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(xml)
    else:
        sys.stdout.write(xml)


if __name__ == '__main__':
    main()
