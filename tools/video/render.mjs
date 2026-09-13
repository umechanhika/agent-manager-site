// Renders tools/video/intro.html into a video file, frame by frame (deterministic).
//
//   PLAYWRIGHT_MODULE=$(npm root -g)/playwright FFMPEG=/path/to/ffmpeg node tools/video/render.mjs --lang en|ja [--out DIR] [--fps 30] [--sheet]
//
// --sheet renders only 13 key frames and tiles them into a contact sheet (fast preview).
// Requires: playwright (chromium), FFMPEG env var pointing at an ffmpeg binary with libvpx / libx264.
// The MP4 step is skipped (with a warning) when the binary lacks libx264.

import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { mkdirSync, rmSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// playwright is resolved from PLAYWRIGHT_MODULE (e.g. a global install) or the local node_modules.
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE || 'playwright');

const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) =>
  a.startsWith('--') ? [a.slice(2), arr[i + 1]?.startsWith('--') || arr[i + 1] === undefined ? true : arr[i + 1]] : []).filter(x => x.length));
const lang = args.lang === 'ja' ? 'ja' : 'en';
const fps = Number(args.fps || 30);
const here = path.dirname(fileURLToPath(import.meta.url));
const out = path.resolve(args.out || path.join(here, 'out'));
const FFMPEG = process.env.FFMPEG;
if (!FFMPEG || !existsSync(FFMPEG)) throw new Error('FFMPEG env var must point at an ffmpeg binary');

const KEY_TIMES = [1.8, 6.6, 10.4, 14.4, 17.0, 20.0, 24.2, 27.4, 31.6, 36.4, 38.6, 43.4, 48.0];

const framesDir = path.join(out, `frames-${lang}${args.sheet ? '-sheet' : ''}`);
rmSync(framesDir, { recursive: true, force: true });
mkdirSync(framesDir, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 960 }, deviceScaleFactor: 1 });
await page.goto(`file://${path.join(here, 'intro.html')}?lang=${lang}&capture=1`);
await page.evaluate(() => document.fonts.ready);
const DURATION = await page.evaluate(() => window.DURATION);   // the page owns its length

const times = args.sheet ? KEY_TIMES : Array.from({ length: DURATION * fps }, (_, i) => i / fps);
for (let i = 0; i < times.length; i++) {
  await page.evaluate(t => window.seek(t), times[i]);
  await page.screenshot({ path: path.join(framesDir, `${String(i).padStart(4, '0')}.png`), clip: { x: 0, y: 0, width: 1200, height: 960 } });
  if (!args.sheet && i % 150 === 0) console.log(`frame ${i}/${times.length}`);
}
await browser.close();

function ff(argv, label) {
  const r = spawnSync(FFMPEG, ['-y', '-hide_banner', '-loglevel', 'error', ...argv], { stdio: 'inherit' });
  if (r.status !== 0) throw new Error(`ffmpeg failed: ${label}`);
}

if (args.sheet) {
  const sheet = path.join(out, `sheet-${lang}.png`);
  ff(['-i', path.join(framesDir, '%04d.png'), '-vf', 'scale=560:-1,tile=4x4:padding=6:margin=6:color=black', sheet], 'sheet');
  console.log(`sheet: ${sheet}`);
} else {
  const input = ['-framerate', String(fps), '-i', path.join(framesDir, '%04d.png')];
  const webm = path.join(out, `intro-${lang}.webm`);
  ff([...input, '-c:v', 'libvpx', '-b:v', '2.5M', '-auto-alt-ref', '0', '-pix_fmt', 'yuv420p', '-an', webm], 'webm');
  console.log(`webm: ${webm}`);
  const encoders = spawnSync(FFMPEG, ['-hide_banner', '-encoders'], { encoding: 'utf8' }).stdout || '';
  if (encoders.includes('libx264')) {
    const mp4 = path.join(out, `intro-${lang}.mp4`);
    ff([...input, '-c:v', 'libx264', '-crf', '21', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', mp4], 'mp4');
    console.log(`mp4: ${mp4}`);
  } else {
    console.warn('WARNING: ffmpeg lacks libx264 — MP4 skipped');
  }
  const poster = path.join(out, `intro-poster-${lang}.jpg`);
  ff(['-i', path.join(framesDir, String(Math.round(20.0 * fps)).padStart(4, '0') + '.png'), '-q:v', '4', poster], 'poster');
  console.log(`poster: ${poster}`);
}
