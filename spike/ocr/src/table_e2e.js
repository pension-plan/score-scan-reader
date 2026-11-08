'use strict';
// Markdown table for end-to-end summaries. Usage: node src/table_e2e.js results/summary_e2e.json
const S = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const p = v => (v == null ? '-' : (100 * v).toFixed(1));
const V = ['clean300', 'scan300', 'bilevel300', 'copy200', 'phone150'];
let s = '| config | line recall% | line precision% | CER% raw / fused | SylER% fused | WER% fused | hyphen P/R% (OCR only) | hyphen P/R% (fused) | OCR ms/page | ' + V.map(v => v + ' CER%').join(' | ') + ' |\n';
s += '|' + '---|'.repeat(10 + V.length - 1) + '\n';
for (const [k, r] of Object.entries(S).sort((a, b) => a[1].union.CER - b[1].union.CER)) {
  s += `| ${k} | ${p(r.det.recall)} | ${p(r.det.precision)} | ${p(r.raw.CER)} / ${p(r.union.CER)} | ${p(r.union.SylER)} | ${p(r.union.WER)} | ${p(r.raw.hyP)}/${p(r.raw.hyR)} | ${p(r.union.hyP)}/${p(r.union.hyR)} | ${r.ocrMsPerPage.toFixed(0)} | ` + V.map(v => r.byVariant[v] ? p(r.byVariant[v].union.CER) : '-').join(' | ') + ' |\n';
}
const any = Object.values(S)[0];
s += `\nDetection (strips.js, shared by all configs): ${any.pages} pages, ${any.det.gt} GT lyric lines, recall ${p(any.det.recall)}%, precision ${p(any.det.precision)}% (${any.det.fp} false lines, ${any.det.dup} duplicates), font-size estimate rel. error median ${p(any.sizeRelErrMedian)}% / p90 ${p(any.sizeRelErrP90)}%, ${any.detMsPerPage.toFixed(0)} ms/page.\n`;
s += `Geometric hyphen detector: P ${p(any.geoHyphen.P)}% R ${p(any.geoHyphen.R)}% (tp ${any.geoHyphen.tp}, fp ${any.geoHyphen.fp}, fn ${any.geoHyphen.fn}); extender detector: P ${p(any.geoExtender.P)}% R ${p(any.geoExtender.R)}% (tp ${any.geoExtender.tp}, fp ${any.geoExtender.fp}, fn ${any.geoExtender.fn}).\n`;
s += 'Per-variant line recall: ' + V.map(v => `${v} ${p(any.byVariant[v].recall)}% (fp ${any.byVariant[v].fp})`).join(', ') + '\n';
process.stdout.write(s);
