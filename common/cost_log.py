"""Cost log of Claude Code runs: `docs/cost-log.md` (table) and `docs/cost-log.csv` (same columns).

Figures are list-price `total_cost_usd` from the stream-json `result` event (subscription plan:
reference costs, not charges).

CLI:
  uv run python -m common.cost_log add <run>.jsonl --track r1b --label R1b --try 1 [--note ..]
      [--status-file .worktrees/r1b/docs/status/r1b.md]
  uv run python -m common.cost_log add-paid --vendor nabrah --model studio-tts --usd 4.20 \
      --step R10-voice-ab --approved-usd 60 [--note ..]
  uv run python -m common.cost_log fix-outcomes
  uv run python -m common.cost_log summary [--by track|label|model|day] [--md]
  uv run python -m common.cost_log check
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import typer

from common import REPO_ROOT

DEFAULT_MD = REPO_ROOT / "docs" / "cost-log.md"
DEFAULT_CSV = REPO_ROOT / "docs" / "cost-log.csv"
COLUMNS = [
    "date",
    "run_id",
    "track",
    "label",
    "models",
    "try",
    "duration_min",
    "turns",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "usd_list",
    "outcome",
    "notes",
]
EMPTY = "—"
PAID_LABEL = "PAID"
PAID_ALERT_SHARE = 0.8  # model policy rule 3 (CLAUDE.md): alert Tariq at 80 % of an approved amount
RATE_LIMIT = re.compile(r"rate.?limit|overloaded|usage limit|\b429\b", re.IGNORECASE)

app = typer.Typer(add_completion=False, help="Log Claude Code runs; summarise list-price cost.")


def read_events(path: Path) -> list[dict[str, Any]]:
    events = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def last_result(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    for ev in reversed(events):
        if ev.get("type") == "result":
            return ev
    return None


def _run_date(events: list[dict[str, Any]], path: Path) -> str:
    for ev in reversed(events):
        ts = ev.get("timestamp")
        if isinstance(ts, str) and len(ts) >= 10:
            return ts[:10]
    return dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.UTC).date().isoformat()


def _model_name(key: str, usage: dict[str, Any]) -> str:
    return usage.get("canonicalModel") or re.sub(r"\[.*\]$", "", key)


def parse_run(
    path: Path,
    track: str,
    label: str,
    try_n: int,
    note: str = "",
    status_file: Path | None = None,
) -> dict[str, str]:
    """Build one cost-log row from a stream-json file."""
    events = read_events(path)
    res = last_result(events)
    row = dict.fromkeys(COLUMNS, EMPTY)
    row.update(
        date=_run_date(events, path) if events else EMPTY,
        run_id=path.stem,
        track=track,
        label=label,
        **{"try": str(try_n)},
        notes=note,
    )
    if res is None:
        row["outcome"] = "failed"
        row["notes"] = "; ".join(x for x in (note, "no result event in the log") if x)
        return row
    mu: dict[str, dict[str, Any]] = res.get("modelUsage") or {}
    models = sorted({_model_name(k, v) for k, v in mu.items()})
    tok = defaultdict(int)
    for v in mu.values():
        tok["in"] += int(v.get("inputTokens", 0))
        tok["out"] += int(v.get("outputTokens", 0))
        tok["cr"] += int(v.get("cacheReadInputTokens", 0))
        tok["cw"] += int(v.get("cacheCreationInputTokens", 0))
    if not mu and isinstance(res.get("usage"), dict):
        u = res["usage"]
        tok.update(
            {
                "in": int(u.get("input_tokens", 0)),
                "out": int(u.get("output_tokens", 0)),
                "cr": int(u.get("cache_read_input_tokens", 0)),
                "cw": int(u.get("cache_creation_input_tokens", 0)),
            }
        )
    cost = res.get("total_cost_usd")
    dur = res.get("duration_ms")
    row.update(
        models="+".join(models) if models else EMPTY,
        duration_min=f"{dur / 60000:.1f}" if isinstance(dur, int | float) else EMPTY,
        turns=str(res.get("num_turns", EMPTY)),
        input_tokens=str(tok["in"]),
        output_tokens=str(tok["out"]),
        cache_read_tokens=str(tok["cr"]),
        cache_write_tokens=str(tok["cw"]),
        usd_list=f"{cost:.2f}" if isinstance(cost, int | float) else EMPTY,
        outcome=_outcome(res, label, status_file),
    )
    return row


def _outcome(res: dict[str, Any], label: str, status_file: Path | None) -> str:
    """Error result: failed/rate-limited; else done/blocked from the status line; else failed."""
    text = str(res.get("result") or "")
    if res.get("is_error"):
        return "rate-limited" if RATE_LIMIT.search(text) else "failed"
    status = status_file.read_text(encoding="utf-8") if status_file and status_file.exists() else ""
    for src in (text, status):
        m = status_line(label).search(src)
        if m:
            return m.group(1)
    if RATE_LIMIT.search(text) and res.get("subtype") != "success":
        return "rate-limited"
    return "failed"


def status_line(label: str) -> re.Pattern[str]:
    """`LABEL: done|blocked` at line start; backticks or bold tolerated (as in run_track.sh)."""
    return re.compile(rf"^[`*_ ]*{re.escape(label)}: (done|blocked)", re.MULTILINE)


def find_status_file(track: str, root: Path = REPO_ROOT) -> Path | None:
    """The track's status file: in its worktree first, then in the main checkout."""
    for p in (
        root / ".worktrees" / track / "docs" / "status" / f"{track}.md",
        root / "docs" / "status" / f"{track}.md",
    ):
        if p.exists():
            return p
    return None


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8")


def md_line(row: dict[str, str]) -> str:
    return "| " + " | ".join(str(row.get(c, "")).replace("|", "/") for c in COLUMNS) + " |"


def md_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines() if path.exists() else []:
        if not line.startswith("| ") or line.startswith("| date ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) == len(COLUMNS):
            rows.append(dict(zip(COLUMNS, cells, strict=True)))
    return rows


def is_placeholder(row: dict[str, str]) -> bool:
    """A row written for a run that ended without a result event (killed, crashed): no cost."""
    return row.get("usd_list", EMPTY) == EMPTY and row.get("outcome") == "failed"


def append_row(row: dict[str, str], md: Path, csv_path: Path) -> bool:
    """Append to both files; False if the run_id was already logged with a result (idempotent).

    A placeholder row for the same run_id (a killed try that left no result event) never blocks
    the measured row: it is replaced in place in both files and its note is kept.
    """
    rows = read_csv(csv_path)
    existing = [r for r in rows if r["run_id"] == row["run_id"]]
    in_md = [r for r in md_rows(md) if r["run_id"] == row["run_id"]]
    if existing or in_md:
        prior = existing[0] if existing else in_md[0]
        if not (is_placeholder(prior) and not is_placeholder(row)):
            return False
        kept = prior.get("notes", "")
        if kept and kept not in row["notes"]:
            extra = f"replaced placeholder ({kept})"
            row["notes"] = "; ".join(x for x in (row["notes"], extra) if x)
        rows = [row if r["run_id"] == row["run_id"] else r for r in rows]
        if not existing:
            rows.append(row)
        write_csv(rows, csv_path)
        if in_md:
            write_md_rows([row], md)
        else:
            text = md.read_text(encoding="utf-8") if md.exists() else ""
            if text and not text.endswith("\n"):
                text += "\n"
            md.write_text(text + md_line(row) + "\n", encoding="utf-8")
        return True
    rows.append(row)
    write_csv(rows, csv_path)
    text = md.read_text(encoding="utf-8") if md.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    md.write_text(text + md_line(row) + "\n", encoding="utf-8")
    return True


def _num(x: str) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def summarise(rows: list[dict[str, str]], by: str = "track") -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for r in rows:
        if by == "model":
            keys = [m.strip() for m in re.split(r"[+,]", r["models"]) if m.strip()]
        else:
            keys = [r.get("date" if by == "day" else by, "")]
        for k in keys:
            agg = out[k]
            agg["runs"] += 1
            agg["hours"] += _num(r["duration_min"]) / 60
            agg["usd"] += _num(r["usd_list"]) / len(keys)
            agg["tokens"] += sum(
                _num(r[c])
                for c in (
                    "input_tokens",
                    "output_tokens",
                    "cache_read_tokens",
                    "cache_write_tokens",
                )
            )
    return {k: dict(v) for k, v in out.items()}


@app.command()
def add(
    log: Path = typer.Argument(
        ..., help="stream-json log (logs/orch/<track>-<label>-try<n>.jsonl)"
    ),
    track: str = typer.Option(..., "--track"),
    label: str = typer.Option(..., "--label"),
    try_n: int = typer.Option(1, "--try"),
    note: str = typer.Option("", "--note"),
    md: Path = typer.Option(DEFAULT_MD, "--md-file"),
    csv_path: Path = typer.Option(DEFAULT_CSV, "--csv-file"),
    status_file: Path | None = typer.Option(
        None, "--status-file", help="default: .worktrees/<track>/docs/status/<track>.md, then docs/"
    ),
) -> None:
    """Parse the final result event and append one row to the Markdown and CSV logs."""
    status = status_file or find_status_file(track)
    row = parse_run(log, track, label, try_n, note, status)
    if append_row(row, md, csv_path):
        typer.echo(
            f"logged {row['run_id']}: USD {row['usd_list']} (list), {row['duration_min']} min"
        )
    else:
        typer.echo(f"{row['run_id']} already logged with a result; skipped")


def paid_total(rows: list[dict[str, str]], step: str) -> float:
    """Running list-price total of the paid-model rows logged for one approved step."""
    return sum(_num(r["usd_list"]) for r in rows if r["label"] == PAID_LABEL and r["track"] == step)


def paid_row(
    vendor: str, model: str, usd: float, step: str, approved_usd: float, note: str, now: dt.datetime
) -> dict[str, str]:
    row = dict.fromkeys(COLUMNS, EMPTY)
    notes = f"approved USD {approved_usd:g}" + (f"; {note}" if note else "")
    row.update(
        date=now.strftime("%Y-%m-%d"),
        run_id=f"paid-{vendor}-{now.strftime('%Y%m%d-%H%M')}",
        track=step,
        label=PAID_LABEL,
        models=f"{vendor}/{model}",
        usd_list=f"{usd:.2f}",
        outcome="paid",
        notes=notes,
    )
    return row


@app.command("add-paid")
def add_paid(
    vendor: str = typer.Option(..., "--vendor"),
    model: str = typer.Option(..., "--model"),
    usd: float = typer.Option(..., "--usd", help="list-price USD of this paid call or batch"),
    step: str = typer.Option(..., "--step", help="the approved step (paid-model request)"),
    approved_usd: float = typer.Option(..., "--approved-usd", help="Tariq's approved cap"),
    note: str = typer.Option("", "--note"),
    md: Path = typer.Option(DEFAULT_MD, "--md-file"),
    csv_path: Path = typer.Option(DEFAULT_CSV, "--csv-file"),
) -> None:
    """Log one paid model/API call (model policy rule 3) and warn at 80 % of the approved cap."""
    row = paid_row(vendor, model, usd, step, approved_usd, note, dt.datetime.now())
    base, n = row["run_id"], 1
    existing = {r["run_id"] for r in read_csv(csv_path)} | {r["run_id"] for r in md_rows(md)}
    while row["run_id"] in existing:  # several calls in the same minute stay separate rows
        n += 1
        row["run_id"] = f"{base}-{n}"
    append_row(row, md, csv_path)
    total = paid_total(read_csv(csv_path), step)
    typer.echo(
        f"logged {row['run_id']}: USD {row['usd_list']} (list); {step} total USD {total:.2f}"
    )
    if approved_usd > 0 and total >= PAID_ALERT_SHARE * approved_usd:
        pct = 100 * total / approved_usd
        typer.echo(f"ALERT: {step} at {pct:.0f} % of approved USD {approved_usd:g}")


def write_md_rows(rows: list[dict[str, str]], md: Path) -> None:
    """Rewrite the table rows of the Markdown log in place, keeping every other line."""
    by_id = {r["run_id"]: r for r in rows}
    out = []
    for line in md.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ") and not line.startswith("| date ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            if len(cells) == len(COLUMNS) and cells[1] in by_id:
                line = md_line(by_id[cells[1]])
        out.append(line)
    md.write_text("\n".join(out) + "\n", encoding="utf-8")


def recompute_outcomes(
    rows: list[dict[str, str]], logs: Path, root: Path = REPO_ROOT
) -> list[tuple[str, str, str]]:
    """Recompute `outcome` from each run's log and status file; return (run_id, old, new)."""
    changes = []
    for r in rows:
        log = logs / f"{r['run_id']}.jsonl"
        if not log.exists():
            continue  # manual rows (no stream-json log) keep their outcome
        res = last_result(read_events(log))
        status = find_status_file(r["track"], root)
        new = "failed" if res is None else _outcome(res, r["label"], status)
        if new != r["outcome"]:
            changes.append((r["run_id"], r["outcome"], new))
            r["outcome"] = new
    return changes


@app.command("fix-outcomes")
def fix_outcomes(
    md: Path = typer.Option(DEFAULT_MD, "--md-file"),
    csv_path: Path = typer.Option(DEFAULT_CSV, "--csv-file"),
    logs: Path = typer.Option(REPO_ROOT / "logs" / "orch", "--logs"),
    root: Path = typer.Option(REPO_ROOT, "--root", help="repository root holding .worktrees/"),
) -> None:
    """Recompute the outcome column of every logged run from the status files and is_error."""
    rows = read_csv(csv_path)
    changes = recompute_outcomes(rows, logs, root)
    write_csv(rows, csv_path)
    write_md_rows(rows, md)
    for run_id, old, new in changes:
        typer.echo(f"{run_id}: {old} -> {new}")
    typer.echo(f"{len(changes)} outcome(s) changed of {len(rows)} rows")


@app.command()
def summary(
    by: str = typer.Option("track", "--by", help="track | label | model | day"),
    as_md: bool = typer.Option(False, "--md"),
    csv_path: Path = typer.Option(DEFAULT_CSV, "--csv-file"),
) -> None:
    """Totals per group and overall: runs, agent-hours, list-price USD, tokens."""
    all_rows = read_csv(csv_path)
    paid = [r for r in all_rows if r["label"] == PAID_LABEL]
    rows = [r for r in all_rows if r["label"] != PAID_LABEL]
    groups = summarise(rows, by)
    total = summarise([{**r, "track": "all"} for r in rows], "track").get(
        "all", {"runs": 0, "hours": 0, "usd": 0, "tokens": 0}
    )
    lines = []
    if as_md:
        lines += [f"| {by} | runs | agent-hours | USD (list) | tokens |", "|---|---|---|---|---|"]
        fmt = "| {} | {:.0f} | {:.2f} | {:.2f} | {:.0f} |"
    else:
        fmt = "{:<24} runs {:>3.0f}  hours {:>7.2f}  USD {:>9.2f}  tokens {:>12.0f}"
    for k in sorted(groups):
        g = groups[k]
        lines.append(fmt.format(k, g["runs"], g["hours"], g["usd"], g["tokens"]))
    lines.append(fmt.format("TOTAL", total["runs"], total["hours"], total["usd"], total["tokens"]))
    if paid:  # paid models and APIs (model policy) are reported apart from Claude Code runs
        steps = sorted({r["track"] for r in paid})
        if as_md:
            lines += ["", "| paid step | calls | USD (list) |", "|---|---|---|"]
            pfmt = "| {} | {} | {:.2f} |"
        else:
            lines.append("PAID models and APIs (not Claude Code runs):")
            pfmt = "{:<24} calls {:>3}  USD {:>9.2f}"
        for s in steps:
            lines.append(pfmt.format(s, sum(r["track"] == s for r in paid), paid_total(paid, s)))
        lines.append(pfmt.format("PAID TOTAL", len(paid), sum(_num(r["usd_list"]) for r in paid)))
    typer.echo("\n".join(lines))


@app.command()
def check(
    md: Path = typer.Option(DEFAULT_MD, "--md-file"),
    csv_path: Path = typer.Option(DEFAULT_CSV, "--csv-file"),
    logs: Path = typer.Option(REPO_ROOT / "logs" / "orch", "--logs"),
) -> None:
    """The CSV and the Markdown table agree, and every log with a result event has a row."""
    a = {r["run_id"]: r for r in read_csv(csv_path)}
    b = {r["run_id"]: r for r in md_rows(md)}
    problems = [f"{k}: in one file only" for k in sorted(set(a) ^ set(b))]
    problems += [f"{k}: CSV and Markdown differ" for k in sorted(set(a) & set(b)) if a[k] != b[k]]
    for f in sorted(logs.glob("*.jsonl")) if logs.exists() else []:
        if f.stem not in a and last_result(read_events(f)) is not None:
            problems.append(f"{f.name}: result event but no row")
    for p in problems:
        typer.echo(f"FAIL {p}", err=True)
    if problems:
        raise typer.Exit(1)
    typer.echo(f"cost log OK: {len(a)} rows")


if __name__ == "__main__":
    app()
