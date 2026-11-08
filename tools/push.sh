#!/bin/bash
# Commit everything that is ready and push to pension-plan/score-scan-reader.
# Usage: tools/push.sh "<conventional commit subject>" ["<body>"] [path ...]
# With paths, only those paths (plus the status page, timeline, orchestration scripts
# and .gitignore) are committed, so one agent's push does not sweep in another agent's
# work in progress; other changes stay in the working tree (autostashed over the rebase).
# Without paths it refuses, unless PUSH_ALL=1 is set (commits the whole tree).
set -euo pipefail
ROOT=/Users/d.sloane/music
SCRATCH=/tmp/claude-501/-Users-d-sloane-music/69a237da-a02e-40d9-a1a9-90390e5b5eb2/scratchpad
cd "$ROOT"
# one push at a time: agents share this working tree, and two runs interleaving
# (one staging while another rebases) orphaned a commit once
exec 9>"$ROOT/.git/push.sh.lock"
if ! flock -w 900 9; then echo "refusing: another push.sh has held the lock for 15 minutes" >&2; exit 1; fi
SUBJECT="${1:-chore: sync}"; BODY="${2:-}"
shift $(( $# < 2 ? $# : 2 )); PATHS=("$@")
# keep test-only corpus items out (ATTRIBUTION mentions restricted permission)
sed -i '/^# -- restricted (auto) --$/q' .gitignore
grep -rl -i -E "used by permission|greentree" corpus --include=ATTRIBUTION.txt 2>/dev/null | xargs -r -n1 dirname | sort -u | sed 's#$#/#' >> .gitignore
grep -rl -i -E "used by permission|greentree" corpus --include='*.py' 2>/dev/null >/dev/null || true
# mirror docs, status page and orchestration scripts
cp "$SCRATCH/omr-build.html" docs/status/omr-build.html 2>/dev/null || true
python3 -I tools/timeline.py >/dev/null || echo 'timeline not written'
cp /Users/d.sloane/.claude/projects/-Users-d-sloane-music/69a237da-a02e-40d9-a1a9-90390e5b5eb2/workflows/scripts/*.js orchestration/ 2>/dev/null || true
if [ ${#PATHS[@]} -gt 0 ]; then
  git add -A -- "${PATHS[@]}" docs/status docs/TIMELINE.md orchestration .gitignore
elif [ "${PUSH_ALL:-}" = 1 ]; then
  git add -A
else
  # several agents share this working tree: a pathless push would sweep in their
  # uncommitted work (it happened in d176663), so name your files
  echo "refusing: name the paths to commit (tools/push.sh \"<subject>\" \"<body>\" <path> ...); PUSH_ALL=1 commits the whole tree" >&2
  exit 1
fi
# refuse oversize files and anything that looks like a credential
big=$(git diff --cached --name-only --diff-filter=AM -z | xargs -0 -r du -k 2>/dev/null | awk '$1>51200{print $2}' || true)
if [ -n "$big" ]; then echo "refusing: files over 50 MB staged:"; echo "$big"; exit 1; fi
if git diff --cached -U0 | grep -E '^\+' | grep -q -E 'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY'; then
  echo "refusing: staged content looks like a credential"; exit 1; fi
if git diff --cached --quiet; then echo "nothing to commit"; else
  # the whole working tree is committed (ship first), so list every source/UI/tool file in it:
  # commit titles describe the main change, this list shows everything that went in
  FILES=$(git diff --cached --name-status -- mvp/src mvp/ui mvp/tools tools .github | sed 's/^/  /')
  [ -n "$FILES" ] && BODY="$BODY

Code files in this commit:
$FILES"
  git commit -q -m "$SUBJECT" -m "$BODY" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
fi
CRED=(-c credential.helper= -c credential.helper='!f(){ echo username=x-access-token; echo "password=$(tr -d " \n\r" < ~/github-amiga-exposed.txt)"; }; f')
# release-please merges land on origin/main: rebase onto them before pushing
git "${CRED[@]}" fetch -q origin main
# untracked files that upstream also has (agents regenerate files while we push)
# would block the rebase: hold them aside, rebase, put them back
HOLD=$(mktemp -d)
git ls-tree -r --name-only origin/main | while read -r f; do
  if [ -e "$f" ] && ! git ls-files --error-unmatch "$f" >/dev/null 2>&1; then mkdir -p "$HOLD/$(dirname "$f")"; mv "$f" "$HOLD/$f"; fi
done
git -c rebase.autoStash=true rebase -q origin/main || { git rebase --abort 2>/dev/null; cp -a "$HOLD/." . ; echo "rebase failed"; exit 1; }
cp -a "$HOLD/." . 2>/dev/null; rm -rf "$HOLD"
git "${CRED[@]}" push -q origin HEAD:main
git log --oneline -1
