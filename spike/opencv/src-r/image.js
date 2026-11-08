'use strict';
// Image I/O + small raster helpers.  Core type everywhere:
//   gray  = { width, height, data: Uint8ClampedArray }   (0 = black, 255 = white)
//   binary= { width, height, data: Uint8Array }          (1 = ink, 0 = paper)
// Only the file readers/writers touch node APIs; everything else is
// environment-agnostic (works in a browser / worker unchanged).

function makeGray(width, height, fill = 255) {
  const data = new Uint8ClampedArray(width * height);
  if (fill) data.fill(fill);
  return { width, height, data };
}

function makeBinary(width, height) {
  return { width, height, data: new Uint8Array(width * height) };
}

function cloneBinary(b) {
  return { width: b.width, height: b.height, data: new Uint8Array(b.data) };
}

// --- Netpbm (P5 gray / P6 rgb) -------------------------------------------------
function parsePNM(buf) {
  let pos = 0;
  const tokens = [];
  while (tokens.length < 4) {
    // skip whitespace and comments
    while (pos < buf.length) {
      const c = buf[pos];
      if (c === 35) { while (pos < buf.length && buf[pos] !== 10) pos++; }
      else if (c === 32 || c === 9 || c === 10 || c === 13) pos++;
      else break;
    }
    let s = '';
    while (pos < buf.length && !/\s/.test(String.fromCharCode(buf[pos]))) s += String.fromCharCode(buf[pos++]);
    tokens.push(s);
  }
  pos++; // single whitespace after maxval
  const [magic, w, h, maxv] = tokens;
  const width = +w, height = +h;
  if (+maxv !== 255) throw new Error('only 8-bit PNM supported');
  if (magic === 'P5') return { width, height, channels: 1, data: buf.subarray(pos, pos + width * height) };
  if (magic === 'P6') return { width, height, channels: 3, data: buf.subarray(pos, pos + width * height * 3) };
  throw new Error('unsupported PNM ' + magic);
}

function rgbToGray(width, height, rgb, channels = 3) {
  const out = makeGray(width, height, 0);
  for (let i = 0, j = 0; i < width * height; i++, j += channels) {
    out.data[i] = (rgb[j] * 299 + rgb[j + 1] * 587 + rgb[j + 2] * 114 + 500) / 1000;
  }
  return out;
}

// Reads PGM/PPM/PNG into a gray image (node only).
function readGray(path) {
  const fs = require('fs');
  const buf = fs.readFileSync(path);
  if (buf[0] === 0x89 && buf[1] === 0x50) {
    const { PNG } = require('pngjs');
    const png = PNG.sync.read(buf);
    return rgbToGray(png.width, png.height, png.data, 4);
  }
  const p = parsePNM(buf);
  if (p.channels === 1) return { width: p.width, height: p.height, data: new Uint8ClampedArray(p.data) };
  return rgbToGray(p.width, p.height, p.data, 3);
}

// Reads an RGB image (PPM or PNG) -> { width, height, data: Uint8Array rgb }
function readRGB(path) {
  const fs = require('fs');
  const buf = fs.readFileSync(path);
  if (buf[0] === 0x89 && buf[1] === 0x50) {
    const { PNG } = require('pngjs');
    const png = PNG.sync.read(buf);
    const out = new Uint8Array(png.width * png.height * 3);
    for (let i = 0, j = 0; i < png.width * png.height; i++, j += 4) {
      out[i * 3] = png.data[j]; out[i * 3 + 1] = png.data[j + 1]; out[i * 3 + 2] = png.data[j + 2];
    }
    return { width: png.width, height: png.height, data: out };
  }
  const p = parsePNM(buf);
  if (p.channels !== 3) throw new Error('expected PPM');
  return { width: p.width, height: p.height, data: new Uint8Array(p.data) };
}

function writePGM(path, img) {
  const fs = require('fs');
  const header = Buffer.from(`P5\n${img.width} ${img.height}\n255\n`);
  fs.writeFileSync(path, Buffer.concat([header, Buffer.from(img.data.buffer, img.data.byteOffset, img.data.length)]));
}

// rgb: Uint8Array w*h*3
function writePNGrgb(path, width, height, rgb) {
  const fs = require('fs');
  const { PNG } = require('pngjs');
  const png = new PNG({ width, height });
  for (let i = 0, j = 0; i < width * height; i++, j += 4) {
    png.data[j] = rgb[i * 3]; png.data[j + 1] = rgb[i * 3 + 1]; png.data[j + 2] = rgb[i * 3 + 2]; png.data[j + 3] = 255;
  }
  fs.writeFileSync(path, PNG.sync.write(png));
}

function writePNGgray(path, img) {
  const rgb = new Uint8Array(img.width * img.height * 3);
  for (let i = 0; i < img.width * img.height; i++) rgb[i * 3] = rgb[i * 3 + 1] = rgb[i * 3 + 2] = img.data[i];
  writePNGrgb(path, img.width, img.height, rgb);
}

function binaryToGray(b) {
  const g = makeGray(b.width, b.height, 0);
  for (let i = 0; i < b.data.length; i++) g.data[i] = b.data[i] ? 0 : 255;
  return g;
}

// Bilinear rotation of a gray image about its centre.  angleRad > 0 rotates the
// content counter-clockwise (visually, y axis pointing down).
function rotateGray(img, angleRad) {
  const { width: w, height: h, data } = img;
  const out = makeGray(w, h, 255);
  const cx = (w - 1) / 2, cy = (h - 1) / 2;
  const c = Math.cos(angleRad), s = Math.sin(angleRad);
  // dst d -> src s = c + M^T (d - c), M = [[c, s], [-s, c]]
  for (let y = 0; y < h; y++) {
    const dy = y - cy;
    for (let x = 0; x < w; x++) {
      const dx = x - cx;
      const sx = cx + c * dx - s * dy;
      const sy = cy + s * dx + c * dy;
      const x0 = Math.floor(sx), y0 = Math.floor(sy);
      if (x0 < 0 || y0 < 0 || x0 >= w - 1 || y0 >= h - 1) continue;
      const fx = sx - x0, fy = sy - y0, i = y0 * w + x0;
      const v = (data[i] * (1 - fx) + data[i + 1] * fx) * (1 - fy) + (data[i + w] * (1 - fx) + data[i + w + 1] * fx) * fy;
      out.data[y * w + x] = v;
    }
  }
  return out;
}

// Map a point through the same rotation (src -> dst).
function rotatePoint(x, y, w, h, angleRad) {
  const cx = (w - 1) / 2, cy = (h - 1) / 2;
  const c = Math.cos(angleRad), s = Math.sin(angleRad);
  const dx = x - cx, dy = y - cy;
  return [cx + c * dx + s * dy, cy - s * dx + c * dy];
}

// --- bit-packed binaries (memory per page) -------------------------------------
// A page keeps its staff-removed binary (fr.R) until the score is built from all
// pages. keepPacked(obj, key) stores obj[key] at one bit per pixel and unpacks a
// fresh copy when it is read; at most UNPACKED_MAX pages stay unpacked (the least
// recently read is packed again from its current bytes, so writes are kept, and a
// caller still holding that copy keeps reading it). A binary holding a value other
// than 0/1 is left as it is.
const UNPACKED_MAX = 3;
const unpacked = []; // holders, most recently read last
function packBits(d) {
  const n = d.length, bits = new Uint8Array((n + 7) >> 3), m = n & ~7;
  let j = 0;
  for (let i = 0; i < m; i += 8, j++) {
    bits[j] = d[i] | (d[i + 1] << 1) | (d[i + 2] << 2) | (d[i + 3] << 3) | (d[i + 4] << 4) | (d[i + 5] << 5) | (d[i + 6] << 6) | (d[i + 7] << 7);
  }
  for (let i = m; i < n; i++) if (d[i]) bits[j] |= 1 << (i & 7);
  return bits;
}
function unpackBits(bits, n) {
  const d = new Uint8Array(n), m = n & ~7;
  for (let i = 0, j = 0; i < m; i += 8, j++) {
    const b = bits[j];
    if (!b) continue; // paper: most of a page
    d[i] = b & 1; d[i + 1] = (b >> 1) & 1; d[i + 2] = (b >> 2) & 1; d[i + 3] = (b >> 3) & 1;
    d[i + 4] = (b >> 4) & 1; d[i + 5] = (b >> 5) & 1; d[i + 6] = (b >> 6) & 1; d[i + 7] = b >> 7;
  }
  for (let i = m; i < n; i++) d[i] = (bits[i >> 3] >> (i & 7)) & 1;
  return d;
}
function keepPacked(obj, key) {
  const desc = Object.getOwnPropertyDescriptor(obj, key);
  const b = desc && desc.value;
  if (!b || !(b.data instanceof Uint8Array)) return false;
  const d = b.data;
  for (let i = 0; i < d.length; i++) if (d[i] > 1) return false;
  const h = { shape: Object.assign({}, b, { data: null }), bits: packBits(d), n: d.length, cur: null };
  h.pack = () => { h.bits = packBits(h.cur.data); h.cur = null; };
  Object.defineProperty(obj, key, {
    configurable: true, enumerable: true,
    get() {
      if (!h.cur) {
        h.cur = Object.assign({}, h.shape, { data: unpackBits(h.bits, h.n) });
        h.bits = null;
        unpacked.push(h);
        while (unpacked.length > UNPACKED_MAX) unpacked.shift().pack();
      } else if (unpacked[unpacked.length - 1] !== h) {
        unpacked.splice(unpacked.indexOf(h), 1);
        unpacked.push(h);
      }
      return h.cur;
    },
    set(v) {
      const k = unpacked.indexOf(h);
      if (k >= 0) unpacked.splice(k, 1);
      Object.defineProperty(obj, key, { configurable: true, enumerable: true, writable: true, value: v });
    },
  });
  return true;
}

module.exports = {
  makeGray, makeBinary, cloneBinary, parsePNM, rgbToGray, readGray, readRGB,
  writePGM, writePNGrgb, writePNGgray, binaryToGray, rotateGray, rotatePoint, keepPacked,
};
