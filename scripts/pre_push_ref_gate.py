"""Refuse to push any ref but ``master``, because publishing is the one thing
this repository cannot take back.

WHY THIS EXISTS, and it is a measured hazard rather than a precaution.

This checkout carries 59 local branches. Ten of them are NOT ancestors of
master, and one class of them is kept deliberately: ``integrate-1821`` is the
only ref under which 22 cited SHAs resolve, and
``_audit/2026-09-20-the-six-unremapped.md`` rules it *"KEEP, do not delete, do
not push"*. Those branches carry blobs that ``scripts/purge_denied_term.py``
removed from the history that master publishes.

**Until this file existed, that protection was a sentence in an audit file.**
``git push --all`` and ``git push --mirror`` would have published every one of
them, and the repository is PUBLIC. A force-push does not undo that: retained
objects stay resolvable by SHA, and the only remedy measured to work was
delete-and-recreate, which cost this account a sibling repo's entire pull
request history once.

WHAT IT REFUSES, AND WHAT THAT IS WORTH. It refuses on the REMOTE ref, which
is the thing that becomes public -- ``git push origin HEAD:refs/heads/x`` is
caught where a check on the local ref would not be. It refuses deletes too,
naming them as deletes: removing a published ref is deliberate work and should
not ride in on a wildcard.

WHAT IT IS NOT. Not a purity check on the branch's CONTENT. A ref that passes
here has not been swept; it has only been named. The sweeps are
``sweep_tracked_for_identity.py`` (the working tree) and
``sweep_blobs_for_identity.py`` (a commit range), and this gate does not
duplicate either -- it stops the accident, not the decision.

MEASURED 2026-09-21, so the threat model is stated rather than assumed:
``origin`` already serves 13 refs besides master, of which ``ci-offload`` is an
ORPHAN commit with no parent, holding 498 blobs master does not have. It was
swept and reads PASS on all 218 spellings. So the accident has already
happened once, harmlessly, before anything stopped it.

AN EMPTY STDIN IS NOT A PASS. Git always feeds this hook at least one line for
a push that would transfer anything. Reading none means the hook was invoked in
a way this script does not understand, and saying "allowed" to that is how a
gate becomes decoration. It says so and allows, loudly, rather than pretending
it checked.

THE OVERRIDE IS DELIBERATE AND NAMED. Set ``LINKEDIN_MCP_ALLOW_ANY_REF=1`` for
one command when a non-master push is genuinely wanted. Accidents do not set
environment variables; that is the entire security model here and it is stated
rather than implied.

Install with ``scripts/install_git_hooks.py``. Run by hand:

    git push --dry-run --all 2>/dev/null   # then read what this would have said
"""

from __future__ import annotations

import os
import sys

ALLOWED_REMOTE_REFS = frozenset({"refs/heads/master"})

OVERRIDE_ENV = "LINKEDIN_MCP_ALLOW_ANY_REF"

ZERO = "0" * 40


def verdicts(lines: list[str]) -> list[tuple[str, str, str]]:
    """(verdict, remote_ref, why) for each pre-push stdin line.

    Git's format is ``<local ref> <local sha> <remote ref> <remote sha>``. A
    line this cannot parse is REFUSED rather than skipped -- an unparsed line
    is an unknown push, and the whole point of the file is to not guess.
    """
    out: list[tuple[str, str, str]] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 4:
            out.append(("REFUSE", line, "unparsed line -- not 4 fields"))
            continue
        local_ref, local_sha, remote_ref, _remote_sha = parts
        if remote_ref in ALLOWED_REMOTE_REFS:
            out.append(("ALLOW", remote_ref, f"from {local_ref}"))
        elif local_sha == ZERO:
            out.append(("REFUSE", remote_ref, "this is a DELETE of a published ref"))
        else:
            out.append(("REFUSE", remote_ref, f"not master (from {local_ref})"))
    return out


def main(argv: list[str]) -> int:
    remote = argv[1] if len(argv) > 1 else "(unnamed)"
    lines = sys.stdin.read().splitlines()

    if not lines:
        print(f"pre-push: read NO ref lines for remote {remote}. "
              "THIS IS NOT A CHECK -- nothing was examined. Allowing, because "
              "refusing a push this script does not understand would be worse "
              "than saying so.", file=sys.stderr)
        return 0

    results = verdicts(lines)
    refused = [r for r in results if r[0] == "REFUSE"]

    # SAY WHAT WAS SEEN, ALWAYS -- on the allow path too. A gate that prints
    # only when it fires cannot be distinguished from one that never ran.
    allowed = len(results) - len(refused)
    if not refused:
        print(f"pre-push: {allowed} ref(s) to {remote}, all master. Allowed.",
              file=sys.stderr)
        return 0

    if os.environ.get(OVERRIDE_ENV) == "1":
        print(f"pre-push: {len(refused)} non-master ref(s) ALLOWED by "
              f"{OVERRIDE_ENV}=1:", file=sys.stderr)
        for _v, ref, why in refused:
            print(f"    {ref}  ({why})", file=sys.stderr)
        return 0

    print("", file=sys.stderr)
    print(f"PUSH REFUSED: {len(refused)} of {len(results)} ref(s) are not "
          f"{'/'.join(sorted(ALLOWED_REMOTE_REFS))}.", file=sys.stderr)
    print("", file=sys.stderr)
    for _v, ref, why in refused:
        print(f"    {ref}", file=sys.stderr)
        print(f"        {why}", file=sys.stderr)
    print("", file=sys.stderr)
    print("This repository is PUBLIC, and branches outside master carry blobs "
          "that were", file=sys.stderr)
    print("purged from the history master publishes. Publishing is not "
          "reversible: retained", file=sys.stderr)
    print("objects stay resolvable by SHA after a force-push, and only "
          "delete-and-recreate", file=sys.stderr)
    print("was measured to remove them.", file=sys.stderr)
    print("", file=sys.stderr)
    print("If you meant it, sweep the range first and then say so for one "
          "command:", file=sys.stderr)
    print("    venv/Scripts/python.exe scripts/sweep_blobs_for_identity.py "
          "'master..<ref>'", file=sys.stderr)
    print(f"    {OVERRIDE_ENV}=1 git push ...", file=sys.stderr)
    print("", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
