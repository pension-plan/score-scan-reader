# Changelog

## [0.30.1](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.30.0...score-scan-reader-v0.30.1) (2026-11-08)


### Bug Fixes

* **meter:** a system's last real bar is not dropped with the courtesy signature after it ([b51ba25](https://github.com/pension-plan/score-scan-reader/commit/b51ba25ddc6a7efa615439a8fd06ea31ad84893c))

## [0.30.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.29.0...score-scan-reader-v0.30.0) (2026-11-08)


### Features

* **heads:** heads fused with their accidentals, parenthesised courtesy signs ([6b891a8](https://github.com/pension-plan/score-scan-reader/commit/6b891a86b87cc072ea4cc2a4c34cfba23a4783f7))
* **lyrics:** opt-in stanzasAsVerses sets stanzas printed below the music as verses (L5b) ([959bcac](https://github.com/pension-plan/score-scan-reader/commit/959bcacc77b546aa054968c0da6b2370b5f0d74c))
* **ui:** option to set stanzas printed below the music as verses (L5b) ([a942ffe](https://github.com/pension-plan/score-scan-reader/commit/a942ffeec7652ea5ca8f2bd2ea36bc5890e13747))


### Bug Fixes

* **front:** grace notes keep their short stems next to a chord ([84d0451](https://github.com/pension-plan/score-scan-reader/commit/84d0451e380314a2088b8419aaf12700149404bb))
* **meter:** worn signatures chosen by bar contents; courtesy signatures after a courtesy key; bar counts across pages ([c03021c](https://github.com/pension-plan/score-scan-reader/commit/c03021c364cd8d04c0de18f50e0ee026c698cab9))
* **ocr:** second-pass reader no longer asks for ita.special-words ([18e3f41](https://github.com/pension-plan/score-scan-reader/commit/18e3f4160d647bbac584f077ffbb9484599f7dc9))
* **systems:** staves regrouped into equal systems when their joining lines were lost; spreads with a staff traced across the gutter ([5dc261f](https://github.com/pension-plan/score-scan-reader/commit/5dc261f1bfcb959908fb6931ee53cdb827be5d9d))
* **text:** D.S./D.C. before 'al Coda' recovered; part labels with merged-word components; concurrent text OCR ([b36a858](https://github.com/pension-plan/score-scan-reader/commit/b36a858a956cefd0bebac96688f3cbfa447737b4))


### Performance Improvements

* **load:** conversion starts while OCR loads; split Tesseract core; notation library lazy ([34dad95](https://github.com/pension-plan/score-scan-reader/commit/34dad9520848fc66f7a2169ee1e589f0e17b9aff))

## [0.29.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.28.1...score-scan-reader-v0.29.0) (2026-11-08)


### Features

* pedal bracket lines, circled rehearsal numbers; looser digit thresholds; flat strokes no longer elisions ([15ec03e](https://github.com/pension-plan/score-scan-reader/commit/15ec03e5af42c97000c8f01c05f2ce0871fbd8aa))

## [0.28.1](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.28.0...score-scan-reader-v0.28.1) (2026-11-08)


### Bug Fixes

* **spread:** a left-page staff overlapping the gutter by up to a staff space no longer hides a book spread ([f64bd71](https://github.com/pension-plan/score-scan-reader/commit/f64bd71b33509cd1501c5762bbcc0ceac07767a5))
* **structure:** voltas over chord symbols and from a system's first bar ([69e30f1](https://github.com/pension-plan/score-scan-reader/commit/69e30f1930441dbafa20cfc1c852e44761edf6b2))


### Performance Improvements

* **ocr:** reads started together on a pool of two readers, PGM input, lazy rest scoring ([6ee5e2e](https://github.com/pension-plan/score-scan-reader/commit/6ee5e2e6c70bf222b09b12c70da5b3df566c1120))

## [0.28.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.27.1...score-scan-reader-v0.28.0) (2026-11-08)


### Features

* **layout:** brace tip detector; brackets, C clefs and ensembles never read as a piano; instrument names (L18/L6/L9/L4b) ([a25dd3b](https://github.com/pension-plan/score-scan-reader/commit/a25dd3b7fe7c27378b8b1035e81a904116a2e3b8))


### Bug Fixes

* **lyrics:** record inferred melismas so the missed-syllable check runs (L4b); note why tied bass-staff text goes to both voices (L7) ([e89e2eb](https://github.com/pension-plan/score-scan-reader/commit/e89e2eb94cf7c39404dcf43e6fbc8145273cd15e))
* **score:** articulations on every note of a chord ([d176663](https://github.com/pension-plan/score-scan-reader/commit/d176663fab2a8233777a74f31bbac8ae0b0a36fd))


### Reverts

* files swept into d176663 by mistake (other agents' work in progress) ([f7861d5](https://github.com/pension-plan/score-scan-reader/commit/f7861d5ad322bc5f46a9c6394a86510744d5f837))

## [0.27.1](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.27.0...score-scan-reader-v0.27.1) (2026-11-08)


### Bug Fixes

* **ottava:** octave lines up to ten spaces from the staff ([a7ad2d2](https://github.com/pension-plan/score-scan-reader/commit/a7ad2d255cfe02f0570e29badf8ec5283d8a1112))


### Performance Improvements

* **ui:** page image drawn into a canvas, freeing decoded pages (L26) ([8045059](https://github.com/pension-plan/score-scan-reader/commit/804505900e96402b74c906b80804c7d53130326e))

## [0.27.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.26.0...score-scan-reader-v0.27.0) (2026-11-08)


### Features

* **keys,voltas,meter:** one-sign key changes, upright pages with sharp courtesy keys, volta numbers read, implausible meters dropped ([f2e4a8b](https://github.com/pension-plan/score-scan-reader/commit/f2e4a8b19790c3418aed0209050b1a9dd2460a70))
* pedal marks, fingering, rehearsal marks and chord symbols written; tempo/expression words snapped to terms ([411aade](https://github.com/pension-plan/score-scan-reader/commit/411aadeca20d9cd4101586d78911d404f8bd2353))
* **rests:** 16th-64th rests from templates, also when a false head sits on them ([04e1879](https://github.com/pension-plan/score-scan-reader/commit/04e18798e792c08fdc7973ea3ea2349f31a49841))


### Bug Fixes

* **artic,ottava:** accent over a staccato, marcato pieces joined, 15ma read and continued ([8060286](https://github.com/pension-plan/score-scan-reader/commit/8060286a505f32fdc2fcb62ae01d209cccc42773))
* **regress:** per-run output paths so concurrent runs don't overwrite each other ([c7607e2](https://github.com/pension-plan/score-scan-reader/commit/c7607e25ca8204b8ccded324dde0a495f97e6b10))
* restore f2e4a8b's score.js hunks reverted by 411aade ([1b60f3b](https://github.com/pension-plan/score-scan-reader/commit/1b60f3bcff514bfc9effe58f86af43ce78d7564f))


### Performance Improvements

* faster template scoring and component labelling, identical output ([2851d4d](https://github.com/pension-plan/score-scan-reader/commit/2851d4debe57c4d5b8687f31ccbd59d1761056f3))

## [0.26.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.25.0...score-scan-reader-v0.26.0) (2026-11-08)


### Features

* **lyrics:** lazy second OCR pass with fra/spa/ita/ces for accented rows; elisions across word gaps ([42f3d40](https://github.com/pension-plan/score-scan-reader/commit/42f3d40a32d2725cb7baaca261d14cd2b4e24b74))


### Bug Fixes

* **artic:** marcato cut in two by staff-line removal joined ([03ada96](https://github.com/pension-plan/score-scan-reader/commit/03ada96c263c7b9835951f337c22421209d62df4))
* **meter,artic:** meters after missed barlines and on worn digits; fewer false articulations ([0155e68](https://github.com/pension-plan/score-scan-reader/commit/0155e6816dccb130c2c1b3cee18121d2269a575b))


### Performance Improvements

* **memory:** flat memory per page in long documents (L26) ([8b5d595](https://github.com/pension-plan/score-scan-reader/commit/8b5d595a9896589aaafe1bf0a69d5d5b19e027ee))

## [0.25.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.24.0...score-scan-reader-v0.25.0) (2026-11-08)


### Features

* grace notes from narrow detected heads on by default ([926ec3a](https://github.com/pension-plan/score-scan-reader/commit/926ec3a9c8bba94a1392bcc5af7e55f1b271776f))
* **meter:** time signatures on every system, after barlines and at system ends (L16/L21) ([3d15815](https://github.com/pension-plan/score-scan-reader/commit/3d15815d631383b1eb4d6aaca35c03ae842111a8))
* **structure:** repeats, voltas, barline styles, segno/coda, beams, articulations, octave lines, multi-bar rests, double dots (L22/L14/L15) ([d0f1105](https://github.com/pension-plan/score-scan-reader/commit/d0f1105ccc9d4950858479e1a484f25f077f688f))


### Bug Fixes

* **front:** drop beam pieces taken for filled heads ([c177285](https://github.com/pension-plan/score-scan-reader/commit/c1772858bb5a0b4e083b221ae141a2bf030fd9d4))

## [0.24.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.23.0...score-scan-reader-v0.24.0) (2026-11-08)


### Features

* **heads:** split stacks of hollow heads (whole/half-note chords) ([5aa6a21](https://github.com/pension-plan/score-scan-reader/commit/5aa6a21b682fd1b092a2c4e87ca16706f040bb9c))


### Bug Fixes

* **heads:** hollow heads on ledger lines read as half/whole notes ([858beb7](https://github.com/pension-plan/score-scan-reader/commit/858beb7baade8a34cf0bf54f16ee8fcbec84ebab))
* **lyrics:** credits never underlay, tall accented rows kept, elisions written ([40a5631](https://github.com/pension-plan/score-scan-reader/commit/40a5631282a7d4f4094d15e8249c52fcc1b83919))

## [0.23.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.22.0...score-scan-reader-v0.23.0) (2026-11-08)


### Features

* ties found between same-pitch neighbour heads with an arc of ink ([b357ba7](https://github.com/pension-plan/score-scan-reader/commit/b357ba7aeff97bab43cac3764ad175a3ce097c5e))

## [0.22.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.21.1...score-scan-reader-v0.22.0) (2026-11-08)


### Features

* metronome marks read and written as tempo (words, metronome, sound tempo) ([3ae56fa](https://github.com/pension-plan/score-scan-reader/commit/3ae56fa4c849bbe436035bfefa4428686655138b))

## [0.21.1](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.21.0...score-scan-reader-v0.21.1) (2026-11-08)


### Bug Fixes

* **playback:** audible first dynamic, staff-scoped dynamics, sound dynamics export, dynamic shown in the transport ([437afb3](https://github.com/pension-plan/score-scan-reader/commit/437afb3087b8f4792fd4c494e507d63b365a2de7))

## [0.21.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.20.0...score-scan-reader-v0.21.0) (2026-11-08)


### Features

* fermatas written to MusicXML ([35b4034](https://github.com/pension-plan/score-scan-reader/commit/35b4034f2337dc44dec743d67807481b65308485))
* **notes:** read 32nd and 64th notes (beam stacks past 1.6 spaces, 1680 divisions) ([713fbe7](https://github.com/pension-plan/score-scan-reader/commit/713fbe786ed37abe89c3f7ba0deca56cdcd3bdcd))
* optional grace notes from narrow detected heads (opts.graceHeads, off) ([0cd2fc0](https://github.com/pension-plan/score-scan-reader/commit/0cd2fc0bb46c6b03e5ef29b88aa5f45e183ce704))

## [0.20.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.19.0...score-scan-reader-v0.20.0) (2026-11-08)


### Features

* **cv:** read double sharps and double flats from templates ([d4757fc](https://github.com/pension-plan/score-scan-reader/commit/d4757fcb2b1c5edeba711f0adcc5b7c0b7fa34c8))

## [0.19.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.18.1...score-scan-reader-v0.19.0) (2026-11-08)


### Features

* slurs, ties and grace notes written to MusicXML ([2b560bc](https://github.com/pension-plan/score-scan-reader/commit/2b560bc36a6c4099b4e31f7b981505636b74c65b))

## [0.18.1](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.18.0...score-scan-reader-v0.18.1) (2026-11-08)


### Bug Fixes

* **staves:** re-anchor dashed staves found one line off ([ec2a68e](https://github.com/pension-plan/score-scan-reader/commit/ec2a68e3dde8b115ca684fd26b620410d79fb316))

## [0.18.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.17.0...score-scan-reader-v0.18.0) (2026-11-08)


### Features

* bar-number fix pass limited to clean single-barline corrections (opt-in) ([888d6ab](https://github.com/pension-plan/score-scan-reader/commit/888d6ab14bd299c3f34eeb3af5baf9bc65ae6881))
* **staves:** fallback finder for staff lines broken into dashes ([e97dbde](https://github.com/pension-plan/score-scan-reader/commit/e97dbdee16ffba243cae06f05fa70bf60d671c46))

## [0.17.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.16.0...score-scan-reader-v0.17.0) (2026-11-08)


### Features

* bar numbers read by digit shape and checked against the bars read; braces classified ([0f00a0e](https://github.com/pension-plan/score-scan-reader/commit/0f00a0e1dbf9db2189c75e43e43467e2abd7c8c9))
* **cv:** dewarp photographed and curled pages from their staves; flatten severe phone shots ([389d23b](https://github.com/pension-plan/score-scan-reader/commit/389d23beb22edf212a9f6d93d1493d37e8a115bb))
* **ui:** shorter unrecognised-marks copy ([50decc0](https://github.com/pension-plan/score-scan-reader/commit/50decc0a5bd7f4e58ef8be13b8a8afe4ad747c09))


### Bug Fixes

* **ui:** scan and preview use the full page width again ([54eb7b3](https://github.com/pension-plan/score-scan-reader/commit/54eb7b36bfd3f9605dae6b3dfe096384e376ca33))

## [0.16.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.15.0...score-scan-reader-v0.16.0) (2026-11-08)


### Features

* **ui:** unrecognised marks first: views, larger highlights, say what a mark is, user corrections ([f0cb830](https://github.com/pension-plan/score-scan-reader/commit/f0cb8303e45169893e3a1c7deb954911753015c6))

## [0.15.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.14.0...score-scan-reader-v0.15.0) (2026-11-08)


### Features

* play the transcribed score with General MIDI instruments ([9d1b30b](https://github.com/pension-plan/score-scan-reader/commit/9d1b30b238a3d8c1259e20bfd1621e8fe39fe51f))
* **site:** changelog moves to the bottom of /app/, collapsed ([e0c6c6b](https://github.com/pension-plan/score-scan-reader/commit/e0c6c6b0d1f795a61b86c86b30ce92eed7161cf4))

## [0.14.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.13.0...score-scan-reader-v0.14.0) (2026-11-08)


### Features

* **cv:** pre-clean in plain JS, OpenCV.js no longer shipped ([4aab1af](https://github.com/pension-plan/score-scan-reader/commit/4aab1af96319f776b4a12c68d39000e854af49f2))
* **cv:** read time-signature numbers and unread clefs from templates (plain JS, default on) ([9a124ee](https://github.com/pension-plan/score-scan-reader/commit/9a124eec7f0754b94c81845a0c7b8f751708521c))

## [0.13.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.12.0...score-scan-reader-v0.13.0) (2026-11-08)


### Features

* **cv:** OpenCV pre-clean for degraded scans ([045d08f](https://github.com/pension-plan/score-scan-reader/commit/045d08f1f9145b3e83906d09b8720e966f60ad80))

## [0.12.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.11.0...score-scan-reader-v0.12.0) (2026-11-08)


### Features

* recognise text, dynamics and instrument names ([6ed273c](https://github.com/pension-plan/score-scan-reader/commit/6ed273ca31997609e3a520666c336d6444d9791f))

## [0.11.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.10.0...score-scan-reader-v0.11.0) (2026-11-08)


### Features

* **ui:** mark for repair: draw over the page, note each mark, export repair notes ([b10c817](https://github.com/pension-plan/score-scan-reader/commit/b10c8176136dcd91c7d927a5be0d59eafea61b4f))

## [0.10.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.9.0...score-scan-reader-v0.10.0) (2026-11-08)


### Features

* **ui:** All examples picker loads any of the 19 shareable benchmark scans ([184d5b5](https://github.com/pension-plan/score-scan-reader/commit/184d5b54279d26ebb2eda98b80714a3c484b96fe))
* **ui:** overlay marks every recognised symbol, labels pitch and duration, highlights unrecognised ink ([42663a6](https://github.com/pension-plan/score-scan-reader/commit/42663a6c5878dc9457a766f4bd590f0a1fb87896))

## [0.9.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.8.0...score-scan-reader-v0.9.0) (2026-11-08)


### Features

* ship fix-forward round 3 (benchmark 0.948, real scans 0.926, challenge 0.910) ([7ae1200](https://github.com/pension-plan/score-scan-reader/commit/7ae1200feb5f99495b1333b749fbab1d0259500f))

## [0.8.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.7.0...score-scan-reader-v0.8.0) (2026-11-08)


### Features

* **heads:** broken-staff-line recovery for thin photocopies, fewer false heads next to accidentals, chord tops above ledgers (round 3) ([0a92fc6](https://github.com/pension-plan/score-scan-reader/commit/0a92fc65f0ceda620a81941b9fe5e052002e3577))
* **ml:** copista-2m correction pass (note values, false/missed heads, safety gate), available as an option (round 3) ([151a209](https://github.com/pension-plan/score-scan-reader/commit/151a20947b1369cfb2ab7405f7110ea3d6e9071a))

## [0.7.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.6.0...score-scan-reader-v0.7.0) (2026-11-08)


### Features

* **parts:** two voices inside piano parts, small instrument staves as separate parts, key changes across systems (round 3) ([7c6721c](https://github.com/pension-plan/score-scan-reader/commit/7c6721c3a41f103cb417c6c2709060ce9c7f2337))
* **rests:** wide H-bar multi-rests with bar counts, rests outside the staff, rest blocks replace false noteheads ([2879ed9](https://github.com/pension-plan/score-scan-reader/commit/2879ed954510cfffc8feb267de3d56d739ca7058))


### Bug Fixes

* **score:** remove Node-only debug flags; keyboard two-voice split is the default (round 3) ([ae60855](https://github.com/pension-plan/score-scan-reader/commit/ae608555ca98957b697412ce52ac83f744178c91))

## [0.6.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.5.1...score-scan-reader-v0.6.0) (2026-11-08)


### Features

* **ui:** St. Anselm second sample, eng+deu OCR, per-page reading notes, spread overlays (round 3) ([2005ecd](https://github.com/pension-plan/score-scan-reader/commit/2005ecdad2d3c7dc2a8ead1cc6e61741159380fb))


### Bug Fixes

* **build:** commit the app's copista-2m model assets so CI and Pages builds stop failing ([648042b](https://github.com/pension-plan/score-scan-reader/commit/648042b615e443e3174c1db6e63dfd129f4ab609))
* **eval:** busy-wait message no longer references log before it is defined ([0dd5e70](https://github.com/pension-plan/score-scan-reader/commit/0dd5e70c7edd4d89f0ad00b2424205f8598b5543))
* **rests:** key-signature sharps and naturals no longer read as quarter rests (rests F1 0.726 benchmark, 0.729 challenge) ([2ad21bc](https://github.com/pension-plan/score-scan-reader/commit/2ad21bc894faead1b5e4a8be7c09ee6788dc7de6))

## [0.5.1](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.5.0...score-scan-reader-v0.5.1) (2026-11-08)


### Bug Fixes

* **rests:** detect rest glyphs in every voice incl. piano (src/rests.js); rests F1 0.445 -&gt; 0.581 ([89f667d](https://github.com/pension-plan/score-scan-reader/commit/89f667d09310313b7fa86c1cb37a1553d44461b6))

## [0.5.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.4.0...score-scan-reader-v0.5.0) (2026-11-08)


### Features

* **app:** Maple Leaf Rag as the default sample; ship round 2 (aggregate 0.925, real scans 0.907) ([f9f5855](https://github.com/pension-plan/score-scan-reader/commit/f9f585536bf0c5e83bcb975d9b2681158e4d8093))

## [0.4.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.3.0...score-scan-reader-v0.4.0) (2026-11-08)


### Features

* **heads:** ledger checks on both binaries, narrow-font heads, fewer false hollow heads, front-end fallbacks (round 2) ([2166f93](https://github.com/pension-plan/score-scan-reader/commit/2166f93405fc7b5fc7486f000264d0cd9edc2737))
* **site:** changelog panel and engine label on /app/; ci: regression check against the last release on every push ([03214a3](https://github.com/pension-plan/score-scan-reader/commit/03214a346afa4fa0a4e989104503b2018af25761))
* **symbols:** tuplet detection with 840 divisions, robust key/clef reading on old prints, clef/key change detection (round 2) ([bae11b0](https://github.com/pension-plan/score-scan-reader/commit/bae11b09277df56154849862d502fd7f9c6ebd09))

## [0.3.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.2.0...score-scan-reader-v0.3.0) (2026-11-08)


### Features

* **demo:** copista-2m ML detector demo on GitHub Pages (/ml-demo/) ([f812157](https://github.com/pension-plan/score-scan-reader/commit/f81215705b45ebf5eddec196e321f79a38214b54))
* **lyrics:** split multi-note words, port strips line detector, read part labels and stanzas (round 2) ([e1c2221](https://github.com/pension-plan/score-scan-reader/commit/e1c2221d1252d6013fc434d9b4f4b842f82ec299))
* **parts:** lyric-to-voice assignment, melisma extenders, printed part names, stanza credits (round 2) ([20100ec](https://github.com/pension-plan/score-scan-reader/commit/20100ecc2601edcff2152ce46c833efc3a279a36))
* **site:** release footer on every Pages page with version, release age (AEDT) and build commit ([663c80b](https://github.com/pension-plan/score-scan-reader/commit/663c80ba9bca6d9ca84651f7d24b630f8f96f06e))
* **site:** version bar at the top of every Pages page, including commits ahead of the release ([e9c5c3a](https://github.com/pension-plan/score-scan-reader/commit/e9c5c3a496824152553373539c6ba1e83a0d44ca))
* **ui:** read up to 40 pages page by page in a Web Worker with progress and Stop (round 2) ([56859ef](https://github.com/pension-plan/score-scan-reader/commit/56859ef146641e92e608e058541078b44eb34bd6))

## [0.2.0](https://github.com/pension-plan/score-scan-reader/compare/score-scan-reader-v0.1.0...score-scan-reader-v0.2.0) (2026-11-08)


### Features

* **heads:** ledger-line check, faint-staff detection, hollow-head recovery, wide-blob splitting (round 1) ([177e0e8](https://github.com/pension-plan/score-scan-reader/commit/177e0e8a66cc9e6b177c3892357283430a1168c6))
* **lyrics:** wider word gaps, junk-row rejection, verse numbers and cross-system hyphens (round 1) ([aca893f](https://github.com/pension-plan/score-scan-reader/commit/aca893fc0a15a4ba476a1fa5bf510b21189c7204))
* **parts:** barline-based piano detection, clef-based part names, per-measure rhythm repair, rest detection (round 1) ([bcfb9e0](https://github.com/pension-plan/score-scan-reader/commit/bcfb9e0172e393b43a5dcaca25a5f6845f06739f))
* publish the app, status page and docs on GitHub Pages ([ee204e4](https://github.com/pension-plan/score-scan-reader/commit/ee204e443022c8a53504d5cc074cefc30a614ed8))
* score scan reader v1, eval harness, corpora, design docs, CI and release-please ([ccbb2b6](https://github.com/pension-plan/score-scan-reader/commit/ccbb2b618d918d8ce8e801e34e6f8ba5c80474ca))
* ship fix-forward round 1 (aggregate 0.589 -&gt; 0.884) ([d9c3916](https://github.com/pension-plan/score-scan-reader/commit/d9c3916d3827ffef4a7d87a9166dad5015f0568c))
* **symbols:** header parsing for clef/key/time, robust accidentals, treble-8vb clef (round 1) ([7990370](https://github.com/pension-plan/score-scan-reader/commit/799037052709bb86f8329a92e50ee9ec45309095))


### Bug Fixes

* **ci:** use Playwright's bundled Chromium when the local cached build is absent ([7d39275](https://github.com/pension-plan/score-scan-reader/commit/7d39275a17a355b71dd54fe3c466fcbe5c391822))
