"""A committed document may CITE an ignored file; it may not DEFER to one.

THE DEFECT. `_audit/2026-09-19-blocker-map-ruling-requests.md` told its reader
that the remaining empty blockers "are enumerated with their candidate counts
in `_audit/_scratch/_progress-unlocatable-recovery.md` section 47". That path
is gitignored -- `.gitignore` quarantines `_audit/_scratch/` precisely so
working notes cannot be swept into a commit, and
`tests/test_every_ignore_entry_is_declared.py` pins the entry -- so the
enumeration reaches no clone and no worktree. A standing verdict rested on a
file no reader could open, and the document gave no sign of it.

THE DISTINCTION THIS GUARD IS BUILT ON, because without it the guard is
unkeepable. MEASURED over the 150 tracked documents under `_audit/`: 60
paragraphs name a file under `_audit/_scratch/` and only ONE of them deferred
without saying the path was unreadable. So the repository already has the
convention -- `tests/test_readonly_boundary_invariant.py` writes "which is
gitignored, so THE EVIDENCE DOES NOT ..." -- and 59 of 60 paragraphs keep it.
A guard demanding a marker on every MENTION would have been red on thirty
documents the day it was written, and the `.gitignore` comment in this very
repository explains what happens to a rule its own repo violates: the next
person deletes it, taking the protection with it. So the scope is exactly the
paragraphs that send a reader somewhere they cannot go:

  CITATION  -- the claim is stated here and the ignored path is provenance.
               Allowed, unmarked. This is 59 of the 60.
  DEFERRAL  -- the claim is NOT stated here; the reader is told to go and
               read it. Allowed ONLY with an explicit unreadability marker,
               because otherwise the document is promising a source it cannot
               deliver.

SHOWN FAILING BEFORE IT WAS TRUSTED, on three real paragraphs rather than a
fixture: the pre-fix text of both referring documents, and a third instance
this guard FOUND -- `_audit/_census/network.md` deferring the enumeration of
24 unwalked pages to `_audit/_scratch/_census-hc-following.md`. That third one
is the argument for the guard existing at all: two waves had read the defect
report naming the first two, and nobody had asked whether there were others.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]

#: A reference to a SPECIFIC FILE under the quarantine directory. Naming the
#: DIRECTORY (the convention, "working notes live under `_audit/_scratch/`") is
#: not a reference to anything a reader could be sent to, and is not matched.
IGNORED_FILE = re.compile(r"_audit/_scratch/[A-Za-z0-9_.\-]+")

#: Phrases that hand the reader an errand. Deliberately literal: a guess at
#: "deferral" in general would be a sentiment classifier, and this has to be
#: arguable by whoever it fires on.
DEFERRAL_CUES = re.compile(
    r"(are enumerated|is enumerated|enumerated with|enumerated in"
    r"|see\s+`?_audit/_scratch|listed in|unchanged since|deferred to"
    r"|full list in|full detail in|the enumeration in|for the enumeration"
    r"|details? (?:are|is) in)",
    re.I,
)

#: Any one of these in the same paragraph discharges the duty. The wording is
#: not prescribed -- only that the paragraph SAYS the path does not ship.
UNREADABILITY_MARKERS = re.compile(
    r"(gitignor|not committed|reaches no clone|no clone|working notes"
    r"|does not ship|quarantin|in no worktree|does not exist in a worktree"
    r"|not on disk|provenance)",
    re.I,
)


def _tracked_audit_docs() -> list[pathlib.Path]:
    out = subprocess.run(
        ["git", "ls-files", "_audit/*.md", "_audit/**/*.md"],
        cwd=str(_ROOT), capture_output=True, check=True,
    ).stdout.decode("utf-8", errors="replace").split()
    return [_ROOT / rel for rel in out]


def offenders_in(text: str, label: str) -> list[str]:
    """Paragraphs of `text` that defer to an ignored path unmarked."""
    out: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        hit = IGNORED_FILE.search(para)
        if not hit:
            continue
        if not DEFERRAL_CUES.search(para):
            continue
        if UNREADABILITY_MARKERS.search(para):
            continue
        first = para.strip().splitlines()[0][:100]
        out.append(f"{label}: defers to {hit.group(0)} -- {first}")
    return out


def test_no_tracked_audit_document_defers_to_an_ignored_path():
    offenders: list[str] = []
    docs = _tracked_audit_docs()
    assert len(docs) > 100, (
        f"only {len(docs)} tracked documents found under _audit/; the listing "
        f"broke and this guard is certifying an almost-empty set."
    )
    for path in docs:
        offenders += offenders_in(
            path.read_text(encoding="utf-8", errors="replace"),
            path.relative_to(_ROOT).as_posix(),
        )
    assert offenders == [], (
        f"{len(offenders)} committed paragraph(s) send a reader to a file under "
        f"`_audit/_scratch/`, which `.gitignore` quarantines so it reaches no "
        f"clone and no worktree. A standing verdict must not rest on a file no "
        f"reader can open.\n"
        f"THE FIX IS ALMOST NEVER TO TRACK THE FILE: the quarantine is a ruling "
        f"with a dated rationale in `.gitignore` and a guard in "
        f"`tests/test_every_ignore_entry_is_declared.py`, and these notes are "
        f"live work logs that go stale in minutes -- the one behind this guard "
        f"was a 12:21 snapshot that a document had already been misled by at "
        f"12:40. State the value here, or point at an instrument that "
        f"recomputes it, and keep the path as provenance with a word that says "
        f"it does not ship.\n  " + "\n  ".join(offenders)
    )


# ------------------------------------------------------ the guard must fire

#: The EXACT pre-fix text of the three paragraphs this guard was built from,
#: kept verbatim. A guard that has only ever been run against a tree where it
#: passes has not been shown to fire at all -- and ten checks that could not
#: fire were found in this repository in two days.
REAL_PRE_FIX_PARAGRAPHS = {
    "blocker-map-ruling-requests.md, before 2026-09-19":
        "The remaining EMPTY blockers not listed above fail on the same three "
        "axes and\nare enumerated with their candidate counts in\n"
        "`_audit/_scratch/_progress-unlocatable-recovery.md` section 47. They "
        "are not\nraised individually because each is one or two rows and the "
        "answers would be\nguesses of the same kind.",
    "the-empty-blockers.md, before 2026-09-19":
        "* **`THREAD-REPLY-BOX` (2W), `POST-COMMENT-CONTROLS` (4).** Untouched "
        "this wave.\n  See `_audit/_scratch/_progress-unlocatable-recovery.md`; "
        "unchanged since section 47.",
    "network.md 9.2, before 2026-09-19":
        "| **24 linked-but-unwalked pages** in the following cluster | Link "
        "budget | Enumerated in `_audit/_scratch/_census-hc-following.md` |",
}


@pytest.mark.parametrize("label", sorted(REAL_PRE_FIX_PARAGRAPHS))
def test_the_guard_fires_on_the_text_it_was_built_from(label):
    found = offenders_in(REAL_PRE_FIX_PARAGRAPHS[label], label)
    assert len(found) == 1, (
        f"the guard no longer fires on {label}, which is the text it exists "
        f"to catch. It has been narrowed into a check that cannot fail."
    )


@pytest.mark.parametrize("para", [
    # A citation: the claim is here, the path is provenance. 59 of the 60
    # paragraphs measured in this repository look like this.
    "The refreeze attribution was measured by "
    "`_audit/_scratch/_probe_newsletter_refreeze_attribution.py`, which put the "
    "line at 41 and is reproduced in full below.",
    # A deferral that DOES discharge the duty.
    "The remaining rows are enumerated in "
    "`_audit/_scratch/_progress-unlocatable-recovery.md`, which is gitignored "
    "and reaches no clone -- named as provenance only.",
    # Naming the directory, not a file in it.
    "Working notes are quarantined under `_audit/_scratch/` and enter no commit.",
    # A deferral to a TRACKED path is not this guard's business.
    "The full list is enumerated in `_audit/_census/blocker-map.tsv`.",
])
def test_the_guard_does_not_fire_on_these(para):
    assert offenders_in(para, "fixture") == [], (
        "the guard flagged a paragraph that is not a deferral to an unreadable "
        "path. It is widening, and a guard that flags ordinary citations gets "
        "switched off -- which is worse than not having one."
    )
