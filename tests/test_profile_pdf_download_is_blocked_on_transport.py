"""Row 58 PROFILE-PDF-DOWNLOAD (census ``P C8``): the TRANSPORT half is built,
and this file now pins what that route is, what it is not, and what still
blocks the row.

## 2026-09-24 -- THE ROUTE THIS FILE SAID HAD NOWHERE TO LIVE NOW EXISTS

Until today this file answered its question NO, for a structural reason:

    In ATTACH mode this package NEVER CREATES A CONTEXT. ``cdp_bridge`` does
    ``contexts = list(client.contexts)`` and returns ``contexts[0]`` verbatim.
    ``accept_downloads`` is a CONTEXT CREATION OPTION, so there is no call
    site in the attach path where it could be passed -- not "nobody wrote it
    yet", but *there is nowhere to write it*.

Every sentence of that is still true, and three tests below still pin it. What
changed is that the question it answered -- *can this server NAME a file a
download produces?* -- now has a route that goes around the context entirely:

    ``linkedin_server/cdp_download.py`` sets Chrome's OWN download behaviour
    (``Browser.setDownloadBehavior``, ``allowAndName``) over a DevTools
    session on the ATTACHED browser, into a directory under ``_state/``, and
    sets it back to ``default`` afterwards. It creates no context -- the
    ruling ``D4-NO-OWN-BROWSER-CONTEXT`` (2026-09-24) says the package never
    does -- and it adopts none.

So the old claim becomes the thing the new route answers: the context option
still has nowhere to live, and the package no longer needs it to. The detector
below gains a second vocabulary for that route, and the measurement now reads
YES -- through that route and no other.

## AND THE LIBRARY UNDERNEATH NEVER HAD THE GAP

DERIVED from the installed Playwright driver (1.63.0 on 2026-09-24), not
observed live, and recorded in ``_audit/2026-09-24-lane-d-d6-pdf.md``:
``connect_over_cdp`` gives the adopted default context an ``"accept"`` download
setting by default and sends ``Browser.setDownloadBehavior`` with
``allowAndName`` into its own temporary directory at attach time. So "the
download cannot land as a file" was a fact about this package's call sites,
never about the attached browser. That default is not tested here -- the
requirement is ``playwright>=1.40``, and a test reading one version's bundle
would be a fact about whichever version CI installed -- and the transport does
not lean on it.

## WHAT STILL BLOCKS THE ROW, pinned as the last test

The transport has NO CALLER. The act that starts P C8's download is
LinkedIn's own "Save to PDF" item behind the profile's "More" menu, and no
press in this package reaches it: its shape has never been measured, and a
press that is an ACT rather than a disclosure has no sanctioned route. The
final test fails the moment something calls the capture -- and when it does,
the row is buildable and must be re-filed, not this test relaxed.

## THE DETECTOR IS FACTORED OUT OF ITS ASSERTION

:func:`download_capability` takes a mapping of source text and returns a
verdict. It is exercised on synthetic sources BEFORE it is aimed at the real
package, and the ORDER IS THE POINT: a reading no instrument can fail is not a
reading, and a detector shown only agreeing with its author is the defect this
repository has caught three times.
"""
from __future__ import annotations

import ast
import pathlib

from linkedin_server import readonly

REPO = pathlib.Path(__file__).resolve().parent.parent

#: THE PLAYWRIGHT CONTEXT ROUTE. A context created with ``accept_downloads``,
#: plus an ``expect_download`` / download event to get the ``Download`` object,
#: plus ``suggested_filename`` or ``save_as`` to put it somewhere nameable.
DOWNLOAD_VOCABULARY = (
    "accept_downloads",
    "expect_download",
    "suggested_filename",
    "save_as",
    "downloads_path",
)

#: THE DEVTOOLS ROUTE, added 2026-09-24: Chrome's own download behaviour, set
#: over a browser-level session, and the two events that name the download.
#: A package using these can name a file WITHOUT creating a context.
CDP_DOWNLOAD_VOCABULARY = (
    "Browser.setDownloadBehavior",
    "Browser.downloadWillBegin",
    "Browser.downloadProgress",
    "new_browser_cdp_session",
)

#: The calls that CREATE a browser context -- the only places
#: ``accept_downloads`` could ever be passed.
CONTEXT_CREATION = ("new_context", "launch_persistent_context")

#: The attach path's tell: it adopts a context rather than making one.
ADOPTION = "client.contexts"


def download_capability(sources: dict[str, str]) -> dict[str, object]:
    """Could a package with these sources NAME a downloaded file, and how?

    ``sources`` maps a label to source text. Returns::

        {
            "can_name_a_file":   bool,
            "vocabulary_sites":  int,   labels using the CONTEXT route's terms
            "cdp_route_sites":   int,   labels using the DEVTOOLS route's terms
            "creation_sites":    int,   labels that create a context
            "adopts_context":    bool,  does any label adopt an existing one
            "why":               a word from a closed vocabulary
        }

    ``why`` is ``"has_download_vocabulary"`` (the context route),
    ``"cdp_download_behaviour"`` (the DevTools route and not the context
    route), ``"no_context_creation_at_all"`` or ``"no_download_vocabulary"``.
    The context route is reported in preference when both are present, because
    it is the one that needs a context and so the one D4 would refuse; the
    third is reported in preference to the fourth because it is the STRONGER
    statement: a package that creates no context has nowhere to put the option.
    """
    vocabulary_sites = sum(
        1
        for text in sources.values()
        if any(term in text for term in DOWNLOAD_VOCABULARY)
    )
    cdp_route_sites = sum(
        1
        for text in sources.values()
        if any(term in text for term in CDP_DOWNLOAD_VOCABULARY)
    )
    creation_sites = sum(
        1 for text in sources.values() if any(call in text for call in CONTEXT_CREATION)
    )
    adopts = any(ADOPTION in text for text in sources.values())

    if vocabulary_sites:
        why = "has_download_vocabulary"
    elif cdp_route_sites:
        why = "cdp_download_behaviour"
    elif creation_sites == 0:
        why = "no_context_creation_at_all"
    else:
        why = "no_download_vocabulary"

    return {
        "can_name_a_file": bool(vocabulary_sites or cdp_route_sites),
        "vocabulary_sites": vocabulary_sites,
        "cdp_route_sites": cdp_route_sites,
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


def test_the_detector_reports_the_devtools_route_without_any_context():
    """THE SECOND CONTROL, added with the route: YES, and with no context."""
    verdict = download_capability(
        {
            "bridge.py": "contexts = list(client.contexts)",
            "transport.py": (
                "session = await browser.new_browser_cdp_session()\n"
                "await session.send('Browser.setDownloadBehavior', params)"
            ),
        }
    )
    assert verdict["can_name_a_file"] is True
    assert verdict["why"] == "cdp_download_behaviour"
    assert verdict["cdp_route_sites"] == 1
    assert verdict["vocabulary_sites"] == 0
    assert verdict["creation_sites"] == 0
    assert verdict["adopts_context"] is True


def test_the_context_route_outranks_the_devtools_route_when_both_appear():
    """Both present reads as the context route: that is the one D4 refuses."""
    verdict = download_capability(
        {
            "a.py": "await pw.chromium.new_context(accept_downloads=True)",
            "b.py": "await session.send('Browser.setDownloadBehavior', params)",
        }
    )
    assert verdict["why"] == "has_download_vocabulary"
    assert verdict["can_name_a_file"] is True


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
    """Adoption is the fact that made the attach path unfixable in place."""
    verdict = download_capability({"bridge.py": "contexts = list(client.contexts)"})
    assert verdict["adopts_context"] is True
    assert verdict["creation_sites"] == 0


# ------------------------------------- 2. aimed at the real package


def test_this_package_names_a_downloaded_file_only_through_the_devtools_route():
    """THE MEASUREMENT. Every number here is recomputed at run time.

    Until 2026-09-24 this read NO. It reads YES now, through exactly one
    module, and still with none of the context route's terms anywhere: if a
    context-route term appears, somebody has reached for the option D4 says
    this package never gets to pass, and that is a finding to read rather
    than a test to relax.
    """
    sources = _package_sources()
    verdict = download_capability(sources)
    assert verdict["vocabulary_sites"] == 0, (
        "a context-route download term appeared in the package. The package "
        "creates no context (D4-NO-OWN-BROWSER-CONTEXT), so that option has "
        "nowhere to live; the transport is cdp_download.py."
    )
    cdp_sites = sorted(
        name for name, text in sources.items()
        if any(term in text for term in CDP_DOWNLOAD_VOCABULARY)
    )
    assert cdp_sites == ["cdp_download.py"], cdp_sites
    assert verdict["can_name_a_file"] is True
    assert verdict["why"] == "cdp_download_behaviour"


def test_exactly_one_place_in_the_package_creates_a_context_and_it_is_launch_mode():
    """And the fleet does not use it.

    The single creation site is LAUNCH mode. Every wave and every tool runs
    in ATTACH mode against the operator's own Chrome, where this package
    adopts a context it did not create -- and the download transport added on
    2026-09-24 did not add a second creation site.
    """
    sources = _package_sources()
    creators = sorted(
        name
        for name, text in sources.items()
        if any(call + "(" in text for call in CONTEXT_CREATION)
    )
    assert creators == ["browser.py"], creators


def test_the_attach_path_adopts_a_context_rather_than_creating_one():
    """The structural fact the old finding rested on, and D4 keeps it true.

    Stated as a test rather than quoted from a comment, because a comment is
    read as current truth and asserted by nothing.
    """
    bridge = (REPO / "linkedin_server" / "cdp_bridge.py").read_text(
        encoding="utf-8", errors="replace"
    )
    assert "client.contexts" in bridge
    assert not any(call + "(" in bridge for call in CONTEXT_CREATION), (
        "cdp_bridge now creates a context. D4-NO-OWN-BROWSER-CONTEXT says the "
        "package never does; read the ruling before reading this test."
    )


# --------------------------------- 3. the boundary half, pinned as cost zero


def test_the_profile_address_is_already_allowed_so_the_row_costs_no_boundary():
    """The half the predecessor settled, pinned so the cost claim is testable.

    The ranked table charged row 58 at cost 2 / DECIDE. The boundary
    component of that is ZERO and always was.
    """
    readonly.assert_read_url("https://www.linkedin.com/in/me/")


# ------------------------------ 4. what still blocks the row: nothing calls it


def _callers_of_the_capture(sources: dict[str, str]) -> list[str]:
    """Modules that CALL ``capture_download``, other than the one defining it."""
    out = []
    for name, text in sources.items():
        if name == "cdp_download.py":
            continue
        for node in ast.walk(ast.parse(text)):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "capture_download"):
                out.append(name)
                break
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "capture_download"):
                out.append(name)
                break
    return sorted(out)


def test_the_caller_detector_finds_a_planted_caller():
    """THE CONTROL for the tripwire below."""
    planted = {
        "cdp_download.py": "async def capture_download(b, t, **k):\n    return {}\n",
        "server.py": (
            "async def tool():\n"
            "    return await cdp_download.capture_download(b, t, label='x')\n"
        ),
    }
    assert _callers_of_the_capture(planted) == ["server.py"]


def test_the_row_is_blocked_by_the_press_and_not_by_the_transport_or_the_boundary():
    """A refusal must name what it SAW, and so must a permission.

    The address is admitted (the boundary half), the package can name a
    downloaded file (the transport half), and NOTHING CALLS THE CAPTURE --
    because the act that starts the download, the "Save to PDF" item behind
    the profile's "More" menu, is a press no route in this package reaches.

    WHEN THIS GOES RED, somebody has wired the press. That is the row becoming
    COVERED-UNFIRED: re-file ``P C8`` in ``_audit/_census/profile.md`` and its
    line in ``_audit/_census/read-addresses.tsv``, and delete this test's
    last assertion in the same commit -- do not relax it.

    THE TRANSPORT GOT ITS FIRST CALLER ON 2026-11-28, AND IT IS NOT P C8's.
    Lane build28 wired ``resume_files.download_resume`` (census ``J 72`` /
    ``P M4``): a stored resume's own ``Download`` item, on his application
    settings page. The caller list below names that one module, and the
    module is held to that page, so the tripwire still fires the moment ANY
    other module calls the capture -- the profile's "Save to PDF" included.
    Stated as an exact list, not loosened to "at most one": a second caller is
    a second press, and it must be read before this list is edited.
    """
    from linkedin_server import application_settings, resume_files

    readonly.assert_read_url("https://www.linkedin.com/in/me/")
    sources = _package_sources()
    assert download_capability(sources)["can_name_a_file"] is True
    assert _callers_of_the_capture(sources) == ["resume_files.py"], (
        "something new calls cdp_download.capture_download. If it is P C8's "
        "press, it has landed: re-file the row rather than relaxing this test."
    )
    # The one caller presses on his application settings page and nowhere
    # else: its module's one page is that page's admitted address, and no
    # profile address appears in it.
    assert resume_files.PAGE_URL == application_settings.PAGE_URL
    assert "/in/" not in sources["resume_files.py"]
    assert "Save to PDF" not in sources["resume_files.py"]
