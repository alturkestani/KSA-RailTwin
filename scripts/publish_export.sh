#!/usr/bin/env bash
# Build the public export (docs/publish/checklist.md §7 Option B, §10): a NEW standalone
# repository with one squashed commit of a reviewed tree. Never adds a remote, never pushes,
# never tags. The private repository is only read (git archive).
#
#   SRC=~/Documents/Projects/KSA-RailTwin EXPORT=~/Documents/Projects/KSA-RailTwin-public \
#   PUBLIC_NAME="Tariq Alturkestani" PUBLIC_EMAIL=alturkestani@users.noreply.github.com \
#   LOG=logs/publish-export ./scripts/publish_export.sh [COMMIT]
#
# The private names are NOT in this script or any tracked file. They live in the gitignored
# list PRIVATE_NAMES (default $SRC/.publish/private-names.txt, mode 600): one term per line,
# optional TAB + replacement (default "[private name]"), lines starting with # are comments.
# Matching is case-insensitive and substring-wide; a space in a term also matches "-", "_" or
# nothing. The script refuses to run without the list.
#
# Steps: archive COMMIT (default: main) -> drop docs/publish/export-exclude.txt -> redaction R2
# on text files only (binaries are never edited; a binary that contains a term stops the build)
# -> residue check over text, PDF text and xlsx/docx XML (must print nothing) -> git init -> one
# commit under the public identity -> git grep of the commit -> gitleaks.
set -euo pipefail

SRC=${SRC:?set SRC to the private repository}
EXPORT=${EXPORT:?set EXPORT to a folder that does not exist}
PUBLIC_NAME=${PUBLIC_NAME:?set PUBLIC_NAME}
PUBLIC_EMAIL=${PUBLIC_EMAIL:?set PUBLIC_EMAIL}
PRIVATE_NAMES=${PRIVATE_NAMES:-$SRC/.publish/private-names.txt}
LOG=${LOG:-$(mktemp -d)}
COMMIT=$(git -C "$SRC" rev-parse "${1:-main}")
SHORT=$(git -C "$SRC" rev-parse --short "$COMMIT")

test -s "$PRIVATE_NAMES" || { echo "private-name list missing: $PRIVATE_NAMES" >&2; exit 1; }
test ! -e "$EXPORT" || { echo "$EXPORT exists; choose another folder" >&2; exit 1; }
PRIVATE_NAMES=$(cd "$(dirname "$PRIVATE_NAMES")" && pwd)/$(basename "$PRIVATE_NAMES")
mkdir -p "$LOG"
LOG=$(cd "$LOG" && pwd)
# One ERE alternation of every term (regex metacharacters escaped; space -> [ _-]?).
NAMES=$(grep -v '^#' "$PRIVATE_NAMES" | sed '/^$/d' | cut -f1 \
  | sed -e 's/[][\.*^$+?(){}|/]/\\&/g' -e 's/ /[ _-]?/g' | paste -sd'|' -)
NAMES="($NAMES)"
echo "terms in the private list: $(grep -v '^#' "$PRIVATE_NAMES" | sed '/^$/d' | wc -l | tr -d ' ')" > "$LOG/summary.txt"

mkdir -p "$EXPORT"
git -C "$SRC" archive --format=tar "$COMMIT" | tar -x -C "$EXPORT"
cd "$EXPORT"
echo "source commit: $COMMIT" >> "$LOG/summary.txt"
echo "files after archive: $(find . -type f | wc -l | tr -d ' ')" >> "$LOG/summary.txt"

# 1. Drop list (the files stay on the private main).
grep -v '^#' docs/publish/export-exclude.txt | sed '/^$/d' | while read -r f; do
  rm -v -- "$f"
done > "$LOG/dropped.txt"
echo "files after drop list: $(find . -type f | wc -l | tr -d ' ')" >> "$LOG/summary.txt"

# 2. Redaction R2: text files only (grep -I skips binaries); a binary match stops the build.
grep -rlaiE "$NAMES" . | sort > "$LOG/all-matching.txt" || true
grep -rlIiE "$NAMES" . | sort > "$LOG/redacted-files.txt" || true
comm -23 "$LOG/all-matching.txt" "$LOG/redacted-files.txt" > "$LOG/skipped-binary.txt"
if [ -s "$LOG/skipped-binary.txt" ]; then
  echo "binary files contain a private term (see $LOG/skipped-binary.txt)" >&2; exit 1
fi
grep -rnoIiE "$NAMES" . | wc -l | tr -d ' ' > "$LOG/matches-before.txt" || true
while read -r f; do
  PRIVATE_NAMES="$PRIVATE_NAMES" perl -pi -e '
    BEGIN {
      open(my $fh, "<", $ENV{PRIVATE_NAMES}) or die;
      while (<$fh>) { chomp; next if /^#/ || /^\s*$/; my ($t, $r) = split /\t/, $_, 2;
        my $p = join("[ _-]?", map { quotemeta } split / /, $t);
        push @R, [qr/$p/i, defined $r ? $r : "[private name]"]; }
    }
    for my $r (@R) { s/$r->[0]/$r->[1]/g }' "$f"
done < "$LOG/redacted-files.txt"
echo "redacted files: $(wc -l < "$LOG/redacted-files.txt" | tr -d ' '); matches: $(cat "$LOG/matches-before.txt"); binary files with a term: 0" >> "$LOG/summary.txt"

# 3. Residue check: must print nothing. Text files, then the text inside PDFs and xlsx/docx/pptx.
{ grep -rnIiE "$NAMES|/Users/[a-z]|/home/[a-z]|[A-Za-z0-9._%+-]@(nabrah|dscan)\.ai" . || true
  find . -name '*.pdf' -print0 | while IFS= read -r -d '' f; do
    if command -v pdftotext >/dev/null; then
      pdftotext -q "$f" - 2>/dev/null | grep -qiE "$NAMES" && echo "PDF text: $f"; fi; true; done
  find . \( -name '*.xlsx' -o -name '*.docx' -o -name '*.pptx' \) -print0 | while IFS= read -r -d '' f; do
    unzip -p "$f" 2>/dev/null | grep -aqiE "$NAMES" && echo "zip XML: $f"; true; done
} | head > "$LOG/residue.txt"
if [ -s "$LOG/residue.txt" ]; then cat "$LOG/residue.txt" >&2; echo "residue found" >&2; exit 1; fi

# 4. One squashed commit under the public identity; no remote, no tag.
git init -q -b main
git config user.name "$PUBLIC_NAME"
git config user.email "$PUBLIC_EMAIL"
git add -A
GIT_AUTHOR_DATE="2026-11-12T12:00:00+03:00" GIT_COMMITTER_DATE="2026-11-12T12:00:00+03:00" \
  git commit -q -m "KSA Rail Twin 1.0.0: public release (squashed from private main $SHORT)"
echo "export commit: $(git rev-parse HEAD)" >> "$LOG/summary.txt"
echo "files in the commit: $(git ls-files | wc -l | tr -d ' ')" >> "$LOG/summary.txt"
if git grep -I -i -c -E "$NAMES" HEAD > "$LOG/git-grep.txt"; then
  echo "private term in the commit" >&2; exit 1; fi
echo "git grep of the commit for the private list: 0 matches" >> "$LOG/summary.txt"

# 5. Secret scan of the export's history (expect: no leaks found).
if command -v gitleaks >/dev/null; then
  gitleaks git --no-banner --redact=100 -c .gitleaks.toml . 2>&1 | tail -3 | tee "$LOG/gitleaks.txt"
fi
cat "$LOG/summary.txt"
