# opencv-4.10.0-noeval.js

Source: npm `@techstark/opencv-js@4.10.0-release.1` (published 2024-08-25), `dist/opencv.js`
(10,378,215 bytes, wasm embedded as base64). Licence: Apache-2.0 (`LICENSE.opencv-js-Apache-2.0.txt`).

Rebuild:

```
cd spike/opencv && npm install
node tools/patch-noeval.js node_modules/@techstark/opencv-js/dist/opencv.js ../../mvp/assets-src/opencv/opencv-4.10.0-noeval.js
node ../../mvp/assets-src/opencv/sync.js
```

The patch and why: `NOTICE.opencv.txt`, `docs/spike-opencv.md`.
