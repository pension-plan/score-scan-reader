'use strict';
// Render summary json as markdown tables. Usage: node src/table.js results/summary.json [cfgFilterRegex]
const fs = require('fs');
const S = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const re = new RegExp(process.argv[3] || '.');
const pct = v => (100 * v).toFixed(1);
const V = ['clean300', 'scan300', 'bilevel300', 'copy200', 'phone150'];
let s = '| config | n | CER% | SylER% | WER% | line exact% | hyphen P/R% | ms/line | ' + V.map(v => v + ' CER%').join(' | ') + ' | eng/deu/lat CER% |\n';
s += '|' + '---|'.repeat(9 + V.length) + '\n';
for (const [k, r] of Object.entries(S).filter(([k]) => re.test(k)).sort((a, b) => a[1].all.CER - b[1].all.CER)) {
  const a = r.all;
  s += `| ${k} | ${r.n} | ${pct(a.CER)} | ${pct(a.SylER)} | ${pct(a.WER)} | ${pct(a.lineExact)} | ${pct(a.hyP)}/${pct(a.hyR)} | ${a.msPerLine.toFixed(0)} | ` +
    V.map(v => r.byVariant[v] ? pct(r.byVariant[v].CER) : '-').join(' | ') + ` | ${['eng', 'deu', 'lat'].map(l => r.byLang[l] ? pct(r.byLang[l].CER) : '-').join('/')} |\n`;
}
process.stdout.write(s);
