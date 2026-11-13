#!/usr/bin/env node
// Record one full playback of a nara-flow-map page to mp4 (needs ffmpeg).
// Installs nothing: it uses a playwright-core or playwright that is already installed, locally or globally.
// It refuses to record a page whose flowSelfCheck() is not ok, so a video never shows a broken map.
//
// Usage: node record_flow_map.mjs <page.html> <out.mp4> [--speed 0.65] [--size 1440x900]
// Exit: 0 recorded, 1 self-check failed or playback did not finish, 2 bad arguments, 3 no browser driver,
// 4 no ffmpeg.
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const opt = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : fallback; };
const speed = opt("--speed", "0.65");
const [w, h] = opt("--size", "1440x900").split("x").map(Number);
const [page, out] = args;
if (!page || !out || !existsSync(page) || !(w > 0 && h > 0)) {
  console.error("usage: node record_flow_map.mjs <page.html> <out.mp4> [--speed 0.65] [--size 1440x900]");
  process.exit(2);
}

function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const roots = [process.cwd()];
  try { roots.push(execFileSync("npm", ["root", "-g"], { encoding: "utf8" }).trim()); } catch { /* npm not on PATH */ }
  for (const root of roots) {
    for (const name of ["playwright-core", "playwright", "@playwright/cli/node_modules/playwright-core"]) {
      try { return require(require.resolve(name, { paths: [root] })); } catch { /* try the next candidate */ }
    }
  }
  return null;
}
const pw = loadPlaywright();
if (!pw) {
  console.error("no playwright-core found (local or global). Not installing one; record with a browser MCP or skip.");
  process.exit(3);
}

let browser;
// Bundled Chromium first: system Chrome in headless mode crops recorded frames to about 812px tall.
for (const launch of [{}, { channel: "chrome" }]) {
  try { browser = await pw.chromium.launch({ headless: true, ...launch }); break; } catch { /* fall back to system Chrome */ }
}
if (!browser) { console.error("no Chromium could be launched"); process.exit(3); }

const dir = mkdtempSync(join(tmpdir(), "flow-map-rec-"));
let code = 0;
try {
  const url = pathToFileURL(resolve(page)).href;
  // The self-check replays every step, so it runs in its own unrecorded tab.
  const checkCtx = await browser.newContext({ viewport: { width: w, height: h } });
  const checkTab = await checkCtx.newPage();
  await checkTab.goto(url);
  const check = await checkTab.evaluate(() => (typeof flowSelfCheck === "function" ? flowSelfCheck() : { ok: false, missing: true }));
  await checkCtx.close();

  if (!check.ok) {
    console.error("flowSelfCheck is not ok; fix the page first:\n" + JSON.stringify(check, null, 1));
    code = 1;
  } else {
    // Frames are full-viewport screenshots taken back to back (about 23 per second measured 2026-11-13),
    // not the browser's video recorder: headless Chrome's recorder drops the bottom ~88px of every frame.
    // Slowing the page down for more frames does not work: CDP's Animation.setPlaybackRate also slows the
    // requestAnimationFrame clock, and the camera never finishes its move.
    const ctx = await browser.newContext({ viewport: { width: w, height: h } });
    const tab = await ctx.newPage();
    const errors = [];
    tab.on("pageerror", e => errors.push(String(e)));
    await tab.goto(url);
    // Same recording mode as the page's own save button: controls hidden, step title as a subtitle.
    // speedOverride, not the <select>: a --speed value that is not one of its options would read as 0.
    await tab.evaluate(s => { speedOverride = s; setRecording(true); }, Number(speed));
    await tab.waitForTimeout(300);
    const frames = [];
    const shoot = async () => {
      const file = join(dir, `f${String(frames.length).padStart(6, "0")}.jpg`);
      await tab.screenshot({ path: file, type: "jpeg", quality: 90 });
      frames.push({ file, at: Date.now() });
    };
    const steps = await tab.evaluate(() => STEPS.length);
    const until = async (ms, cond) => { const end = Date.now() + ms; while (Date.now() < end && (await cond())) await shoot(); };
    await until(600, async () => true); // a moment on the start screen
    await tab.evaluate(() => startPlay());
    // Generous per-step budget: playback at "느리게" can take several seconds a step.
    await until(steps * 30000, () => tab.evaluate(() => playing));
    if (await tab.evaluate(() => playing)) errors.push("playback did not reach the last step in time");
    await until(1500, async () => true); // hold the last step
    await ctx.close();
    if (errors.length) { console.error("page errors during playback:\n" + errors.join("\n")); code = 1; }
    else {
      // Each frame lasts until the next one was taken, so uneven screenshot timing keeps real time.
      const list = frames.map((f, i) => `file '${f.file}'\nduration ${(((frames[i + 1] || f).at - f.at) / 1000 || 0.04).toFixed(4)}`);
      writeFileSync(join(dir, "list.txt"), list.join("\n") + `\nfile '${frames[frames.length - 1].file}'\n`);
      try {
        execFileSync("ffmpeg", ["-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", join(dir, "list.txt"),
          "-vf", "fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]);
        console.log(`recorded ${out} (${frames.length} frames)`);
      } catch (e) {
        console.error("ffmpeg is needed to join the frames and was not found or failed: " + e.message.split("\n")[0]);
        code = 4;
      }
    }
  }
} finally {
  await browser.close();
  rmSync(dir, { recursive: true, force: true });
}
process.exit(code);
