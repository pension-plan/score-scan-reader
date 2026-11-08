'use strict';
// Page assemblies -> parts (closed-score split / grand staff / single), time
// signature inference, per-measure rhythm repair, lyrics alignment, MusicXML.
const { staffMeasureEvents, pitchOf, keyAlters, DIV } = require('./assemble');

const COLORS = ['#d1495b', '#edae49', '#00798c', '#30638e', '#7b5ea7', '#3a7d44'];

// most common value; ties go to the larger value
function mode(a) {
  const c = new Map();
  for (const v of a) c.set(v, (c.get(v) || 0) + 1);
  let best = null, bn = -1;
  for (const [v, n] of c) if (n > bn || (n === bn && v > best)) { best = v; bn = n; }
  return best;
}

// ------------------------------------------------------------ layout evidence
function staffStats(systems, idx) {
  let n = 0, n2 = 0, n3 = 0, mix = 0;
  for (const sy of systems) {
    const s = sy.staves[idx]; if (!s) continue;
    for (const c of s.chords) {
      n++;
      const dirs = new Set(c.heads.map(h => h.stemDir));
      if (c.heads.length >= 3) n3++;
      else if (c.heads.length === 2 || dirs.has(2)) n2++;
      if (dirs.has(1) && dirs.has(-1)) { n2 += 0.5; mix++; }
    }
  }
  return { n, f2: n ? n2 / n : 0, f3: n ? n3 / n : 0, mix: n ? mix / n : 0 };
}

// Share of the barlines of staff k that run on into staff k+1. Engraving
// convention: barlines are drawn through a keyboard grand staff (one player)
// but stop at each staff of a choir or a voice (so they never cross the text).
function pairConnectivity(systems, k) {
  let n = 0, c = 0;
  for (const sy of systems) {
    const a = sy.staves[k], b = sy.staves[k + 1];
    if (!a || !b || !sy.fr || !sy.fr.barlines) continue;
    const ss = sy.fr.ss || a.st.space;
    for (const bl of sy.fr.barlines) {
      if (bl.staff !== a.st.index) continue;
      n++;
      if (bl.bot >= b.st.yAt(0, bl.x) - 0.5 * ss) c++;
    }
  }
  return { n, frac: n ? c / n : null };
}

// fraction of systems whose OCR found an underlay line (>= 3 syllables) below staff k
function lyricPresence(systems, lyricsBySystem, nSt) {
  const pres = new Array(nSt).fill(0);
  let ns = 0;
  for (const sy of systems) {
    ns++;
    const lyr = lyricsBySystem[sy.page + ':' + sy.index] || [];
    const bands = new Set(lyr.filter(v => v.syllables && v.syllables.length >= 3).map(v => v.band));
    for (const b of bands) if (b >= 0 && b < nSt) pres[b]++;
  }
  return pres.map(x => (ns ? x / ns : 0));
}

function staffClef(systems, k) {
  const read = systems.map(sy => sy.staves[k]).filter(s => s && !s.hdr.clefGuessed).map(s => s.hdr.clef);
  if (read.length) return mode(read);
  const any = systems.map(sy => sy.staves[k]).filter(Boolean).map(s => s.hdr.clef);
  return any.length ? mode(any) : 'G';
}

// Names for the vocal parts, from the staff / voice pattern and the clefs
// (research-voices.md §6 fallback when no labels are read).
function vocalNames(vs) {
  // vs: [{ staff, split, clef }] top to bottom
  const nV = vs.reduce((a, v) => a + (v.split ? 2 : 1), 0);
  const isLow = c => c === 'F';
  const sig = vs.map(v => (v.split ? '2' : '1') + (v.clef === 'G8' ? 't' : isLow(v.clef) ? 'b' : 'g')).join('');
  const table = {
    '2g2b': ['Soprano', 'Alto', 'Tenor', 'Bass'],
    '2t2b': ['Tenor I', 'Tenor II', 'Baritone', 'Bass'],
    '2g2g': ['Soprano I', 'Soprano II', 'Alto I', 'Alto II'],
    '2t2t': ['Tenor I', 'Tenor II', 'Bass I', 'Bass II'],
    '2b2b': ['Tenor I', 'Tenor II', 'Bass I', 'Bass II'],
    '2g1b': ['Soprano', 'Alto', 'Baritone'],
    '1g1g1g1b': ['Soprano', 'Alto', 'Tenor', 'Bass'],
    '1g1g1t1b': ['Soprano', 'Alto', 'Tenor', 'Bass'],
    '1g1g1b1b': ['Soprano', 'Alto', 'Tenor', 'Bass'],
    '1g1t1b': ['Soprano', 'Tenor', 'Bass'],
    '2g': ['Soprano', 'Alto'],
    '2t': ['Tenor', 'Bass'],
    '2b': ['Tenor', 'Bass'],
  };
  if (table[sig]) return table[sig];
  // a solo line (or several) above a four-part choir in open score
  if (vs.length > 4 && vs.every(v => !v.split)) {
    const tail = vs.slice(-4).map(v => (v.clef === 'G8' ? 't' : isLow(v.clef) ? 'b' : 'g')).join('');
    if (/^gg[gtb]b$/.test(tail)) {
      const head = vs.slice(0, -4).map((_, i, a) => (a.length === 1 ? 'Voice' : `Voice ${i + 1}`));
      return head.concat(['Soprano', 'Alto', 'Tenor', 'Bass']);
    }
  }
  if (nV === 1) return ['Voice'];
  const out = [];
  let i = 0;
  for (const v of vs) {
    i++;
    const base = vs.length === 1 ? 'Voice' : `Voice ${i}`;
    if (v.split) out.push(`${base} upper`, `${base} lower`); else out.push(base);
  }
  return out;
}

// Decide the part layout for the whole piece (never per measure):
//  - adjacent staves joined by barlines with no underlay between them are a
//    keyboard grand staff: one part, never split (voices kept inside it);
//  - every other staff is a vocal / melody staff; one that carries two voices
//    (stems up and down, at most two heads per stem) is split by stem direction
//    into two parts (closed score SATB, SSAA, TTBB, divisi).
function chooseLayout(systems, lyricsBySystem = {}, opts = {}) {
  const nSt = mode(systems.map(s => s.staves.length)) || 1;
  const sel = systems.filter(s => s.staves.length === nSt);
  const stats = [], clefs = [];
  for (let i = 0; i < nSt; i++) { stats.push(staffStats(sel, i)); clefs.push(staffClef(sel, i)); }
  const lyr = lyricPresence(sel, lyricsBySystem, nSt);
  const anyLyrics = lyr.some(x => x > 0);
  const ocr = opts.ocr !== false;
  const notes = [];
  // keyboard links between adjacent staves
  const link = [];
  for (let k = 0; k + 1 < nSt; k++) {
    const c = pairConnectivity(sel, k);
    const underlay = lyr[k] >= 0.3;
    let kb;
    // accompaniment cue (research-voices.md section 5): the bottom pair of
    // staves carries chords but no text while a staff above it carries the
    // underlay -> voice(s) over a piano whose barlines were not seen joined
    const chordy = Math.max(stats[k].f2 + stats[k].f3, stats[k + 1].f2 + stats[k + 1].f3) >= 0.2;
    const accomp = ocr && k + 1 === nSt - 1 && lyr.slice(0, k).some(x => x >= 0.3) && lyr[k] < 0.15 && lyr[k + 1] < 0.15 && chordy;
    if (c.n >= 2) kb = (c.frac >= 0.5 && !underlay) || accomp;
    else {
      // no barline evidence: two chordal staves with no text at all read as piano
      const chordal = (stats[k].f3 + stats[k + 1].f3) / 2 >= 0.2 || (stats[k].f2 + stats[k + 1].f2) / 2 <= 0.3;
      kb = nSt === 2 && !underlay && (chordal || (ocr && !anyLyrics));
    }
    link.push(kb);
  }
  // groups: runs of linked staves (max 3: organ) are one keyboard part
  const groups = [];
  for (let i = 0; i < nSt;) {
    let j = i;
    while (j + 1 < nSt && link[j] && j - i < 2) j++;
    groups.push({ staves: Array.from({ length: j - i + 1 }, (_, t) => i + t), keyboard: j > i });
    i = j + 1;
  }
  // vocal staves: split when two voices share the staff for the whole piece
  const vocal = groups.filter(g => !g.keyboard).map(g => g.staves[0]);
  const vs = vocal.map(k => ({ staff: k, clef: clefs[k], split: stats[k].f2 > 0.35 && stats[k].f3 < 0.2 }));
  // a two-staff closed score decides once for both staves
  if (vs.length === 2 && nSt === 2) {
    const both = (stats[0].f2 + stats[1].f2) / 2 > 0.3 && (stats[0].f3 + stats[1].f3) / 2 < 0.2;
    vs.forEach(v => { v.split = both; });
  }
  const vnames = vocalNames(vs);
  const parts = [];
  let vi = 0;
  const nKb = groups.filter(g => g.keyboard).length;
  let kbi = 0;
  for (const g of groups) {
    if (g.keyboard) {
      kbi++;
      parts.push({ name: nKb > 1 ? `Piano ${kbi}` : 'Piano', kind: 'keyboard', src: g.staves.map(s => ({ staff: s, voice: 'chordal' })) });
      notes.push(`Staves ${g.staves.map(s => s + 1).join('+')}: read as a keyboard grand staff (barlines joined or chords without lyrics under a sung line), kept together as one part and never split.`);
      continue;
    }
    const v = vs.find(x => x.staff === g.staves[0]);
    if (v.split) {
      parts.push({ name: vnames[vi++], kind: 'vocal', src: [{ staff: v.staff, voice: 1 }] });
      parts.push({ name: vnames[vi++], kind: 'vocal', src: [{ staff: v.staff, voice: 2 }] });
      notes.push(`Staff ${v.staff + 1}: two voices on one staff, split by stem direction into ${parts[parts.length - 2].name} and ${parts[parts.length - 1].name}.`);
    } else parts.push({ name: vnames[vi++], kind: 'vocal', src: [{ staff: v.staff, voice: 'chordal' }] });
  }
  parts.forEach((p, i) => { p.id = 'P' + (i + 1); p.color = COLORS[i % COLORS.length]; });
  return { parts, nSt, notes, clefs, stats, link };
}

// Key signature: every staff carries the same key. A staff whose accidentals
// were missed reads as 0 (or as fewer accidentals than printed), while extra
// accidentals are rare, so the largest key that several staves agree on wins.
function chooseKey(systems) {
  const all = [];
  systems.forEach(sy => sy.staves.forEach(s => all.push(s.hdr.fifths | 0)));
  if (!all.length) return 0;
  const nz = all.filter(v => v !== 0);
  if (!nz.length || (nz.length < 2 && nz.length < 0.2 * all.length)) return 0;
  const pos = nz.filter(v => v > 0).length, neg = nz.length - pos;
  const sgn = pos >= neg ? 1 : -1;
  const same = nz.filter(v => Math.sign(v) === sgn).map(Math.abs);
  const cnt = {};
  same.forEach(v => { cnt[v] = (cnt[v] || 0) + 1; });
  const vals = Object.keys(cnt).map(Number).sort((a, b) => b - a);
  for (const v of vals) if (cnt[v] >= 2 || cnt[v] >= 0.25 * same.length) return sgn * v;
  return sgn * vals[vals.length - 1];
}

const qsum = (evs) => evs.reduce((a, e) => a + e.q, 0);
const EPS = 1e-6;

// onsets of the stream that disagree with an onset another voice has at the
// same x (simultaneous notes are printed vertically aligned)
function anchorMisses(evs, anchors, sp) {
  if (!anchors.length) return 0;
  let t = 0, miss = 0;
  for (const e of evs) {
    if (!e.rest && e.x != null) {
      const near = anchors.filter(a => Math.abs(a.x - e.x) <= 0.8 * sp);
      if (near.length && !near.some(a => Math.abs(a.t - t) < EPS)) miss++;
    }
    t += e.q;
  }
  return miss;
}

// Rest glyphs printed in a voice's measure (the note detector does not report
// rests). Components of the staff-removed page inside the staff band that are
// not part of a note, not an accidental just before a note and shaped like a
// whole / half block, a quarter squiggle or an eighth hook. {x, q} sorted by x.
function findRests(seg, s, voice) {
  const st = s.st, sp = st.space, xa = seg.xa, xb = seg.xb;
  const xMin = Math.max(xa, (s.hdr && s.hdr.end) || -1e9) + 0.3 * sp;
  const heads = [];
  for (const c of s.chords) if (c.x > xa - 2 * sp && c.x < xb + 2 * sp) for (const h of c.heads) heads.push(h);
  const out = [];
  for (const c of seg.sy.comps || []) {
    if (c.x0 < xMin || c.x1 > xb - 0.3 * sp) continue;
    const xc = (c.x0 + c.x1) / 2, y0 = st.yAt(0, xc);
    const top = (c.y0 - y0) / sp, bot = (c.y1 - y0) / sp, cy = (top + bot) / 2;
    if (top < -0.6 || bot > 4.6) continue;
    const h = (c.y1 - c.y0 + 1) / sp, w = (c.x1 - c.x0 + 1) / sp, fill = c.area / ((c.x1 - c.x0 + 1) * (c.y1 - c.y0 + 1));
    let q = 0;
    if (h >= 0.35 && h <= 0.95 && w >= 0.9 && w <= 1.9 && fill >= 0.6 && top >= 0.6 && bot <= 2.6) q = top < 1.3 ? 4 : 2;
    else if (h >= 2.3 && h <= 3.4 && w >= 0.6 && w <= 1.4 && fill >= 0.25 && fill <= 0.65 && cy >= 0.9 && cy <= 3.1) q = 1;
    else if (h >= 1.4 && h < 2.3 && w >= 0.6 && w <= 1.3 && fill >= 0.2 && fill <= 0.6 && cy >= 0.7 && cy <= 3.3) q = 0.5;
    if (!q) continue;
    // part of a note (head, stem, flag) or an accidental in front of one
    if (heads.some(hd => hd.x + 0.7 * sp >= c.x0 && hd.x - 0.7 * sp <= c.x1 && hd.y + 0.6 * sp >= c.y0 && hd.y - 0.6 * sp <= c.y1)) continue;
    if (heads.some(hd => hd.x - c.x1 >= 0 && hd.x - c.x1 <= 3.0 * sp && hd.y >= c.y0 - 0.3 * sp && hd.y <= c.y1 + 0.3 * sp)) continue;
    // two voices on a staff: rests of the upper voice are raised, of the lower lowered
    if (voice === 1 && cy > 2.4) continue;
    if (voice === 2 && cy < 1.6) continue;
    out.push({ x: xc, q });
  }
  return out.sort((a, b) => a.x - b.x);
}

// Put found rests into a voice that falls short of the measure, at their x
// position; their lengths come from their shapes when those add up to the
// gap, otherwise the gap is shared out. Returns null when that does not fit.
function placeRests(evs, rests, gap) {
  if (!rests.length) return null;
  let qs = rests.map(r => r.q);
  const tot = qs.reduce((a, b) => a + b, 0);
  if (Math.abs(tot - gap) > EPS) {
    if (rests.length === 1) qs = [gap];
    else if (qToType(gap / rests.length)) qs = rests.map(() => gap / rests.length);
    else return null;
  }
  const add = [];
  rests.forEach((r, i) => {
    const parts = qToType(qs[i]) ? [qs[i]] : restsFor(qs[i]);
    for (const q of parts) add.push({ rest: true, q, dots: qToType(q) ? qToType(q).dots : 0, x: r.x });
  });
  const out = evs.slice();
  for (const r of add) {
    let k = out.findIndex(e => e.x != null && e.x > r.x);
    if (k < 0) k = out.length;
    out.splice(k, 0, r);
  }
  return out;
}

// Cheapest set of duration edits that makes a voice fill the measure exactly:
// a missed / extra augmentation dot, a missed / extra flag or beam (halve /
// double) or, in an over-full measure, a false notehead dropped. A dynamic
// programme over the events and the time reached so far; an edit that puts a
// note's onset out of step with a voice printed at the same x (simultaneous
// notes are vertically aligned) costs extra. Returns {events, ok}.
function searchRepair(evs, target, anchors, sp, over) {
  const U = DIV, T = Math.round(target * U);
  const near = evs.map(e => (e.rest || e.x == null) ? null : anchors.filter(a => Math.abs(a.x - e.x) <= 0.8 * sp).map(a => Math.round(a.t * U)));
  const opts = evs.map(e => {
    const q = e.q, d = e.dots || 0, o = [[q, 0]];
    if (!e.rest) {
      if (!d) o.push([q * 1.5, 1.0]);
      if (d === 1) o.push([q / 1.5, 1.2]);
      o.push([q / 2, 1.5]);
      if (q * 2 <= 4 + EPS) o.push([q * 2, 1.6]);
      // a note that took a syllable is printed for sure: dropping it costs more
      if (over) o.push([0, e.lyrics ? 3.5 : 1.8]);
    }
    return o.filter(([nq]) => nq === 0 || qToType(nq)).map(([nq, c]) => [Math.round(nq * U), nq, c]);
  });
  const layers = [new Map([[0, { c: 0, from: 0, q: null }]])];
  for (let i = 0; i < evs.length; i++) {
    const cur = layers[i], nxt = new Map();
    for (const [t, st] of cur) {
      const nr = near[i];
      for (const [du, nq, c] of opts[i]) {
        const t2 = t + du;
        if (t2 > T) continue;
        const cost = st.c + c + (du > 0 && nr && nr.length && !nr.includes(t) ? 2 : 0);
        const p = nxt.get(t2);
        if (!p || cost < p.c - 1e-9) nxt.set(t2, { c: cost, from: t, q: nq });
      }
    }
    layers.push(nxt);
  }
  const end = layers[evs.length].get(T);
  if (!end) return null;
  const qs = new Array(evs.length);
  for (let i = evs.length, t = T; i > 0; i--) { const st = layers[i].get(t); qs[i - 1] = st.q; t = st.from; }
  return { cost: end.c, qs };
}

function repairStream(evs, target, anchors, sp) {
  const sum = qsum(evs), diff = target - sum;
  const base = anchorMisses(evs, anchors, sp);
  const best = searchRepair(evs, target, anchors, sp, diff < -EPS);
  // leaving a gap costs about as much as two edits; an over-full bar must be
  // fixed, so a little more is spent there before squeezing it
  const gapCost = 2.6 + 2 * base;
  if (best && best.cost < gapCost + (diff < -EPS ? 1.2 : 0)) {
    const out = [];
    evs.forEach((e, i) => {
      const nq = best.qs[i];
      if (nq === 0) return;
      if (Math.abs(nq - e.q) > EPS) { e.q = nq; e.dots = qToType(nq).dots; }
      out.push(e);
    });
    return { events: out, ok: true };
  }
  if (diff > EPS) return { events: evs.concat([{ forward: true, q: diff }]), ok: false };
  // still over-full: shorten the longest values (drop a dot, else halve) until
  // the voice fits, so every note read is kept; pad any small gap left over
  {
    const tr = evs.map(e => ({ ...e }));
    let sum = qsum(tr);
    while (sum > target + EPS) {
      let k = -1;
      tr.forEach((e, i) => { if (e.q > 0.25 + EPS && (k < 0 || e.q > tr[k].q + EPS || (e.rest && !tr[k].rest && Math.abs(e.q - tr[k].q) < EPS))) k = i; });
      if (k < 0) break;
      const e = tr[k], nq = e.dots ? e.q / 1.5 : e.q / 2;
      if (!qToType(nq)) break;
      sum -= e.q - nq; e.q = nq; e.dots = qToType(nq).dots;
    }
    if (sum <= target + EPS) {
      evs.forEach((e, i) => { e.q = tr[i].q; e.dots = tr[i].dots; });
      const out = evs.slice();
      if (target - sum > EPS) out.push({ forward: true, q: target - sum });
      return { events: out, ok: false };
    }
  }
  // cannot be shortened enough: keep what fits and cut the note that crosses
  // the barline so the measure stays importable (notation programs reject
  // over-full bars)
  const out = [];
  let t = 0;
  for (const e of evs) {
    if (t >= target - EPS) break;
    if (t + e.q > target + EPS) {
      const rest = target - t, tt = qToType(rest);
      if (tt) { e.q = rest; e.dots = tt.dots; out.push(e); }
      else for (const q of restsFor(rest)) out.push({ forward: true, q });
      t = target; break;
    }
    out.push(e); t += e.q;
  }
  return { events: out, ok: false };
}

// Two voices sharing a staff (closed score): stem up -> upper voice, stem
// down -> lower voice, a head with both stems -> both (unison). Heads printed
// side by side for a second between the voices are one onset. A lone head goes
// to its stem's voice and is copied to the other voice as a unison only when
// that voice is not still holding a note (a missed head there would otherwise
// leave a hole in its rhythm). With reliable stems, a voice that reaches a
// shared onset early has its previous note lengthened (a missed dot or flag),
// or gets a rest there when no note value fits.
function splitTwoVoices(chordal, sp, trust) {
  const slots = [];
  const only = (dirs, d) => !!dirs && dirs.size === 1 && dirs.has(d);
  for (const ev of chordal) {
    const dirs = new Set(ev.heads.map(h => h.stemDir));
    const last = slots[slots.length - 1];
    const near = last && ev.x - last.x1 < 1.5 * sp;
    // opposite stems side by side, or two lone heads a step apart (a second
    // between the voices is printed with the heads beside each other)
    const opposite = (only(last && last.dirs, 1) && only(dirs, -1)) || (only(last && last.dirs, -1) && only(dirs, 1));
    const second = last && last.heads.length === 1 && ev.heads.length === 1 && Math.abs(last.heads[0].p - ev.heads[0].p) === 1;
    if (near && (opposite || second)) {
      last.heads.push(...ev.heads); last.x1 = ev.x; dirs.forEach(d => last.dirs.add(d)); last.pair = true;
      continue;
    }
    slots.push({ x: ev.x, x1: ev.x, heads: ev.heads.slice(), dirs });
  }
  const out = { 1: [], 2: [] }, cur = { 1: 0, 2: 0 };
  const mk = (sl, h) => ({ x: sl.x, heads: [h], q: h.dur.q, dots: h.dur.dots });
  for (const sl of slots) {
    const hs = sl.heads.slice().sort((a, b) => a.y - b.y);
    const v1 = hs.filter(h => h.stemDir === 1 || h.stemDir === 2), v2 = hs.filter(h => h.stemDir === -1 || h.stemDir === 2);
    let a1 = null, a2 = null;
    if (sl.pair && hs.length === 2 && !(hs[0].stemDir === -1 && hs[1].stemDir === 1)) { a1 = hs[0]; a2 = hs[1]; }
    else if (v1.length && v2.length) { a1 = v1[0]; a2 = v2[v2.length - 1]; }
    else if (v1.length || v2.length) {
      const c = v1.length ? v1 : v2;
      if (c.length >= 2) { a1 = c[0]; a2 = c[c.length - 1]; } // two voices on one stem
      else {
        const h = c[0], mine = v1.length ? 1 : 2, other = 3 - mine;
        const free = cur[other] <= cur[mine] + 1e-6;
        if (mine === 1) { a1 = h; if (free) a2 = h; } else { a2 = h; if (free) a1 = h; }
      }
    } else if (hs.length) { a1 = hs[0]; a2 = hs[hs.length - 1]; } // stemless (whole notes)
    const vs = [[1, a1], [2, a2]].filter(([, h]) => h);
    const t = Math.max(...vs.map(([v]) => cur[v]));
    for (const [v, h] of vs) {
      const gap = t - cur[v];
      if (trust && gap > 1e-6) {
        // a hole before an onset the other voice shares: most often a missed
        // dot or flag on the previous note, rarely a printed rest
        const prev = out[v][out[v].length - 1];
        if (prev && !prev.rest && qToType(prev.q + gap)) { prev.q += gap; prev.dots = qToType(prev.q).dots; }
        else for (const q of restsFor(gap)) out[v].push({ rest: true, q, dots: 0, x: sl.x });
      }
      cur[v] = t;
      out[v].push(mk(sl, h));
      cur[v] += h.dur.q;
    }
  }
  return out;
}

function qToType(q) {
  const table = [[4, 'whole', 0], [3, 'half', 1], [2, 'half', 0], [1.5, 'quarter', 1], [1, 'quarter', 0], [0.75, 'eighth', 1],
    [0.5, 'eighth', 0], [0.375, '16th', 1], [0.25, '16th', 0], [0.125, '32nd', 0], [6, 'whole', 1]];
  for (const [v, t, d] of table) if (Math.abs(v - q) < 1e-6) return { type: t, dots: d };
  return null;
}

function restsFor(q) {
  // split a gap into standard rest values
  const out = [];
  let left = Math.round(q * DIV) / DIV;
  for (const v of [4, 3, 2, 1.5, 1, 0.75, 0.5, 0.25, 0.125]) while (left >= v - 1e-6) { out.push(v); left -= v; }
  return out;
}

function buildScore(pages, lyricsBySystem = {}, opts = {}) {
  const warnings = [];
  const systems = pages.flatMap(p => p.asm.systems.map(s => ({ ...s, fr: p.fr, comps: p.asm.comps })));
  if (!systems.length) return { parts: [], measures: 0, warnings: ['No music systems found.'], xml: emptyXML() };
  const layout = chooseLayout(systems, lyricsBySystem, opts);
  const { parts } = layout;
  const fifths = chooseKey(systems);
  const kAlt = keyAlters(fifths);
  // clefs per staff index (majority of the clefs read across systems)
  const clefs = layout.clefs;
  if (systems.some(sy => sy.staves.some(s => s.hdr.clefGuessed))) warnings.push('Clef not recognised on some staves; assumed treble on top / bass below.');

  // collect events per raw measure segment, per part
  const segs = [];
  for (const sy of systems) for (const [xa, xb] of sy.measures) segs.push({ sy, xa, xb });
  // stems are trusted on a staff when up and down stems are seen together on it
  const trust = layout.stats.map(st => st.mix >= 0.25);
  const segEv = segs.map(m => {
    const cache = {};
    return parts.map(p => p.src.map(src => {
      const s = m.sy.staves[src.staff];
      if (!s) return [];
      const c = (cache[src.staff] ||= staffMeasureEvents(m.sy.fr, m.sy.fr.R, m.sy.comps, s, m.xa, m.xb));
      if (src.voice === 1 || src.voice === 2) {
        c.split ||= splitTwoVoices(c.chordal, s.st.space, !!trust[src.staff]);
        return c.split[src.voice];
      }
      return c[src.voice] || [];
    }));
  });
  // length of each segment: the most common stream total (a stream that lost
  // a note or a rest comes out short, so one stream alone is not trusted)
  const segSum = segEv.map(e => {
    const sums = [];
    e.forEach(streams => streams.forEach(evs => {
      const s = evs.reduce((a, x) => a + x.q, 0);
      if (s > 0) sums.push(Math.round(s * 4) / 4);
    }));
    return sums.length ? mode(sums) : 0;
  });
  // time signature: most common full-measure length, also counting pairs of
  // short segments (phrase barlines / measures split across systems)
  const votes = {};
  const vote = (v, wgt) => { const r = Math.round(v * 2) / 2; if (r > 0) votes[r] = (votes[r] || 0) + wgt; };
  segSum.forEach((v, i) => { vote(v, 1); if (i + 1 < segSum.length) vote(v + segSum[i + 1], 0.6); });
  // prior: common metres need less evidence than rare ones (measure length
  // in quarters: 4 = 4/4, 3 = 3/4 or 6/8, 2 = 2/4, 6 = 6/4 or 3/2, ...)
  const PRIOR = { 4: 1, 3: 0.9, 2: 0.75, 6: 0.45, 1.5: 0.4, 5: 0.25, 3.5: 0.15 };
  let mq = +(Object.entries(votes).filter(([k]) => +k >= 1.5 && PRIOR[+k]).map(([k, v]) => [k, v * PRIOR[+k]]).sort((a, b) => b[1] - a[1])[0] || [4])[0];
  let time = { beats: 4, type: 4 };
  if (Number.isInteger(mq) && mq >= 2 && mq <= 6) time = { beats: mq, type: 4 };
  else if (mq === 1.5) time = { beats: 3, type: 8 };
  else if (mq === 3.5) time = { beats: 7, type: 8 };
  else { mq = 4; warnings.push('Could not infer a time signature; using 4/4.'); }
  const mLen = (time.beats * 4) / time.type;
  warnings.push(`Time signature inferred from measure contents: ${time.beats}/${time.type}.`);
  // Barline reconciliation. Barline detection both misses barlines and finds
  // false ones (stems, brackets, text). Within each system the raw segments
  // are grouped into measures by a small dynamic programme: a group costs how
  // far its content is from a full bar plus a charge for every barline it
  // drops (cheap when one side is a sliver no wider than a few staff spaces,
  // which is how a stem misread as a barline shows up). An opening pickup and
  // a closing short bar cost nothing. Over-full groups are cut later.
  const nStreams = segEv.length ? segEv[0].reduce((a, ps) => a + ps.length, 0) : 0;
  const segStreamSums = segEv.map(e => e.flatMap(ps => ps.map(evs => qsum(evs))));
  const groupDev = (a, b, edge) => {
    // dropping a barline must never make a bar over-full (its notes would be cut)
    const sums = [];
    for (let k = 0; k < nStreams; k++) {
      let s = 0;
      for (let i = a; i <= b; i++) s += segStreamSums[i][k] || 0;
      if (s > 1e-6) sums.push(Math.round(s * 4) / 4);
    }
    if (!sums.length) return 0; // nothing but rests: a bar of rests
    const S = mode(sums);
    if (b > a && Math.max(...sums) > mLen + 1e-6) return Infinity;
    if (Math.abs(S - mLen) < 1e-6 || (edge && S < mLen)) return 0;
    return 0.1 + Math.min(1, Math.abs(S - mLen) / mLen);
  };
  const measures = []; // [{segs:[...]}]
  for (let i0 = 0; i0 < segs.length;) {
    let i1 = i0;
    while (i1 + 1 < segs.length && segs[i1 + 1].sy === segs[i0].sy) i1++;
    const n = i1 - i0 + 1, best = new Array(n + 1).fill(Infinity), from = new Array(n + 1).fill(-1);
    best[0] = 0;
    for (let j = 1; j <= n; j++) {
      for (let i = Math.max(0, j - 5); i < j; i++) {
        if (best[i] === Infinity) continue;
        const a = i0 + i, b = i0 + j - 1;
        const edge = a === 0 || b === segs.length - 1;
        let c = 2 * groupDev(a, b, edge);
        for (let t = a; t < b; t++) {
          const sp = (segs[t].sy.staves[0] && segs[t].sy.staves[0].st.space) || 16;
          const w = Math.min(segs[t].xb - segs[t].xa, segs[t + 1].xb - segs[t + 1].xa) / sp;
          c += w < 4 ? 0.15 : 0.45;
        }
        if (best[i] + c < best[j] - 1e-9) { best[j] = best[i] + c; from[j] = i; }
      }
    }
    const groups = [];
    for (let j = n; j > 0; j = from[j]) groups.unshift(Array.from({ length: j - from[j] }, (_, t) => i0 + from[j] + t));
    groups.forEach(g => measures.push({ segs: g }));
    i0 = i1 + 1;
  }
  // a bar split across a system break: two short halves that make one bar
  for (let k = 1; k + 1 < measures.length; k++) {
    const a = measures[k], b = measures[k + 1];
    if (segs[a.segs[0]].sy === segs[b.segs[0]].sy || a.segs.length > 1 || b.segs.length > 1) continue;
    const sa = segSum[a.segs[0]], sb = segSum[b.segs[0]];
    if (sa < mLen - 1e-6 && sb > 1e-6 && Math.abs(sa + sb - mLen) < 1e-6) { a.segs.push(...b.segs); measures.splice(k + 1, 1); }
  }
  if (opts.debug) segs.forEach((sg, i) => opts.debug.push(`seg ${i} sys ${sg.sy.page}:${sg.sy.index} x ${Math.round(sg.xa)}-${Math.round(sg.xb)} sum ${segSum[i]} streams ${segEv[i].map(ps => ps.map(evs => evs.map(e => (e.rest ? 'r' : '') + e.q).join(',')).join('/')).join(' | ')}`));
  const perPart = parts.map((p, pi) => measures.map(m => p.src.map((src, k) => ({
    staff: src.staff, events: m.segs.flatMap(si => segEv[si][pi][k]),
  }))));
  measures.forEach(m => { m.sy = segs[m.segs[0]].sy; m.sys = m.segs.map(si => segs[si].sy); });
  // remember which parts each head ended up in (overlay colouring)
  perPart.forEach((pm, pi) => pm.forEach(streams => streams.forEach(st => st.events.forEach(e => (e.heads || []).forEach(h => {
    (h.parts ||= []); if (!h.parts.includes(pi)) h.parts.push(pi);
  })))));

  // lyrics: each underlay line belongs to the staff above it. On a staff split
  // into two voices the line goes to ONE voice, chosen once per text band for
  // the whole piece from how well the syllables sit under each voice's onsets
  // (summed over every system and verse). With no clear winner a line between
  // staves goes to the upper voice (the melody) and a line under the lowest
  // split staff to its lower voice (the nearer one). A line whose local fit is
  // clearly better in the other voice (a divisi passage) follows that voice.
  // opts.copyLyrics copies every line to all fitting voices of its staff
  // (research-voices.md section 7.2). Keyboard staves never take underlay.
  const lyrNotes = new Set();
  const vocalStaves = parts.filter(p => p.kind !== 'keyboard').map(p => p.src[0].staff);
  const topVocal = vocalStaves.length ? Math.min(...vocalStaves) : -1;
  const splitStaves = parts.filter(p => p.kind !== 'keyboard' && p.src[0].voice === 2).map(p => p.src[0].staff);
  const lowestSplit = splitStaves.length ? Math.max(...splitStaves) : -1;
  const lines = [];
  for (const sy of systems) {
    const lyr = lyricsBySystem[sy.page + ':' + sy.index];
    if (!lyr || !lyr.length) continue;
    const sp = sy.staves[0] ? sy.staves[0].st.space : 16;
    const evCache = {};
    // sung notes of a part in this system (rests never take a syllable)
    const evOf = (pi) => (evCache[pi] ||= segs.flatMap((sg, si) => (sg.sy === sy ? segEv[si][pi][0] : [])).filter(e => !e.rest && !e.forward && e.heads && e.heads.length));
    const fitOf = (v) => parts.map((p, pi) => ({ p, pi })).filter(({ p }) => p.kind !== 'keyboard' && p.src[0].staff === v.band)
      .map(c => { const evs = evOf(c.pi); return { ...c, evs, fit: lyricFit(v.syllables, evs, sp), soft: softFit(v.syllables, evs, sp) }; });
    const sysLines = lyr.filter(v => v.syllables && v.syllables.length && !v.stanza).map(v => ({ sy, v, sp, cands: fitOf(v) })).filter(L => L.cands.length);
    // verses stack under the same staff: once one line of a band clearly
    // follows the notes, its sibling lines (same band, same system) are
    // underlay too and need only a looser fit (unhyphenated multi-note words
    // and OCR-merged words pull a line's syllables off the onsets)
    const bandOK = new Set(sysLines.filter(L => wordy(L.v.syllables) && L.cands.some(c => c.fit >= 0.5)).map(L => L.v.band));
    sysLines.forEach(L => { L.minFit = bandOK.has(L.v.band) ? 0.3 : 0.5; });
    lines.push(...sysLines);
  }
  // piece-wide evidence per text band: summed soft fit of each candidate part
  const bandEv = {};
  for (const L of lines) {
    if (L.cands.length < 2 || !wordy(L.v.syllables)) continue;
    const b = (bandEv[L.v.band] ||= {});
    for (const c of L.cands) b[c.pi] = (b[c.pi] || 0) + c.soft;
  }
  const bandVoice = {};
  for (const band in bandEv) {
    const e = bandEv[band], pis = Object.keys(e).map(Number).sort((a, b) => a - b);
    const lowest = +band === lowestSplit && +band !== topVocal;
    const prior = lowest ? pis[pis.length - 1] : pis[0];
    // a syllable under an onset that only one voice has adds about 1 to that
    // voice's total; voices that share every onset tie. A voice whose onsets
    // include the other's (eighths against quarters) can only gain, so a line
    // between staves leaves the melody (upper voice) only on strong evidence.
    let best = prior;
    for (const pi of pis) if (e[pi] > (lowest ? e[best] + 0.6 : 1.25 * e[best] + 2)) best = pi;
    bandVoice[band] = best;
    if (pis.length > 1) lyrNotes.add(`Lyrics under staff ${+band + 1} attached to ${parts[best].name} (${best === prior ? (lowest ? 'nearest voice' : 'upper voice') : 'its rhythm fits the syllables best'}).`);
  }
  for (const L of lines) {
    const { v, cands, sp } = L;
    let best = cands.find(c => c.pi === bandVoice[v.band]) || cands[0];
    // a clearly better local fit wins (a passage where the other voice sings the text)
    // (each voice with its own words and rhythm: the line sits under nearly
    // every onset of one voice and misses several of the other's)
    const nSyl = v.syllables.length, margin = Math.max(1.5, 0.15 * nSyl);
    for (const c of cands) {
      if (c === best || c.soft < best.soft + margin) continue;
      if ((best.fit < 0.6 && c.fit >= 0.8) || (c.soft >= 0.88 * nSyl && best.soft < 0.8 * nSyl)) best = c;
    }
    if (best.fit < L.minFit || !wordy(v.syllables)) { lyrNotes.add(`A text line under staff ${v.band + 1} does not follow the notes; not used as lyrics.`); continue; }
    const take = opts.copyLyrics ? cands.filter(c => c.fit >= L.minFit) : [best];
    if (opts.debug) opts.debug.push({ sys: L.sy.page + ':' + L.sy.index, band: v.band, n: v.number, nsyl: v.syllables.length, fits: cands.map(c => [c.p.name, +c.fit.toFixed(2), c.evs.length, +c.soft.toFixed(2)]), take: take.map(c => c.p.name) });
    for (const c of take) alignSyllables(v, c.evs, sp);
    v.used = take.map(c => c.p.name).join(', ');
  }
  lyrNotes.forEach(n => warnings.push(n));

  // rhythm repair: every voice must fill its measure. Measure length is the
  // time signature, or for an opening pickup / closing short bar the length
  // most voices agree on. Voices that do not fit are repaired by the cheapest
  // duration edits that make them fit and keep their onsets in step with the
  // voices that already fit; failing that the gap is left as <forward>.
  let mismatch = 0, repaired = 0, restsFound = 0, splitBars = 0;
  // a missed barline leaves two (or more) bars in one segment: when the voices
  // agree on about k bar lengths, cut every voice at the bar boundaries (notes
  // crossing a boundary are split and tied). A segment clearly longer than a
  // bar whose length is not a whole number of bars (a misread value inside)
  // is cut by position instead: at the onsets of a reference voice that fall
  // on whole bars, every voice cut at the same x.
  const units = [];
  measures.forEach((m, mi) => {
    const byPart = perPart.map(pm => pm[mi]);
    const sums = [];
    byPart.forEach(sts => sts.forEach(st => { const q = qsum(st.events); if (q > 1e-6) sums.push(Math.round(q * 4) / 4); }));
    const S = sums.length ? mode(sums) : 0;
    const k = Math.round(S / mLen);
    const agree = sums.filter(x => Math.abs(x - S) <= 0.25 * mLen).length;
    if (k >= 2 && Math.abs(S - k * mLen) <= 0.25 * mLen && agree >= Math.max(1, 0.5 * sums.length)) {
      splitBars += k - 1;
      const chunks = Array.from({ length: k }, () => byPart.map(sts => sts.map(st => ({ staff: st.staff, events: [] }))));
      byPart.forEach((sts, pi) => sts.forEach((st, si) => {
        let t = 0;
        for (const e of st.events) {
          let left = e.q, cur = e, first = true;
          while (left > 1e-6) {
            const c = Math.min(k - 1, Math.floor((t + 1e-6) / mLen));
            const room = (c + 1) * mLen - t;
            const take = c === k - 1 ? left : Math.min(left, room);
            const piece = take === e.q ? e : { ...cur, q: take, dots: qToType(take) ? qToType(take).dots : 0 };
            if (piece !== e) {
              if (!first) { piece.tieStop = true; piece.lyrics = undefined; }
              if (left - take > 1e-6 && !e.rest) piece.tieStart = true;
            }
            chunks[c][pi][si].events.push(piece);
            t += take; left -= take; first = false;
          }
        }
      }));
      chunks.forEach(ch => units.push({ m, streams: ch, split: true }));
      return;
    }
    if (S >= 1.75 * mLen - 1e-6 && sums.filter(x => x >= 1.5 * mLen).length >= Math.max(1, 0.5 * sums.length)) {
      // reference: the voice with the most onsets on whole bars
      let ref = null;
      byPart.forEach(sts => sts.forEach(st => {
        let t = 0;
        const cuts = [];
        st.events.forEach((e, i) => {
          if (i > 0 && t > 1e-6 && e.x != null && st.events[i - 1].x != null && Math.abs(t / mLen - Math.round(t / mLen)) < 1e-6) cuts.push((st.events[i - 1].x + e.x) / 2);
          t += e.q;
        });
        if (cuts.length && (!ref || cuts.length > ref.length)) ref = cuts;
      }));
      if (ref) {
        const xs = ref.sort((a, b) => a - b);
        const chunks = Array.from({ length: xs.length + 1 }, () => byPart.map(sts => sts.map(st => ({ staff: st.staff, events: [] }))));
        byPart.forEach((sts, pi) => sts.forEach((st, si) => {
          let c = 0;
          for (const e of st.events) {
            if (e.x != null) while (c < xs.length && e.x > xs[c]) c++;
            chunks[c][pi][si].events.push(e);
          }
        }));
        splitBars += xs.length;
        chunks.forEach(ch => units.push({ m, streams: ch, split: true }));
        return;
      }
    }
    units.push({ m, streams: byPart, split: false });
  });
  const partMeasures = parts.map(() => []);
  units.forEach((u, mi) => {
    const m = u.m;
    const streams = [];
    parts.forEach((p, pi) => u.streams[pi].forEach((st, k) => streams.push({ pi, k, staff: st.staff, events: st.events.slice() })));
    const sums = streams.map(st => qsum(st.events));
    const nz = sums.filter(x => x > 1e-6).map(x => Math.round(x * DIV) / DIV);
    let target = mLen;
    const ms = nz.length ? mode(nz) : 0;
    const agree = nz.filter(x => Math.abs(x - ms) < 1e-6).length;
    const edge = mi === 0 || mi === units.length - 1;
    if (edge && ms > 1e-6 && ms < mLen - 1e-6 && agree >= Math.max(2, 0.5 * nz.length)) target = ms;
    else if (edge && ms > 1e-6 && ms < mLen - 1e-6 && nz.length === 1) target = ms;
    // rests printed in the voices of a measure (looked up only when needed)
    const restCache = new Map();
    const restsOf = (st) => {
      if (u.split || m.segs.some(si => segs[si].sy !== segs[m.segs[0]].sy)) return [];
      if (!restCache.has(st)) {
        const s0 = segs[m.segs[0]], seg = { ...s0, xb: segs[m.segs[m.segs.length - 1]].xb }, sv = seg.sy.staves[st.staff];
        restCache.set(st, sv ? findRests(seg, sv, parts[st.pi].src[st.k].voice) : []);
      }
      return restCache.get(st);
    };
    // a short opening bar whose voices show printed rests that fill it up is
    // a full bar starting with rests, not a pickup
    if (mi === 0 && target < mLen - 1e-6) {
      const short = streams.filter((st, i) => sums[i] > 1e-6 && sums[i] < mLen - 1e-6);
      const filled = short.filter(st => restsOf(st).length && placeRests(st.events, restsOf(st), mLen - qsum(st.events))).length;
      if (filled && filled >= 0.5 * short.length) target = mLen;
    }
    const implicit = mi === 0 && target < mLen - 1e-6;
    const sp = (m.sy.staves[0] && m.sy.staves[0].st.space) || 16;
    const anchors = [];
    streams.forEach((st, i) => {
      if (Math.abs(sums[i] - target) > 1e-6) return;
      let t = 0;
      for (const e of st.events) { if (!e.rest && e.x != null) anchors.push({ x: e.x, t, i }); t += e.q; }
    });
    streams.forEach((st, i) => {
      let evs = st.events;
      if (sums[i] <= 1e-6) evs = [{ rest: true, q: target, dots: 0, whole: true }];
      else if (Math.abs(sums[i] - target) > 1e-6) {
        let placed = null;
        if (sums[i] < target) placed = placeRests(evs, restsOf(st), target - sums[i]);
        if (placed) { evs = placed; restsFound++; }
        else {
          const r = repairStream(evs, target, anchors.filter(a => a.i !== i), sp);
          evs = r.events;
          if (r.ok) repaired++; else mismatch++;
        }
      }
      (partMeasures[st.pi][mi] ||= [])[st.k] = { staff: st.staff, events: evs, implicit };
    });
  });
  if (splitBars) warnings.push(`${splitBars} barlines were missing on the page; bars were split by their contents.`);
  if (restsFound) warnings.push(`${restsFound} voice-measures completed with rests read from the page.`);
  if (repaired) warnings.push(`${repaired} voice-measures repaired to fit ${time.beats}/${time.type} (likely misread dots, flags or beams).`);
  if (mismatch) warnings.push(`${mismatch} voice-measures still did not add up to ${time.beats}/${time.type}; gaps left empty, notes past the barline cut.`);
  const xml = toMusicXML({ parts, partMeasures, fifths, kAlt, time, clefs, measures });
  const nNotes = partMeasures.map(pm => pm.reduce((a, m) => a + m.reduce((b, s) => b + s.events.filter(e => !e.rest && !e.forward).length, 0), 0));
  const ranges = partMeasures.map(pm => {
    let lo = null, hi = null;
    pm.forEach(m => m.forEach(st => st.events.forEach(e => (e.heads || []).forEach(h => {
      if (!h.pitch) return;
      if (!lo || h.pitch.d < lo.d) lo = h.pitch;
      if (!hi || h.pitch.d > hi.d) hi = h.pitch;
    }))));
    return lo ? `${lo.step}${lo.octave}\u2013${hi.step}${hi.octave}` : '-';
  });
  // UI compares clefs with 'F'; 'G8' stays a treble clef there
  return { parts, layout, fifths, time, clefs, ranges, measures: units.length, nNotes, warnings: warnings.concat(layout.notes), xml };
}

// Horizontal extent of a syllable: lyrics.js may report x0/x1; otherwise it is
// estimated from the letter count (about 1.1 staff spaces per letter).
function sylBox(s, sp) {
  if (s.x0 != null && s.x1 != null && s.x1 > s.x0) return [s.x0, s.x1];
  const w = Math.max(1, String(s.text || '').length) * 1.1 * sp;
  return [s.x - w / 2, s.x + w / 2];
}

// Distance from a syllable to a notehead centre at x. A syllable is printed
// centred under its note, except one that starts a melisma (a word held over
// several notes, drawn with an extender line), which is left-aligned with the
// notehead; so a long syllable may also sit with its left edge at the head.
// Long tokens (7+ letters) are more often two syllables OCR read as one word
// ("cherchons") and keep the centred reading only.
function sylDist(s, x, sp) {
  const c = Math.abs(x - s.x);
  if (String(s.text || '').replace(/[^\p{L}]/gu, '').length > 6) return c;
  const x0 = sylBox(s, sp)[0];
  return Math.min(c, Math.abs(x - (x0 + 0.55 * sp)) + 0.15 * sp);
}

// share of syllables that sit under an onset of the stream
function lyricFit(syl, evs, sp) {
  if (!syl.length || !evs.length) return 0;
  let hit = 0;
  for (const s of syl) {
    let d = 1e9;
    for (const e of evs) { const t = sylDist(s, e.x, sp); if (t < d) d = t; }
    if (d <= 1.2 * sp) hit++;
  }
  return hit / syl.length;
}

// graded version of lyricFit: 1 for a syllable right under an onset, falling
// to 0 at `tol` staff spaces away (separates two voices of one staff that
// share most onsets)
function softFit(syl, evs, sp, tol = 0.8) {
  let s = 0;
  for (const y of syl) {
    let d = 1e9;
    for (const e of evs) if (!e.rest && e.x != null) d = Math.min(d, sylDist(y, e.x, sp));
    s += Math.max(0, 1 - d / (tol * sp));
  }
  return s;
}

// OCR junk (dynamics, stray marks read as letters) rather than words
function wordy(syl) {
  if (syl.length < 3) return false;
  const good = syl.filter(s => /[a-zà-ɏ]{2}/.test(s.text) || /^[A-ZÀ-Þ][a-zà-ɏ]/.test(s.text)).length;
  return good >= 0.4 * syl.length;
}

// Monotonic alignment of the syllables of one verse line to the onsets of one
// voice (both left to right): each syllable takes one onset, onsets without a
// syllable are melisma continuations, syllables far from any onset are dropped.
// Tied continuation notes never take a syllable. A word-final syllable held
// over the following notes of its voice gets an extender (<extend/> start on
// its note, stop on the last note of the melisma); hyphenated syllables do not
// (their hyphen spans the melisma).
function alignSyllables(verse, evs, sp) {
  const syl = verse.syllables, n = syl.length, m = evs.length;
  if (!n || !m) return;
  const SKIP_EV = 0.15, DROP_SYL = 2.2;
  const cost = (i, j) => (evs[j].tieStop ? Infinity : Math.min(3, sylDist(syl[i], evs[j].x, sp) / sp));
  // D[i][j]: best cost using syllables < i and onsets < j
  const W = m + 1;
  const D = new Float64Array((n + 1) * W).fill(Infinity), T = new Uint8Array((n + 1) * W);
  D[0] = 0;
  for (let i = 0; i <= n; i++) for (let j = 0; j <= m; j++) {
    const here = D[i * W + j];
    if (here === Infinity) continue;
    if (i < n && j < m) { const v = here + cost(i, j); if (v < D[(i + 1) * W + j + 1]) { D[(i + 1) * W + j + 1] = v; T[(i + 1) * W + j + 1] = 1; } }
    if (j < m) { const v = here + SKIP_EV; if (v < D[i * W + j + 1]) { D[i * W + j + 1] = v; T[i * W + j + 1] = 2; } }
    if (i < n) { const v = here + DROP_SYL; if (v < D[(i + 1) * W + j]) { D[(i + 1) * W + j] = v; T[(i + 1) * W + j] = 3; } }
  }
  let i = n, j = m;
  const pairs = [];
  while (i > 0 || j > 0) {
    const t = T[i * W + j];
    if (t === 1) { pairs.push([i - 1, j - 1]); i--; j--; }
    else if (t === 2) j--;
    else i--;
  }
  pairs.reverse();
  const num = verse.number;
  const placed = [];
  for (const [a, b] of pairs) {
    const ev = evs[b], s = syl[a];
    ev.lyrics ||= {};
    if (ev.lyrics[num]) continue;
    ev.lyrics[num] = { text: s.text, syllabic: s.syllabic };
    placed.push([a, b]);
  }
  // melismas between placed syllables
  placed.forEach(([a, b], k) => {
    const s = syl[a];
    if (s.syllabic !== 'single' && s.syllabic !== 'end') return;
    const next = k + 1 < placed.length ? placed[k + 1][1] : null;
    // after the last syllable of the line only with an extender seen in print
    const last = next != null ? next - 1 : (s.ext ? m - 1 : b);
    if (last <= b || (last - b > 6 && !s.ext)) return;
    for (let t = b + 1; t <= last; t++) if (evs[t].lyrics && evs[t].lyrics[num]) return;
    evs[b].lyrics[num].extend = true;
    (evs[last].lyrExt ||= {})[num] = true;
  });
}

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function emptyXML() {
  return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n<score-partwise version="4.0"><part-list/></score-partwise>\n';
}

function clefXML(c, n) {
  const num = n ? ` number="${n}"` : '';
  if (c === 'F') return `<clef${num}><sign>F</sign><line>4</line></clef>`;
  if (c === 'G8') return `<clef${num}><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change></clef>`;
  return `<clef${num}><sign>G</sign><line>2</line></clef>`;
}

function toMusicXML({ parts, partMeasures, fifths, kAlt, time, clefs, title }) {
  const L = [];
  L.push('<?xml version="1.0" encoding="UTF-8" standalone="no"?>');
  L.push('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">');
  L.push('<score-partwise version="4.0">');
  L.push(`  <work><work-title>${esc(title || 'Scanned score')}</work-title></work>`);
  L.push('  <identification><encoding><software>Score Scan Reader (classical OMR, browser)</software></encoding></identification>');
  L.push('  <part-list>');
  // vocal parts split from shared staves are bracketed as one choir group
  const vocalIdx = parts.map((p, i) => (p.kind === 'vocal' ? i : -1)).filter(i => i >= 0);
  const groupChoir = vocalIdx.length >= 2 && vocalIdx.every((v, k) => k === 0 || v === vocalIdx[k - 1] + 1) &&
    parts.some(p => p.kind === 'vocal' && (p.src[0].voice === 1 || p.src[0].voice === 2));
  parts.forEach((p, i) => {
    if (groupChoir && i === vocalIdx[0]) L.push('    <part-group type="start" number="1"><group-name>Choir</group-name><group-symbol>bracket</group-symbol><group-barline>no</group-barline></part-group>');
    L.push(`    <score-part id="${p.id}"><part-name>${esc(p.name)}</part-name></score-part>`);
    if (groupChoir && i === vocalIdx[vocalIdx.length - 1]) L.push('    <part-group type="stop" number="1"/>');
  });
  L.push('  </part-list>');
  parts.forEach((p, pi) => {
    L.push(`  <part id="${p.id}">`);
    const nStaves = p.src.length;
    const multi = nStaves > 1;
    partMeasures[pi].forEach((streams, mi) => {
      const implicit = streams.every(s => s.implicit);
      L.push(`    <measure number="${implicit ? 0 : mi + (partMeasures[pi][0].every(s => s.implicit) ? 0 : 1)}"${implicit ? ' implicit="yes"' : ''}>`);
      if (mi === 0) {
        L.push(`      <attributes><divisions>${DIV}</divisions><key><fifths>${fifths}</fifths></key><time><beats>${time.beats}</beats><beat-type>${time.type}</beat-type></time>` +
          (multi ? `<staves>${nStaves}</staves>${p.src.map((s, k) => clefXML(clefs[s.staff], k + 1)).join('')}` : clefXML(clefs[p.src[0].staff])) + '</attributes>');
      }
      streams.forEach((s, si) => {
        if (si > 0) {
          const prev = streams[si - 1].events.reduce((a, e) => a + Math.max(1, Math.round(e.q * DIV)), 0);
          if (prev) L.push(`      <backup><duration>${prev}</duration></backup>`);
        }
        const clef = clefs[s.staff] || 'G';
        const measAcc = {};
        const voice = multi ? 1 + 4 * si : 1;
        const staffTag = multi ? `<staff>${si + 1}</staff>` : '';
        for (const e of s.events) {
          const dur = Math.max(1, Math.round(e.q * DIV));
          const tt = qToType(e.q);
          const typeXML = tt ? `<type>${tt.type}</type>${'<dot/>'.repeat(tt.dots)}` : '';
          if (e.forward) {
            L.push(`      <forward><duration>${dur}</duration><voice>${voice}</voice>${staffTag}</forward>`);
            continue;
          }
          if (e.rest) {
            if (e.whole) L.push(`      <note><rest measure="yes"/><duration>${dur}</duration><voice>${voice}</voice>${staffTag}</note>`);
            else L.push(`      <note><rest/><duration>${dur}</duration><voice>${voice}</voice>${typeXML}${staffTag}</note>`);
            continue;
          }
          e.heads.forEach((h, hi) => {
            const pos = h.p;
            const pk = pitchOf(clef, pos, kAlt, {});
            if (h.acc) measAcc[pk.step + pk.octave] = h.acc === 'sharp' ? 1 : h.acc === 'flat' ? -1 : 0;
            const pt = pitchOf(clef, pos, kAlt, measAcc);
            h.pitch = pt;
            const acc = h.acc && !e.tieStop ? `<accidental>${h.acc}</accidental>` : '';
            const tie = (e.tieStop ? '<tie type="stop"/>' : '') + (e.tieStart ? '<tie type="start"/>' : '');
            const tied = e.tieStop || e.tieStart ? `<notations>${e.tieStop ? '<tied type="stop"/>' : ''}${e.tieStart ? '<tied type="start"/>' : ''}</notations>` : '';
            const stem = h.stemDir === 1 ? '<stem>up</stem>' : h.stemDir === -1 ? '<stem>down</stem>' : '';
            let lyr = '';
            if (hi === 0 && (e.lyrics || e.lyrExt)) {
              const nums = new Set([...Object.keys(e.lyrics || {}), ...Object.keys(e.lyrExt || {})]);
              for (const n of [...nums].sort((a, b) => a - b)) {
                const l = e.lyrics && e.lyrics[n];
                if (l) lyr += `<lyric number="${n}"><syllabic>${l.syllabic}</syllabic><text>${esc(l.text)}</text>${l.extend ? '<extend type="start"/>' : ''}</lyric>`;
                else lyr += `<lyric number="${n}"><extend type="stop"/></lyric>`;
              }
            }
            L.push(`      <note>${hi > 0 ? '<chord/>' : ''}<pitch><step>${pt.step}</step>${pt.alter ? `<alter>${pt.alter}</alter>` : ''}<octave>${pt.octave}</octave></pitch>` +
              `<duration>${dur}</duration>${tie}<voice>${voice}</voice>${typeXML}${acc}${stem}${staffTag}${tied}${lyr}</note>`);
          });
        }
      });
      if (mi === partMeasures[pi].length - 1) L.push('      <barline location="right"><bar-style>light-heavy</bar-style></barline>');
      L.push('    </measure>');
    });
    L.push('  </part>');
  });
  L.push('</score-partwise>');
  return L.join('\n') + '\n';
}

module.exports = { buildScore, chooseLayout, chooseKey, COLORS };
