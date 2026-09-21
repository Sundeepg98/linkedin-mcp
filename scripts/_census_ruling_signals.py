"""Census ruling-related signals across the tracked _audit/ markdown corpus.

Closed-form extraction script. Reads a repo-relative file list (the tracked
audit corpus), applies 14 named regex signals line-by-line to each file, and
writes a strict-ASCII markdown report with four sections:

  1. SUMMARY TABLE       - per-signal distinct-file / hit-line / fenced counts
  2. OVERLAP              - per-signal overlap with S01_ruled_colon, plus the
                            any-signal / no-signal file counts
  3. PER-SIGNAL HITS      - every hit line, one row each, pipe-delimited
  4. FILES BY SIGNAL COUNT - files ranked by how many distinct signals they hit

This script performs no adjudication of what counts as a "ruling" -- it only
measures where the given signal patterns occur, verbatim as specified.

Run from the repository root::

    venv/Scripts/python.exe scripts/_census_ruling_signals.py [OUTPUT.md]

**EVERY PATH IS DERIVED, NONE IS LITERAL.** The first version hard-coded the
absolute worktree path and two absolute scratchpad paths. An absolute
workspace path is an identifier in this repository and may not enter a tracked
file, and it would also have made the script runnable on exactly one box.
The corpus now comes from `git ls-files`, which is the same domain
`build_audit_index.tracked_documents` uses and the only one that is the same
in a clone.
"""
import re
import subprocess
import sys
from pathlib import Path
from collections import OrderedDict, defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "_audit" / "_scratch" / "ruling-signals.md"


def tracked_corpus():
    """Every git-tracked `_audit/*.md`, repo-relative, sorted.

    Asks git rather than walking the disk: `_audit/_scratch/` is gitignored
    and a check whose verdict depends on which tree it runs in is not
    measuring the repository.
    """
    proc = subprocess.run(["git", "ls-files", "--", "_audit"],
                          cwd=str(REPO_ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("git ls-files failed: %s" % proc.stderr.strip())
    return sorted({line.strip() for line in proc.stdout.splitlines()
                   if line.strip().endswith(".md")})

# Signals, named exactly as specified by the lead. Order is preserved
# throughout (dict is insertion-ordered) so every section lists signals in
# this same S01..S14 order.
SIGNALS = OrderedDict(
    [
        ("S01_ruled_colon", re.compile(r"RULED:")),
        (
            "S02_heading_ruling",
            re.compile(r"^#{1,6} .*\b(RULED|RULING|Ruled|Ruling|ruled|ruling|RULINGS|rulings)\b"),
        ),
        ("S03_bold_start_ruling", re.compile(r"^\*\*.*\b(RULED|RULING|RULINGS)\b")),
        ("S04_the_ruling", re.compile(r"\bTHE RULING\b")),
        (
            "S05_needs_a_ruling",
            re.compile(
                r"(?i)\b(needs? a ruling|ruling needed|ruling request|needs an? (operator )?answer"
                r"|awaiting a ruling|wants a ruling)\b"
            ),
        ),
        (
            "S06_named_ruling_id",
            re.compile(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+-RULING\b|\bRULING-[A-Z0-9-]+\b"),
        ),
        ("S07_excluded_ruled", re.compile(r"\bEXCLUDED-RULED\b")),
        ("S08_standing_ruling", re.compile(r"(?i)\bstanding ruling\b")),
        (
            "S09_lead_or_operator_rule",
            re.compile(
                r"(?i)\b(the lead ruled|lead's ruling|the operator ruled|operator's ruling"
                r"|on the team lead's ruling|the lead has ruled|I ruled|I rule that)\b"
            ),
        ),
        ("S10_bare_ruled", re.compile(r"(?i)\bruled\b")),
        (
            "S11_decision_marker",
            re.compile(r"^\*\*.*\b(DECIDED|DECISION)\b|^#{1,6} .*\b(DECIDED|DECISION|DECIDES)\b"),
        ),
        ("S12_ruling_is", re.compile(r"(?i)\bthe ruling (is|was|says|stands|holds)\b")),
        (
            "S13_this_is_not_a_ruling",
            re.compile(r"(?i)\b(is not a ruling|not a ruling|no ruling|nobody ruled|never ruled|unruled)\b"),
        ),
        ("S14_register_R_id", re.compile(r"\bR(?:[1-9]|1[0-9])\b")),
    ]
)

# Volume exception applies only to these three signals.
SUPPRESS_SIGNALS = {"S07_excluded_ruled", "S10_bare_ruled", "S14_register_R_id"}
SUPPRESS_THRESHOLD = 300

ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
FENCE_PREFIX = "```"


def to_ascii(s):
    """Replace every non-ASCII char with '?'. Length-preserving per char."""
    return s.encode("ascii", "replace").decode("ascii")


def strip_heading_text(text):
    # Strip an optional closing ATX sequence, e.g. "## Foo ##" -> "Foo".
    return re.sub(r"\s+#+\s*$", "", text)


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    rel_paths = tracked_corpus()
    if not rel_paths:
        print("FATAL: git tracks no _audit/*.md -- wrong tree?",
              file=sys.stderr)
        sys.exit(1)

    # Surprise check up front: report ALL missing files in one shot, then
    # stop rather than silently excluding them from the census.
    missing = [rel for rel in rel_paths if not (REPO_ROOT / rel).exists()]
    if missing:
        print(
            f"FATAL: {len(missing)} of {len(rel_paths)} corpus files not found on disk "
            f"under {REPO_ROOT}:",
            file=sys.stderr,
        )
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)

    # hits[signal_name] = ordered list of hit dicts
    hits = {name: [] for name in SIGNALS}
    # file -> signal -> hit count (for OVERLAP + FILES BY SIGNAL COUNT)
    file_signal_hits = defaultdict(lambda: defaultdict(int))

    for rel in rel_paths:
        abs_path = REPO_ROOT / rel
        try:
            content = abs_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            print(f"FATAL: could not read {rel}: {exc}", file=sys.stderr)
            sys.exit(1)

        lines = content.splitlines()
        in_fence = False
        current_heading = None

        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()

            # --- fence tracking ---
            if stripped.startswith(FENCE_PREFIX):
                # The delimiter line itself counts as NOT inside the fence;
                # it toggles the state for the lines that follow.
                line_is_fenced = False
                in_fence = not in_fence
            else:
                line_is_fenced = in_fence

            # --- nearest-preceding-ATX-heading tracking ---
            m = ATX_HEADING_RE.match(line)
            if m:
                current_heading = strip_heading_text(m.group(2))

            # --- signal matching ---
            for name, pattern in SIGNALS.items():
                if pattern.search(line):
                    hits[name].append(
                        {
                            "path": rel,
                            "lineno": lineno,
                            "fenced": line_is_fenced,
                            "heading": current_heading,
                            "text": stripped,
                        }
                    )
                    file_signal_hits[rel][name] += 1

    # ---------------- build report ----------------
    out = []

    # Section 1: SUMMARY TABLE
    out.append("## SUMMARY TABLE")
    out.append("")
    out.append("| signal | distinct files | total hit lines | hits inside fence |")
    out.append("|---|---|---|---|")
    summary_rows = []
    for name in SIGNALS:
        hs = hits[name]
        distinct_files = len(set(h["path"] for h in hs))
        total = len(hs)
        fenced_count = sum(1 for h in hs if h["fenced"])
        summary_rows.append((name, distinct_files, total, fenced_count))
        out.append(f"| {name} | {distinct_files} | {total} | {fenced_count} |")
    out.append("")

    # Section 2: OVERLAP
    out.append("## OVERLAP")
    out.append("")
    s01_files = set(h["path"] for h in hits["S01_ruled_colon"])
    out.append("Per-signal overlap with S01_ruled_colon (what the `RULED:` grep alone misses):")
    out.append("")
    out.append("| signal | files also hit by S01_ruled_colon | total files for signal |")
    out.append("|---|---|---|")
    for name in SIGNALS:
        files_for_signal = set(h["path"] for h in hits[name])
        overlap_n = len(files_for_signal & s01_files)
        out.append(f"| {name} | {overlap_n} | {len(files_for_signal)} |")
    out.append("")

    any_signal_files = set()
    for name in SIGNALS:
        any_signal_files |= set(h["path"] for h in hits[name])
    all_files = set(rel_paths)
    no_signal_files = sorted(all_files - any_signal_files)

    out.append(f"Files hit by ANY signal: {len(any_signal_files)}")
    out.append(f"Files hit by NO signal: {len(no_signal_files)}")
    out.append("")
    out.append("No-signal files:")
    if no_signal_files:
        for f in no_signal_files:
            out.append(f"- {f}")
    else:
        out.append("(none)")
    out.append("")

    # Section 3: PER-SIGNAL HITS
    out.append("## PER-SIGNAL HITS")
    out.append("")
    for name in SIGNALS:
        hs = hits[name]
        out.append(f"### {name} ({len(hs)} hits)")
        out.append("")
        limit = SUPPRESS_THRESHOLD if (name in SUPPRESS_SIGNALS and len(hs) > SUPPRESS_THRESHOLD) else None
        shown = hs[:limit] if limit else hs
        for h in shown:
            fenced_str = "yes" if h["fenced"] else "no"
            heading = h["heading"] if h["heading"] else "(none)"
            heading = to_ascii(heading)[:100]
            text = to_ascii(h["text"])[:220]
            out.append(f"{name} | {h['path']} | {h['lineno']} | fenced={fenced_str} | {heading} | {text}")
        if limit and len(hs) > limit:
            out.append(f"... {len(hs) - limit} more hits suppressed for this signal")
        out.append("")

    # Section 4: FILES BY SIGNAL COUNT
    out.append("## FILES BY SIGNAL COUNT")
    out.append("")
    out.append("| file | distinct signals | total hits |")
    out.append("|---|---|---|")
    file_rows = []
    for f, sig_counts in file_signal_hits.items():
        distinct = len(sig_counts)
        total = sum(sig_counts.values())
        file_rows.append((f, distinct, total))
    file_rows.sort(key=lambda r: (-r[1], -r[2], r[0]))
    for f, distinct, total in file_rows:
        out.append(f"| {f} | {distinct} | {total} |")
    out.append("")

    output_text = to_ascii("\n".join(out))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output_text, encoding="ascii")

    # Print the summary table (+ overlap) to stdout so the lead sees it directly.
    print("## SUMMARY TABLE")
    print()
    print("| signal | distinct files | total hit lines | hits inside fence |")
    print("|---|---|---|---|")
    for name, distinct_files, total, fenced_count in summary_rows:
        print(f"| {name} | {distinct_files} | {total} | {fenced_count} |")
    print()
    print(f"Corpus files censused: {len(rel_paths)}")
    print(f"Files hit by ANY signal: {len(any_signal_files)}")
    print(f"Files hit by NO signal: {len(no_signal_files)}")
    print()
    print(f"Deliverable written to: {out_path}")


if __name__ == "__main__":
    main()
