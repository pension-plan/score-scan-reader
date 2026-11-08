# Synthetic pages for the letter / chord-symbol templates (tools/textglyphs.js): rehearsal letters
# A-Z boxed and circled, digits 1-9, 0 boxed, and a common chord-symbol set, each page in one text
# font (LilyPond + pdftoppm). usage: python3 mvp/tools/glyphsynth.py  (writes mvp/work/glyphsynth/)
import subprocess, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work', 'glyphsynth')
os.makedirs(OUT, exist_ok=True)
os.chdir(OUT)
FONTS = {'c059': 'C059', 'nimbusroman': 'Nimbus Roman', 'nimbussans': 'Nimbus Sans', 'liberationserif': 'Liberation Serif', 'dejavusans': 'DejaVu Sans'}
LET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
CHORDS = ['c1', 'c:m', 'c:7', 'c:m7', 'c:maj7', 'c:6', 'c:m6', 'c:9', 'c:sus4', 'c:dim', 'c:dim7', 'c:m7.5-', 'c:aug',
          'd1', 'd:m', 'd:7', 'e:m7', 'f1', 'f:maj7', 'g:7', 'g:sus4', 'a:m', 'a:m7', 'b:m7.5-', 'b:dim7',
          'bes1', 'bes:7', 'ees:maj7', 'aes1', 'fis:m', 'cis:m7', 'des:9', 'ges:6', 'c1/e', 'g1/b', 'f1/a', 'd:m/f', 'a:7/cis',
          'e:aug', 'a:sus2', 'g:m6', 'c:m9', 'f:9', 'e:7', 'b:7', 'd:maj7']
def page(name, font, body, extra=''):
    ly = f'''\\version "2.24.0"
\\paper {{ #(set-paper-size "letter") property-defaults.fonts.serif = "{font}" property-defaults.fonts.sans = "{font}" tagline = ##f }}
\\header {{ tagline = ##f }}
{body}
'''
    open(f'{name}.ly', 'w').write(ly)
    subprocess.run(['lilypond', '-s', f'{name}.ly'], check=True)
    subprocess.run(['pdftoppm', '-gray', '-r', '200', f'{name}.pdf', name], check=True)
for key, font in FONTS.items():
    for enc in ['box', 'circle']:
        bars = ' '.join(f'\\mark \\markup \\{enc} \\bold "{c}" c\'\'1 |' + (' \\break' if (i + 1) % 6 == 0 else '') for i, c in enumerate(LET))
        page(f'marks-{enc}-{key}', font, f'\\score {{ \\new Staff {{ \\cadenzaOff \\time 4/4 {bars} }} \\layout {{ }} }}')
    # single digits in boxes (rehearsal numbers): 1-9 and 0
    for enc in ['box']:
        bars = ' '.join(f'\\mark \\markup \\{enc} \\bold "{c}" c\'\'1 |' + (' \\break' if (i + 1) % 5 == 0 else '') for i, c in enumerate('1234567890'))
        page(f'digits-{enc}-{key}', font, f'\\score {{ \\new Staff {{ \\time 4/4 {bars} }} \\layout {{ }} }}')
    seq = ' '.join(CHORDS)
    notes = ' '.join("c''1" + (' \\break' if (i + 1) % 6 == 0 else '') for i in range(len(CHORDS)))
    # chord names in this page's font (LilyPond otherwise sets them in its default sans)
    page(f'chords-{key}', font, f'''\\score {{ << \\new ChordNames \\with {{ \\override ChordName.font-family = #'roman }} {{ \\chordmode {{ {seq} }} }} \\new Staff {{ \\time 4/4 {notes} }} >> \\layout {{ }} }}''')
# LilyPond's own chord-name look (its default sans), as most lead sheets engraved with it show
seq = ' '.join(CHORDS)
notes = ' '.join("c''1" + (' \\break' if (i + 1) % 6 == 0 else '') for i in range(len(CHORDS)))
open('chords-default.ly', 'w').write(f'''\\version "2.24.0"
\\paper {{ #(set-paper-size "letter") tagline = ##f }}
\\score {{ << \\new ChordNames {{ \\chordmode {{ {seq} }} }} \\new Staff {{ \\time 4/4 {notes} }} >> \\layout {{ }} }}
''')
subprocess.run(['lilypond', '-s', 'chords-default.ly'], check=True)
subprocess.run(['pdftoppm', '-gray', '-r', '200', 'chords-default.pdf', 'chords-default'], check=True)
