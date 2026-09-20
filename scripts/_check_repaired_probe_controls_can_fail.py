"""Receipt: the two probe controls repaired on 2026-09-20 CAN refuse.

WHY THIS EXISTS. ``_audit/2026-09-20-control-census.md`` found 129 probe
self-checks that are computed, printed and never branched on. Two of them sat
under a BANKED census row, and this wave made them gate:

  * ``scripts/_probe_membership_sections.py`` ``_analyse() -> silent`` -- a
    must-stay-silent control printed with the literal words PASS and FAIL and
    then read by nothing. The function could print FAIL and return True in the
    same run. It now produces the verdict alongside the census-agreement
    control. (``_audit/_census/network.md`` row 162.)
  * ``scripts/_probe_creator_content_analytics.py`` ``main() -> feed_hits`` --
    the vocabulary half of the /feed/ control, printed fifteen lines from the
    number it exists to be compared against, with nothing comparing them.
    (``_audit/_census/messaging-and-content.md`` row C40.)

A REPAIR ANNOUNCED IS NOT A REPAIR SHOWN. ``_audit/INSTRUMENTS.md`` admits an
instrument only once it has been SHOWN FAILING, and a control that comes back
the colour you expected is exactly the one nobody re-examines. So this script
makes each repaired control REFUSE on demand and prints the receipt.

TWO KINDS OF DEMONSTRATION, and they answer different doubts:

A. BEHAVIOURAL (membership only, because it is the offline probe). The real
   ``_analyse`` is imported and run over two synthetic captures built here,
   one injection apart: the clean one must return True, the one carrying a
   single impossible heading must return False. Same function, same inputs but
   for that injection, opposite verdicts. It is also run over the REAL capture
   when that gitignored file is present -- and says LOUDLY when it is not,
   because a worktree carries no gitignored file and a silent skip there would
   read as a pass.

B. MECHANICAL (both). ``detect_unbranched_probe_controls`` is run over the
   HEAD blob and over the working file. The variable must appear in
   ``findings`` at HEAD and in ``branched_controls`` now. Same file, two shas,
   opposite verdicts -- the shape the census's own calibration used, and the
   only receipt available for the creator-analytics repair, whose branch needs
   a live browser session to execute.

NOT CLAIMED. ``feed_hits``'s new branch is PROVISIONAL-UNSMOKED: it is proven
to be a real use of the value and proven reachable only by reading. What would
smoke it is one live run (``LINKEDIN_CDP_ATTACH=1``) in which the /feed/
control completes, printing the two vocabulary totals on one line.

Usage::

    ./venv/Scripts/python.exe scripts/_check_repaired_probe_controls_can_fail.py
"""
from __future__ import annotations

import io
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import detect_unbranched_probe_controls as detector  # noqa: E402

#: A minimal document carrying exactly what ``_analyse`` reads: group hrefs to
#: count, two headings to assign them under, and one aria-label. Every token is
#: written here; nothing is taken from a page.
CLEAN = (
    "<html><body>"
    "<h2>Section one</h2>"
    '<a href="/groups/aaa">x</a>'
    '<a href="/groups/bbb" aria-label="More">y</a>'
    "<h2>Section two</h2>"
    '<a href="/groups/ccc">z</a>'
    "</body></html>"
)

#: THE INJECTION, and it is one tag. ``IMPOSSIBLE_HEADING`` is ``<h9>`` -- a
#: level HTML does not have -- so on any real capture this control reads 0 by
#: construction. That is the honest limit of the needle and it is stated rather
#: than glossed: what this demonstration proves is that the WIRING now refuses,
#: not that the needle is strong.
BROKEN = CLEAN.replace("<h2>Section two</h2>", "<h9>ZZ</h9><h2>Section two</h2>")

ANCHOR_PATTERN = r'href="[^"]*/groups/([A-Za-z0-9\-_%.]+)'

RESULTS: list[tuple[bool, str]] = []


def record(ok: bool, text: str) -> None:
    RESULTS.append((ok, text))
    print("%-6s %s" % ("PASS" if ok else "FAIL", text))


def _run_analyse(html: str, tmp: Path, expected: int) -> bool:
    import _probe_membership_sections as probe  # noqa: PLC0415

    path = tmp / "_probe-synthetic.html"
    path.write_text(html, encoding="utf-8")
    buf = io.StringIO()
    with redirect_stdout(buf):
        verdict = probe._analyse("synthetic", path, ANCHOR_PATTERN, expected)
    return bool(verdict)


def demonstration_a(tmp: Path) -> None:
    print("\nA. BEHAVIOURAL -- the real _analyse over two synthetic captures,")
    print("   one impossible heading apart. Opposite verdicts required.")
    clean = _run_analyse(CLEAN, tmp, expected=3)
    record(clean is True,
           "A1: the clean capture returns True (3 anchors, no <h9>)")
    broken = _run_analyse(BROKEN, tmp, expected=3)
    record(broken is False,
           "A2: the SAME capture plus one <h9> returns False -- the "
           "must-stay-silent control now voids the tallies")
    record(clean != broken,
           "A3: the two verdicts differ, so _analyse reads the control "
           "rather than asserting an answer")

    print("\n   AND THE SAME CONTROL, DELIBERATELY MISSED, to show A2 is not")
    print("   an artefact of the anchor control firing instead:")
    wrong_count = _run_analyse(CLEAN, tmp, expected=99)
    record(wrong_count is False,
           "A4 control-for-the-control: a clean capture with the WRONG "
           "expected count also returns False, by the OTHER control")


def demonstration_a_live() -> None:
    print("\nA-LIVE. The real gitignored capture, if this checkout has one.")
    real = REPO / "_audit" / "_probe-groups-hyd.html"
    if not real.is_file():
        record(False,
               "A-LIVE: %s IS ABSENT. A worktree carries no gitignored file, "
               "so this demonstration did NOT run. Reported loudly rather "
               "than skipped: a silent skip here reads as a pass."
               % real.name)
        return
    import _probe_membership_sections as probe  # noqa: PLC0415

    buf = io.StringIO()
    with redirect_stdout(buf):
        verdict = probe._analyse("groups", real, probe.CAPTURES[0][2],
                                 probe.CAPTURES[0][3])
    text = buf.getvalue()
    record(verdict is True,
           "A-LIVE1: the real groups capture still returns True with the "
           "control now gating -- the banked reading survives")
    record("CONTROL must stay silent: 0 PASS" in text,
           "A-LIVE2: and it does so because the control read 0, not "
           "because nothing consulted it")


def demonstration_b() -> None:
    print("\nB. MECHANICAL -- same file, two shas, opposite verdicts.")
    for relpath, func, var in (
        ("scripts/_probe_membership_sections.py", "_analyse", "silent"),
        ("scripts/_probe_creator_content_analytics.py", "main", "feed_hits"),
    ):
        name = Path(relpath).name
        head = subprocess.run(
            ["git", "show", "HEAD:%s" % relpath],
            cwd=REPO, capture_output=True, text=True, check=False,
        )
        if head.returncode != 0:
            record(False, "B: could not read HEAD:%s" % relpath)
            continue
        before = detector.analyse_source(head.stdout, filename=name)
        after = detector.analyse_file(REPO / relpath)
        was_finding = any(f["function"] == func and f["variable"] == var
                          for f in before["findings"])
        now_branched = any(f["function"] == func and f["variable"] == var
                           for f in after["branched_controls"])
        now_finding = any(f["function"] == func and f["variable"] == var
                          for f in after["findings"])
        record(was_finding,
               "B: %s %s() -> %r is a FINDING at HEAD" % (name, func, var))
        record(now_branched and not now_finding,
               "B: %s %s() -> %r is CORRECTLY BRANCHED in the working tree"
               % (name, func, var))


def main() -> int:
    import tempfile  # noqa: PLC0415

    print("=" * 70)
    print("RECEIPT: the two repaired probe controls can refuse")
    print("=" * 70)
    with tempfile.TemporaryDirectory() as raw:
        demonstration_a(Path(raw))
    demonstration_a_live()
    demonstration_b()

    failed = [text for ok, text in RESULTS if not ok]
    print()
    if failed:
        print("NOT ALL DEMONSTRATIONS BEHAVED AS STATED -- %d of %d:"
              % (len(failed), len(RESULTS)))
        for text in failed:
            print("   %s" % text)
        return 1
    print("all %d demonstrations behaved as stated" % len(RESULTS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
