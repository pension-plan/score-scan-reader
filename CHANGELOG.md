# Changelog

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
