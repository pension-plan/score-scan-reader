#!/usr/bin/env python3
"""Build corpus/manifest-real.json and every corpus/real/<id>/ATTRIBUTION.txt from the table below.

usage: python3 corpus/real/tools/build_manifest.py
Re-runs mkxml.py --stats for items with a truth.src, and reads pixel sizes from source-page.jpg.
Entry shape matches corpus/manifest-synthetic.json (origin: 'real-scan'), plus provenance fields.
"""
import json, os, subprocess, sys, hashlib
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REAL = os.path.dirname(HERE)
CORPUS = os.path.dirname(REAL)

IA_NOTE = ("Scan by the Internet Archive / contributing library. A faithful photographic reproduction of a "
           "public-domain 2-D work; no new copyright arises in the US (Bridgeman v. Corel, 1999). "
           "The Internet Archive marks such items 'NOT_IN_COPYRIGHT' / Public Domain Mark where stated below.")

ITEMS = [
    dict(
        id='golden1923-america',
        title='America ("My Country, \'Tis of Thee") - closed-score SATB, 4 verses',
        work='America (My Country, \'Tis of Thee); words Samuel Francis Smith (1831); music attributed to Henry Carey (tune "God Save the King")',
        book='The Golden Book of Favorite Songs, revised ed., ed. John W. Beattie et al., Chicago: Hall & McCreary, 1923',
        page_label='p. 3', ia='goldenbookoffavo00beat_0', leaf=2, ppi=500,
        scan_by='Music Library, University of North Carolina at Chapel Hill (Don Yoder Collection of American Hymnody); scanned by the Internet Archive (scribe1.chapelhill), 2014-06-30, Canon EOS 5D Mark II',
        ia_rights='possible-copyright-status not stated; item in collections uncmus/americana',
        license='Public domain in the USA (published 1923; US copyright term expired 1 Jan 2019). Words (Smith, d. 1895) and tune are public domain worldwide.',
        rights_notes='The book\'s editorial content (compilers incl. J. W. Beattie, d. 1962) is PD in the US by publication date; in life+70 countries the arrangement on this page may not be PD until 2033 - treat as US-PD only. The hymn-style harmonization of "America" is the standard traditional one.',
        degradations=['library_stamp_over_music', 'paper_yellowing', 'show_through', 'heavy_ink_spread', 'slight_skew', 'jpeg'],
        features=['lyrics', 'multi_voice_staff', 'satb_closed', 'multi_verse', 'hymn', 'melisma', 'dynamics', 'stamp_noise', 'text_blocks_on_page'],
        expected_parts=['Soprano', 'Alto', 'Tenor', 'Bass'], shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
        lyrics_parts=[{'part': 'Soprano', 'verses': 4}],
        notes='Library stamp "PROPERTY OF CENTRAL STATE NORMAL SCHOOL, LOCK HAVEN, PENN." in blue ink crosses system 1 and the prose box. Page also has a prose history box, the text-only hymn "God Bless Our Native Land" (2 stanzas) and "The American\'s Creed" box: none of that is music and none of it is in the truth. Truth = the 14-measure hymn only (dynamics/tempo/hairpin omitted).',
    ),
    dict(
        id='methodist1905-st-anselm',
        title='St. Anselm (hymn 72) - closed-score SATB, 1 interlined verse + 2 block-text stanzas',
        work='Hymn tune ST. ANSELM (7.6.7.6.D) by Joseph Barnby (1838-1896); words "The dawn of God\'s dear Sabbath" by Ada Cross (Ada Cambridge, 1844-1926)',
        book='The Methodist Hymnal: official hymnal of the Methodist Episcopal Church and the Methodist Episcopal Church, South. New York: Eaton & Mains; Cincinnati: Jennings & Graham, 1905',
        page_label='p. 50 (hymn 72)', ia='methodisthymnalo00meth', leaf=63, ppi=400,
        scan_by='Princeton Theological Seminary Library copy; scanned by the Internet Archive (scribe1.nyc), 2008-12-22, Canon 5D',
        ia_rights='possible-copyright-status: NOT_IN_COPYRIGHT',
        license='Public domain (published 1905; composer d. 1896, author d. 1926).',
        rights_notes='',
        degradations=['paper_yellowing', 'show_through', 'page_curvature', 'slight_skew', 'jpeg'],
        features=['lyrics', 'multi_voice_staff', 'satb_closed', 'hymn', 'pickup', 'accidentals', 'unison_shared_noteheads', 'mid_measure_barlines', 'amen', 'text_stanzas_below', 'cue_text'],
        expected_parts=['Soprano', 'Alto', 'Tenor', 'Bass'], shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
        lyrics_parts=[{'part': 'Soprano', 'verses': 1}],
        notes='Hymnal style: heavy single barlines mark the end of each text line in the MIDDLE of a 4/4 measure, so the truth follows the printed barlines (25 measures incl. pickup, several partial). Stanzas 2-3 are printed as block text below the music (not in truth). Small cue words "As some" over the tenor at the end of system 1 are not lyrics. Tenor B3 tied over the system break (dotted tie). A-men on two final half notes.',
    ),
    dict(
        id='klauser1867-schumann-melodie',
        title='Schumann: Melodie, Op. 68 No. 1 - piano grand staff (must not split)',
        work='Robert Schumann (1810-1856), Album fuer die Jugend Op. 68 No. 1 "Melodie" (comp. 1848)',
        book='Erstes Album fuer die Jugend Op. 68, 43 kleine Clavierstuecke, progressiv geordnet und mit Fingersatz versehen von K. Klauser. Leipzig: J. Schuberth & Co., [1867] (plate 4359)',
        page_label='p. 3', ia='b26976821', leaf=2, ppi=300,
        scan_by='Gaylord Music Library, Washington University in St. Louis (uploaded to the Internet Archive)',
        ia_rights='licenseurl: http://creativecommons.org/publicdomain/mark/1.0/ (Public Domain Mark 1.0)',
        license='Public domain (composer d. 1856; editor Karl Klauser d. 1905; published 1867). Scan marked Public Domain Mark 1.0.',
        rights_notes='',
        degradations=['grayscale', 'heavy_ink', 'paper_tone', 'book_edge_border', 'jpeg'],
        features=['piano', 'must_not_split', 'grand_staff_multi_voice', 'repeats', 'clef_change', 'chords', 'fingerings', 'slurs', 'dynamics', 'title_page_header'],
        expected_parts=['Piano'], shared_staves=[],
        lyrics_parts=[],
        notes='Negative test for part splitting: one Piano part with 2 staves; the upper staff has a second voice only in m8 and m16 (encoded as voice 2, preceded by <forward>). Both staves in treble clef (lower staff of system 1 shows bass clef then an immediate treble clef). Fingerings, slurs, dynamics, accent marks omitted from truth. Pitches cross-checked against the Mutopia Project Peters-based edition: identical.',
    ),
    dict(
        id='haupt1867-aus-meines-herzens-grunde',
        title='Aus meines Herzens Grunde - German chorale, closed-score SATB, repeat with 2 text lines',
        work='Chorale "Aus meines Herzens Grunde" (melody Hamburg 1598); 4-part setting from August Haupt\'s Choralbuch (Haupt 1810-1891)',
        book='August Haupt, Choralbuch zum haeuslichen Gebrauch: enthaltend 109 der schoensten Choralmelodieen mit beigefuegtem Text, einfach 4-stimmig. Berlin: Schlesinger, 1867',
        page_label='chorale no. 11 (leaf 22)', ia='bub_gb_T75IAAAAcAAJ', leaf=22, ppi=300,
        scan_by='Bavarian State Library (Bayerische Staatsbibliothek) copy, digitised by Google Books (id T75IAAAAcAAJ); mirrored to the Internet Archive (collection europeanlibraries)',
        ia_rights='licenseurl: http://creativecommons.org/publicdomain/mark/1.0/ (Public Domain Mark 1.0)',
        license='Public domain (published 1867; arranger d. 1891). Scan marked Public Domain Mark 1.0.',
        rights_notes='Google Books scans come with Google\'s non-binding "usage guidelines" (asks for non-commercial use and keeping attribution); they are not a copyright licence. Flagged for awareness only.',
        degradations=['google_bitonal_processing', 'thin_broken_staff_lines', 'low_contrast_hollow_heads', 'jpeg'],
        features=['lyrics', 'multi_voice_staff', 'satb_closed', 'chorale', 'pickup', 'repeats', 'lyrics_under_repeat', 'half_note_beat', 'fermata', 'german_text', 'text_stanzas_below'],
        expected_parts=['Soprano', 'Alto', 'Tenor', 'Bass'], shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
        lyrics_parts=[{'part': 'Soprano', 'verses': 2}],
        notes='No truth yet (hand transcription attempted; low-quality Google bitonal scan makes hollow half notes hard to read reliably). Repeated first section carries two text lines (1st and 2nd time) of stanza 1; stanzas 2-4 are block text below. Mostly half notes in common time, fermatas at line ends.',
    ),
    dict(
        id='efss1906-cold-blows-the-wind',
        title='Cold Blows the Wind (No. 6) - folk song, voice + piano, 1 interlined verse',
        work='English folk song "Cold blows the wind", collected and arranged by S. Baring-Gould (1834-1924) and Cecil J. Sharp (1859-1924)',
        book='English Folk-Songs for Schools, collected and arranged by S. Baring Gould and Cecil J. Sharp. London: J. Curwen & Sons, [1906]',
        page_label='p. 12 (No. 6)', ia='englishfolksongs00goul', leaf=23, ppi=300,
        scan_by='Internet Archive (scanning centre nyc, 2007-07-13, Canon 5D), copy contributed by the Internet Archive',
        ia_rights='possible-copyright-status: NOT_IN_COPYRIGHT (copyright-region US)',
        license='Public domain (published c.1906; arrangers d. 1924 - PD in the US and in life+70 countries since 1995).',
        rights_notes='',
        degradations=['paper_tone', 'slight_skew', 'jpeg'],
        features=['lyrics', 'voice_piano', 'piano', 'must_not_split', 'grand_staff_multi_voice', 'compound_meter', 'pickup', 'fermata', 'repeats', 'slurs', 'old_style_bass_clef'],
        expected_parts=['Voice', 'Piano'], shared_staves=[],
        lyrics_parts=[{'part': 'Voice', 'verses': 1}],
        notes='No truth. 6/8, D major. Three-staff systems (voice + piano); piano lower staff uses the Curwen-style reversed-C bass clef glyph. Voice staff and piano must not be split; piano right hand carries 2-3 voices.',
    ),
    dict(
        id='methodist1905-tappan-dennis',
        title='Tappan (hymn 99) + Dennis (hymn 100) - two closed-score SATB hymns on one page',
        work='TAPPAN C.M. by George Kingsley (1811-1884), words Henry Kirke White (1785-1806); DENNIS S.M. arr. from Hans G. Naegeli (1773-1836) [by Lowell Mason], words Philip Doddridge (1702-1751)',
        book='The Methodist Hymnal, New York: Eaton & Mains, 1905',
        page_label='p. 60 (hymns 99-100)', ia='methodisthymnalo00meth', leaf=82, ppi=400,
        scan_by='Princeton Theological Seminary Library copy; scanned by the Internet Archive (scribe1.nyc), 2008-12-22, Canon 5D',
        ia_rights='possible-copyright-status: NOT_IN_COPYRIGHT',
        license='Public domain (published 1905; all creators d. before 1885).',
        rights_notes='',
        degradations=['paper_yellowing', 'show_through', 'page_curvature', 'jpeg'],
        features=['lyrics', 'multi_voice_staff', 'satb_closed', 'hymn', 'two_pieces_one_page', 'key_change_between_pieces', 'time_change_between_pieces', 'amen', 'text_stanzas_below', 'slurs'],
        expected_parts=['Soprano', 'Alto', 'Tenor', 'Bass'], shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
        lyrics_parts=[{'part': 'Soprano', 'verses': 1}],
        notes='No truth. Tappan: G major, 3/2. Dennis: F major, 3/4. Each has stanza 1 interlined and the rest as block text. Tests segmentation of two independent pieces on one page.',
    ),
    dict(
        id='golden1923-auld-lang-syne',
        title='Auld Lang Syne + Comin\' Thro\' the Rye - two SATB songs on one page, multi-verse, refrain',
        work='Auld Lang Syne (words Robert Burns, Scottish air); Comin\' Thro\' the Rye (words Robert Burns, Scottish air)',
        book='The Golden Book of Favorite Songs, revised ed., Chicago: Hall & McCreary, 1923',
        page_label='p. 37', ia='goldenbookoffavo00beat_0', leaf=36, ppi=500,
        scan_by='Music Library, University of North Carolina at Chapel Hill; scanned by the Internet Archive, 2014',
        ia_rights='possible-copyright-status not stated',
        license='Public domain in the USA (published 1923). Words (Burns, d. 1796) and airs are public domain worldwide.',
        rights_notes='As for golden1923-america: arrangements are US-PD by publication date; treat as US-PD only.',
        degradations=['paper_yellowing', 'show_through', 'stains', 'heavy_ink_spread', 'jpeg'],
        features=['lyrics', 'multi_voice_staff', 'satb_closed', 'multi_verse', 'refrain', 'two_pieces_one_page', 'key_change_between_pieces', 'pickup', 'fermata', 'slurs', 'melisma'],
        expected_parts=['Soprano', 'Alto', 'Tenor', 'Bass'], shared_staves=[['Soprano', 'Alto'], ['Tenor', 'Bass']],
        lyrics_parts=[{'part': 'Soprano', 'verses': 3}],
        notes='No truth. Auld Lang Syne: F major 4/4, 2 verses + refrain (single text line). Comin\' Thro\' the Rye: Ab major, 3 verses + refrain with brace. Verse count given is the maximum on the page.',
    ),
    dict(
        id='sharp1911-rambling-sailor',
        title='The Rambling Sailor (LXXX) - folk song, voice + piano, 1 interlined verse',
        work='English folk song "The Rambling Sailor", collected and arranged by Cecil J. Sharp (1859-1924)',
        book='Folk Songs from Somerset, gathered and edited with pianoforte accompaniment by Cecil J. Sharp, 4th series, 2nd ed. London: Simpkin; Taunton: Barnicott & Pearce, 1911',
        page_label='p. 2 (song LXXX)', ia='folksongsfromsom00shar', leaf=17, ppi=350,
        scan_by='University of Toronto, Faculty of Music Library copy; scanned by the Internet Archive (scribe3.toronto), 2022-05-09',
        ia_rights='possible-copyright-status not stated (University of Toronto collection)',
        license='Public domain (published 1911; editor d. 1924 - PD in the US and in life+70 countries since 1995).',
        rights_notes='',
        degradations=['paper_tone', 'small_staff_size', 'jpeg'],
        features=['lyrics', 'voice_piano', 'piano', 'must_not_split', 'grand_staff_multi_voice', 'repeats', 'slurs', 'dynamics', 'small_print', 'multi_page'],
        expected_parts=['Voice', 'Piano'], shared_staves=[],
        lyrics_parts=[{'part': 'Voice', 'verses': 1}],
        notes='No truth. F major, common time, Vivo. First page of a two-page song (continues on leaf 18, not included). Piano lower staff uses the old-style C-shaped bass clef glyph.',
    ),
]


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    out = []
    for it in ITEMS:
        d = os.path.join(REAL, it['id'])
        rel = 'real/' + it['id'] + '/'
        img = os.path.join(d, 'source-page.jpg')
        w, h = Image.open(img).size
        has_truth = os.path.exists(os.path.join(d, 'truth.musicxml'))
        stats = None
        if os.path.exists(os.path.join(d, 'truth.src')):
            stats = json.loads(subprocess.check_output([sys.executable, os.path.join(HERE, 'mkxml.py'),
                                                        os.path.join(d, 'truth.src'), '--stats']))
        src_url = 'https://archive.org/details/%s/page/n%d/mode/1up' % (it['ia'], it['leaf'])
        img_url = 'https://archive.org/download/%s/page/n%d.jpg' % (it['ia'], it['leaf'])
        verify = sorted(f for f in os.listdir(os.path.join(d, 'verify'))) if os.path.isdir(os.path.join(d, 'verify')) else []
        e = dict(
            id=it['id'], title=it['title'], source_url=src_url, license=it['license'], origin='real-scan',
            dpi=it['ppi'], degradations=it['degradations'], has_ground_truth=has_truth, features=it['features'],
            expected_parts=it['expected_parts'], shared_staves=it['shared_staves'], lyrics_parts=it['lyrics_parts'],
            pages=1, measures=(stats['measures'] if stats else None),
            engraver='original 19th/20th-century plate engraving or type, photographed (real scan)',
            scan=rel + 'scan.pdf', truth=(rel + 'truth.musicxml' if has_truth else None),
            clean=None, engraving=None, attribution=rel + 'ATTRIBUTION.txt', notes=it['notes'],
            # --- real-scan provenance / extras ---
            work=it['work'], source_book=it['book'], source_page=it['page_label'],
            source_item='https://archive.org/details/' + it['ia'], source_leaf=it['leaf'], source_image_url=img_url,
            scan_contributor=it['scan_by'], scan_rights_metadata=it['ia_rights'], rights_notes=it['rights_notes'] or None,
            image_px=[w, h], source_image=rel + 'source-page.jpg', scan_sha256=sha256(os.path.join(d, 'scan.pdf')),
            truth_printed=(rel + 'truth-printed.musicxml' if os.path.exists(os.path.join(d, 'truth-printed.musicxml')) else None),
            truth_source=(rel + 'truth.src' if stats else None),
            truth_stats=({k: stats[k] for k in ('measures', 'pickup', 'time', 'fifths', 'notes_total', 'verses')} |
                         {'voices': {k: {kk: v[kk] for kk in ('noteheads', 'rests', 'syllables')} for k, v in stats['voices'].items()}}
                         if stats else None),
            verify_images=[rel + 'verify/' + f for f in verify if f.endswith('-compare.png')],
        )
        out.append(e)
        att = []
        att.append('%s - real scanned page for the OMR test corpus' % it['id'])
        att.append('=' * len(att[0]))
        att.append('')
        att.append('Content      : ' + it['title'])
        att.append('Work         : ' + it['work'])
        att.append('Printed in   : ' + it['book'] + ', ' + it['page_label'])
        att.append('Scan source  : ' + src_url)
        att.append('Page image   : ' + img_url + '  (%dx%d px, %d ppi per IA metadata)' % (w, h, it['ppi']))
        att.append('Scanned by   : ' + it['scan_by'])
        att.append('IA rights    : ' + it['ia_rights'])
        att.append('Licence      : ' + it['license'])
        if it['rights_notes']:
            att.append('Rights notes : ' + it['rights_notes'])
        att.append('Scan status  : ' + IA_NOTE)
        att.append('')
        att.append('Files')
        att.append('  source-page.jpg  the Internet Archive page JPEG, byte-for-byte as downloaded (no edits)')
        att.append('  scan.pdf         one-page IMAGE-ONLY PDF wrapping source-page.jpg unmodified (img2pdf, DCTDecode,')
        att.append('                   no fonts, no text layer), page size = pixels / ppi above')
        if has_truth:
            att.append('  truth.musicxml   hand-transcribed ground truth, MusicXML 4.0 partwise, TARGET layout: one part per')
            att.append('                   voice (shared-staff voices separated into their own parts, lyrics on the voice that')
            att.append('                   carries them). Validated against the MusicXML 4.0 XSD.')
            att.append('  truth-printed.musicxml  same notes in the AS-ENGRAVED layout (voices sharing a staff kept on one')
            att.append('                   staff with stems up/down) - for symbol-level evaluation before part separation.')
            att.append('  truth.src        transcription source (compiled by tools/mkxml.py); header comments list what is')
            att.append('                   deliberately not encoded (dynamics, fingering, slurs, block-text stanzas, ...).')
            att.append('  verify/          musicxml2ly + LilyPond engraving of the truth beside the scan, used to verify the')
            att.append('                   transcription note by note.')
            att.append('  Transcription: corpus agent (Claude), 2026-11-08; dedicated to the public domain (CC0 1.0).')
        else:
            att.append('  (no ground truth yet)')
        att.append('')
        att.append('Re-fetch: corpus/real/tools/fetch_scans.sh')
        with open(os.path.join(d, 'ATTRIBUTION.txt'), 'w') as f:
            f.write('\n'.join(att) + '\n')
    with open(os.path.join(CORPUS, 'manifest-real.json'), 'w') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print('wrote %d entries; with truth: %d' % (len(out), sum(e['has_ground_truth'] for e in out)))


if __name__ == '__main__':
    main()
