'use strict';
// Orchestrator: gray pages -> score (parts, MusicXML), overlay data, warnings.
const { front } = require('./front');
const { assemblePage } = require('./assemble');
const { readLyrics } = require('./lyrics');
const { buildScore } = require('./score');

async function convert(grayPages, opts = {}) {
  const progress = opts.onProgress || (() => {});
  const pages = [];
  const lyricsBySystem = {};
  const warnings = [];
  for (let i = 0; i < grayPages.length; i++) {
    progress(`Page ${i + 1}/${grayPages.length}: finding staves and notes`);
    await tick();
    let fr;
    try { fr = front(grayPages[i]); } catch (e) { warnings.push(`Page ${i + 1}: image analysis failed (${e.message}).`); continue; }
    fr.warnings.forEach(w => warnings.push(`Page ${i + 1}: ${w}`));
    if (!fr.staves.length) continue;
    const asm = assemblePage(fr, i);
    pages.push({ fr, asm, index: i });
    if (opts.ocr) {
      progress(`Page ${i + 1}: reading lyrics`);
      try {
        const lyr = await readLyrics(fr, opts.ocr, (d, n) => progress(`Page ${i + 1}: reading lyrics (${d}/${n} lines)`));
        for (const k in lyr) lyricsBySystem[i + ':' + k] = lyr[k];
      } catch (e) { warnings.push(`Lyrics OCR failed: ${e.message}`); }
    }
  }
  progress('Building parts');
  let score;
  try { score = buildScore(pages, lyricsBySystem, { ocr: !!opts.ocr, copyLyrics: !!opts.copyLyrics }); }
  catch (e) { score = { parts: [], warnings: ['Assembly failed: ' + e.message], xml: '' }; }
  // show only the text lines that were attached to notes (stanza text printed
  // below the music, titles and dynamics are not underlay)
  if (score.layout && Object.values(lyricsBySystem).some(l => l.some(v => v.used))) {
    for (const k in lyricsBySystem) lyricsBySystem[k] = lyricsBySystem[k].filter(v => v.used);
  }
  if (!pages.length) warnings.push('No staves were detected. Try a cleaner or higher-resolution scan.');
  return { pages, score, lyricsBySystem, warnings: warnings.concat(score.warnings || []) };
}

const tick = () => new Promise(r => setTimeout(r, 0));

module.exports = { convert };
