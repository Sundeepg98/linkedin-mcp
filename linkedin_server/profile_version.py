"""Would this launch DOWNGRADE the persistent profile? Asked before launching.

Chromium writes its own version into a one-line ``Last Version`` file at the
root of every user-data-dir. When it opens a profile stamped by a NEWER build
it does not refuse and it does not warn: it runs a downgrade migration, moves
the profile aside, and starts clean. The signed-in session is in the part that
gets moved aside.

    Measured 2026-08-25: playwright's chromium met a profile that real Chrome
    had stamped, and the operator signed in again, and again, and again.
    ``session_store.restore_into_context`` exists because of that day.

THE SESSION STORE IS A NET, NOT A GATE. It runs AFTER the launch, it is
additive and conditional, and every failure path in it returns
``restored: False`` and leaves the launch exactly as it was. By the time it is
asked anything, Chrome has already migrated the profile. A net placed under a
fall is worth having; it is not a reason to keep walking off the ledge.

So the rule -- *never launch playwright's chromium onto the persistent
profile* -- has lived as PROSE: a comment in ``browser.py``, a docstring in
``scripts/start_chrome.ps1``, a paragraph in a handoff file. A rule enforced
by discipline is enforced only for as long as everyone who edits the call site
has read the prose. This module is that rule with a runtime consequence.

WHAT IT REFUSES, AND WHAT IT DELIBERATELY DOES NOT:

* profile stamp NEWER than the chromium about to run -- REFUSED. That is the
  downgrade, and it is the only case that has ever cost anything.
* stamp OLDER, or EQUAL -- ALLOWED. An ordinary forward upgrade. Chromium
  migrates forward routinely and the session survives it; refusing here would
  block the daily path to prevent nothing.
* NO stamp file -- ALLOWED. A directory with no ``Last Version`` is a profile
  no Chromium has opened yet, which is precisely first-run. A gate that
  refuses a brand-new profile has broken the thing it was protecting.
* a stamp that will not parse, or a chromium version that cannot be resolved
  -- ALLOWED, and this one is a decision rather than an oversight. **You
  cannot prove a downgrade you cannot read.** Failing closed on an unreadable
  one-line file would let a corrupt byte block every tool in the server, and
  the failure it would be preventing is one nobody had evidence of.

WHERE THE CHROMIUM VERSION COMES FROM. Not from a constant -- pinning "151"
here would be wrong the next time ``pip install -U playwright`` runs, and
wrong silently, in the direction of passing. Not by running the binary either:
a launch is the thing being gated, and gating it on a launch is circular. It
is read off the path PLAYWRIGHT ITSELF published, which ``preflight`` has
already resolved by the time this runs:

    <browsers>/chromium-1234/chrome-win64/chrome.exe             the executable
    <browsers>/chromium-1234/chrome-win64/151.0.7922.34.manifest the version

The version is the NAME of a file sitting beside the binary -- Chrome for
Testing's own layout. That is the primary route, because it describes the
binary that will actually run rather than the one a manifest somewhere thinks
should be there.

The fallback covers a layout without that manifest: the revision is in the
path (``chromium-1234``) and the playwright package ships
``driver/package/browsers.json`` mapping revision to ``browserVersion``. If
the two ever disagree the manifest wins, for the reason above. If neither
answers, this module says so and the launch proceeds.

Nothing here launches a browser, starts a driver, opens a profile, writes a
file or touches the network. It reads two names and one small JSON file.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Optional, Union

from linkedin_server.errors import BrowserUnavailableError

#: Chromium's own version stamp, at the root of a user-data-dir. The name has
#: a space in it and no extension; it is Chromium's, not ours.
PROFILE_STAMP_FILE = "Last Version"

#: A dotted numeric version and nothing else. Anchored at both ends on
#: purpose: a stamp file with trailing prose is not a version, and treating
#: the leading digits of one as a version would be inventing a reading.
_VERSION_RE = re.compile(r"^\d+(?:\.\d+)*$")

#: ``151.0.7922.34.manifest`` -- the marker Chrome for Testing leaves beside
#: its binary. The stem is the version.
_MANIFEST_SUFFIX = ".manifest"

#: ``chromium-1234`` or ``chromium_headless_shell-1234``: a playwright browser
#: directory, whose trailing number is the revision ``browsers.json`` keys on.
_REVISION_DIR_RE = re.compile(r"^(chromium(?:[_-][a-z-]+)*)-(\d+)$")

#: Where the playwright package keeps the revision -> version mapping. Found
#: relative to the imported package, never by a path guess.
_BROWSERS_JSON = ("driver", "package", "browsers.json")

PathLike = Union[str, "os.PathLike[str]"]


def parse_version(text: Optional[str]) -> Optional[tuple[int, ...]]:
    """``"151.0.7922.34"`` -> ``(151, 0, 7922, 34)``; anything else ``None``.

    INTEGER TUPLES, NOT STRINGS, and the reason is that string comparison
    happens to be right often enough to look correct. ``"152..." > "151..."``
    sorts fine and would have passed a review; ``"9.0.1.0" > "10.0.1.0"`` is
    True as strings and false as versions. A comparison that is right for the
    versions you happened to test with is not a comparison.

    Returns ``None`` rather than raising, because every caller here treats
    unreadable as "no opinion" and a raise would make that the caller's
    problem to remember.
    """
    if text is None:
        return None
    stripped = text.strip()
    if not _VERSION_RE.match(stripped):
        return None
    try:
        return tuple(int(part) for part in stripped.split("."))
    except ValueError:  # pragma: no cover - the regex already excluded this
        return None


def _read_profile_stamp(profile_dir: PathLike) -> Optional[str]:
    """The profile's ``Last Version`` line, or ``None`` if there is not one.

    ``None`` covers every way of not having an answer -- no directory, no
    file, an unreadable file, an empty one -- because the caller does the same
    thing with all of them: allow the launch. Distinguishing them here would
    be a distinction nothing acts on.

    UNDERSCORED, AND NOT TO DODGE A GUARD -- the rename is what the guard
    correctly pointed out. ``tests/test_readers_outside_dom_are_a_pinned_
    inventory.py`` selects module-level ``read_*`` functions that NO OTHER
    MODULE calls, because a reader the package ships and nobody can reach
    passes every test it has. Named ``read_profile_stamp`` this tripped it,
    and the honest reading is that the name was wrong rather than the guard:
    every other ``read_*`` in this package is an entry point some other module
    calls, while this one is a step inside :func:`check`. The module IS wired
    -- ``browser.start()`` calls :func:`assert_no_downgrade` -- so the right
    fix was to stop claiming a vocabulary this function does not belong to,
    not to add the package's first line to that inventory's deliberately
    EMPTY dict.

    READ AS ``utf-8-sig``, NOT ``utf-8``, and this is the one decoding detail
    that matters. Every "cannot read it" path in this module ends in the
    launch being ALLOWED, so an encoding wrinkle does not produce an error --
    it produces a silent pass on the exact input the gate exists to refuse. A
    leading BOM would leave ``\\ufeff153.0.8010.48``, which fails the version
    pattern and opens the gate on a real downgrade. ``utf-8-sig`` strips a BOM
    if there is one and is identical to ``utf-8`` when there is not, so it
    costs nothing and removes the only realistic way a genuine stamp goes
    unread. Chrome writes this file as plain ASCII today; that is a fact about
    today's Chrome, not a property of the file.
    """
    try:
        path = Path(profile_dir) / PROFILE_STAMP_FILE
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
    except (OSError, ValueError):
        return None
    line = raw.strip().splitlines()[0].strip() if raw.strip() else ""
    return line or None


def _version_from_manifest(exe_dir: Path) -> Optional[str]:
    """A ``<version>.manifest`` sitting beside the binary, if there is one."""
    try:
        entries = list(exe_dir.iterdir())
    except OSError:
        return None
    for entry in entries:
        if not entry.name.endswith(_MANIFEST_SUFFIX):
            continue
        stem = entry.name[: -len(_MANIFEST_SUFFIX)]
        if parse_version(stem) is not None:
            return stem
    return None


def _revision_from_path(resolved_path: Path) -> Optional[tuple[str, str]]:
    """``(browser name, revision)`` from a ``chromium-1234`` path component."""
    for part in resolved_path.parts:
        match = _REVISION_DIR_RE.match(part)
        if match is not None:
            return match.group(1), match.group(2)
    return None


def _version_from_browsers_json(name: str, revision: str) -> Optional[str]:
    """Playwright's own revision -> version mapping, read from the package.

    Located through the imported ``playwright`` module rather than by
    searching the filesystem, so this reads the manifest of the package that
    would do the launching and not some other copy on the box.
    """
    try:
        import playwright  # noqa: PLC0415 - deliberately lazy; see below
    except ImportError:
        return None
    try:
        package_dir = Path(playwright.__file__).resolve().parent
        data = json.loads(
            (package_dir.joinpath(*_BROWSERS_JSON)).read_text(encoding="utf-8")
        )
        for entry in data.get("browsers", []):
            if entry.get("name") == name and str(entry.get("revision")) == revision:
                version = entry.get("browserVersion")
                if parse_version(version) is not None:
                    return str(version)
    except (OSError, ValueError, TypeError, AttributeError):
        return None
    return None


def chromium_version_from_executable(resolved_path: Optional[str]) -> Optional[str]:
    """The version of the chromium at ``resolved_path``, or ``None``.

    ``resolved_path`` is what ``preflight`` got from
    ``playwright.chromium.executable_path`` -- this module never asks
    Playwright a second time, and never starts a driver of its own.

    The import of ``playwright`` inside the fallback is lazy on purpose: this
    module is imported by ``browser.py`` at module scope, and the whole point
    of the sibling ``preflight`` module is that a missing or broken playwright
    install must produce a diagnosable message rather than an ImportError at
    import time.
    """
    if not resolved_path:
        return None
    path = Path(resolved_path)

    from_manifest = _version_from_manifest(path.parent)
    if from_manifest is not None:
        return from_manifest

    found = _revision_from_path(path)
    if found is None:
        return None
    return _version_from_browsers_json(*found)


def downgrade_message(
    *, profile_stamp: str, chromium_version: str, profile_dir: PathLike
) -> str:
    """The one actionable line a refused launch produces.

    Shaped after ``preflight.missing_browser_message``: it names the two
    facts that are in tension, the object they are in tension about, and the
    route out. Somebody reading it at 2am should not have to find this file.
    """
    return (
        f"Refusing to launch: the persistent Chrome profile at {profile_dir} "
        f"is stamped {profile_stamp}, and the chromium Playwright would launch "
        f"is {chromium_version}. Opening a newer-stamped profile with an older "
        f"Chromium is a DOWNGRADE: Chromium migrates the profile, moves it "
        f"aside and starts clean, which discards the signed-in LinkedIn "
        f"session (measured 2026-08-25). Fix: use ATTACH mode, which launches "
        f"nothing and drives a real Chrome that already opened this profile -- "
        f"start it with scripts/start_chrome.ps1 and set LINKEDIN_CDP_ATTACH=1 "
        f"in this server's environment. To use the launch path instead, the "
        f"profile must be one this chromium can open: upgrade Playwright's "
        f"browsers until its chromium is at least {profile_stamp}, or point "
        f"LINKEDIN_PROFILE_DIR at a different directory. Do NOT delete the "
        f"stamp file to get past this -- that hides the skew, it does not "
        f"remove it."
    )


def check(profile_dir: PathLike, resolved_path: Optional[str]) -> dict[str, Any]:
    """A verdict rather than a raise, so a diagnostic can report it.

    Args:
        profile_dir: the user-data-dir the launch would open.
        resolved_path: the executable path Playwright published, from
            ``preflight``. ``None`` is accepted and means "no opinion".

    Keys, mirroring ``preflight.check`` so the two read alike:

    * ``ok`` -- may the launch proceed. True for every case but a proven
      downgrade.
    * ``reason`` -- which arm decided it: ``no_stamp_file``,
      ``stamp_unparseable``, ``chromium_version_unresolved``,
      ``older_or_equal`` or ``downgrade``.
    * ``profile_stamp`` / ``chromium_version`` -- the raw strings, or ``None``.
    * ``message`` -- present only when ``ok`` is False.
    """
    stamp = _read_profile_stamp(profile_dir)
    verdict: dict[str, Any] = {
        "ok": True,
        "profile_dir": str(profile_dir),
        "profile_stamp": stamp,
        "chromium_version": None,
        "reason": "no_stamp_file",
    }
    if stamp is None:
        return verdict

    stamp_parts = parse_version(stamp)
    if stamp_parts is None:
        verdict["reason"] = "stamp_unparseable"
        return verdict

    chromium_version = chromium_version_from_executable(resolved_path)
    verdict["chromium_version"] = chromium_version
    chromium_parts = parse_version(chromium_version)
    if chromium_parts is None:
        verdict["reason"] = "chromium_version_unresolved"
        return verdict

    if stamp_parts > chromium_parts:
        verdict["ok"] = False
        verdict["reason"] = "downgrade"
        verdict["message"] = downgrade_message(
            profile_stamp=stamp,
            chromium_version=str(chromium_version),
            profile_dir=profile_dir,
        )
        return verdict

    verdict["reason"] = "older_or_equal"
    return verdict


def assert_no_downgrade(
    profile_dir: PathLike, resolved_path: Optional[str]
) -> dict[str, Any]:
    """Return the verdict, or raise with the one actionable line.

    Raises:
        BrowserUnavailableError: the launch would downgrade the profile. The
            same class ``preflight`` raises, because from a caller's point of
            view this is the same fact: there is no browser it can usefully
            launch against this profile.
    """
    verdict = check(profile_dir, resolved_path)
    if not verdict["ok"]:
        raise BrowserUnavailableError(verdict["message"])
    return verdict
