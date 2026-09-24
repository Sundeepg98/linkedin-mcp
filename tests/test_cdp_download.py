"""The download transport on the attached browser, driven against a fake Chrome.

``linkedin_server/cdp_download.py`` is the transport the D4 ruling gave census
row ``P C8``: Chrome's own download behaviour, set over a browser-level
DevTools session, with no browser context created. Nothing here reaches a
browser, LinkedIn or the network. Every test runs on :class:`FakeChrome`.

## WHAT THE FAKE MODELS, AND WHY THAT IS THE WHOLE TEST

The capture can only be as good as the fake is faithful, so the fake carries
the four behaviours the protocol names and nothing it does not:

    default        Chrome's own UI takes the download. The file goes to HIS
                   downloads folder under the page's suggested name, and no
                   DevTools session is told anything.
    allow          the file goes to ``downloadPath`` under the page's name.
    allowAndName   the file goes to ``downloadPath`` under the browser's GUID.
    deny           the download begins and is canceled; nothing is written.

Events go only to the session that switched them on, as ``eventsEnabled``
asks. A fresh fake starts at ``default`` -- a browser nobody has told anything.

## THE ORDER IS THE POINT

1. THE CONTROL FIRST: the same capture, with the one step that SETS THE
   BEHAVIOUR removed, must FAIL -- ``no_download_began``, and the bytes in his
   downloads folder rather than ours. Without that, a green capture could be
   a fake that delivers files whatever anybody sends it.
2. A second control: a behaviour that lets the PAGE name the file (``allow``)
   must not be accepted as a capture. The module looks for the GUID, finds
   nothing under it, and says ``file_missing`` -- it never goes looking for a
   name the page chose.
3. Then the capture itself, and every way it can stop, each of which must
   still RESTORE the behaviour.
"""
from __future__ import annotations

import ast
import asyncio
import json
import pathlib
import uuid
from typing import Any, Optional

import pytest

from linkedin_server import cdp_download

REPO = pathlib.Path(__file__).resolve().parent.parent
PACKAGE = REPO / "linkedin_server"

#: Synthetic bytes. A PDF's magic, then nothing that identifies anybody.
PDF_BYTES = b"%PDF-1.4\n% synthetic bytes for a transport test\n%%EOF\n"
#: What LinkedIn might send instead of a PDF -- an HTML page.
HTML_BYTES = b"<!doctype html><html><body>not a pdf</body></html>"

#: Needles for "no page string crosses into the result". Deliberately not
#: name-shaped: a person's name is never a literal in this repository.
SUGGESTED_NEEDLE = "NEEDLE-SUGGESTED-7f3a.pdf"
URL_NEEDLE = "NEEDLE-URL-TOKEN-91c2"
LINKEDIN_URL = f"https://www.linkedin.com/ambry/?x={URL_NEEDLE}"

FAST = {"begin_timeout_s": 0.05, "complete_timeout_s": 0.05}


# ---------------------------------------------------------------------------
# The fake browser
# ---------------------------------------------------------------------------


class FakeSession:
    """A DevTools session: records what was sent, emits what Chrome says."""

    def __init__(self, chrome: "FakeChrome") -> None:
        self.chrome = chrome
        self.sent: list[tuple[str, dict[str, Any]]] = []
        self.handlers: dict[str, list[Any]] = {}
        self.detached = False
        self.fail_on: set[str] = set()

    def on(self, event: str, handler: Any) -> None:
        self.handlers.setdefault(event, []).append(handler)

    def remove_listener(self, event: str, handler: Any) -> None:
        self.handlers.get(event, []).remove(handler)

    def emit(self, event: str, params: dict[str, Any]) -> None:
        for handler in list(self.handlers.get(event, [])):
            handler(params)

    async def send(self, method: str, params: Optional[dict[str, Any]] = None) -> dict:
        params = dict(params or {})
        self.sent.append((method, params))
        if method in self.fail_on:
            raise ConnectionError("the session dropped")
        if method == "Browser.setDownloadBehavior":
            self.chrome.set_behaviour(self, params)
        return {}

    async def detach(self) -> None:
        self.detached = True


class FakeChrome:
    """One browser, one default context -- his -- and what it does with a download."""

    def __init__(self, user_downloads: pathlib.Path) -> None:
        self.behaviour = "default"
        self.download_path: Optional[str] = None
        self.events_to: Optional[FakeSession] = None
        self.user_downloads = user_downloads
        self.sessions: list[FakeSession] = []
        self.contexts_created = 0

    def set_behaviour(self, session: FakeSession, params: dict[str, Any]) -> None:
        self.behaviour = params["behavior"]
        self.download_path = params.get("downloadPath")
        self.events_to = session if params.get("eventsEnabled") else None

    def _tell(self, event: str, params: dict[str, Any]) -> None:
        if self.events_to is not None:
            self.events_to.emit(event, params)

    def download(
        self,
        data: bytes,
        *,
        suggested: str = SUGGESTED_NEEDLE,
        url: str = LINKEDIN_URL,
        guid: Optional[str] = None,
        complete: bool = True,
    ) -> str:
        """Start one download the way the page's own script would."""
        guid = guid or str(uuid.uuid4())
        if self.behaviour == "default":
            self.user_downloads.mkdir(parents=True, exist_ok=True)
            (self.user_downloads / suggested).write_bytes(data)
            return guid
        self._tell("Browser.downloadWillBegin", {
            "frameId": "FRAME", "guid": guid, "url": url,
            "suggestedFilename": suggested,
        })
        if self.behaviour == "deny":
            self._tell("Browser.downloadProgress", {
                "guid": guid, "totalBytes": len(data), "receivedBytes": 0,
                "state": "canceled",
            })
            return guid
        if not complete:
            self._tell("Browser.downloadProgress", {
                "guid": guid, "totalBytes": len(data), "receivedBytes": 1,
                "state": "inProgress",
            })
            return guid
        name = guid if self.behaviour == "allowAndName" else suggested
        (pathlib.Path(self.download_path) / name).write_bytes(data)
        self._tell("Browser.downloadProgress", {
            "guid": guid, "totalBytes": len(data), "receivedBytes": len(data),
            "state": "completed",
        })
        return guid


class FakeBrowser:
    """The attached Playwright ``Browser``, as far as the transport touches it."""

    def __init__(self, chrome: FakeChrome) -> None:
        self.chrome = chrome

    async def new_browser_cdp_session(self) -> FakeSession:
        session = FakeSession(self.chrome)
        self.chrome.sessions.append(session)
        return session

    async def new_context(self, **_kwargs: Any) -> None:
        """Present so a regression that calls it is COUNTED, then refused."""
        self.chrome.contexts_created += 1
        raise AssertionError("the transport created a browser context")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _never_the_real_state_directory(tmp_path, monkeypatch):
    """No test may write under the real ``_state/``, and the switch starts OFF."""
    monkeypatch.setattr(cdp_download, "DOWNLOAD_ROOT", tmp_path / "default-root")
    monkeypatch.delenv(cdp_download.DOWNLOADS_FLAG, raising=False)


@pytest.fixture
def enabled(monkeypatch):
    monkeypatch.setenv(cdp_download.DOWNLOADS_FLAG, "1")


@pytest.fixture
def chrome(tmp_path) -> FakeChrome:
    return FakeChrome(tmp_path / "his-downloads")


@pytest.fixture
def root(tmp_path) -> pathlib.Path:
    return tmp_path / "state-downloads"


def _files_under(path: pathlib.Path) -> list[pathlib.Path]:
    return sorted(p for p in path.rglob("*") if p.is_file()) if path.exists() else []


async def _capture(chrome, root, trigger, **kwargs):
    kwargs.setdefault("label", "profile")
    kwargs.setdefault("suffix", ".pdf")
    kwargs.setdefault("expect_magic", b"%PDF-")
    # The fake emits its events INSIDE the trigger, so a working capture never
    # waits. Short bounds keep a REGRESSION fast: with the production 20 s and
    # 60 s, a planted defect took this file from 3 s to 264 s, measured.
    kwargs.setdefault("begin_timeout_s", 0.5)
    kwargs.setdefault("complete_timeout_s", 0.5)
    return await cdp_download.capture_download(
        FakeBrowser(chrome), trigger, root=root, **kwargs
    )


# ---------------------------------------------------------------------------
# 1. THE CONTROLS -- shown failing before anything is trusted
# ---------------------------------------------------------------------------


async def test_control_without_the_behaviour_set_the_capture_fails(
    enabled, chrome, root, monkeypatch
):
    """THE CONTROL. Remove the step that sets the behaviour; the capture must fail.

    Chrome is left at ``default``, exactly as a browser nobody told anything
    is. The download still happens -- into HIS folder, under the page's name
    -- and this session hears nothing about it. If this capture returned
    ``saved`` the fake would be delivering files whatever was sent, and every
    green test below would be a fact about the fake.
    """
    async def _skip(_session, _run_dir):
        return None

    monkeypatch.setattr(cdp_download, "_set_behaviour", _skip)

    async def trigger():
        chrome.download(PDF_BYTES)

    result = await _capture(chrome, root, trigger, **FAST)

    assert result["saved"] is False
    assert result["why"] == "no_download_began"
    assert result["downloads_began"] == 0
    assert [p.name for p in _files_under(chrome.user_downloads)] == [SUGGESTED_NEEDLE]
    assert _files_under(root) == []


async def test_control_the_same_capture_saves_when_the_behaviour_is_set(
    enabled, chrome, root
):
    """The other half of the control: identical trigger, the step left in."""
    async def trigger():
        chrome.download(PDF_BYTES)

    result = await _capture(chrome, root, trigger)

    assert result["saved"] is True, result
    assert result["why"] == "saved"
    assert _files_under(chrome.user_downloads) == []


async def test_control_a_behaviour_that_lets_the_page_name_the_file_is_not_a_capture(
    enabled, chrome, root, monkeypatch
):
    """``allow`` saves under the PAGE's suggested name. That is refused, not found.

    The module looks for the file under the browser's GUID and nowhere else,
    so a page-chosen name can never become the file this server reports.
    """
    monkeypatch.setattr(
        cdp_download,
        "_behaviour",
        lambda run_dir: {"behavior": "allow", "downloadPath": str(run_dir),
                         "eventsEnabled": True},
    )

    async def trigger():
        chrome.download(PDF_BYTES)

    result = await _capture(chrome, root, trigger)

    assert result["saved"] is False
    assert result["why"] == "file_missing"
    assert [p.name for p in _files_under(root)] == [SUGGESTED_NEEDLE]


# ---------------------------------------------------------------------------
# 2. THE CAPTURE
# ---------------------------------------------------------------------------


async def test_a_pdf_is_saved_under_our_name_in_a_run_directory_of_its_own(
    enabled, chrome, root
):
    async def trigger():
        chrome.download(PDF_BYTES)

    result = await _capture(chrome, root, trigger)

    assert result["saved"] is True, result
    files = _files_under(root)
    assert [p.name for p in files] == ["profile.pdf"]
    run_dir = files[0].parent
    assert run_dir.parent == root and run_dir.name.startswith("profile-")
    assert files[0].read_bytes() == PDF_BYTES
    assert result["bytes"] == len(PDF_BYTES)
    assert result["magic_ok"] is True
    assert result["downloads_began"] == 1
    assert result["other_downloads"] == 0
    assert result["from_linkedin"] is True
    assert result["final_state"] == "completed"
    assert result["context_created"] is False
    assert chrome.contexts_created == 0


async def test_the_behaviour_sent_is_allow_and_name_into_the_run_directory(
    enabled, chrome, root
):
    async def trigger():
        chrome.download(PDF_BYTES)

    await _capture(chrome, root, trigger)

    (session,) = chrome.sessions
    (first, params), (last, restore) = session.sent
    assert first == last == "Browser.setDownloadBehavior"
    assert params["behavior"] == "allowAndName"
    assert params["eventsEnabled"] is True
    assert pathlib.Path(params["downloadPath"]).parent == root
    assert restore == {"behavior": "default"}


async def test_after_a_capture_his_browser_is_back_on_chromes_own_behaviour(
    enabled, chrome, root
):
    """Restored means Chrome's ``default`` -- his pre-attach state -- and a
    download he starts afterwards goes to HIS folder, not ours."""
    async def trigger():
        chrome.download(PDF_BYTES)

    result = await _capture(chrome, root, trigger)
    assert result["behaviour_restored"] is True
    assert chrome.behaviour == "default"
    assert chrome.sessions[0].detached is True

    chrome.download(b"his own file", suggested="his-own.bin")
    assert [p.name for p in _files_under(chrome.user_downloads)] == ["his-own.bin"]
    assert [p.name for p in _files_under(root)] == ["profile.pdf"]


async def test_a_file_that_is_not_the_expected_kind_is_kept_and_not_called_saved(
    enabled, chrome, root
):
    async def trigger():
        chrome.download(HTML_BYTES)

    result = await _capture(chrome, root, trigger)

    assert result["saved"] is False
    assert result["why"] == "magic_mismatch"
    assert result["magic_ok"] is False
    assert result["file"] is not None
    assert [p.name for p in _files_under(root)] == ["profile.pdf"]


async def test_without_an_expected_kind_any_completed_file_is_saved(
    enabled, chrome, root
):
    async def trigger():
        chrome.download(HTML_BYTES)

    result = await _capture(chrome, root, trigger, expect_magic=None, suffix="")

    assert result["saved"] is True
    assert result["magic_ok"] is None
    assert [p.name for p in _files_under(root)] == ["profile"]


async def test_a_second_download_in_the_window_is_counted_and_left_where_it_landed(
    enabled, chrome, root
):
    """The behaviour belongs to the CONTEXT, so his own download could land here.

    Ours is the first to begin. Any other is counted and never deleted.
    """
    async def trigger():
        chrome.download(PDF_BYTES)
        chrome.download(b"his own file")

    result = await _capture(chrome, root, trigger)

    assert result["saved"] is True
    assert result["downloads_began"] == 2
    assert result["other_downloads"] == 1
    names = sorted(p.name for p in _files_under(root))
    assert "profile.pdf" in names and len(names) == 2


async def test_no_page_string_crosses_into_the_result(enabled, chrome, root):
    """The suggested name and the url are the page's. Neither is returned."""
    async def trigger():
        chrome.download(PDF_BYTES)

    result = await _capture(chrome, root, trigger)

    rendered = json.dumps(result)
    assert SUGGESTED_NEEDLE not in rendered
    assert URL_NEEDLE not in rendered
    assert result["from_linkedin"] is True


async def test_a_download_from_another_host_is_said_so_as_one_boolean(
    enabled, chrome, root
):
    async def trigger():
        chrome.download(PDF_BYTES, url="https://files.example.invalid/x.pdf")

    result = await _capture(chrome, root, trigger)

    assert result["saved"] is True
    assert result["from_linkedin"] is False


async def test_the_saved_path_is_rendered_for_display_not_absolute(
    enabled, chrome, root, monkeypatch
):
    """``config.display`` renders it, because an absolute path carries a username."""
    seen: list[Any] = []

    def _display(raw):
        seen.append(raw)
        return "<displayed>"

    monkeypatch.setattr(cdp_download, "display", _display)

    async def trigger():
        chrome.download(PDF_BYTES)

    result = await _capture(chrome, root, trigger)
    assert result["file"] == "<displayed>"
    assert len(seen) == 1 and pathlib.Path(seen[0]).name == "profile.pdf"


# ---------------------------------------------------------------------------
# 3. EVERY WAY IT STOPS, AND THE RESTORE THAT FOLLOWS EACH
# ---------------------------------------------------------------------------


async def test_off_by_default_nothing_is_touched(chrome, root):
    async def trigger():
        raise AssertionError("the trigger ran with the switch off")

    result = await _capture(chrome, root, trigger)

    assert result["why"] == "downloads_disabled"
    assert chrome.sessions == []
    assert not root.exists()


async def test_in_launch_mode_there_is_no_attached_browser_and_nothing_is_touched(
    enabled, chrome, root
):
    class _Page:
        class context:  # noqa: N801 -- mimics page.context
            browser = FakeBrowser(chrome)

    assert cdp_download.attached_browser(_Page(), attached=False) is None
    assert cdp_download.attached_browser(_Page(), attached=True) is _Page.context.browser

    async def trigger():
        raise AssertionError("the trigger ran with no attached browser")

    result = await cdp_download.capture_download(
        None, trigger, label="profile", root=root
    )
    assert result["why"] == "not_attached"
    assert chrome.sessions == []
    assert not root.exists()


@pytest.mark.parametrize(
    "label, suffix, why",
    [
        ("../profile", ".pdf", "bad_label"),
        ("Profile", ".pdf", "bad_label"),
        ("profile.pdf", "", "bad_label"),
        ("", ".pdf", "bad_label"),
        ("profile", "pdf", "bad_suffix"),
        ("profile", "./pdf", "bad_suffix"),
        ("profile", ".p/df", "bad_suffix"),
    ],
)
async def test_a_bad_name_is_refused_before_anything_is_touched(
    enabled, chrome, root, label, suffix, why
):
    async def trigger():
        raise AssertionError("the trigger ran on a refused name")

    result = await _capture(chrome, root, trigger, label=label, suffix=suffix)
    assert result["why"] == why
    assert chrome.sessions == []
    assert not root.exists()


async def test_a_trigger_that_raises_is_named_by_type_and_the_behaviour_restored(
    enabled, chrome, root
):
    """The TYPE crosses, never the text: an exception's text can quote a page."""
    async def trigger():
        raise ValueError(f"the page said {SUGGESTED_NEEDLE}")

    result = await _capture(chrome, root, trigger)

    assert result["why"] == "trigger_raised"
    assert result["error"] == "ValueError"
    assert SUGGESTED_NEEDLE not in json.dumps(result)
    assert result["behaviour_restored"] is True
    assert chrome.behaviour == "default"


async def test_no_download_beginning_is_named_and_the_behaviour_restored(
    enabled, chrome, root
):
    async def trigger():
        return None

    result = await _capture(chrome, root, trigger, **FAST)

    assert result["why"] == "no_download_began"
    assert result["behaviour_restored"] is True
    assert chrome.behaviour == "default"


async def test_a_download_that_never_completes_is_named_and_the_behaviour_restored(
    enabled, chrome, root
):
    async def trigger():
        chrome.download(PDF_BYTES, complete=False)

    result = await _capture(chrome, root, trigger, **FAST)

    assert result["why"] == "download_incomplete"
    assert result["downloads_began"] == 1
    assert result["behaviour_restored"] is True


async def test_a_canceled_download_is_named_canceled(enabled, chrome, root, monkeypatch):
    monkeypatch.setattr(
        cdp_download,
        "_behaviour",
        lambda run_dir: {"behavior": "deny", "eventsEnabled": True},
    )

    async def trigger():
        chrome.download(PDF_BYTES)

    result = await _capture(chrome, root, trigger)

    assert result["why"] == "download_canceled"
    assert result["final_state"] == "canceled"
    assert result["behaviour_restored"] is True


async def test_a_guid_that_is_not_guid_shaped_never_becomes_a_path(
    enabled, chrome, root
):
    async def trigger():
        chrome.download(PDF_BYTES, guid="not-a-guid!")

    result = await _capture(chrome, root, trigger)

    assert result["why"] == "bad_guid"
    assert result["file"] is None
    assert [p.name for p in _files_under(root)] == ["not-a-guid!"]


async def test_a_session_that_cannot_be_opened_is_named(enabled, chrome, root):
    class _Refusing(FakeBrowser):
        async def new_browser_cdp_session(self):
            raise ConnectionError("no browser target")

    async def trigger():
        raise AssertionError("the trigger ran without a session")

    result = await cdp_download.capture_download(
        _Refusing(chrome), trigger, label="profile", root=root
    )
    assert result["why"] == "session_failed"
    assert result["error"] == "ConnectionError"
    assert result["behaviour_restored"] is None


async def test_a_behaviour_that_cannot_be_set_is_named_and_still_restored(
    enabled, chrome, root
):
    """The set RAISED, so whether Chrome applied it is unknown -- restore anyway."""
    class _Dropping(FakeBrowser):
        async def new_browser_cdp_session(self):
            session = await super().new_browser_cdp_session()
            session.fail_on.add("Browser.setDownloadBehavior")
            return session

    async def trigger():
        raise AssertionError("the trigger ran with no behaviour set")

    result = await cdp_download.capture_download(
        _Dropping(chrome), trigger, label="profile", root=root
    )
    assert result["why"] == "behaviour_not_set"
    assert result["behaviour_restored"] is False
    assert result["restore_error"] == "ConnectionError"
    assert [m for m, _ in chrome.sessions[0].sent] == [
        "Browser.setDownloadBehavior", "Browser.setDownloadBehavior",
    ]
    assert chrome.sessions[0].detached is True


# ---------------------------------------------------------------------------
# 4. THE CLOSED TABLE, AND THE PACKAGE'S DEVTOOLS SITES PINNED BY AST
# ---------------------------------------------------------------------------


async def test_a_method_off_the_table_is_refused_and_never_sent(chrome):
    session = FakeSession(chrome)
    with pytest.raises(cdp_download.CdpMethodRefused):
        await cdp_download._send(session, "Runtime.evaluate", {"expression": "1"})
    assert session.sent == []


def _devtools_sites(sources: dict[str, str]) -> dict[str, list[tuple[str, str]]]:
    """Every ``X.send(...)`` and ``X.new_browser_cdp_session(...)`` call, by AST.

    Returns ``{"send": [(module, enclosing function)], "session": [...]}``,
    attributed to the INNERMOST enclosing function by the shipped
    ``readonly.enclosing_function`` -- the same attribution the mutation
    allowlist uses, rather than a second copy of it. Calls, never mentions: a
    docstring naming a method is not a call.
    """
    from linkedin_server import readonly

    out: dict[str, list[tuple[str, str]]] = {"send": [], "session": []}
    for name, source in sources.items():
        for node in ast.walk(ast.parse(source)):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            key = {"send": "send", "new_browser_cdp_session": "session"}.get(
                node.func.attr
            )
            if key is None:
                continue
            owner = readonly.enclosing_function(source, node.lineno) or "<module>"
            out[key].append((name, owner))
    return {key: sorted(sites) for key, sites in out.items()}


def _package_sources() -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(PACKAGE.glob("*.py"))
    }


def test_the_site_detector_finds_a_planted_devtools_call():
    """THE CONTROL for the pin below: a second ``send`` must be SEEN."""
    planted = {
        "cdp_download.py": "async def _send(s, m, p):\n    return await s.send(m, p)\n",
        "elsewhere.py": (
            "async def sneak(b):\n"
            "    s = await b.new_browser_cdp_session()\n"
            "    await s.send('Input.dispatchMouseEvent', {})\n"
        ),
    }
    sites = _devtools_sites(planted)
    assert ("elsewhere.py", "sneak") in sites["send"]
    assert sites["session"] == [("elsewhere.py", "sneak")]


def test_the_package_has_exactly_one_devtools_send_and_two_session_sites():
    """``scan_source_for_mutations`` has no DevTools pattern; this pin stands in.

    Exactly one ``send``, in ``cdp_download._send``, which refuses anything
    off :data:`cdp_download.CDP_METHODS`; exactly two sessions, the capture's
    and the attach-time reset's, both in this module. A further site
    anywhere in the package is a new capability and fails here.
    """
    sites = _devtools_sites(_package_sources())
    assert sites["send"] == [("cdp_download.py", "_send")], sites["send"]
    assert sites["session"] == [
        ("cdp_download.py", "capture_download"),
        ("cdp_download.py", "reset_download_behaviour"),
    ], sites["session"]
    assert cdp_download.CDP_METHODS == frozenset({"Browser.setDownloadBehavior"})


def test_the_transport_module_creates_no_context_and_adopts_none():
    """D4: the transport attaches to what is there. It makes and adopts nothing."""
    source = (PACKAGE / "cdp_download.py").read_text(encoding="utf-8")
    for token in ("new_context", "launch_persistent_context", "client.contexts",
                  "new_page", "goto("):
        assert token not in source, token


def test_every_why_the_capture_can_return_is_in_the_closed_vocabulary():
    """Read off the source, so a new refusal cannot skip the table."""
    source = (PACKAGE / "cdp_download.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    returned: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_refused" and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)):
            returned.add(node.args[1].value)
    returned.add("saved")
    assert returned == set(cdp_download.WHY), sorted(returned ^ set(cdp_download.WHY))


# ---------------------------------------------------------------------------
# 5. THE RESET AT ATTACH -- his downloads handed back to his own Chrome
# ---------------------------------------------------------------------------
#
# The library's handshake sets ``allowAndName`` on his default context, into a
# temporary directory it deletes on disconnect. ``cdp_bridge.attach`` calls
# ``reset_download_behaviour`` straight after; ``tests/test_cdp_attach.py``
# shows the attach sending it. These show what it does to the fake Chrome.


def _the_library_took_his_downloads(chrome: FakeChrome, tmp_path) -> pathlib.Path:
    """What the library's own handshake does, per its driver source."""
    artifacts = tmp_path / "library-artifacts"
    artifacts.mkdir()
    chrome.set_behaviour(FakeSession(chrome), {
        "behavior": "allowAndName",
        "downloadPath": str(artifacts),
        "eventsEnabled": True,
    })
    return artifacts


async def test_control_after_the_handshake_alone_his_file_lands_in_the_librarys_folder(
    chrome, tmp_path
):
    """THE HAZARD, in the fake, as the control: with no reset, his own
    download is written under a GUID into the folder the library deletes."""
    artifacts = _the_library_took_his_downloads(chrome, tmp_path)
    chrome.download(b"his own file", suggested="his-own.bin")

    assert _files_under(chrome.user_downloads) == []
    assert len(_files_under(artifacts)) == 1


async def test_the_reset_hands_his_downloads_back_to_chromes_own_behaviour(
    chrome, tmp_path
):
    artifacts = _the_library_took_his_downloads(chrome, tmp_path)

    outcome = await cdp_download.reset_download_behaviour(FakeBrowser(chrome))

    assert outcome == {"restored": True, "error": None}
    assert chrome.behaviour == "default"
    (session,) = chrome.sessions
    assert session.sent == [("Browser.setDownloadBehavior", {"behavior": "default"})]
    assert session.detached is True
    chrome.download(b"his own file", suggested="his-own.bin")
    assert [p.name for p in _files_under(chrome.user_downloads)] == ["his-own.bin"]
    assert _files_under(artifacts) == []


async def test_the_reset_is_not_behind_the_capture_switch(chrome, tmp_path):
    """The switch gates TAKING a download. The reset gives his back."""
    assert cdp_download.downloads_enabled() is False
    _the_library_took_his_downloads(chrome, tmp_path)

    outcome = await cdp_download.reset_download_behaviour(FakeBrowser(chrome))

    assert outcome["restored"] is True
    assert chrome.behaviour == "default"


async def test_a_reset_with_no_devtools_session_says_so():
    assert await cdp_download.reset_download_behaviour(None) == {
        "restored": False, "error": "no_cdp_session",
    }


async def test_a_reset_that_raises_is_named_by_type_and_its_session_detached(chrome):
    class _Dropping(FakeBrowser):
        async def new_browser_cdp_session(self):
            session = await super().new_browser_cdp_session()
            session.fail_on.add("Browser.setDownloadBehavior")
            return session

    outcome = await cdp_download.reset_download_behaviour(_Dropping(chrome))

    assert outcome == {"restored": False, "error": "ConnectionError"}
    assert chrome.sessions[0].detached is True


async def test_a_reset_that_hangs_is_abandoned_within_its_bound(chrome):
    """A wedged browser must not hang the attach."""
    class _Hanging(FakeBrowser):
        async def new_browser_cdp_session(self):
            await asyncio.Event().wait()

    outcome = await cdp_download.reset_download_behaviour(
        _Hanging(chrome), timeout_s=0.05
    )

    assert outcome == {"restored": False, "error": "TimeoutError"}
