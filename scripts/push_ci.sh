#!/bin/sh
# Put the CURRENT tree on the free runners. One command, no history published.
#
# WHY THIS EXISTS. On 2026-09-19 this repository went 8.5 hours without a single
# CI run while every gate was paid for on the build box -- 601s per suite, and a
# ~2-builder ceiling because a local gate serialises the fleet. The reason was
# not policy. It was a FALSE PREMISE nobody re-tested: "history-dependent tests
# cannot resolve SHAs on an orphan branch, so CI there is broken."
#
# THAT PREMISE WAS MEASURED AND IT IS FALSE. A shallow single-branch clone --
# 1 commit, .git/shallow present, 1024 commits of history absent -- runs
# tests/test_build_echo.py and tests/test_stale_process_is_announced.py at
# 27 passed in 19.42s. Nothing in this suite needs ancestry.
#
# SO THE ORPHAN BRANCH IS A WORKING CI TARGET, and it is the SAFE one: a
# parentless commit reaches no earlier object, so pushing it publishes no
# history. Measured on the same commit: 509 objects reachable from the orphan
# against 6014 from master.
set -e
BRANCH="${1:-ci-offload}"
SRC="${2:-HEAD}"
ROOT=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
cd "$ROOT"

# The gate that actually matters before anything leaves this machine.
./venv/Scripts/python.exe scripts/sweep_tracked_for_identity.py || {
  echo "push_ci: identity sweep REFUSED. Nothing pushed." >&2; exit 1; }

TREE=$(git rev-parse "$SRC^{tree}")
C=$(git commit-tree "$TREE" -m "ci: $(git log -1 --format=%s "$SRC")

Parentless commit carrying the tree of $SRC. No ancestry, so no history is
published by pushing it. Built by scripts/push_ci.sh.")

# ASSERT the safety property rather than trusting it.
n=$(git rev-list --count "$C")
[ "$n" = "1" ] || { echo "push_ci: orphan reaches $n commits, expected 1. REFUSING." >&2; exit 1; }

git branch -f "$BRANCH" "$C"
git push -f origin "$BRANCH"
echo "push_ci: $BRANCH -> $C  (1 commit, $(git rev-list --objects "$C" | wc -l) objects)"
gh run list --branch "$BRANCH" --limit 1 2>/dev/null || true
