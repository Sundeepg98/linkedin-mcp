"""Row 58 PROFILE-PDF-DOWNLOAD is blocked on a TRANSPORT capability, not on
the read boundary -- and this pins both halves so the claim cannot rot.

THE ROW WAS HALF-SETTLED AND THE HALVES POINT IN OPPOSITE DIRECTIONS.
``_audit/2026-09-05-settings-tail.md`` section 4 established the first:
``https://www.linkedin.com/in/me/`` is ALREADY ALLOWED, so the row carries
**no boundary cost at all** and the ranked table's "cost 2" overstates it on
that axis. Its author said plainly that it had answered the address and not
the question, and named the unanswered half: *whether the download lands as a
file this server can name.*

THIS FILE ANSWERS THAT HALF, and the answer is NO -- for a reason that is
structural rather than a missing line of code:

    In ATTACH mode this package NEVER CREATES A CONTEXT. ``cdp_bridge`` does
    ``contexts = list(client.contexts)`` and returns ``contexts[0]`` verbatim,
    with its own comment explaining why: a new context would be "incognito-ish
    and signed into nothing, which is the opposite of why anyone attaches."

``accept_downloads`` is a CONTEXT CREATION OPTION. A context this package did
not create is a context whose download options it did not set, and there is no
call site in the attach path where it could -- not "nobody wrote it yet", but
*there is nowhere to write it*. The whole fleet runs in attach mode.

**SO THE ROW'S BLOCKER IS MIS-FILED, and it is mis-filed in the direction that
makes it look cheap.** It is queued DECIDE at cost 2 as though a ruling were
the binding constraint. The ruling was already given -- his own profile as a
file is a read of his own data. What binds is a transport capability nobody
has built, on a surface that is not this one.

## WHY THIS IS A TEST AND NOT A PARAGRAPH IN AN AUDIT DOC

A docstring is the one class the correction machinery cannot bind, and an
audit document is a dated record that rots harmlessly while a claim about
what the code CAN DO is read as current truth. If somebody adds download
handling tomorrow, this turns red and they must come and read why the row
said what it said. A note would simply be wrong and silent.

## THE DETECTOR IS FACTORED OUT OF ITS ASSERTION

:func:`download_capability` takes a mapping of source text and returns a
verdict. It is exercised three ways below and the ORDER IS THE POINT:

1. handed synthetic sources that DO carry the capability -- it says yes;
2. handed synthetic sources that do NOT -- it says no;
3. only then aimed at the real package.

A reading no instrument can fail is not a reading, and a detector shown only
agreeing with its author is the defect this repository has caught three times.
Step 1 is what makes step 3 mean anything: without it, "no capability found"
is indistinguishable from a grep with a typo in it.
"""
from __future__ import annotations

import pathlib

from linkedin_server import readonly

REPO = pathlib.Path(__file__).resolve().parent.parent

#: THE VOCABULARY A PACKAGE THAT COULD NAME A DOWNLOADED FILE WOULD HAVE TO
#: USE. Playwright offers exactly one route -- a context created with
#: ``accept_downloads``, plus an ``expect_download`` / download event to get
#: the ``Download`` object, plus ``suggested_filename`` or ``save_as`` to put
#: it somewhere nameable. A package using NONE of these cannot name a file,
#: and that is a claim about Playwright's API rather than about this repo.
DOWNLOAD_VOCABULARY = (
    "accept_downloads",
    "expect_download",
    "suggested_filename",
    "save_as",
    "downloads_path",
)

#: The calls that CREATE a browser context -- the only places
#: ``accept_downloads`` could ever be passed.
CONTEXT_CREATION = ("new_context", "launch_persistent_context")

#: The attach path's tell: it adopts a context rather than making one.
ADOPTION = "client.contexts"


def download_capability(sources: dict[str, str]) -> dict[str, object]:
    """Could a package with these sources NAME a downloaded file?

    ``sources`` maps a label to source text. Returns::

        {
            "can_name_a_file":  bool,
            "vocabulary_sites": int,   how many labels use any download term
            "creation_sites":   int,   how many labels create a context
            "adopts_context":   bool,  does any label adopt an existing one
            "why":              a word from a closed vocabulary
        }

    ``why`` is ``"has_download_vocabulary"``, ``"no_download_vocabulary"`` or
    ``"no_context_creation_at_all"``. The third is reported in preference to
    the second when it also holds, because it is the STRONGER statement: a
    package that creates no context has nowhere to put the option, so adding
    the vocabulary alone would not help it.
    """
    vocabulary_sites = sum(
        1
        for text in sources.values()
        if any(term in text for term in DOWNLOAD_VOCABULARY)
    )
    creation_sites = sum(
        1 for text in sources.values() if any(call in text for call in CONTEXT_CREATION)
    )
    adopts = any(ADOPTION in text for text in sources.values())

    if vocabulary_sites:
        why = "has_download_vocabulary"
    elif creation_sites == 0:
        why = "no_context_creation_at_all"
    else:
        why = "no_download_vocabulary"

    return {
        "can_name_a_file": bool(vocabulary_sites),
        "vocabulary_sites": vocabulary_sites,
        "creation_sites": creation_sites,
        "adopts_context": adopts,
        "why": why,
    }


def _package_sources() -> dict[str, str]:
    """Every tracked python file in the package, by name."""
    return {
        path.name: path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((REPO / "linkedin_server").glob("*.py"))
    }


# ------------------------------------------- 1. the detector can say YES


def test_the_detector_reports_a_capability_when_one_is_present():
    """THE CONTROL. Without this, a zero below is a fact about the grep.

    Handed source that does what a downloading package would do, the
    detector must say so. A detector that can only return False certifies
    nothing at all.
    """
    verdict = download_capability(
        {
            "browser.py": (
                "context = await pw.chromium.new_context(accept_downloads=True)"
            ),
            "reader.py": (
                "async with page.expect_download() as info:\n"
                "    await control.click()\n"
                "path = await info.value.save_as(target)"
            ),
        }
    )
    assert verdict["can_name_a_file"] is True
    assert verdict["why"] == "has_download_vocabulary"
    assert verdict["vocabulary_sites"] == 2
    assert verdict["creation_sites"] == 1


def test_the_detector_reports_no_when_a_context_is_made_without_the_option():
    """The middle case, and it is the one worth distinguishing.

    A package that DOES create a context but never passes the option is one
    line from being able to download. A package that creates no context is
    not. Those two are different findings and the detector must not collapse
    them, because the remedy differs completely.
    """
    verdict = download_capability(
        {"browser.py": "await pw.chromium.launch_persistent_context(user_data_dir=d)"}
    )
    assert verdict["can_name_a_file"] is False
    assert verdict["why"] == "no_download_vocabulary"
    assert verdict["creation_sites"] == 1


def test_the_detector_reports_the_stronger_no_when_nothing_creates_a_context():
    verdict = download_capability({"bridge.py": "return contexts[0]"})
    assert verdict["can_name_a_file"] is False
    assert verdict["why"] == "no_context_creation_at_all"
    assert verdict["creation_sites"] == 0


def test_the_detector_sees_context_adoption_as_distinct_from_creation():
    """Adoption is the fact that makes the attach path unfixable in place."""
    verdict = download_capability({"bridge.py": "contexts = list(client.contexts)"})
    assert verdict["adopts_context"] is True
    assert verdict["creation_sites"] == 0


# ------------------------------------- 2. aimed at the real package


def test_this_package_cannot_name_a_downloaded_file():
    """THE MEASUREMENT. Every number here is recomputed at run time.

    If this goes red, somebody added download handling. That is not a
    failure -- it is the row becoming buildable, and they should read this
    file's docstring and re-file row 58 rather than deleting the test.
    """
    verdict = download_capability(_package_sources())
    assert verdict["vocabulary_sites"] == 0, (
        "a download term appeared in the package. Row 58 PROFILE-PDF-DOWNLOAD "
        "was filed blocked on exactly this absence; if it is now present, the "
        "row is buildable and its blocker must be re-filed rather than this "
        "test relaxed."
    )
    assert verdict["can_name_a_file"] is False
    assert verdict["why"] == "no_download_vocabulary"


def test_exactly_one_place_in_the_package_creates_a_context_and_it_is_launch_mode():
    """And the fleet does not use it.

    The single creation site is LAUNCH mode. Every wave and every tool runs
    in ATTACH mode against the operator's own Chrome, where this package
    adopts a context it did not create. So the one place the option COULD be
    passed is the one path nobody takes.
    """
    sources = _package_sources()
    creators = sorted(
        name
        for name, text in sources.items()
        if any(call + "(" in text for call in CONTEXT_CREATION)
    )
    assert creators == ["browser.py"], creators


def test_the_attach_path_adopts_a_context_rather_than_creating_one():
    """The structural fact the whole finding rests on.

    Stated as a test rather than quoted from a comment, because a comment is
    read as current truth and asserted by nothing.
    """
    bridge = (REPO / "linkedin_server" / "cdp_bridge.py").read_text(
        encoding="utf-8", errors="replace"
    )
    assert "client.contexts" in bridge
    assert not any(call + "(" in bridge for call in CONTEXT_CREATION), (
        "cdp_bridge now creates a context. If it does, accept_downloads has a "
        "call site for the first time and row 58's blocker has moved."
    )


# --------------------------------- 3. the boundary half, pinned as cost zero


def test_the_profile_address_is_already_allowed_so_the_row_costs_no_boundary():
    """The half the predecessor settled, pinned so the cost claim is testable.

    The ranked table charges row 58 at cost 2 / DECIDE. The boundary
    component of that is ZERO and always was.
    """
    readonly.assert_read_url("https://www.linkedin.com/in/me/")


def test_the_row_is_not_blocked_by_the_read_boundary_and_this_says_which_gate():
    """A refusal must name what it SAW, and so must a permission.

    This asserts the positive AND the negative in one place: the address is
    admitted, and the thing that blocks the row is measured one function up.
    Reading only the first would leave a reader thinking the row is ready.
    """
    readonly.assert_read_url("https://www.linkedin.com/in/me/")
    assert download_capability(_package_sources())["can_name_a_file"] is False
