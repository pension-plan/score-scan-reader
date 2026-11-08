#!/usr/bin/env python3
"""Write docs/TIMELINE.md: the build log, accuracy history and every agent run, in AEDT.

Reads the status page's embedded state and agent ledger (docs/status/omr-build.html).
Run by tools/push.sh before each commit.  Usage: python3 -I tools/timeline.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'docs/status/omr-build.html')
OUT = os.path.join(ROOT, 'docs/TIMELINE.md')


def block(html, ident):
    m = re.search(r'<script id="%s" type="application/json">(.*?)</script>' % ident, html, re.S)
    return json.loads(m.group(1).replace('<\\/', '</')) if m else {}


def cell(s):
    return str(s if s is not None else '').replace('|', '\\|').replace('\n', ' ')


html = open(PAGE, encoding='utf-8').read()
st, ledger = block(html, 'state'), block(html, 'ledger')
L = []
L.append('# Build timeline')
L.append('')
L.append('All times are Sydney daylight time (AEDT, UTC+11) on 2026-11-08. '
         'Generated from the status page on every push; last updated %s.' % st.get('updated', '?'))
L.append('')
L.append('## Events')
L.append('')
L.append('| Time | Event |')
L.append('|---|---|')
for t, msg in st.get('log', []):
    L.append('| %s | %s |' % (cell(t), cell(msg)))
L.append('')
L.append('## Accuracy by round')
L.append('')
L.append('Scores are against the benchmark of synthetic and real scans with exact answers (1.00 is perfect).')
L.append('')
L.append('| Run | Overall | Pitch | Duration | Lyrics | Parts | Schema-valid | Real scans |')
L.append('|---|---|---|---|---|---|---|---|')
f = lambda v: '%.3f' % v if isinstance(v, (int, float)) else '–'
for m in st.get('metrics') or []:
    L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (cell(m.get('label')), f(m.get('aggregate')), f(m.get('pitch')), f(m.get('duration')),
             f(m.get('lyrics')), f(m.get('parts')), f(m.get('xsd_valid_ratio')), f(m.get('real_scan_aggregate'))))
L.append('')
L.append('## Known limits')
L.append('')
L.append('| ID | Limit | Owner | Status | Evidence |')
L.append('|---|---|---|---|---|')
for l in st.get('limits', []):
    L.append('| %s |' % ' | '.join(cell(x) for x in l))
L.append('')
L.append('## Runs')
L.append('')
L.append('| Run | What | Status | Agents returned | Note |')
L.append('|---|---|---|---|---|')
for r in ledger.get('runs', []):
    L.append('| %s | %s | %s | %s of %s | %s |' % (cell(r['run']), cell(r['desc']), cell(r['status']), r['done'], r['agents'], cell(r.get('note'))))
L.append('')
L.append('## Agents')
L.append('')
L.append('Every agent started for this build, including stopped runs. Outcomes are on the status page.')
L.append('')
L.append('| Run | Phase | Agent | Status | Started | Finished | Minutes | Tool calls |')
L.append('|---|---|---|---|---|---|---|---|')
for a in ledger.get('agents', []):
    L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (cell(a['run']), cell(a['phase']), cell(a['label']), cell(a['status']),
             cell(a.get('start')), cell(a.get('end') or ''), cell(a.get('mins')), cell(a.get('tools'))))
L.append('')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('wrote', OUT, len(st.get('log', [])), 'events', len(ledger.get('agents', [])), 'agents')
