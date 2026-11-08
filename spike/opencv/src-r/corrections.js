'use strict';
// User corrections: what the reader said an unrecognised mark is, applied to
// the MusicXML after buildScore. Two pure steps, so a re-run of the
// conversion simply applies them again:
//   resolveCorrections(idents, pages, measureMap) -> corrections
//     ties each identified mark to the notes around it (page geometry: the
//     overlay's pageView heads and the result's per-head notes)
//   applyCorrections(xml, corrections) -> { xml, applied, skipped, warnings }
//     edits the MusicXML text at the lines those notes were written on
// correctScore(score, idents, pages) runs both on a score.
//
// An ident is { id, page, box: [x0, y0, x1, y1], type, sub, detail } in the
// page's overlay frame. pages[page] = { ss, heads: [[x, y, r, stem, top, bot]],
// notes: [[step, alter, octave, q, type, dots, tuplet, line] | 0] }.
// Applied: an accidental (to the nearest note to its right on its staff), a
// rest (at its place in the bar, by the notes around it), an augmentation dot
// (to the nearest note to its left) and a dynamic (before the nearest note).
// 'noise' only hides the mark; every other type is kept as a label only.

const ACC_ALTER = { sharp: 1, flat: -1, natural: 0, 'double-sharp': 2, 'flat-flat': -2 };
const REST_Q = { whole: 4, half: 2, quarter: 1, eighth: 0.5, '16th': 0.25, '32nd': 0.125 };
const DYNAMICS = ['pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff', 'sf', 'sfz', 'sffz', 'fp', 'rfz'];

// heads of a page with what was written for them, and the staff band of each
function pageHeads(pg) {
  const out = [];
  (pg.heads || []).forEach((h, k) => {
    const n = (pg.notes || [])[k];
    out.push({ k, x: h[0], y: h[1], r: h[2], top: h[4] != null ? h[4] : h[1], bot: h[5] != null ? h[5] : h[1], note: n || null, line: n && n[7] >= 0 ? n[7] : -1 });
  });
  return out;
}
// heads on the staff a mark at height cy belongs to: the staff (by its
// heads' staff edges) whose band, 3 spaces either side, holds cy most centrally
function staffHeads(hs, cy, ss) {
  let best = null, bd = Infinity;
  for (const h of hs) {
    if (cy < h.top - 3 * ss || cy > h.bot + 3 * ss) continue;
    const d = Math.abs(cy - (h.top + h.bot) / 2);
    if (d < bd) { bd = d; best = h; }
  }
  if (!best) return [];
  return hs.filter(h => Math.abs(h.top - best.top) < 1.5 * ss);
}

function resolveCorrections(idents, pages, measureMap) {
  const out = [];
  for (const id of idents || []) {
    const pg = pages && pages[id.page];
    const base = { id: id.id, page: id.page, type: id.type, sub: id.sub || null };
    if (id.type === 'noise') { out.push({ ...base, kind: 'hide' }); continue; }
    if (!pg || !pg.heads) { out.push({ ...base, kind: 'skip', why: 'page not read in this session' }); continue; }
    const ss = pg.ss || 16, [x0, y0, x1, y1] = id.box, cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    const hs = pageHeads(pg).filter(h => h.line >= 0);
    const onStaff = staffHeads(hs, cy, ss);
    if (id.type === 'acc') {
      const alter = ACC_ALTER[id.sub];
      if (alter === undefined) { out.push({ ...base, kind: 'skip', why: 'unknown accidental' }); continue; }
      let best = null, bd = Infinity;
      for (const h of onStaff) {
        const dx = h.x - x1, dy = Math.abs(h.y - cy);
        if (dx < -0.3 * ss || dx > 4 * ss || dy > 1.3 * ss) continue;
        const d = dx + 2 * dy;
        if (d < bd) { bd = d; best = h; }
      }
      if (!best) { out.push({ ...base, kind: 'skip', why: 'no note just right of it on its staff' }); continue; }
      out.push({ ...base, kind: 'accidental', line: best.line, step: best.note[0], octave: best.note[2], alter, name: id.sub, head: best.k });
    } else if (id.type === 'dot') {
      let best = null, bd = Infinity;
      for (const h of onStaff) {
        const dx = x0 - h.x, dy = Math.abs(h.y - cy);
        if (dx < 0 || dx > 3 * ss || dy > 1.3 * ss) continue;
        const d = dx + 2 * dy;
        if (d < bd) { bd = d; best = h; }
      }
      if (!best) { out.push({ ...base, kind: 'skip', why: 'no note just left of it on its staff' }); continue; }
      out.push({ ...base, kind: 'dot', line: best.line, step: best.note[0], octave: best.note[2], head: best.k });
    } else if (id.type === 'rest') {
      const q = REST_Q[id.sub];
      if (!q) { out.push({ ...base, kind: 'skip', why: 'unknown rest value' }); continue; }
      const m = (measureMap || []).find(mm => mm.page === id.page && cx >= mm.xa && cx <= mm.xb && cy >= mm.y0 - 3 * ss && cy <= mm.y1 + 3 * ss);
      const inBar = onStaff.filter(h => !m || (h.x >= m.xa && h.x <= m.xb));
      const before = inBar.filter(h => h.x < cx).sort((a, b) => b.x - a.x)[0];
      const after = inBar.filter(h => h.x >= cx).sort((a, b) => a.x - b.x)[0];
      if (!m || (!before && !after)) { out.push({ ...base, kind: 'skip', why: m ? 'no note on its staff in that bar to place it by' : 'not inside a bar that was read' }); continue; }
      out.push({ ...base, kind: 'rest', q, value: id.sub, measure: m.n, ...(before ? { afterLine: before.line, head: before.k } : { beforeLine: after.line, head: after.k }) });
    } else if (id.type === 'dyn') {
      if (!DYNAMICS.includes(id.sub)) { out.push({ ...base, kind: 'skip', why: 'unknown dynamic' }); continue; }
      const pool = onStaff.length ? onStaff : hs;
      let best = null, bd = Infinity;
      for (const h of pool) {
        const d = Math.abs(h.x - cx) + (h.x < x0 - ss ? 2 * ss : 0) + 0.3 * Math.abs(h.y - cy);
        if (d < bd) { bd = d; best = h; }
      }
      if (!best) { out.push({ ...base, kind: 'skip', why: 'no note near it' }); continue; }
      out.push({ ...base, kind: 'dynamic', value: id.sub, beforeLine: best.line, placement: cy < best.top ? 'above' : 'below', head: best.k });
    } else out.push({ ...base, kind: 'label' });
  }
  return out;
}

// ------------------------------------------------------------- the XML ---
const isNote = (l) => /^\s*<note>/.test(l || '');
const isChordMate = (l) => /^\s*<note><chord\/>/.test(l || '');
function chordStart(L, i) { while (i > 0 && isChordMate(L[i])) i--; return i; }
function chordEnd(L, i) { while (isChordMate(L[i + 1])) i++; return i; }
// the next <backup> of this measure after line i (its voice ran longer)
function bumpBackup(L, i, d) {
  for (let j = i + 1; j < L.length && !/<\/measure>/.test(L[j]); j++) {
    const m = L[j].match(/<backup><duration>(\d+)<\/duration><\/backup>/);
    if (m) { L[j] = L[j].replace(m[0], `<backup><duration>${+m[1] + d}</duration></backup>`); return; }
  }
}
const measureOf = (L, i) => { for (let j = i; j >= 0; j--) { const m = L[j].match(/<measure number="([^"]+)"/); if (m) return m[1]; } return '?'; };
const tag = (l, t) => { const m = l.match(new RegExp(`<${t}>([^<]*)</${t}>`)); return m ? m[1] : null; };
const TYPE_OF = [[4, 'whole'], [2, 'half'], [1, 'quarter'], [0.5, 'eighth'], [0.25, '16th'], [0.125, '32nd']];

function applyCorrections(xml, corrections) {
  const applied = [], skipped = [], warnings = [];
  if (!xml || !corrections || !corrections.length) return { xml, applied, skipped, warnings };
  const L = xml.split('\n');
  const div = +((xml.match(/<divisions>(\d+)<\/divisions>/) || [])[1] || 0);
  const check = (c, i) => {
    const l = L[i];
    if (!isNote(l) || !/<pitch>/.test(l)) return 'its note is not in this MusicXML';
    if (c.step && (tag(l, 'step') !== c.step || +tag(l, 'octave') !== c.octave)) return 'its note changed since it was identified';
    return null;
  };
  const longer = new Set();
  // edits in place first (line numbers stay), then insertions from the bottom up
  const edits = corrections.filter(c => c.kind === 'accidental' || c.kind === 'dot');
  const inserts = corrections.filter(c => c.kind === 'rest' || c.kind === 'dynamic');
  for (const c of edits) {
    const why = check(c, c.line);
    if (why) { skipped.push({ id: c.id, kind: c.kind, why }); continue; }
    if (c.kind === 'accidental') {
      let l = L[c.line];
      l = l.replace(/<pitch><step>([A-G])<\/step>(?:<alter>[^<]*<\/alter>)?<octave>/, (_, s) => `<pitch><step>${s}</step>${c.alter ? `<alter>${c.alter}</alter>` : ''}<octave>`);
      l = l.replace(/<accidental>[^<]*<\/accidental>/, '');
      const acc = `<accidental>${c.name}</accidental>`;
      if (/<dot\/>/.test(l)) l = l.replace(/((?:<dot\/>)+)/, `$1${acc}`);
      else if (/<\/type>/.test(l)) l = l.replace('</type>', `</type>${acc}`);
      else l = l.replace('</voice>', `</voice>${acc}`);
      L[c.line] = l;
      applied.push({ id: c.id, kind: c.kind, measure: measureOf(L, c.line), text: `${c.name} on ${c.step}${c.octave}` });
    } else {
      const a = chordStart(L, c.line), b = chordEnd(L, c.line);
      const dots = (L[a].match(/<dot\/>/g) || []).length;
      const d0 = +tag(L[a], 'duration');
      const base = d0 / (2 - Math.pow(2, -dots)), d1 = Math.round(base * (2 - Math.pow(2, -(dots + 1))));
      if (!(d1 > d0)) { skipped.push({ id: c.id, kind: c.kind, why: 'the note value cannot take another dot' }); continue; }
      for (let i = a; i <= b; i++) {
        let l = L[i].replace(`<duration>${d0}</duration>`, `<duration>${d1}</duration>`);
        if (/<dot\/>/.test(l)) l = l.replace(/((?:<dot\/>)+)/, '$1<dot/>');
        else if (/<\/type>/.test(l)) l = l.replace('</type>', '</type><dot/>');
        L[i] = l;
      }
      bumpBackup(L, b, d1 - d0);
      longer.add(measureOf(L, a));
      applied.push({ id: c.id, kind: c.kind, measure: measureOf(L, a), text: `dot on ${c.step}${c.octave}` });
    }
  }
  const at = (c) => (c.kind === 'rest' ? (c.afterLine != null ? c.afterLine + 0.5 : c.beforeLine - 0.5) : c.beforeLine - 0.5);
  for (const c of inserts.slice().sort((p, q) => at(q) - at(p))) {
    const ref = c.afterLine != null ? c.afterLine : c.beforeLine;
    if (!isNote(L[ref])) { skipped.push({ id: c.id, kind: c.kind, why: 'its neighbouring note is not in this MusicXML' }); continue; }
    const voice = tag(L[ref], 'voice'), staff = tag(L[ref], 'staff');
    const staffXML = staff ? `<staff>${staff}</staff>` : '';
    if (c.kind === 'rest') {
      if (!div) { skipped.push({ id: c.id, kind: c.kind, why: 'no divisions in the MusicXML' }); continue; }
      const d = Math.max(1, Math.round(c.q * div)), type = (TYPE_OF.find(t => Math.abs(t[0] - c.q) < 1e-6) || [0, c.value])[1];
      const line = `      <note><rest/><duration>${d}</duration><voice>${voice}</voice><type>${type}</type>${staffXML}</note>`;
      const i = c.afterLine != null ? chordEnd(L, c.afterLine) + 1 : chordStart(L, c.beforeLine);
      L.splice(i, 0, line);
      bumpBackup(L, i, d);
      longer.add(measureOf(L, i));
      applied.push({ id: c.id, kind: c.kind, measure: measureOf(L, i), text: `${type} rest` });
    } else {
      const i = chordStart(L, c.beforeLine);
      L.splice(i, 0, `      <direction placement="${c.placement}"><direction-type><dynamics><${c.value}/></dynamics></direction-type>${staffXML}</direction>`);
      applied.push({ id: c.id, kind: c.kind, measure: measureOf(L, i), text: c.value });
    }
  }
  for (const m of longer) warnings.push(`Bar ${m}: your correction makes it longer than its time signature (not rebalanced).`);
  return { xml: L.join('\n'), applied, skipped, warnings };
}

function correctScore(score, idents, pages) {
  const cs = resolveCorrections(idents, pages, score && score.measureMap);
  const r = applyCorrections(score && score.xml, cs.filter(c => c.kind !== 'hide' && c.kind !== 'skip' && c.kind !== 'label'));
  return {
    ...score, xml: r.xml,
    corrections: { applied: r.applied, skipped: r.skipped.concat(cs.filter(c => c.kind === 'skip').map(c => ({ id: c.id, kind: c.type, why: c.why }))),
      hidden: cs.filter(c => c.kind === 'hide').length, labels: cs.filter(c => c.kind === 'label').length, warnings: r.warnings },
  };
}

module.exports = { resolveCorrections, applyCorrections, correctScore, ACC_ALTER, REST_Q, DYNAMICS };
