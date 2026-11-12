// Chrome (Blink) screenshot of a WebVTT cue over a video, for scripts/film_subs_qa.py.
// node scripts/film_subs_qa_chrome.mjs <puppeteer-core dir> <chrome path> <url> <png>
// Waits until the video has seeked and the track has an active cue, then captures 1280x720.
import { createRequire } from "node:module";
const [pptrDir, chrome, url, png] = process.argv.slice(2);
const require = createRequire(pptrDir + "/package.json");
const puppeteer = require(pptrDir);
const browser = await puppeteer.launch({ executablePath: chrome, headless: true, args: ["--autoplay-policy=no-user-gesture-required"] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });
  await page.goto(url, { waitUntil: "load", timeout: 60000 });
  await page.waitForFunction(() => {
    const v = document.getElementById("v");
    const tr = v && v.textTracks[0];
    return v && v.readyState >= 2 && !v.seeking && tr && tr.activeCues && tr.activeCues.length > 0;
  }, { timeout: 30000, polling: 200 });
  await new Promise((r) => setTimeout(r, 500));
  await page.screenshot({ path: png });
  console.log("ok", png);
} finally {
  await browser.close();
}
