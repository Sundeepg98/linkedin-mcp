"""THE RECEIPT for the 2026-09-20 repair of 22 branch-only cited SHAs.

This is a ONE-SHOT repair script, kept because it IS the record of what was
changed and how each cell was derived. It is idempotent: re-running it on an
already-repaired tree makes no edit and says so.

WHAT WAS WRONG. 22 distinct short SHAs across 29 citations in 19 tracked
`_audit/` documents named commits made on a `worktree-agent-*` branch that was
never merged into `master`. The citation was unresolvable from a clone the
moment it was written -- not history-rewrite wreckage, a live generator.

WHAT THE REPAIR IS, and why it is not "rewrite the hash". The dead hash is the
KEY A READER ARRIVES WITH: another document cross-references it, a transcript
carries it, a commit message quotes it. Deleting it strands that reader. So
each document keeps its hash and gains two things, in the corpus's own
established form (the 2026-09-03 repair of 24 SHAs, re-verified 22/22 clean by
the 2026-09-20 sixty-dangling wave):

  1. a SHA NOTE under the title, naming the branch-only hashes;
  2. a `## Dead hashes, recovered` table at the foot, mapping each to its
     `master` twin.

and, where the citation sits in this document's OWN prose, a marker at the
citation itself:

    at `c4d2be2` (branch-only; on `master` at `5073827`)

THE MARKER IS SELF-VERIFYING, and that is the point of its shape rather than a
coincidence of it. ``on `master` at `<live>``` puts the live hash into the
`at-backtick` slot that `check_cited_shas_resolve.py` already reads, so a
marker naming a hash that does not resolve is convicted by the EXISTING,
already-controlled matcher. A repair cannot be faked at a citation site.

FIVE CITATION SITES ARE DELIBERATELY NOT MARKED IN LINE, and the reason is the
same in every case: the line is not this document's own prose. Three sit inside
an indented verbatim transcript (`groups-admission.md` 413, 415, 425), one
inside a block the document itself labels as another wave's words left
byte-identical (`blocker-table-refresh.md` 268), and one inside a quoted record
banner (`the-first-sanctioned-press.md` 5). **Editing a transcript to improve
it falsifies it.** Those five are covered by the note and the table only, and
each document's note says so.

THE WORDING OF THE NOTE AVOIDS DISCLOSURE VOCABULARY ON PURPOSE. The guard's
`MARKED-DISCLOSED` suppressor fires on "does not resolve", "no clone can
reach", "nowhere on `master`" and kin within two lines of a token. If the note
used any of those, every repaired token would be covered TWICE -- by the
mapping table and by the note -- and a per-source mutation control could no
longer show the table doing the work. That is the "a union assertion over a
redundant corpus cannot detect a lost source" defect, written down by the wave
before this one. The note therefore says "reachable only from that branch and
never from `master`", which is true and matches no suppressor.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: dead -> live. EVERY PAIR WAS MEASURED, not inferred from ordering. Seven
#: checks per pair, all 22 clean, with four controls shown able to fail; the
#: table and the controls are in
#: `_audit/2026-09-20-the-evidence-that-resolves.md`.
TWINS: dict[str, str] = {
    "f6ddfe3": "8450abd",
    "ae1894b": "3c0b3e1",
    "c4d2be2": "5073827",
    "1349fe6": "81c8534",
    "a604394": "9e28aec",
    "7bca683": "29e4613",
    "c1991ac": "0aca3d0",
    "744a1f4": "f370443",
    "7668b40": "bd0cfad",
    "a5a988a": "4ac5b61",
    "12c20e1": "e72af67",
    "569dc5e": "09f9961",
    "d588034": "5952ace",
    "c48ec60": "a0379d5",
    "66e2038": "266d030",
    "806360a": "1b94540",
    "eed87a5": "097626a",
    "59192ac": "de2d4bf",
    "889f488": "1c84d34",
    "5c5ebf9dda43": "851bf80d5e8a",
    "70d7c0f62e97": "f66107c2c17b",
    "ded0048": "eb1b6e8",
}

#: Which tokens each document must map. `889f488` appears in
#: `the-last-five-reds.md` NOT as a citation of its own but INSIDE the subject
#: of `59192ac` -- *"audit(last-two): the gate at 889f488, ..."* -- so writing
#: that subject into a mapping table puts `889f488` into an `at-bare` slot and
#: MINTS A CITATION THIS DOCUMENT NEVER MADE. Measured before the table was
#: written, not discovered afterwards: a scan of all 22 subjects through the
#: guard's own `candidates()` found exactly this one, and a control row proved
#: the scan could see such a token. The honest handling is to map it too -- a
#: reader who meets `889f488` in that subject deserves its twin as much as any
#: other reader.
DOC_TOKENS: dict[str, list[str]] = {
    "_audit/2026-09-03-typeahead-name-matching-is-dead.md": ["f6ddfe3"],
    "_audit/2026-09-19-blocker-conflicts.md": ["c4d2be2", "ae1894b"],
    "_audit/2026-09-19-blocker-map-ruling-requests.md": ["a604394", "1349fe6"],
    "_audit/2026-09-19-blocker-table-refresh.md": ["7bca683"],
    "_audit/2026-09-19-events-surface.md": ["c1991ac"],
    "_audit/2026-09-19-groups-admission.md": ["744a1f4", "7668b40", "a5a988a"],
    "_audit/2026-09-19-premium-apply-surfaces.md": ["1349fe6"],
    "_audit/2026-09-19-routing-the-unassigned.md": ["12c20e1"],
    "_audit/2026-09-19-search-admission-preconditions.md": ["569dc5e", "d588034"],
    "_audit/2026-09-19-the-first-sanctioned-press.md": ["c48ec60"],
    "_audit/2026-09-19-the-gate-at-zero.md": ["66e2038", "eed87a5", "806360a"],
    "_audit/2026-09-19-the-last-five-reds.md": ["59192ac", "889f488"],
    "_audit/2026-09-19-the-last-two-reds.md": ["889f488"],
    "_audit/2026-09-19-the-three-ruling-requests-ruled.md": ["c1991ac"],
    "_audit/2026-09-19-the-unassigned-21.md": ["12c20e1"],
    "_audit/2026-09-19-tier1-fires.md": ["5c5ebf9dda43"],
    "_audit/2026-09-19-tier2-fires.md": ["70d7c0f62e97"],
    "_audit/2026-09-19-two-waves-agreed-on-nine-rows.md": ["12c20e1"],
    "_audit/2026-09-19-unblocking-the-stranded-commits.md": ["ded0048"],
}

#: (document, exact old text, exact new text). ONE marker per (document, token)
#: -- the first site in that document's own prose. The mapping table suppresses
#: every site of a mapped token document-wide, so a second marker would be
#: churn in another wave's file for no reader benefit.
#:
#: Each `old` must occur EXACTLY ONCE in its document or the edit is refused.
#: An anchor that matches twice is an anchor that can land in the wrong
#: sentence, and a silently misplaced marker is worse than no marker.
MARKERS: list[tuple[str, str, str]] = [
    (
        "_audit/2026-09-03-typeahead-name-matching-is-dead.md",
        "The full suite at `f6ddfe3` reported four failures.",
        "The full suite at `f6ddfe3` (branch-only; on `master` at `8450abd`)\nreported four failures.",
    ),
    (
        "_audit/2026-09-19-blocker-conflicts.md",
        "Applied at `c4d2be2`. Ratchet, counts and tests at the foot.",
        "Applied at `c4d2be2` (branch-only; on `master` at `5073827`). Ratchet,\ncounts and tests at the foot.",
    ),
    (
        "_audit/2026-09-19-blocker-conflicts.md",
        "### Seven more rows recovered, at `ae1894b`\n",
        "### Seven more rows recovered, at `ae1894b`\n\n*(`ae1894b` is branch-only; on `master` at `3c0b3e1`.)*\n",
    ),
    (
        "_audit/2026-09-19-blocker-map-ruling-requests.md",
        "**Now at 4 of 5** -- committed at `a604394`,",
        "**Now at 4 of 5** -- committed at `a604394`\n(branch-only; on `master` at `9e28aec`),",
    ),
    (
        "_audit/2026-09-19-blocker-map-ruling-requests.md",
        "`J 82` was filed to `PREMIUM-APPLY-SURFACES` at `1349fe6` on the strength of the",
        "`J 82` was filed to `PREMIUM-APPLY-SURFACES` at `1349fe6` (branch-only; on\n`master` at `81c8534`) on the strength of the",
    ),
    (
        "_audit/2026-09-19-events-surface.md",
        "the `N 181` line, committed `c1991ac`\n",
        "the `N 181` line, committed `c1991ac`\n(branch-only; on `master` at `0aca3d0`)\n",
    ),
    (
        "_audit/2026-09-19-premium-apply-surfaces.md",
        "filing was made at `1349fe6` and retracted at `0aca3d0`.",
        "filing was made at `1349fe6` (branch-only; on `master` at `81c8534`) and\nretracted at `0aca3d0`.",
    ),
    (
        "_audit/2026-09-19-routing-the-unassigned.md",
        "`M M35` and `M M49` were refused at `12c20e1` on the ruling's own sentences.",
        "`M M35` and `M M49` were refused at `12c20e1` (branch-only; on\n`master` at `e72af67`) on the ruling's own sentences.",
    ),
    (
        "_audit/2026-09-19-search-admission-preconditions.md",
        "The ruling at `569dc5e`, section 6 of",
        "The ruling at `569dc5e` (branch-only; on `master` at `09f9961`), section 6 of",
    ),
    (
        "_audit/2026-09-19-search-admission-preconditions.md",
        "`scripts/blast_radius.py` (commit `d588034`, subject",
        "`scripts/blast_radius.py` (commit `d588034`, branch-only; on\n`master` at `5952ace`; subject",
    ),
    (
        "_audit/2026-09-19-the-gate-at-zero.md",
        "**Taken on a detached worktree at `66e2038` -- single-writer by construction,",
        "**Taken on a detached worktree at `66e2038` (branch-only; on\n`master` at `266d030`) -- single-writer by construction,",
    ),
    (
        "_audit/2026-09-19-the-gate-at-zero.md",
        "**Measured on a detached worktree at `eed87a5` -- the commit that carries this",
        "**Measured on a detached worktree at `eed87a5` (branch-only; on\n`master` at `097626a`) -- the commit that carries this",
    ),
    (
        "_audit/2026-09-19-the-gate-at-zero.md",
        # THE MARKER MUST NOT COST THE DEAD TOKEN ITS SLOT. `806360a` is in the
        # `landed-after` slot, which requires ``  `HEX` land  `` adjacent ON ONE
        # LINE. A first version put the marker between them; the token then sat
        # in no slot at all and VANISHED from the guard rather than reading as
        # repaired -- measured, not reasoned about. A repaired citation and a
        # deleted one must not look the same either.
        "`806360a` landed at\n16:17:40 -- another writer, correcting two of its own rulings.",
        "`806360a` landed at\n16:17:40 (branch-only; on `master` at `1b94540`) -- another writer,\ncorrecting two of its own rulings.",
    ),
    (
        "_audit/2026-09-19-the-last-five-reds.md",
        "A neighbour committed `59192ac` between my",
        "A neighbour committed `59192ac` (branch-only; on\n`master` at `de2d4bf`) between my",
    ),
    (
        "_audit/2026-09-19-the-last-two-reds.md",
        "Measured on a **detached worktree at `889f488`**, not on the working tree.",
        "Measured on a **detached worktree at `889f488`** (branch-only; on\n`master` at `1c84d34`), not on the working tree.",
    ),
    (
        "_audit/2026-09-19-the-three-ruling-requests-ruled.md",
        "and the measurement at `c1991ac`.",
        "and the measurement at `c1991ac` (branch-only; on `master` at `0aca3d0`).",
    ),
    (
        "_audit/2026-09-19-the-unassigned-21.md",
        "**`J 81` stays UNASSIGNED. The ruling at `12c20e1` stands -- not honoured,",
        # THE MARKER IS ONE CANONICAL STRING, and it wraps only BEFORE
        # ``on `master` at `X` ``, never inside it. A first version wrapped
        # this one between ``master`` and ``at``; the citation was still
        # verified (the slot only needs ``at `X` `` on one line) but the
        # corpus then carried TWO spellings of a machine-read marker, and a
        # matcher that tolerates two spellings is a matcher that will one day
        # tolerate three and then miss one.
        "**`J 81` stays UNASSIGNED. The ruling at `12c20e1` (branch-only;\non `master` at `e72af67`) stands -- not honoured,",
    ),
    (
        "_audit/2026-09-19-tier1-fires.md",
        "checkout at `5c5ebf9dda43`.",
        "checkout at `5c5ebf9dda43`\n   (branch-only; on `master` at `851bf80d5e8a`).",
    ),
    (
        "_audit/2026-09-19-tier2-fires.md",
        "it landed on its own at `70d7c0f62e97`.",
        "it landed on its own at `70d7c0f62e97`\n  (branch-only; on `master` at `f66107c2c17b`).",
    ),
    (
        "_audit/2026-09-19-two-waves-agreed-on-nine-rows.md",
        "citing the ruling at `12c20e1` L68:",
        "citing the ruling at `12c20e1`\n  (branch-only; on `master` at `e72af67`) L68:",
    ),
    (
        "_audit/2026-09-19-unblocking-the-stranded-commits.md",
        "Both are byte-identical to what they were at `ded0048`.",
        "Both are byte-identical to what they were at `ded0048`\n  (branch-only; on `master` at `eb1b6e8`).",
    ),
]

#: Documents where NO citation site is this document's own prose, with the
#: reason stated per document. These get the note and the table only.
UNMARKED_REASON: dict[str, str] = {
    "_audit/2026-09-19-blocker-table-refresh.md":
        "The one citation site sits inside a block this document itself "
        "labels as another wave's words, left byte-identical and credited. "
        "It is not edited here.",
    "_audit/2026-09-19-groups-admission.md":
        "All three citation sites sit inside indented verbatim transcripts. "
        "Editing a transcript to improve it falsifies it, so they are left "
        "byte-identical.",
    "_audit/2026-09-19-the-first-sanctioned-press.md":
        "The one citation site sits inside the quoted record banner this "
        "document exists to preserve. It is left byte-identical.",
}

NOTE_MARK = "**SHA NOTE, added 2026-09-20.**"
TABLE_HEADING = "## Dead hashes, recovered"


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def subject(sha: str) -> str:
    out = git("log", "-1", "--format=%s", sha)
    if out.returncode != 0:
        raise SystemExit("cannot read subject of " + sha + ": " + out.stderr.strip())
    return out.stdout.rstrip("\n")


def _and_list(items: list[str]) -> str:
    quoted = ["`" + i + "`" for i in items]
    if len(quoted) == 1:
        return quoted[0]
    return ", ".join(quoted[:-1]) + " and " + quoted[-1]


def build_note(doc: str, tokens: list[str]) -> str:
    plural = "hash" if len(tokens) == 1 else "hashes"
    it = "it is" if len(tokens) == 1 else "each is"
    lines = [
        "> " + NOTE_MARK + " The short " + plural + " " + _and_list(tokens) + " cited",
        "> below " + ("was" if len(tokens) == 1 else "were") + " committed on a "
        "`worktree-agent-*` branch that never merged, so",
        "> " + ("it is" if len(tokens) == 1 else "they are")
        + " reachable only from that branch and never from `master`. **The work",
        "> itself landed.** Mapped to " + ("its" if len(tokens) == 1 else "their")
        + " `master` " + ("twin" if len(tokens) == 1 else "twins")
        + " -- identical subject, identical",
        "> author date, identical `git patch-id` -- under **\"Dead hashes, recovered\"**",
        "> at the foot of this file; " + it + " kept in place here because a short hash",
        "> is the key a reader arrives with.",
    ]
    reason = UNMARKED_REASON.get(doc)
    if reason:
        lines.append(">")
        lines.append("> " + reason)
    return "\n".join(lines) + "\n"


def build_table(tokens: list[str]) -> str:
    rows = [
        "| `" + t + "` | " + subject(t) + " | `" + TWINS[t] + "` | CONFIRMED |"
        for t in tokens
    ]
    return "\n".join([
        "",
        TABLE_HEADING,
        "",
        "Added 2026-09-20. The " + ("hash" if len(tokens) == 1 else "hashes")
        + " mapped here " + ("was" if len(tokens) == 1 else "were")
        + " made on a `worktree-agent-*` branch",
        "that never merged, so the citation was never checkable from a clone --"
        " NOT",
        "because history was rewritten, but because the branch carrying the commit"
        " was",
        "never published. **The underlying work did reach `master`**, re-applied"
        " under a",
        "new hash.",
        "",
        "Method, measured per pair rather than inferred from ordering: the live"
        " hash is",
        "an ancestor of `master` and the dead hash is not; both commits carry a",
        "byte-identical SUBJECT and a byte-identical author identity and date;",
        "`git patch-id --stable` returns the SAME id for both, so the CONTENT is",
        "identical and not merely the message; that subject occurs EXACTLY ONCE on",
        "`master`, so the key is unambiguous; and the dead hash prefixes exactly"
        " one",
        "object, so a reader typing it gets one answer. The four controls that show"
        " those",
        "checks can fail, and the whole 22-row table, are in",
        "`_audit/2026-09-20-the-evidence-that-resolves.md`.",
        "",
        "| dead hash | subject (the durable reference) | live hash | confidence |",
        "|---|---|---|---|",
        *rows,
        "",
    ])


def repair(apply: bool) -> int:
    changed, skipped = 0, 0
    problems: list[str] = []

    marker_by_doc: dict[str, list[tuple[str, str]]] = {}
    for doc, old, new in MARKERS:
        marker_by_doc.setdefault(doc, []).append((old, new))

    for doc in sorted(DOC_TOKENS):
        path = ROOT / doc
        if not path.exists():
            problems.append("MISSING: " + doc)
            continue
        blob = path.read_text(encoding="utf-8")
        original = blob
        tokens = DOC_TOKENS[doc]

        for old, new in marker_by_doc.get(doc, []):
            n = blob.count(old)
            if n == 0 and new.replace("\n", " ") not in blob.replace("\n", " "):
                problems.append("ANCHOR NOT FOUND in " + doc + ": " + repr(old[:60]))
                continue
            if n > 1:
                problems.append(
                    "ANCHOR AMBIGUOUS (" + str(n) + " hits) in " + doc + ": "
                    + repr(old[:60])
                )
                continue
            if n == 1:
                blob = blob.replace(old, new, 1)

        if NOTE_MARK not in blob:
            lines = blob.split("\n")
            if not lines or not lines[0].startswith("# "):
                problems.append("NO H1 TITLE in " + doc + ", refusing to place the note")
            else:
                note = build_note(doc, tokens)
                blob = lines[0] + "\n\n" + note + "\n" + "\n".join(lines[1:]).lstrip("\n")

        if TABLE_HEADING not in blob:
            blob = blob.rstrip("\n") + "\n" + build_table(tokens)

        if blob == original:
            skipped += 1
            print("  unchanged  " + doc)
            continue
        changed += 1
        print("  REPAIRED   " + doc + "  (" + ", ".join(tokens) + ")")
        if apply:
            path.write_text(blob, encoding="utf-8", newline="\n")

    print("")
    print("documents repaired : " + str(changed))
    print("documents unchanged: " + str(skipped))
    if problems:
        print("")
        print("PROBLEMS -- nothing written for these:")
        for p in problems:
            print("  " + p)
        return 1
    if changed == 0:
        print("NOTHING TO DO -- every document already carries its note and table.")
    return 0


def main(argv: list[str]) -> int:
    apply = "--write" in argv
    if not apply:
        print("DRY RUN (pass --write to apply)")
    missing = sorted(set(TWINS) - {t for ts in DOC_TOKENS.values() for t in ts})
    if missing:
        print("twins declared but mapped into no document: " + repr(missing))
        return 1
    return repair(apply)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
