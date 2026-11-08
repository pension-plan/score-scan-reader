#!/usr/bin/env python3
# Word lists for lyric OCR post-correction (src/lexicon.js): the N most frequent words
# (letters only, an inner apostrophe allowed) of each language in wordfreq 3.1.1's data,
# written as dist/assets/lex-<lang>.txt.gz. Line format: "<-centibels> word word ...",
# most frequent first; a header line starting with '#' names the source and licence.
#
#   pip download wordfreq==3.1.1 --no-deps -d /tmp/wf && unzip -q /tmp/wf/wordfreq-*.whl -d /tmp/wf
#   pip install --target /tmp/wf/lib msgpack
#   PYTHONPATH=/tmp/wf/lib python3 mvp/tools/lexicon.py /tmp/wf/wordfreq/data mvp/dist/assets [N]
#
# The data is CC BY-SA 4.0 (dist/assets/NOTICE.lexicon.txt).
import gzip, os, re, sys
import msgpack

data, out_dir = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
OK = re.compile(r"^[^\W\d_]+(?:['’][^\W\d_]+)?$")
for lang in ['en', 'de', 'fr', 'es', 'it', 'cs']:
    f = os.path.join(data, f'large_{lang}.msgpack.gz')
    if not os.path.exists(f): f = os.path.join(data, f'small_{lang}.msgpack.gz')
    buckets = msgpack.load(gzip.open(f), raw=False)[1:]   # bucket i: words of frequency 10^(-i/100)
    lines, n = [], 0
    for i, b in enumerate(buckets):
        ws = [w for w in b if OK.match(w) and len(w) <= 24]
        if not ws: continue
        ws = ws[:N - n]
        lines.append(f'{i} ' + ' '.join(ws)); n += len(ws)
        if n >= N: break
    text = (f'#lexicon {lang}: the {n} most frequent words of wordfreq 3.1.1 ({os.path.basename(f)}), CC BY-SA 4.0; '
            'line = -centibels then words\n' + '\n'.join(lines) + '\n').encode()
    dst = os.path.join(out_dir, f'lex-{lang}.txt.gz')
    with open(dst, 'wb') as fh:
        fh.write(gzip.compress(text, 9, mtime=0))
    print(lang, n, 'words', os.path.getsize(dst), 'bytes')
