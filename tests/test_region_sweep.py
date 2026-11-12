import glob
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from typer.testing import CliRunner

from common import REPO_ROOT
from screening import region_sweep

runner = CliRunner()


def _write(df: pd.DataFrame, path: Path, meta: dict[str, str]) -> Path:
    t = pa.Table.from_pandas(df, preserve_index=False)
    md = dict(t.schema.metadata or {})
    md.update({k.encode(): v.encode() for k, v in meta.items()})
    pq.write_table(t.replace_schema_metadata(md), path)
    df.to_csv(path.with_suffix(".csv"), index=False)
    return path


def test_all_pilot_registers_validate() -> None:
    files = sorted(glob.glob(str(REPO_ROOT / "cities/ksa/regions/archive/pilot/pilot-*.parquet")))
    assert len(files) == 13
    res = runner.invoke(region_sweep.app, ["validate", *files])
    assert res.exit_code == 0, res.output


def test_header_count_mismatch_fails(fixtures: Path, tmp_path: Path) -> None:
    df = pd.read_parquet(fixtures / "region_register.parquet")
    n = df["governorate"].nunique()
    ok = _write(
        df, tmp_path / "ok.parquet", {"governorates_gastat": str(n), "governorates_listed": str(n)}
    )
    assert runner.invoke(region_sweep.app, ["validate", "--strict", str(ok)]).exit_code == 0
    bad = _write(
        df,
        tmp_path / "bad.parquet",
        {"governorates_gastat": str(n + 1), "governorates_listed": str(n)},
    )
    res = runner.invoke(region_sweep.app, ["validate", str(bad)])
    assert res.exit_code == 1 and "!=" in res.output
    loose = _write(df, tmp_path / "loose.parquet", {"governorates_gastat": "unverified"})
    assert runner.invoke(region_sweep.app, ["validate", str(loose)]).exit_code == 0
    assert runner.invoke(region_sweep.app, ["validate", "--strict", str(loose)]).exit_code == 1


def test_bad_role_fails(fixtures: Path, tmp_path: Path) -> None:
    df = pd.read_parquet(fixtures / "region_register.parquet")
    df.at[df.index[0], "economic_roles"] = [{"role": "spaceport", "source": "S-x"}]
    bad = _write(df, tmp_path / "role.parquet", {})
    res = runner.invoke(region_sweep.app, ["validate", str(bad)])
    assert res.exit_code == 1 and "row 0" in res.output
    df.at[df.index[0], "economic_roles"] = [{"role": "energy", "source": "S-x"}]
    good = _write(df, tmp_path / "energy.parquet", {})
    assert runner.invoke(region_sweep.app, ["validate", str(good)]).exit_code == 0
