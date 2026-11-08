/* global omrRequire */
// Score playback: a transport bar and parts mixer in the notation preview,
// a Web Audio synth (self-hosted sampled General MIDI subset, loaded per
// instrument on first use, oscillator fallback), follow-along on the OSMD
// cursor and on the scan's note heads, and a Standard MIDI File export.
// The timing model is src/playback.js (events), shared with the Node tests.
// app.js calls ScorePlayer.attach({ xml, osmd, book, res }) after each preview
// render; nothing else in app.js depends on this module.
(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const PB = () => omrRequire('playback');
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const fmtT = (s) => { s = Math.max(0, s); const m = Math.floor(s / 60); return `${m}:${String(Math.floor(s % 60)).padStart(2, '0')}`; };
  const LOOKAHEAD = 0.1; // seconds of audio scheduled ahead of the clock
  const TICK_MS = 25;

  // ------------------------------------------------------------ sounds ---
  // sample set per GM program (tools/soundfont.mjs writes assets/gm-<set>.json)
  const ENV = {
    piano: { a: 0.004, r: 0.28, loop: false }, organ: { a: 0.02, r: 0.09, loop: true }, choir: { a: 0.09, r: 0.32, loop: true },
    oohs: { a: 0.08, r: 0.3, loop: true }, strings: { a: 0.07, r: 0.3, loop: true }, flute: { a: 0.04, r: 0.14, loop: true },
    clarinet: { a: 0.03, r: 0.12, loop: true }, brass: { a: 0.03, r: 0.14, loop: true },
  };
  function setFor(program) {
    if (program < 0) return null;
    if (program <= 15 || (program >= 24 && program <= 31) || program === 46 || program === 105 || program === 107) return 'piano';
    if (program <= 23) return 'organ';
    if (program <= 51 || program === 55) return program === 47 ? null : 'strings';
    if (program === 52) return 'choir';
    if (program <= 54) return 'oohs';
    if (program <= 63) return 'brass';
    if (program <= 71) return 'clarinet';
    if (program <= 79) return 'flute';
    if (program === 85 || program === 91) return 'oohs';
    if (program >= 88 && program <= 95) return 'strings';
    return null;
  }
  const sets = new Map(); // name -> Promise<{notes: [[midi, AudioBuffer]]} | null>
  function b64buf(b64) { const bin = atob(b64); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u.buffer; }
  function loadSet(name, ctx) {
    if (!name) return Promise.resolve(null);
    if (sets.has(name)) return sets.get(name);
    const p = (async () => {
      const r = await fetch(`assets/gm-${name}.json`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = await r.json();
      const decode = (ab) => new Promise((res, rej) => { const q = ctx.decodeAudioData(ab, res, rej); if (q && q.then) q.then(res, rej); });
      const notes = await Promise.all(Object.entries(j.notes).map(async ([m, b]) => [+m, await decode(b64buf(b))]));
      notes.sort((a, b) => a[0] - b[0]);
      return { notes };
    })().catch((e) => { st.msg(`The ${name} sounds did not load (${e.message}); a simple synth plays instead.`); return null; });
    sets.set(name, p);
    return p;
  }
  const loadedSet = (name) => { const s = name && st.loaded.get(name); return s || null; };
  function nearest(set, midi) {
    let best = set.notes[0];
    for (const n of set.notes) if (Math.abs(n[0] - midi) < Math.abs(best[0] - midi)) best = n;
    return best;
  }
  // one note on ctx at time t (ctx seconds) for dur seconds into dest; returns a stopper
  function voice(ctx, dest, program, midi, vel, t, dur) {
    const g = ctx.createGain();
    const amp = Math.pow(vel / 127, 1.5) * 0.55;
    g.connect(dest);
    const name = setFor(program), set = loadedSet(name);
    if (set) {
      const env = ENV[name];
      const [sm, buf] = nearest(set, midi);
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.playbackRate.value = Math.pow(2, (midi - sm) / 12);
      const bufDur = buf.duration / src.playbackRate.value;
      if (env.loop && dur > bufDur - 0.45) { src.loop = true; src.loopStart = Math.min(1, buf.duration * 0.35); src.loopEnd = Math.max(src.loopStart + 0.2, buf.duration - 0.35); }
      const end = t + (env.loop ? dur : Math.min(dur, bufDur));
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(amp, t + env.a);
      g.gain.setValueAtTime(amp, Math.max(t + env.a, end));
      g.gain.setTargetAtTime(0, Math.max(t + env.a, end), env.r / 3);
      src.connect(g);
      src.start(t);
      src.stop(end + env.r * 1.6 + 0.05);
      return { stop: (at) => { try { g.gain.cancelScheduledValues(at); g.gain.setTargetAtTime(0, at, 0.02); src.stop(at + 0.1); } catch (e) { /* already stopped */ } }, end: end + env.r * 1.6 };
    }
    // fallback: two detuned oscillators with an ADSR; drums a noise-like click
    const drum = program < 0;
    const fam = PB().gmFamily(program);
    const freq = drum ? 180 + (midi % 12) * 40 : 440 * Math.pow(2, (midi - 69) / 12);
    const o1 = ctx.createOscillator(), o2 = ctx.createOscillator();
    o1.type = drum ? 'square' : fam === 'organ' || fam === 'reed' ? 'square' : fam === 'brass' || fam === 'strings' ? 'sawtooth' : 'triangle';
    o2.type = 'sine';
    o1.frequency.value = freq; o2.frequency.value = freq * (drum ? 1.5 : 1.002);
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = Math.min(9000, freq * (drum ? 4 : 6));
    o1.connect(lp); o2.connect(lp); lp.connect(g);
    const plucked = drum || fam === 'piano' || fam === 'guitar';
    const a = drum ? 0.002 : plucked ? 0.005 : 0.04, r = drum ? 0.05 : plucked ? 0.25 : 0.15;
    const len = drum ? 0.08 : dur;
    const peak = amp * (o1.type === 'triangle' ? 0.9 : 0.35);
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(peak, t + a);
    if (plucked) g.gain.setTargetAtTime(peak * 0.25, t + a, Math.max(0.05, len * 0.6));
    g.gain.setValueAtTime(plucked ? peak * 0.3 : peak * 0.85, Math.max(t + a, t + len));
    g.gain.setTargetAtTime(0, Math.max(t + a, t + len), r / 3);
    const stopAt = t + len + r * 1.6 + 0.05;
    o1.start(t); o2.start(t); o1.stop(stopAt); o2.stop(stopAt);
    return { stop: (at) => { try { g.gain.cancelScheduledValues(at); g.gain.setTargetAtTime(0, at, 0.02); o1.stop(at + 0.1); o2.stop(at + 0.1); } catch (e) { /* already stopped */ } }, end: stopAt };
  }
  function click(ctx, dest, t, down) {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.value = down ? 1760 : 1175;
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(down ? 0.35 : 0.22, t + 0.002); g.gain.setTargetAtTime(0, t + 0.004, 0.012);
    o.connect(g); g.connect(dest); o.start(t); o.stop(t + 0.08);
  }

  // ------------------------------------------------------------- state ---
  const st = {
    xml: '', model: null, all: [], parts: [], osmd: null, book: null, res: null,
    ctx: null, master: null, partNodes: [], loaded: new Map(),
    playing: false, pos: 0, anchorCtx: 0, anchorPos: 0, next: 0, nextBeat: 0, voices: new Set(), timer: 0, raf: 0,
    scale: 1, metro: false, countIn: false, loop: false, loopA: 0, loopB: 0,
    lineHeads: new Map(), stops: null, stopIdx: -1, hlKey: '', hlLayer: null, lastLead: -1,
    msg: (t) => { const m = $('pbMsg'); if (m) m.textContent = t; },
  };
  window.__player = st;

  // ---------------------------------------------------------------- UI ---
  function gmOptions() {
    const fams = ['Piano', 'Chromatic percussion', 'Organ', 'Guitar', 'Bass', 'Strings', 'Ensemble', 'Brass', 'Reed', 'Pipe', 'Synth lead', 'Synth pad', 'Synth effects', 'Ethnic', 'Percussive', 'Sound effects'];
    const GM = PB().GM;
    return fams.map((f, k) => `<optgroup label="${f}">${GM.slice(k * 8, k * 8 + 8).map((n, j) => `<option value="${k * 8 + j}">${k * 8 + j + 1}. ${esc(n)}</option>`).join('')}</optgroup>`).join('') + '<optgroup label="Drums"><option value="-1">Drum kit (channel 10)</option></optgroup>';
  }
  const ICON = {
    play: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4.5 2.8v10.4L13 8z" fill="currentColor"/></svg>',
    pause: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z" fill="currentColor"/></svg>',
    stop: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 3.5h9v9h-9z" fill="currentColor"/></svg>',
  };
  function build() {
    if ($('pb')) return;
    const panel = $('previewPanel');
    if (!panel) return;
    const el = document.createElement('div');
    el.className = 'pb';
    el.id = 'pb';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'Playback');
    el.innerHTML = `
      <div class="pb-row pb-transport">
        <button class="btn small primary pb-play" id="pbPlay" type="button" aria-pressed="false" aria-keyshortcuts="Space" disabled>${ICON.play}<span id="pbPlayLabel">Play</span></button>
        <button class="btn small icon" id="pbStop" type="button" aria-label="Stop and go back to the start" disabled>${ICON.stop}</button>
        <div class="pb-scrub">
          <label class="sr-only" for="pbPos">Position</label>
          <input type="range" id="pbPos" min="0" max="1" step="0.01" value="0" disabled>
          <div class="pb-ticks" id="pbTicks" aria-hidden="true"></div>
        </div>
        <output class="pb-dyn" id="pbDyn" for="pbPos" title="The dynamic marking in force (as played)" hidden></output>
        <output class="pb-time" id="pbTime" for="pbPos">Bar 1 · 0:00 / 0:00</output>
      </div>
      <div class="pb-row pb-opts">
        <div class="pb-tempo">
          <label for="pbTempo">Tempo</label>
          <input type="range" id="pbTempo" min="50" max="200" step="5" value="100">
          <output id="pbTempoOut" for="pbTempo">100%</output>
        </div>
        <button class="toggle" id="pbMetro" type="button" aria-pressed="false"><span class="toggle-track" aria-hidden="true"><span class="toggle-thumb"></span></span><span>Click</span></button>
        <button class="toggle" id="pbCount" type="button" aria-pressed="false"><span class="toggle-track" aria-hidden="true"><span class="toggle-thumb"></span></span><span>Count-in</span></button>
        <div class="pb-loop">
          <button class="toggle" id="pbLoop" type="button" aria-pressed="false" aria-controls="pbLoopA pbLoopB"><span class="toggle-track" aria-hidden="true"><span class="toggle-thumb"></span></span><span>Loop bars</span></button>
          <label class="sr-only" for="pbLoopA">Loop from bar</label><input type="number" id="pbLoopA" min="1" value="1" inputmode="numeric">
          <span aria-hidden="true">to</span>
          <label class="sr-only" for="pbLoopB">Loop to bar</label><input type="number" id="pbLoopB" min="1" value="1" inputmode="numeric">
        </div>
        <button class="btn small" id="pbMidi" type="button" disabled>MIDI file (.mid)</button>
      </div>
      <details class="pb-mix" id="pbMix">
        <summary>Parts mixer <span class="pb-mix-sum" id="pbMixSum"></span></summary>
        <ul class="pb-parts" id="pbParts" aria-label="Parts: instrument, volume, mute and solo"></ul>
      </details>
      <p class="pb-msg" id="pbMsg" role="status" aria-live="polite"></p>`;
    const sheet = panel.querySelector('.sheet');
    panel.insertBefore(el, sheet || null);
    $('pbPlay').addEventListener('click', toggle);
    $('pbStop').addEventListener('click', () => { stop(); seek(st.loop ? loopRange()[0] : 0); });
    const pos = $('pbPos');
    pos.addEventListener('input', () => { st.scrubbing = true; showPos(+pos.value); });
    pos.addEventListener('change', () => { st.scrubbing = false; seek(+pos.value); });
    $('pbTempo').addEventListener('input', () => setScale(+$('pbTempo').value / 100));
    const tg = (id, key, after) => $(id).addEventListener('click', () => { st[key] = !st[key]; $(id).setAttribute('aria-pressed', String(st[key])); if (after) after(); });
    tg('pbMetro', 'metro', () => { st.nextBeat = beatIndexAt(st.pos); });
    tg('pbCount', 'countIn');
    tg('pbLoop', 'loop', () => { if (st.loop) { const [a] = loopRange(); if (st.pos < a - 0.01 || st.pos > loopRange()[1]) seek(a); } });
    ['pbLoopA', 'pbLoopB'].forEach((id) => $(id).addEventListener('change', () => { if (st.loop) { const [a, b] = loopRange(); if (st.pos < a || st.pos > b) seek(a); } }));
    $('pbMidi').addEventListener('click', exportMidi);
    $('pbParts').addEventListener('input', onMix);
    $('pbParts').addEventListener('change', onMix);
    $('pbParts').addEventListener('click', (e) => {
      const b = e.target.closest('button[data-act]');
      if (!b) return;
      const p = st.parts[+b.dataset.i];
      p[b.dataset.act] = !p[b.dataset.act];
      b.setAttribute('aria-pressed', String(p[b.dataset.act]));
      applyMix();
    });
  }
  function renderMixer() {
    const ul = $('pbParts');
    const opts = gmOptions();
    ul.innerHTML = st.parts.map((p, i) => `
      <li class="pb-part">
        <span class="pb-part-name" id="pbPN${i}">${esc(p.name)}</span>
        <label class="sr-only" for="pbInst${i}">Instrument for ${esc(p.name)}</label>
        <select id="pbInst${i}" data-i="${i}" data-k="program" class="pb-inst">${opts}</select>
        <label class="pb-vol"><span class="sr-only">Volume for ${esc(p.name)}</span><input type="range" min="0" max="127" step="1" value="${p.volume}" data-i="${i}" data-k="volume"></label>
        <button class="btn small pb-ms" type="button" data-act="mute" data-i="${i}" aria-pressed="false" aria-label="Mute ${esc(p.name)}">M</button>
        <button class="btn small pb-ms" type="button" data-act="solo" data-i="${i}" aria-pressed="false" aria-label="Solo ${esc(p.name)}">S</button>
      </li>`).join('');
    st.parts.forEach((p, i) => { $(`pbInst${i}`).value = String(p.program); });
    mixSummary();
  }
  function mixSummary() {
    const GM = PB().GM;
    const names = [...new Set(st.parts.map((p) => (p.program < 0 ? 'Drums' : GM[p.program])))];
    $('pbMixSum').textContent = st.parts.length ? `· ${st.parts.length} ${st.parts.length === 1 ? 'part' : 'parts'}: ${names.join(', ')}` : '';
  }
  function onMix(e) {
    const t = e.target, i = +t.dataset.i, k = t.dataset.k;
    if (!k || !st.parts[i]) return;
    st.parts[i][k] = +t.value;
    if (k === 'program') { mixSummary(); if (st.ctx) loadSet(setFor(st.parts[i].program), st.ctx).then((s) => { if (s) st.loaded.set(setFor(st.parts[i].program), s); }); }
    applyMix();
  }
  function applyMix() {
    const solo = st.parts.some((p) => p.solo);
    st.parts.forEach((p, i) => {
      const n = st.partNodes[i];
      if (!n) return;
      const on = !p.mute && (!solo || p.solo);
      n.gain.gain.setTargetAtTime(on ? Math.pow(p.volume / 127, 1.4) * 1.3 : 0, st.ctx.currentTime, 0.02);
    });
  }

  // --------------------------------------------------------- timeline ---
  const scoreToCtx = (p) => st.anchorCtx + (p - st.anchorPos) / st.scale;
  const nowPos = () => (st.playing ? st.anchorPos + (st.ctx.currentTime - st.anchorCtx) * st.scale : st.pos);
  function eventIndexAt(t) { const a = st.all; let lo = 0, hi = a.length; while (lo < hi) { const m = (lo + hi) >> 1; if (a[m].t < t - 1e-6) lo = m + 1; else hi = m; } return lo; }
  function beatIndexAt(t) { const a = st.model ? st.model.beats : []; let lo = 0, hi = a.length; while (lo < hi) { const m = (lo + hi) >> 1; if (a[m].t < t - 1e-6) lo = m + 1; else hi = m; } return lo; }
  function measureAt(t) { const ms = st.model.measures; let lo = 0, hi = ms.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (ms[m].t0 <= t + 1e-6) lo = m; else hi = m - 1; } return lo; }
  // loop: first played bar numbered A, through the first bar numbered B after it
  function loopRange() {
    const ms = st.model.measures;
    const a = String($('pbLoopA').value), b = String($('pbLoopB').value);
    let i = ms.findIndex((m) => m.number === a); if (i < 0) i = Math.max(0, Math.min(ms.length - 1, (+a || 1) - 1));
    let j = ms.findIndex((m, k) => k >= i && m.number === b); if (j < 0) j = Math.max(i, Math.min(ms.length - 1, (+b || 1) - 1));
    return [ms[i].t0, ms[j].t1];
  }
  function ensureCtx() {
    if (st.ctx) return st.ctx;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) throw new Error('this browser has no Web Audio');
    st.ctx = new AC({ latencyHint: 'interactive' });
    buildGraph(st.ctx, st.ctx.destination);
    return st.ctx;
  }
  function buildGraph(ctx, out) {
    if (ctx === st.ctx && st.master) { try { st.master.disconnect(); } catch (e) { /* not connected */ } }
    const comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -14; comp.ratio.value = 4; comp.attack.value = 0.005; comp.release.value = 0.2;
    const master = ctx.createGain(); master.gain.value = 0.9;
    master.connect(comp); comp.connect(out);
    const nodes = st.parts.map((p) => {
      const gain = ctx.createGain();
      let pan = null;
      if (ctx.createStereoPanner) { pan = ctx.createStereoPanner(); pan.pan.value = Math.max(-1, Math.min(1, (p.pan || 0) / 90)); gain.connect(pan); pan.connect(master); } else gain.connect(master);
      return { gain, pan };
    });
    if (ctx === st.ctx) { st.master = master; st.partNodes = nodes; applyMix(); }
    return { master, nodes };
  }
  async function loadNeeded(ctx) {
    const names = [...new Set(st.parts.filter((p) => !p.mute).map((p) => setFor(p.program)).filter(Boolean))];
    const missing = names.filter((n) => !st.loaded.has(n));
    if (!missing.length) return;
    st.msg(`Loading ${missing.join(', ')} sounds…`);
    const timeout = new Promise((r) => setTimeout(r, 15000));
    await Promise.race([Promise.all(missing.map((n) => loadSet(n, ctx).then((s) => { if (s) st.loaded.set(n, s); }))), timeout]);
    st.msg('');
  }

  // --------------------------------------------------------- transport ---
  async function play() {
    if (!st.model || st.playing) return;
    let ctx;
    try { ctx = ensureCtx(); } catch (e) { st.msg(`Playback is not available: ${e.message}.`); return; }
    if (ctx.state !== 'running') { try { await ctx.resume(); } catch (e) { /* resumed by the click */ } }
    setPlayUI(true, true);
    await loadNeeded(ctx);
    if (st.loop) { const [a, b] = loopRange(); if (st.pos < a - 0.01 || st.pos >= b - 0.01) st.pos = a; }
    if (st.pos >= st.model.duration - 0.01) st.pos = 0;
    let lead = 0.06;
    if (st.countIn) {
      const m = st.model.measures[measureAt(st.pos)];
      const bs = st.model.beats.filter((b) => b.m === measureAt(st.pos));
      const beatLen = bs.length > 1 ? (bs[1].t - bs[0].t) : (m.t1 - m.t0) / Math.max(1, bs.length || 4);
      const n = Math.max(2, bs.length || 4);
      for (let k = 0; k < n; k++) click(ctx, st.master, ctx.currentTime + lead + (k * beatLen) / st.scale, k === 0);
      lead += (n * beatLen) / st.scale;
    }
    st.anchorCtx = ctx.currentTime + lead;
    st.anchorPos = st.pos;
    st.next = eventIndexAt(st.pos);
    st.nextBeat = beatIndexAt(st.pos);
    st.playing = true;
    setPlayUI(true);
    clearInterval(st.timer);
    st.timer = setInterval(schedule, TICK_MS);
    schedule();
    cancelAnimationFrame(st.raf);
    st.raf = requestAnimationFrame(frame);
  }
  function pause() {
    if (!st.playing) return;
    st.pos = Math.max(0, Math.min(st.model.duration, nowPos()));
    halt();
    setPlayUI(false);
  }
  function halt() {
    st.playing = false;
    clearInterval(st.timer);
    cancelAnimationFrame(st.raf);
    const at = st.ctx ? st.ctx.currentTime : 0;
    for (const v of st.voices) v.stop(at);
    st.voices.clear();
  }
  function stop() { halt(); setPlayUI(false); }
  function toggle() { if (st.playing) pause(); else play(); }
  function seek(p, autoplay) {
    const was = st.playing || autoplay;
    if (st.playing) halt();
    st.pos = Math.max(0, Math.min(st.model ? st.model.duration : 0, p));
    showPos(st.pos);
    follow(st.pos, true);
    if (was) play(); else setPlayUI(false);
  }
  function setScale(s) {
    const p = nowPos();
    st.scale = s;
    $('pbTempoOut').textContent = `${Math.round(s * 100)}%` + (st.model ? ` (♩ = ${Math.round(st.model.startBpm * s)})` : '');
    if (st.playing) { st.anchorPos = p; st.anchorCtx = st.ctx.currentTime; }
  }
  function schedule() {
    const ctx = st.ctx;
    if (!st.playing || !ctx) return;
    const horizonCtx = ctx.currentTime + LOOKAHEAD;
    let horizon = st.anchorPos + (horizonCtx - st.anchorCtx) * st.scale;
    const [la, lb] = st.loop ? loopRange() : [0, Infinity];
    const endPos = st.loop ? lb : st.model.duration;
    const upto = Math.min(horizon, endPos);
    const a = st.all;
    while (st.next < a.length && a[st.next].t < upto) {
      const n = a[st.next++];
      const p = st.parts[n.part];
      const t = scoreToCtx(n.t);
      if (t < ctx.currentTime - 0.05) continue;
      const d = Math.min(n.d, endPos - n.t) / st.scale;
      const v = voice(ctx, st.partNodes[n.part].gain, p.program, n.midi, n.vel, Math.max(t, ctx.currentTime), Math.max(0.03, d));
      st.voices.add(v);
    }
    if (st.metro) {
      const bs = st.model.beats;
      while (st.nextBeat < bs.length && bs[st.nextBeat].t < upto) {
        const b = bs[st.nextBeat++];
        const t = scoreToCtx(b.t);
        if (t >= ctx.currentTime - 0.01) click(ctx, st.master, Math.max(t, ctx.currentTime), b.down);
      }
    }
    // forget voices that have finished
    if (st.voices.size > 64) for (const v of st.voices) if (v.end < ctx.currentTime) st.voices.delete(v);
    if (horizon >= endPos) {
      if (st.loop) {
        // the loop's end is scheduled: restart at its start, right where the end falls
        st.anchorCtx = scoreToCtx(endPos);
        st.anchorPos = la;
        st.next = eventIndexAt(la);
        st.nextBeat = beatIndexAt(la);
      } else if (ctx.currentTime > scoreToCtx(endPos) + 0.4) {
        stop();
        st.pos = 0;
        showPos(0);
        follow(0, true);
      }
    }
  }
  function setPlayUI(on, loading) {
    const b = $('pbPlay');
    b.setAttribute('aria-pressed', String(on));
    b.innerHTML = (on ? ICON.pause : ICON.play) + `<span id="pbPlayLabel">${on ? (loading ? 'Loading' : 'Pause') : 'Play'}</span>`;
    b.setAttribute('aria-label', on ? 'Pause' : 'Play');
    $('pb').classList.toggle('is-playing', on);
  }
  function showPos(p) {
    if (!st.model) return;
    const r = $('pbPos');
    if (!st.scrubbing) r.value = String(p);
    const m = st.model.measures[measureAt(p)];
    const total = st.model.duration / st.scale;
    const txt = `Bar ${m ? m.number : 1} · ${fmtT(p / st.scale)} / ${fmtT(total)}`;
    $('pbTime').textContent = txt;
    r.setAttribute('aria-valuetext', txt);
    showDyn(p);
  }
  // the marking in force at p: one word when every part (staff) agrees, else per part
  function showDyn(p) {
    const el = $('pbDyn'), m = st.model;
    if (!el || !m) return;
    const cur = new Map();
    for (const d of m.dynamics || []) {
      if (d.t > p + 1e-3) break;
      const per = m.parts[d.part] && m.parts[d.part].perStaffDynamics;
      const key = d.part + (per && d.staff ? ':' + d.staff : '');
      if (!per || !d.staff) for (const k of [...cur.keys()]) if (k === String(d.part) || k.startsWith(d.part + ':')) cur.delete(k);
      cur.set(key, d.v);
    }
    el.hidden = !(m.dynamics || []).length;
    const vals = [...new Set(cur.values())];
    let txt = '';
    if (!cur.size) txt = 'no marking yet';
    else if (vals.length === 1) txt = vals[0];
    else txt = [...cur].slice(0, 4).map(([k, v]) => { const [pi, sf] = k.split(':'); const nm = m.parts[pi].name; return `${sf ? (sf === '1' ? 'RH' : sf === '2' ? 'LH' : 'staff ' + sf) : nm.length > 3 ? nm.slice(0, 1) : nm} ${v}`; }).join(' · ');
    if (el.textContent !== txt) { el.textContent = txt; el.setAttribute('aria-label', `Dynamic: ${txt}`); }
  }
  function frame() {
    if (!st.playing) return;
    const p = nowPos();
    if (p >= st.anchorPos) { st.pos = Math.min(st.model.duration, p); showPos(st.pos); follow(st.pos, false); }
    st.raf = requestAnimationFrame(frame);
  }

  // ------------------------------------------------------ follow-along ---
  // OSMD cursor: its stops (measure index, quarter offset in the measure)
  // listed once, then moved by next() / reset().
  function cursorStops() {
    if (st.stops) return st.stops;
    const o = st.osmd;
    st.stops = [];
    try {
      const c = o && o.cursor;
      if (!c) return st.stops;
      c.reset();
      const it = c.iterator || c.Iterator;
      for (let k = 0; k < 20000 && !it.EndReached; k++) {
        const mi = it.CurrentMeasureIndex;
        const ts = it.currentTimeStamp || it.CurrentSourceTimestamp;
        const meas = it.CurrentMeasure;
        const rel = ts && meas && meas.AbsoluteTimestamp ? (ts.RealValue - meas.AbsoluteTimestamp.RealValue) * 4 : 0;
        st.stops.push([mi, rel]);
        c.next();
      }
      c.reset();
      st.stopIdx = 0;
    } catch (e) { st.stops = []; }
    return st.stops;
  }
  function moveCursor(k) {
    const c = st.osmd && st.osmd.cursor;
    if (!c || k < 0) return;
    try {
      if (k < st.stopIdx || st.stopIdx < 0) { c.reset(); st.stopIdx = 0; }
      while (st.stopIdx < k) { c.next(); st.stopIdx++; }
      c.show();
      const el = c.cursorElement;
      if (el && st.playing) {
        const sh = el.closest('.sheet');
        if (sh) {
          const r = el.getBoundingClientRect(), sr = sh.getBoundingClientRect();
          if (r.left < sr.left || r.right > sr.right) sh.scrollLeft += r.left - sr.left - 40;
        }
      }
    } catch (e) { /* cursor unavailable for this score */ }
  }
  function follow(p, force) {
    if (!st.model) return;
    // the latest onset at or before p
    let i = eventIndexAt(p + 1e-4) - 1;
    while (i > 0 && st.all[i].grace) i--;
    if (i < 0) i = 0;
    if (force || i !== st.lastLead) {
      st.lastLead = i;
      const n = st.all[i];
      if (n) {
        const pm = st.model.measures[n.m];
        const stops = cursorStops();
        const src = pm.src, rel = n.q - pm.q0;
        let best = -1;
        for (let k = 0; k < stops.length; k++) {
          if (stops[k][0] === src && stops[k][1] <= rel + 1e-3) best = k;
          else if (stops[k][0] > src) break;
        }
        if (best < 0) best = stops.findIndex((s) => s[0] === src);
        if (best >= 0) moveCursor(best);
        else if (st.osmd && st.osmd.cursor) try { st.osmd.cursor.hide(); } catch (e) { /* hidden already */ }
      }
    }
    highlight(p, force);
  }
  // scan overlay: rings on the note heads sounding at p
  function headMap() {
    st.lineHeads = new Map();
    const b = st.book;
    if (!b || !b.headNotes) return;
    for (const [pi, notes] of b.headNotes) {
      (notes || []).forEach((n, k) => {
        if (!n || n[7] == null || n[7] < 0) return;
        if (!st.lineHeads.has(n[7])) st.lineHeads.set(n[7], []);
        st.lineHeads.get(n[7]).push([pi, k]);
      });
    }
  }
  function highlight(p, force) {
    const b = st.book;
    if (!b || !b.pages) return;
    const sounding = [];
    const hi = eventIndexAt(p + 1e-4);
    for (let i = hi - 1; i >= 0 && i >= hi - 400; i--) { const n = st.all[i]; if (n.t <= p && n.t + n.d > p) sounding.push(n); }
    const heads = [];
    for (const n of sounding) for (const l of n.lines) for (const h of st.lineHeads.get(l) || []) heads.push(h);
    const playingOn = (st.playing || force) ? heads : [];
    // turn the scan's page when everything sounding is on another one
    if (st.playing && playingOn.length && !playingOn.some((h) => h[0] === b.sel)) {
      const pg = playingOn[0][0];
      if (b.pages[pg] && b.pages[pg].view) { b.follow = false; b.show(pg); }
    }
    const fig = document.querySelector('#pages .pageframe');
    if (!fig) return;
    if (!st.hlLayer || !st.hlLayer.isConnected || st.hlLayer.parentNode !== fig) {
      const page = b.pages[b.sel];
      if (!page || !page.view) return;
      st.hlLayer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      st.hlLayer.setAttribute('class', 'pb-hl');
      st.hlLayer.setAttribute('viewBox', `0 0 ${page.view.width} ${page.view.height}`);
      st.hlLayer.setAttribute('preserveAspectRatio', 'none');
      st.hlLayer.setAttribute('aria-hidden', 'true');
      fig.appendChild(st.hlLayer);
      st.hlKey = '';
    }
    const page = b.pages[b.sel];
    const mine = playingOn.filter((h) => h[0] === b.sel);
    const key = b.sel + ':' + mine.map((h) => h[1]).join(',');
    if (key === st.hlKey) return;
    st.hlKey = key;
    const v = page.view;
    st.hlLayer.innerHTML = mine.map(([, k]) => { const h = v.heads[k]; return h ? `<circle cx="${h[0]}" cy="${h[1]}" r="${(h[2] * 1.9).toFixed(1)}"/>` : ''; }).join('');
    st.hlLayer.dataset.count = String(mine.length);
  }

  // ------------------------------------------------- click to play from ---
  function headAt(e) {
    const b = st.book;
    const fig = e.target.closest && e.target.closest('.pageframe');
    if (!b || !fig) return null;
    const page = b.pages[b.sel];
    const img = fig.querySelector('.pgimg');
    if (!page || !page.view || !img) return null;
    const r = img.getBoundingClientRect();
    const v = page.view;
    const x = ((e.clientX - r.left) / r.width) * v.width, y = ((e.clientY - r.top) / r.height) * v.height;
    const notes = b.headNotes && b.headNotes.get(b.sel);
    if (!notes) return null;
    let best = null, bd = Infinity;
    v.heads.forEach((h, k) => {
      const n = notes[k];
      if (!n || n[7] < 0) return;
      const d = Math.hypot(h[0] - x, h[1] - y) / h[2];
      if (d < 1.8 && d < bd) { bd = d; best = n[7]; }
    });
    return best;
  }
  function onScanClick(e) {
    if (!st.model || e.defaultPrevented) return;
    const pages = $('pages');
    if (pages.classList.contains('drawing') || e.target.closest('.unk') || ($('idPop') && !$('idPop').hidden)) return;
    const line = headAt(e);
    if (line == null) return;
    const n = st.all.find((x) => x.lines.includes(line));
    if (!n) return;
    st.msg(`Playing from bar ${st.model.measures[n.m].number}.`);
    seek(n.t, true);
  }
  // a click on the preview: the measure under the pointer
  function onSheetClick(e) {
    if (!st.model || !st.osmd) return;
    const svg = e.target.closest && e.target.closest('#osmd svg');
    if (!svg) return;
    try {
      const gs = st.osmd.GraphicSheet;
      const zoom = st.osmd.zoom || 1;
      const r = svg.getBoundingClientRect();
      const vb = svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width ? svg.viewBox.baseVal : null;
      const sx = vb ? vb.width / r.width : 1, sy = vb ? vb.height / r.height : 1;
      const x = ((e.clientX - r.left) * sx) / (10 * zoom), y = ((e.clientY - r.top) * sy) / (10 * zoom);
      let hit = -1;
      gs.MeasureList.forEach((staves, mi) => {
        for (const gm of staves || []) {
          if (!gm || !gm.PositionAndShape) continue;
          const ps = gm.PositionAndShape, ap = ps.AbsolutePosition;
          const x0 = ap.x + ps.BorderLeft, x1 = ap.x + ps.BorderRight, y0 = ap.y + ps.BorderTop - 2, y1 = ap.y + ps.BorderBottom + 2;
          if (x >= x0 && x <= x1 && y >= y0 && y <= y1) { hit = mi; return; }
        }
      });
      if (hit < 0) return;
      const idx = st.model.measures.findIndex((m) => m.src === hit);
      if (idx < 0) return;
      st.msg(`Playing from bar ${st.model.measures[idx].number}.`);
      seek(st.model.measures[idx].t0, true);
    } catch (err) { /* layout not available */ }
  }

  // ------------------------------------------------------------ export ---
  function exportMidi() {
    if (!st.model) return;
    const bytes = PB().writeSMF(st.model, { parts: st.parts.map((p) => ({ program: p.program, volume: p.volume, mute: p.mute || (st.parts.some((q) => q.solo) && !p.solo) })) });
    const blob = new Blob([bytes], { type: 'audio/midi' });
    const name = `${(st.model.title || 'score').replace(/[^\w\- ]+/g, '').trim().replace(/\s+/g, '-').toLowerCase() || 'score'}.mid`;
    saveBlob(blob, name);
  }
  // <guarded-download> tools/build.js allows a download link only inside this
  // block: a real <a download> where the page is not framed (GitHub Pages, a
  // local copy), and a new tab inside the claude.ai artifact frame, whose
  // rules forbid download links.
  function framed() { try { return window.self !== window.top; } catch (e) { return true; } }
  function saveBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    setTimeout(() => URL.revokeObjectURL(url), 120000);
    if (!framed()) {
      const a = document.createElement('a');
      a.href = url;
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      st.msg(`Saved ${name} (${Math.max(1, Math.round(blob.size / 1024))} KB).`);
      return;
    }
    let w = null;
    try { w = window.open(url, '_blank'); if (w) w.opener = null; } catch (e) { w = null; }
    st.msg(w ? `${name} opened in a new tab: save it from there.` : `${name} could not open here (new tabs are blocked).`);
  }
  // </guarded-download>

  // bar numbers under the scrubber, as many as fit without touching
  function ticks() {
    const m = st.model, el = $('pbTicks');
    if (!m || !el) return;
    const w = el.clientWidth || 300;
    let last = -Infinity, html = '';
    for (const ms of m.measures) {
      const x = (ms.t0 / m.duration) * w, need = 10 + 7 * String(ms.number).length;
      if (x - last < need) continue;
      last = x;
      html += `<span style="left:${((ms.t0 / m.duration) * 100).toFixed(2)}%">${esc(ms.number)}</span>`;
    }
    el.innerHTML = html;
  }
  let tickTimer = 0;
  window.addEventListener('resize', () => { clearTimeout(tickTimer); tickTimer = setTimeout(ticks, 120); });

  // ----------------------------------------------------------- attach ---
  function attach(o) {
    build();
    if (!$('pb')) return;
    const same = o.xml && o.xml === st.xml;
    st.osmd = o.osmd || null; st.book = o.book || null; st.res = o.res || null;
    st.stops = null; st.stopIdx = -1; st.lastLead = -1; st.hlKey = '';
    headMap();
    if (same && st.model) { follow(st.pos, true); return; }
    if (st.playing) stop();
    st.xml = o.xml || '';
    st.model = null; st.all = []; st.parts = [];
    try {
      if (st.xml) st.model = PB().events(st.xml);
    } catch (e) { st.msg(`This score cannot be played: ${e.message}`); }
    const ok = !!(st.model && st.model.parts.some((p) => p.notes.length));
    ['pbPlay', 'pbStop', 'pbPos', 'pbMidi'].forEach((id) => { $(id).disabled = !ok; });
    if (!ok) { $('pbParts').innerHTML = ''; $('pbTime').textContent = 'Nothing to play'; return; }
    const m = st.model;
    st.parts = m.parts.map((p) => ({ name: p.name, program: p.program, volume: 100, pan: p.pan, mute: false, solo: false }));
    st.all = m.parts.flatMap((p) => p.notes).sort((a, b) => a.t - b.t || a.midi - b.midi);
    st.pos = 0;
    const r = $('pbPos');
    r.max = String(m.duration); r.value = '0'; r.step = String(Math.max(0.01, m.duration / 2000));
    ticks();
    const nums = m.measures.map((x) => x.number);
    $('pbLoopA').value = nums[0] || '1'; $('pbLoopB').value = nums[Math.min(nums.length - 1, 3)] || '1';
    $('pbLoopA').max = $('pbLoopB').max = String(Math.max(...nums.map((x) => +x || 0), m.measures.length));
    renderMixer();
    if (st.ctx) buildGraph(st.ctx, st.ctx.destination);
    setScale(st.scale);
    showPos(0);
    setPlayUI(false);
    const tempoSrc = m.tempos.length ? `♩ = ${Math.round(m.startBpm)}` : '';
    st.msg(`${m.parts.reduce((a, p) => a + p.notes.length, 0).toLocaleString('en')} notes, ${fmtT(m.duration)} at ${tempoSrc}` + (m.measures.length > new Set(m.order).size ? ', repeats played' : '') + '.');
  }

  // Space plays / pauses unless focus is in a field or on a control that uses it
  document.addEventListener('keydown', (e) => {
    if (e.key !== ' ' && e.code !== 'Space') return;
    if (!st.model || e.ctrlKey || e.metaKey || e.altKey) return;
    const t = e.target;
    if (t && (/^(INPUT|TEXTAREA|SELECT|BUTTON|SUMMARY|A)$/.test(t.tagName) || t.isContentEditable) && !(t.tagName === 'INPUT' && t.type === 'range')) return;
    if (($('idPop') && !$('idPop').hidden) || ($('pages') && $('pages').classList.contains('drawing'))) return;
    e.preventDefault();
    toggle();
  });
  document.addEventListener('click', (e) => {
    if (e.target.closest && e.target.closest('#pages')) onScanClick(e);
    else if (e.target.closest && e.target.closest('#osmd')) onSheetClick(e);
  });

  // Offline render for the tests: the first `secs` seconds through an
  // OfflineAudioContext with the same voices; resolves to { rms, peak }.
  async function renderOffline(secs) {
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    const sr = 22050, ctx = new OAC(2, Math.ceil(sr * secs), sr);
    const names = [...new Set(st.parts.map((p) => setFor(p.program)).filter(Boolean))];
    await Promise.all(names.map((n) => loadSet(n, ctx).then((s) => { if (s) st.loaded.set(n, s); })));
    const g = buildGraph(ctx, ctx.destination);
    for (const n of st.all) { if (n.t >= secs) break; voice(ctx, g.nodes[n.part].gain, st.parts[n.part].program, n.midi, n.vel, n.t + 0.01, n.d); }
    const buf = await ctx.startRendering();
    const d = buf.getChannelData(0);
    let s = 0, pk = 0;
    for (let i = 0; i < d.length; i++) { s += d[i] * d[i]; pk = Math.max(pk, Math.abs(d[i])); }
    return { rms: Math.sqrt(s / d.length), peak: pk, sets: names.filter((n) => st.loaded.has(n)) };
  }

  window.ScorePlayer = { attach, play, pause, stop, seek, toggle, renderOffline, state: st };
})();
