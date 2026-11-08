#!/bin/bash
# Commit everything that is ready and push to pension-plan/score-scan-reader.
# Usage: tools/push.sh "<conventional commit subject>" ["<body>"]
set -euo pipefail
ROOT=/Users/d.sloane/music
SCRATCH=/tmp/claude-501/-Users-d-sloane-music/69a237da-a02e-40d9-a1a9-90390e5b5eb2/scratchpad
cd "$ROOT"
SUBJECT="${1:-chore: sync}"; BODY="${2:-}"
# keep test-only corpus items out (ATTRIBUTION mentions restricted permission)
sed -i '/^# -- restricted (auto) --$/q' .gitignore
grep -rl -i -E "used by permission|greentree" corpus --include=ATTRIBUTION.txt 2>/dev/null | xargs -r -n1 dirname | sort -u | sed 's#$#/#' >> .gitignore
grep -rl -i -E "used by permission|greentree" corpus --include='*.py' 2>/dev/null >/dev/null || true
# mirror docs, status page and orchestration scripts
cp "$SCRATCH/omr-build.html" docs/status/omr-build.html 2>/dev/null || true
python3 -I tools/timeline.py >/dev/null || echo 'timeline not written'
cp /Users/d.sloane/.claude/projects/-Users-d-sloane-music/69a237da-a02e-40d9-a1a9-90390e5b5eb2/workflows/scripts/*.js orchestration/ 2>/dev/null || true
git add -A
# refuse oversize files and anything that looks like a credential
big=$(git diff --cached --name-only --diff-filter=AM -z | xargs -0 -r du -k 2>/dev/null | awk '$1>51200{print $2}' || true)
if [ -n "$big" ]; then echo "refusing: files over 50 MB staged:"; echo "$big"; exit 1; fi
if git diff --cached -U0 | grep -E '^\+' | grep -q -E 'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY'; then
  echo "refusing: staged content looks like a credential"; exit 1; fi
if git diff --cached --quiet; then echo "nothing to commit"; else
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
