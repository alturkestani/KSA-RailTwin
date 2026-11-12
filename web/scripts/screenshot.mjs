// Headless capture of the dashboard views (puppeteer-core + the installed Google Chrome).
// Adapted from TrafficTwin Jeddah web/scripts/lib.mjs (Apache-2.0; see NOTICE).
//
//   RT_WEB_URL=http://127.0.0.1:8765 node scripts/screenshot.mjs [shot ...]
//
// Env: RT_WEB_URL (default http://127.0.0.1:8765, i.e. `make dashboard`), CHROME_PATH,
// RT_SHOT_DIR (default ../docs/report/figures), RT_BASEMAP=none for the plain background.
// The motion-graphics track can reuse it with its own SHOTS list.
import { mkdirSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const here = dirname(fileURLToPath(import.meta.url));
const CHROME = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const BASE = process.env.RT_WEB_URL || "http://127.0.0.1:8765";
const OUT = resolve(process.env.RT_SHOT_DIR || resolve(here, "../../docs/report/figures"));
const BASEMAP = process.env.RT_BASEMAP === "none" ? "&basemap=none" : "";
const MAX_BYTES = 1.5 * 1024 * 1024;

export const SHOTS = {
  "dashboard-map": "view=map&scenario=S6-L2",
  "dashboard-register": "view=register&scenario=S6-L2",
  "dashboard-ranges": "view=ranges&scenario=S6-L1",
  "dashboard-pareto": "view=pareto&scenario=S6-L2",
  "dashboard-difference": "view=difference&scenario=S6-L1",
};

async function waitReady(page, timeout = 90000) {
  try {
    await page.waitForFunction(() => window.__rt && window.__rt.ready(), { timeout, polling: 250 });
  } catch {
    const st = await page.evaluate(() => window.__rt?.state());
    throw new Error(`dashboard not ready after ${timeout} ms: ${JSON.stringify(st)}`);
  }
  await new Promise((r) => setTimeout(r, 2500)); // tiles and fonts settle
  await page.waitForFunction(() => window.__rt.ready(), { timeout, polling: 250 });
}

const names = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(SHOTS);
mkdirSync(OUT, { recursive: true });
const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: false, // headless mode chosen by the flag below
  args: ["--headless=new", "--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist", "--enable-webgl", "--hide-scrollbars", "--window-size=1600,1000"],
  defaultViewport: { width: 1600, height: 1000, deviceScaleFactor: 1 },
});
let failed = 0;
try {
  for (const name of names) {
    const q = SHOTS[name];
    if (!q) throw new Error(`unknown shot ${name}; known: ${Object.keys(SHOTS).join(", ")}`);
    const page = await browser.newPage();
    page.on("pageerror", (e) => console.error(`[${name}] page error: ${e.message}`));
    await page.goto(`${BASE}/?${q}${BASEMAP}`, { waitUntil: "domcontentloaded" });
    await waitReady(page);
    const file = resolve(OUT, `${name}.png`);
    await page.screenshot({ path: file, type: "png" });
    const bytes = statSync(file).size;
    const ok = bytes < MAX_BYTES;
    if (!ok) failed += 1;
    console.log(`${ok ? "ok " : "BIG"} ${file} ${(bytes / 1024).toFixed(0)} KiB`);
    await page.close();
  }
} finally {
  await browser.close();
}
process.exit(failed ? 1 : 0);
