#!/usr/bin/env python3
"""Validate MusicXML files against the MusicXML 4.0 XSD (needs lxml and the XSD dir).
usage: validate.py XSD_DIR file.musicxml [...]"""
import sys
from lxml import etree
xsd_dir = sys.argv[1]
schema = etree.XMLSchema(etree.parse(xsd_dir + '/musicxml.xsd'))
ok = True
for f in sys.argv[2:]:
    doc = etree.parse(f)
    if schema.validate(doc):
        print('VALID  ', f)
    else:
        ok = False
        print('INVALID', f)
        for e in list(schema.error_log)[:10]:
            print('   line %d: %s' % (e.line, e.message))
sys.exit(0 if ok else 1)
