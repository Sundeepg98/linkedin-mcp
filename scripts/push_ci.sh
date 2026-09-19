#!/bin/sh
# Put the CURRENT tree on the free runners. One command, no history published.
#
# WHY THIS EXISTS. On 2026-09-19 this repository went 8.5 hours without a CI run
# while every gate was paid for on the build box -- 601s per suite, and a
# ~2-builder ceiling because a local gate serialises the fleet.
#
# WHAT THIS SCRIPT IS FOR, AND WHAT IT IS NOT. It publishes the CURRENT TREE as
# a PARENTLESS commit, so pushing it reveals no history. That is the right tool
# when a tree's history genuinely cannot be published -- measured on the same
# commit: 509 objects reachable from the orphan against 6014 from master.
#
# **IT IS NOT A WORKING CI TARGET FOR THIS SUITE, AND AN EARLIER VERSION OF THIS
# COMMENT CLAIMED IT WAS. THAT CLAIM WAS WRONG AND CI DISPROVED IT.** The census
# tests resolve a FROZEN BASELINE BY LITERAL COMMIT SHA -- build_blocker_map.py
# sets FROZEN_REF = 1c08e5f, test_connections_reader.py pins 84dccba -- and on a
# parentless commit those objects do not exist, so every shard ERRORS AT SETUP.
# Measured on run 35446775017: 18 of 18 pytest shards red, on the orphan branch
# this script pushes.
#
# HOW THE WRONG CLAIM WAS REACHED, because the method matters more than the
# claim: the two files that use git PLUMBING were run against a shallow clone,
# passed 27 tests in 19.42s, and that was taken as proof. The grep behind it
# searched rev-list|rev-parse|log|cat-file and CANNOT MATCH `git show
# <sha>:<path>`, which is the shape that actually breaks. A green result from a
# probe that cannot reach the defect looks exactly like a green result from a
# healthy system.
#
# SO: PREFER PUSHING REAL HISTORY, with .github/workflows/ci.yml's
# fetch-depth: 0. Reach for this script only when history cannot be published,
# and expect the frozen-SHA tests to need a skip-with-reason first.
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
