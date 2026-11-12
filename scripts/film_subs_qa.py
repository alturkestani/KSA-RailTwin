"""Subtitle RTL/bidi QA for the R10 film (half 2): screenshots in two players plus a measured probe.

  uv run python scripts/film_subs_qa.py            (needs the four MP4s and film/subs/*.vtt)

1. For each cut and language, three cues are picked from the VTT (the first cue, the first with a
   digit, and in Arabic the first with Latin letters, else the next cue with a digit). A 6 s clip
   of the delivered MP4 around the cue and a one-cue VTT (the cue text copied byte for byte,
   times shifted) are served from a local-only HTTP server (127.0.0.1) and shown in an HTML5
   <video> with a <track> in two players, both headless: Google Chrome (Blink, driven by
   puppeteer-core, which waits until the track has an active cue) and Firefox (Gecko).
   Screenshots: film/subs/qa/<cut>-<lang>-<cue>-<player>.png (1280x720).
2. Every Arabic cue is laid out right-to-left in an HTML page and measured with
   common.ar_render bidi-probe (numeric runs in logical order, never split across lines);
   results in film/subs/qa/bidi-<cut>-ar.json. Nothing leaves the machine.
"""

from __future__ import annotations

import http.server
import json
import re
import subprocess
import sys
import threading
import time
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBS = ROOT / "film/subs"
QA = SUBS / "qa"
OUT = ROOT / "film/renders/out"
WORK = ROOT / "film/renders/_subsqa"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FIREFOX = "/Applications/Firefox.app/Contents/MacOS/firefox"
PORT = 8793
TS = re.compile(r"(\d+):(\d\d):(\d\d)\.(\d{3}) --> (\d+):(\d\d):(\d\d)\.(\d{3})")


def secs(h, m, s, ms) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def vtt_cues(path: Path) -> list[tuple[float, float, list[str]]]:
    out = []
    blocks = path.read_text(encoding="utf-8").split("\n\n")
    for b in blocks:
        lines = b.strip().split("\n")
        for i, ln in enumerate(lines):
            m = TS.match(ln)
            if m:
                g = m.groups()
                out.append((secs(*g[:4]), secs(*g[4:]), lines[i + 1 :]))
                break
    return out


def pick(cues, lang: str) -> list[int]:
    idx = [0]
    digit = next((i for i, c in enumerate(cues) if re.search(r"\d", " ".join(c[2]))), None)
    if digit is not None:
        idx.append(digit)
    if lang == "ar":
        lat = next((i for i, c in enumerate(cues) if re.search(r"[A-Za-z]", " ".join(c[2]))), None)
        if lat is None:
            lat = next(
                (
                    i
                    for i, c in enumerate(cues)
                    if i not in idx and re.search(r"\d", " ".join(c[2]))
                ),
                None,
            )
        if lat is not None:
            idx.append(lat)
    else:
        nxt = next(
            (i for i, c in enumerate(cues) if i not in idx and re.search(r"\d", " ".join(c[2]))),
            None,
        )
        if nxt is not None:
            idx.append(nxt)
    return list(dict.fromkeys(idx))


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a) -> None:  # quiet
        pass

    def do_GET(self) -> None:
        if self.path.startswith("/slow"):
            time.sleep(5)  # holds Firefox's load event until the video has seeked
            self.send_response(200)
            self.send_header("Content-Type", "image/gif")
            self.end_headers()
            self.wfile.write(b"GIF89a\x01\x00\x01\x00\x00\x00\x00;")
            return
        super().do_GET()


def main_checkout() -> Path:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return Path(out).parent


def shoot(url: str, png: Path, player: str) -> None:
    if player == "chrome":
        # puppeteer-core from the dashboard's node_modules (main checkout): waits for an active cue
        pptr = main_checkout() / "web/node_modules/puppeteer-core"
        cmd = [
            "node",
            str(ROOT / "scripts/film_subs_qa_chrome.mjs"),
            str(pptr),
            CHROME,
            url,
            str(png),
        ]
    else:
        cmd = [FIREFOX, "--headless", "--window-size=1280,720", "--screenshot", str(png), url]
    subprocess.run(cmd, capture_output=True, timeout=180, check=False)


def main() -> int:
    QA.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    srv = http.server.ThreadingHTTPServer(
        ("127.0.0.1", PORT), partial(Handler, directory=str(WORK))
    )
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    report = []
    try:
        for cut in ("main", "trailer"):
            for lang in ("ar", "en"):
                mp4 = OUT / f"ksa-rail-twin-{cut}-{lang}.mp4"
                cues = vtt_cues(SUBS / f"{cut}.{lang}.vtt")
                for i in pick(cues, lang):
                    s, e, text = cues[i]
                    tag = f"{cut}-{lang}-cue{i + 1:03d}"
                    t0 = s  # clip starts at the cue: the local server has no Range support
                    clip = WORK / f"{tag}.mp4"
                    subprocess.run(
                        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t0:.3f}"]
                        + ["-i", str(mp4), "-t", "6", "-an", "-vf", "scale=1280:720"]
                        + ["-c:v", "libx264", "-preset", "veryfast", str(clip)],
                        check=True,
                    )
                    a, b = s - t0, min(e - t0, 6.0)
                    vtt = WORK / f"{tag}.vtt"
                    vtt.write_text(
                        "WEBVTT\n\n"
                        + f"00:00:{a:06.3f} --> 00:00:{b:06.3f}\n"
                        + "\n".join(text)
                        + "\n",
                        encoding="utf-8",
                    )
                    page = WORK / f"{tag}.html"
                    page.write_text(
                        '<!doctype html><html><body style="margin:0;background:#000">'
                        f'<video id="v" src="{clip.name}" width="1280" height="720" muted '
                        f'preload="auto"><track kind="subtitles" srclang="{lang}" '
                        f'src="{vtt.name}" default></video><img src="/slow.gif" width="1" '
                        'height="1"><script>const v=document.getElementById("v");'
                        f"const go=()=>{{v.currentTime={a + 0.5:.2f};}};"
                        'if(v.readyState>=1){go();}else{v.addEventListener("loadedmetadata",go);}'
                        'v.textTracks[0].mode="showing";</script></body></html>',
                        encoding="utf-8",
                    )
                    url = f"http://127.0.0.1:{PORT}/{page.name}"
                    for player in ("chrome", "firefox"):
                        png = QA / f"{tag}-{player}.png"
                        shoot(url, png, player)
                        report.append(
                            {
                                "file": png.name,
                                "cue": i + 1,
                                "player": player,
                                "exists": png.exists(),
                            }
                        )
                        print(png.name, png.exists(), flush=True)
    finally:
        srv.shutdown()
    # measured bidi probe of every Arabic cue
    for cut in ("main", "trailer"):
        cues = vtt_cues(SUBS / f"{cut}.ar.vtt")
        md = WORK / f"bidi-{cut}-ar.md"
        md.write_text(
            "\n\n".join(" ".join(ln.replace("‏", "") for ln in c[2]) for c in cues) + "\n",
            encoding="utf-8",
        )
        html_path = WORK / f"bidi-{cut}-ar.html"
        subprocess.run(
            ["uv", "run", "python", "-m", "common.ar_render", "html", str(md), str(html_path)],
            check=True,
            cwd=ROOT,
        )
        res = subprocess.run(
            ["uv", "run", "python", "-m", "common.ar_render", "bidi-probe", str(html_path)]
            + ["--json", str(QA / f"bidi-{cut}-ar.json")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        tail = (res.stdout.strip().splitlines() or [""])[-1]
        report.append({"file": f"bidi-{cut}-ar.json", "exit": res.returncode, "summary": tail})
        print(f"bidi-probe {cut}-ar exit {res.returncode}: {tail}", flush=True)
    (QA / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
