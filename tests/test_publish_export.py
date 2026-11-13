"""FIX_PDF_CONNECTED (Tariq, 13 Nov 2026): scripts/publish_export.sh refresh mode.

The refresh mode updates the existing public repository with ONE new commit: same archive, drop
list, R2 redaction and residue check; .git untouched; identity per command; no network git.
"""

from __future__ import annotations

import re
import subprocess

from common import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts/publish_export.sh"


def test_script_parses() -> None:
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_refresh_mode_never_touches_remotes_or_config() -> None:
    code = "\n".join(
        ln for ln in SCRIPT.read_text().splitlines() if not ln.lstrip().startswith("#")
    )
    for verb in ("push", "fetch", "pull", "rebase", "reset", "remote", "tag"):
        assert not re.search(rf"\bgit\b[^\n]*\b{verb}\b", code), verb
    refresh = code[code.index("refresh base:") : code.index("git init -q -b main")]
    assert "git config" not in refresh and "git init" not in refresh
    assert "--exclude=/.git" in refresh and "rsync -a --delete" in refresh
    assert '--author "$PUBLIC_NAME <$PUBLIC_EMAIL>"' in refresh
    assert 'GIT_COMMITTER_EMAIL="$PUBLIC_EMAIL"' in refresh


def test_refresh_refuses_a_dirty_export() -> None:
    text = SCRIPT.read_text()
    assert "status --porcelain --ignored" in text and "refusing to refresh" in text
