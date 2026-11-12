import shutil
from pathlib import Path

from typer.testing import CliRunner

from common import cost_log

runner = CliRunner()
HEADER = "| " + " | ".join(cost_log.COLUMNS) + " |\n|" + "---|" * len(cost_log.COLUMNS) + "\n"


def _copies(tmp_path: Path, fixtures: Path) -> tuple[Path, Path, Path]:
    log = tmp_path / "main-FIXTURE-try1.jsonl"
    shutil.copy(fixtures / "stream-json-sample.jsonl", log)
    md = tmp_path / "cost-log.md"
    md.write_text("# Cost log\n\n" + HEADER, encoding="utf-8")
    return log, md, tmp_path / "cost-log.csv"


def test_parse_result_event(tmp_path: Path, fixtures: Path) -> None:
    log, _, _ = _copies(tmp_path, fixtures)
    row = cost_log.parse_run(log, "main", "FIXTURE", 1)
    assert row["run_id"] == "main-FIXTURE-try1"
    assert row["date"] == "2026-10-30"
    assert row["models"] == "claude-haiku-5-5+claude-opus-5-5"
    assert row["usd_list"] == "12.35"
    assert row["duration_min"] == "30.0"
    assert row["turns"] == "42"
    assert row["input_tokens"] == "100"
    assert row["output_tokens"] == "4000"
    assert row["cache_read_tokens"] == "300000"
    assert row["cache_write_tokens"] == "2000"
    assert row["outcome"] == "done"


def test_add_is_idempotent_and_files_agree(tmp_path: Path, fixtures: Path) -> None:
    log, md, csv_path = _copies(tmp_path, fixtures)
    args = ["add", str(log), "--track", "main", "--label", "FIXTURE", "--try", "1"]
    args += ["--md-file", str(md), "--csv-file", str(csv_path)]
    assert runner.invoke(cost_log.app, args).exit_code == 0
    res = runner.invoke(cost_log.app, args)
    assert "already logged" in res.output
    assert len(cost_log.read_csv(csv_path)) == 1
    assert len(cost_log.md_rows(md)) == 1
    res = runner.invoke(
        cost_log.app,
        ["check", "--md-file", str(md), "--csv-file", str(csv_path), "--logs", str(tmp_path)],
    )
    assert res.exit_code == 0, res.output
    res = runner.invoke(cost_log.app, ["summary", "--csv-file", str(csv_path)])
    assert "TOTAL" in res.output and "12.35" in res.output


def test_missing_result_event_is_failed_row(tmp_path: Path) -> None:
    log = tmp_path / "x-R9-try1.jsonl"
    log.write_text('{"type":"system","subtype":"init"}\n', encoding="utf-8")
    row = cost_log.parse_run(log, "x", "R9", 1)
    assert row["outcome"] == "failed"
    assert row["usd_list"] == cost_log.EMPTY
    assert "no result event" in row["notes"]


def test_summary_by_model_splits_cost() -> None:
    rows = [dict.fromkeys(cost_log.COLUMNS, "0")]
    rows[0].update(models="a+b", usd_list="10", duration_min="60", track="t")
    s = cost_log.summarise(rows, "model")
    assert s["a"]["usd"] == 5 and s["b"]["usd"] == 5


def test_repo_cost_log_has_no_fixture_rows() -> None:
    """The real log holds only real runs (the tests write to temp copies)."""
    ids = [r["run_id"] for r in cost_log.md_rows(cost_log.DEFAULT_MD)]
    ids += [r["run_id"] for r in cost_log.read_csv(cost_log.DEFAULT_CSV)]
    assert not [i for i in ids if "FIXTURE" in i or "fixture" in i]


def _result(text: str = "Summary.", is_error: bool = False) -> dict:
    return {"type": "result", "subtype": "success", "is_error": is_error, "result": text}


def test_status_line_tolerates_backticks_and_bold(tmp_path: Path) -> None:
    for line in ("`R7: done`", "**R7: done**", "R7: blocked - reason"):
        st = tmp_path / "s.md"
        st.write_text(f"# status\n\n{line}\n", encoding="utf-8")
        assert cost_log._outcome(_result(), "R7", st) == line.strip("`*").split(":")[1].split()[0]
    st.write_text("- note: R7: done later\n", encoding="utf-8")
    assert cost_log._outcome(_result(), "R7", st) == "failed"


def test_error_result_is_failed_even_with_status_line(tmp_path: Path) -> None:
    st = tmp_path / "s.md"
    st.write_text("R7: done\n", encoding="utf-8")
    assert cost_log._outcome(_result("boom", is_error=True), "R7", st) == "failed"
    assert cost_log._outcome(_result("usage limit hit", is_error=True), "R7", st) == "rate-limited"


def test_status_file_prefers_worktree(tmp_path: Path) -> None:
    main = tmp_path / "docs" / "status" / "r1b.md"
    wt = tmp_path / ".worktrees" / "r1b" / "docs" / "status" / "r1b.md"
    main.parent.mkdir(parents=True)
    main.write_text("old\n", encoding="utf-8")
    assert cost_log.find_status_file("r1b", tmp_path) == main
    wt.parent.mkdir(parents=True)
    wt.write_text("R1b: done\n", encoding="utf-8")
    assert cost_log.find_status_file("r1b", tmp_path) == wt
    assert cost_log.find_status_file("nope", tmp_path) is None


def test_fix_outcomes_rewrites_both_files(tmp_path: Path, fixtures: Path) -> None:
    log, md, csv_path = _copies(tmp_path, fixtures)
    logs = tmp_path / "logs"
    logs.mkdir()
    shutil.move(log, logs / log.name)
    log = logs / log.name
    st = tmp_path / ".worktrees" / "main" / "docs" / "status" / "main.md"
    st.parent.mkdir(parents=True)
    st.write_text("`FIXTURE: blocked - waiting`\n", encoding="utf-8")
    row = cost_log.parse_run(log, "main", "FIXTURE", 1)
    row["outcome"] = "failed"
    cost_log.append_row(row, md, csv_path)
    # the fixture's own result text says "FIXTURE: done", which wins over the status file
    args = ["fix-outcomes", "--md-file", str(md), "--csv-file", str(csv_path)]
    res = runner.invoke(cost_log.app, [*args, "--logs", str(logs), "--root", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert "failed -> done" in res.output
    assert cost_log.read_csv(csv_path)[0]["outcome"] == "done"
    assert cost_log.md_rows(md)[0]["outcome"] == "done"
    res = runner.invoke(
        cost_log.app,
        ["check", "--md-file", str(md), "--csv-file", str(csv_path), "--logs", str(logs)],
    )
    assert res.exit_code == 0, res.output


def test_add_accepts_status_file(tmp_path: Path, fixtures: Path) -> None:
    log, md, csv_path = _copies(tmp_path, fixtures)
    text = log.read_text(encoding="utf-8").replace("FIXTURE: done", "no status")
    log.write_text(text, encoding="utf-8")
    st = tmp_path / "elsewhere.md"
    st.write_text("**FIXTURE: blocked - x**\n", encoding="utf-8")
    args = ["add", str(log), "--track", "zz", "--label", "FIXTURE", "--status-file", str(st)]
    res = runner.invoke(cost_log.app, [*args, "--md-file", str(md), "--csv-file", str(csv_path)])
    assert res.exit_code == 0, res.output
    assert cost_log.read_csv(csv_path)[0]["outcome"] == "blocked"


def test_add_paid_logs_rows_and_alerts_at_80_percent(tmp_path: Path) -> None:
    md, csv_path = tmp_path / "cost-log.md", tmp_path / "cost-log.csv"
    md.write_text("| date | run_id |\n|---|---|\n")
    args = ["add-paid", "--vendor", "fixturevendor", "--model", "fixture-tts", "--step", "S-fix"]
    files = ["--approved-usd", "10", "--md-file", str(md), "--csv-file", str(csv_path)]
    res = runner.invoke(cost_log.app, [*args, "--usd", "5", *files])
    assert res.exit_code == 0, res.output
    assert "ALERT" not in res.output
    res = runner.invoke(cost_log.app, [*args, "--usd", "3.5", "--note", "take 2", *files])
    assert res.exit_code == 0, res.output
    assert "ALERT: S-fix at 85 % of approved USD 10" in res.output
    rows = cost_log.read_csv(csv_path)
    assert len(rows) == 2 and len({r["run_id"] for r in rows}) == 2
    assert all(r["run_id"].startswith("paid-fixturevendor-") for r in rows)
    assert {r["label"] for r in rows} == {"PAID"} and {r["outcome"] for r in rows} == {"paid"}
    assert rows[0]["models"] == "fixturevendor/fixture-tts" and rows[1]["track"] == "S-fix"
    assert rows[1]["notes"] == "approved USD 10; take 2"
    assert cost_log.paid_total(rows, "S-fix") == 8.5
    assert {r["run_id"] for r in cost_log.md_rows(md)} == {r["run_id"] for r in rows}


def test_summary_reports_paid_apart_from_claude_runs(tmp_path: Path, fixtures: Path) -> None:
    md, csv_path = tmp_path / "cost-log.md", tmp_path / "cost-log.csv"
    md.write_text("| date | run_id |\n|---|---|\n")
    shutil.copy(fixtures / "stream-json-sample.jsonl", tmp_path / "run.jsonl")
    files = ["--md-file", str(md), "--csv-file", str(csv_path)]
    add = ["add", str(tmp_path / "run.jsonl"), "--track", "fixture", "--label", "FIX", *files]
    assert runner.invoke(cost_log.app, add).exit_code == 0
    claude_usd = cost_log.read_csv(csv_path)[0]["usd_list"]
    paid = ["add-paid", "--vendor", "fv", "--model", "m", "--usd", "2", "--step", "S-fix"]
    assert runner.invoke(cost_log.app, [*paid, "--approved-usd", "60", *files]).exit_code == 0
    res = runner.invoke(cost_log.app, ["summary", "--csv-file", str(csv_path)])
    assert res.exit_code == 0, res.output
    total_line = next(line for line in res.output.splitlines() if line.startswith("TOTAL"))
    assert "runs   1" in total_line and f"{float(claude_usd):.2f}" in total_line
    assert "PAID models and APIs" in res.output and "PAID TOTAL" in res.output
    res = runner.invoke(cost_log.app, ["summary", "--md", "--csv-file", str(csv_path)])
    assert "| S-fix | 1 | 2.00 |" in res.output


def test_placeholder_row_never_blocks_the_measured_row(tmp_path: Path, fixtures: Path) -> None:
    """A killed try leaves a no-result row; the restarted run's measured row must replace it."""
    log, md, csv_path = _copies(tmp_path, fixtures)
    md.write_text(HEADER, encoding="utf-8")
    # same run_id (same file name), but written before the run had a result event
    empty = tmp_path / "empty.jsonl"
    empty.write_text('{"type":"system","subtype":"init"}\n', encoding="utf-8")
    placeholder = cost_log.parse_run(empty, "main", "FIXTURE", 1, note="killed by the coordinator")
    placeholder["run_id"] = "main-FIXTURE-try1"
    assert cost_log.is_placeholder(placeholder)
    assert cost_log.append_row(placeholder, md, csv_path) is True
    args = ["add", str(log), "--track", "main", "--label", "FIXTURE", "--try", "1"]
    args += ["--md-file", str(md), "--csv-file", str(csv_path)]
    res = runner.invoke(cost_log.app, args)
    assert res.exit_code == 0 and "logged main-FIXTURE-try1: USD 12.35" in res.output
    rows = cost_log.read_csv(csv_path)
    assert len(rows) == 1 and rows[0]["usd_list"] == "12.35" and rows[0]["outcome"] != "failed"
    assert "replaced placeholder" in rows[0]["notes"]
    assert "killed by the coordinator" in rows[0]["notes"]
    assert len(cost_log.md_rows(md)) == 1 and cost_log.md_rows(md)[0]["usd_list"] == "12.35"
    # a measured row is still idempotent
    assert "already logged" in runner.invoke(cost_log.app, args).output
    assert len(cost_log.read_csv(csv_path)) == 1
