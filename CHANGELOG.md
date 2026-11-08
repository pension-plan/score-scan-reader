# Changelog

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
