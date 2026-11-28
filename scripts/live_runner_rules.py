"""The live runner's identity-free PURE rules, tracked so that CI runs their checks.

WHY THIS FILE EXISTS. The live lane's session runner and its Chrome teardown live in gitignored
state (``_state/live-runner/<session>/``). The runner names this machine's paths, loads the job
pipeline from the installed skill, and carries the session's plan. Its red-first check sets
therefore ran only on the operator's machine: 74 minutes of waits on the real clock, and about
9.5 minutes in check mode, before session 14b (``_audit/2026-11-27-live-session-14.md``, 11.7).
Lane ci-checks28 (``_audit/2026-11-28-live-runner-checks-on-ci.md``) moved the checks whose
subject is PURE into tracked tests, which free CI runs on every cell. This module is that subject.

TWO KINDS OF CONTENT, and the difference matters to anyone who changes either:

* VERBATIM. The text session 14b's runner (r3e, ``runner_s14b.py``) or its teardown
  (``close_chrome_s14b.py``) runs, byte for byte: ``FORM_SIGS_JS`` and ``FORM_DELTA_JS``,
  the panel rule's evidence; ``SECTION_DIGEST_JS``, a region's digest; ``PUBLISH_WORDS`` and
  ``PANEL_CLOSE_WORDS``; ``press_landing``; ``user_data_dir_of``. The lane checked each against
  the pinned files by source segment (its record, section 4).
* RE-CUT. The same decisions as the runner's and the teardown's, with the reads they made passed
  in, so that nothing here touches a port, a process or a file:

  - ``judge_command_line`` is the teardown's ``judged`` minus its process read;
  - ``teardown_preclose`` is the teardown's ``main`` up to the close;
  - ``dedicated_listener`` is the runner's ``_dedicated_listener``;
  - ``browser_digest`` is ``_browser_instance``;
  - ``tabs_reading``, ``unanswered_reading`` and ``tabs_stop`` are ``tabs_check``;
  - ``tabs_gate`` is ``_tabs_gate``.

  ONE NAMED DIFFERENCE: ``norm_profile_path`` reads a path as a WINDOWS path
  (``PureWindowsPath``). The teardown's ``_norm`` uses ``Path``, which on Windows, the only
  platform the teardown runs on, IS a Windows path. On ubuntu a ``Path`` would leave a backslash
  in a segment, so this keeps the decision the same on every CI cell.

WHAT IS NOT HERE, and why. The runner's page code: its phases, its one click site, the close path
(``close_all``), the meter around ``BROWSER.goto``. It is neither pure nor small. Tracking it is
the proposal's own first step, "the runner's tracked, path-free form", which no ruling has ordered.
Its checks stay local; the lane's record lists them by name.

THE PINNED RUNNER DOES NOT IMPORT THIS MODULE. Session 14b's runner and teardown are pinned by
sha256 for a live sitting, and each keeps its own copy. This module is the tracked source a later
session's runner imports in their place. From then on, these tests guard the code the session
runs.

Importing this module does nothing: no call, no read, no write (``tests/test_scripts_are_import_safe.py``).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import PureWindowsPath
from typing import Any, Callable, Optional
from urllib.parse import parse_qs, urlsplit

from linkedin_server import self_profile

# ---------------------------------------------------------------------------------------------
# The panel rule's evidence (runner F, 14b r1b K3, r2b MINOR-A), VERBATIM.
# ---------------------------------------------------------------------------------------------

#: F. A PANEL DRAWN OUTSIDE ANY DIALOG (session 12, finding 4: All filters on
#: both people searches and the content search) flips no aria-expanded and
#: draws no popup, so session 12's close rule read "nothing_opened" and left it
#: open. Its evidence here is the FORM CONTROLS it adds, as a multiset of
#: signatures (tag, type, role, name), so a toolbar that re-renders its own
#: pills adds nothing, and a page hydrating headings and links (session 11's
#: false stop of 23:23) adds nothing either. Counted in the page; no name
#: crosses. A visually hidden input counts by its own label's visibility.
FORM_SIGS_JS = r"""
() => {
  const norm = (s) => (s || "").replace(/\s+/g, " ").trim().slice(0, 80);
  const shown = (e) => !!e && (!e.checkVisibility || e.checkVisibility({visibilityProperty: true}));
  const SEL = 'input[type=checkbox], input[type=radio], [role=checkbox], [role=radio], [role=switch], select, input[type=range]';
  const labelOf = (e) => (e.id ? document.querySelector('label[for="' + CSS.escape(e.id) + '"]') : null) || e.closest("label");
  const m = new Map();
  for (const e of document.querySelectorAll(SEL)) {
    const l = labelOf(e);
    if (!(shown(e) || (l && shown(l)))) continue;
    const name = norm(e.getAttribute("aria-label")) || (l ? norm(l.textContent) : "") || norm(e.textContent);
    const s = e.tagName.toLowerCase() + "|" + (e.getAttribute("type") || "") + "|" + (e.getAttribute("role") || "") + "|" + name;
    m.set(s, (m.get(s) || 0) + 1);
  }
  // 14b r1b (K3, round 1's MINOR-1): the sections of main that exist NOW, kept with the snapshot
  // under a key no signature can take, so the delta can tell a section rendered after the press.
  m.set("\u0000main_sections", new Set(document.querySelectorAll("main section")));
  return m;
}
"""

FORM_DELTA_JS = r"""
(before) => {
  const norm = (s) => (s || "").replace(/\s+/g, " ").trim().slice(0, 80);
  const shown = (e) => !!e && (!e.checkVisibility || e.checkVisibility({visibilityProperty: true}));
  const SEL = 'input[type=checkbox], input[type=radio], [role=checkbox], [role=radio], [role=switch], select, input[type=range]';
  const labelOf = (e) => (e.id ? document.querySelector('label[for="' + CSS.escape(e.id) + '"]') : null) || e.closest("label");
  const now = new Map();
  const kindOf = new Map();
  const had = (before && before.get("\u0000main_sections")) || null;
  // 14b r2b (round 2's MINOR-A): "late" also needs main's sections to have GROWN over the press; a
  // section the press REDRAWS keeps the count, so a panel drawn in it stays evidence.
  const grew = !!had && document.querySelectorAll("main section").length > had.size;
  for (const e of document.querySelectorAll(SEL)) {
    const l = labelOf(e);
    if (!(shown(e) || (l && shown(l)))) continue;
    const name = norm(e.getAttribute("aria-label")) || (l ? norm(l.textContent) : "") || norm(e.textContent);
    // 14b r1b (K3): a control whose nearest section of main did NOT exist at the snapshot is the
    // page rendering on (session 14's photo press: 5 checkboxes in sections drawn after it);
    // a control in a section that existed, a panel revealed in place included, is evidence.
    const sec = e.closest("main section");
    const late = !!sec && !!had && !had.has(sec) && grew;
    const s = (late ? "late:" : "") + e.tagName.toLowerCase() + "|" + (e.getAttribute("type") || "") + "|" + (e.getAttribute("role") || "") + "|" + name;
    now.set(s, (now.get(s) || 0) + 1);
    const t = (e.getAttribute("type") || e.getAttribute("role") || e.tagName.toLowerCase());
    kindOf.set(s, ["checkbox", "radio", "switch", "select", "range"].includes(t) ? t : "other");
  }
  let added = 0;
  let in_new_sections = 0;
  const kinds = {};
  for (const [s, n] of now) {
    const more = n - ((before && before.get(s)) || 0);
    if (more <= 0) continue;
    if (s.startsWith("late:")) { in_new_sections += more; continue; }
    added += more; const k = kindOf.get(s); kinds[k] = (kinds[k] || 0) + more;
  }
  return {added, kinds, in_new_sections};
}
"""

# ---------------------------------------------------------------------------------------------
# A region's digest (MAJOR-4, MINOR-C), VERBATIM.
# ---------------------------------------------------------------------------------------------

SECTION_DIGEST_JS = r"""
(el) => {
  const norm = (s) => (s || "").replace(/\s+/g, " ").trim();
  // MAJOR-4 (the cold review): the region's CONTROL STATES are digested with its text,
  // so a toggle's flip is a change.
  // MINOR-C (the warm re-check): the value ITSELF and a select's index -- only the digest crosses.
  const states = Array.from(el.querySelectorAll("input, select, textarea, [aria-checked], [aria-pressed], [aria-selected]"))
    .map((c) => [c.tagName, c.type || "", c.checked === true ? 1 : 0, c.getAttribute("aria-checked") || "",
                 c.getAttribute("aria-pressed") || "", c.getAttribute("aria-selected") || "",
                 typeof c.selectedIndex === "number" ? c.selectedIndex : "", c.value || ""].join(":")).join("|");
  let x = 0x811c9dc5; const s = norm(el.innerText) + "#" + states;
  for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 0x01000193) >>> 0; }
  return ("0000000" + x.toString(16)).slice(-8);
}
"""

# ---------------------------------------------------------------------------------------------
# The words a press may never aim at, and the words a panel may be closed by, VERBATIM.
# ---------------------------------------------------------------------------------------------

PUBLISH_WORDS = frozenset({
    "Publish", "Publish now", "Schedule", "Schedule post", "Schedule for later", "Post",
    "Post now", "Share", "Repost", "Send", "Submit", "Apply", "Confirm", "Save", "Done",
    "Follow", "Subscribe", "Unsubscribe", "Delete", "Remove", "Upload", "Accept", "Ignore",
})

PANEL_CLOSE_WORDS = ("Close", "Dismiss", "Cancel", "Back", "Hide filters", "Close filters",
                     "Close all filters", "Exit")
# MINOR-4 (the cold review): never a word PUBLISH_WORDS forbids as an aim.
assert not set(PANEL_CLOSE_WORDS) & PUBLISH_WORDS

# ---------------------------------------------------------------------------------------------
# Where a self-root press went (the cold review's MAJOR-1, the warm re-check's NIT-A), VERBATIM.
# ---------------------------------------------------------------------------------------------


def press_landing(now_url: str, raw: str, member: str, root_path: str, loaded: bool) -> str:
    """PURE (the cold review's MAJOR-1). Where a self-root press went, against the
    target the matcher matched: ``target`` -- the as-drawn path or its alias
    form, with the target's own query when a document loaded; ``his_root`` --
    his root's own path (an in-page opening that routed nowhere, or a document
    LinkedIn redirected home, as session 12 measured for direct loads); else
    ``not_its_target``. The query is compared in process and never printed."""
    try:
        t, n = urlsplit(raw), urlsplit(str(now_url or ""))
    except ValueError:
        return "not_its_target"
    if (n.scheme, n.netloc) != ("https", "www.linkedin.com") or n.fragment:
        return "not_its_target"
    alias = "/in/" + self_profile.SELF_ALIAS + "/"
    mine = "/in/" + member + "/"
    forms = {t.path, t.path.replace(mine, alias, 1), t.path.replace(alias, mine, 1)}
    if n.path in forms:
        if not loaded:
            return "target"
        # NIT-A (the warm re-check): each of the target's OWN parameters must be there with
        # exactly its value, once; a key LinkedIn adds on landing is not a veto.
        want, got = parse_qs(t.query, keep_blank_values=True), parse_qs(n.query, keep_blank_values=True)
        return "target" if all(got.get(k) == v for k, v in want.items()) else "not_its_target"
    if n.path in (root_path, mine, alias):
        return "his_root"
    return "not_its_target"


# ---------------------------------------------------------------------------------------------
# Which browser may be closed (the teardown, round 4's NIT-4, round 5's NIT-6).
# ---------------------------------------------------------------------------------------------


def norm_profile_path(path: str) -> str:
    """The teardown's ``_norm``, read as a WINDOWS path on every platform (the named difference in
    this module's docstring): separators as backslashes, no trailing one, case-folded."""
    return str(PureWindowsPath(path)).replace("/", "\\").rstrip("\\").lower()


def user_data_dir_of(cmd: str) -> str:
    """The WHOLE value of ``--user-data-dir=`` on a command line, quoted or bare; '' when absent."""
    m = re.search(r'--user-data-dir=(?:"([^"]+)"|(\S+))', cmd)
    return (m.group(1) or m.group(2)) if m else ""


def judge_command_line(read: Optional[tuple[str, str]], port: int, profile: str) -> tuple[bool, str]:
    """The teardown's ``judged(pid, port, profile)`` with its process read passed in: ``read`` is
    ``command_line_of(pid)``, an (image name, command line) pair, ``('', '')`` when the process is
    gone, or None when the OS could not be read in time.

    True only for chrome.exe started with THIS debugging port and EXACTLY this profile (round 4's
    NIT-4b: the whole --user-data-dir value, never a substring, so a profile that only starts with
    this one's path is refused)."""
    if read is None:
        return False, "the process could not be read"
    name, cmd = read
    if not name:
        return False, "no such process"
    if name.lower() != "chrome.exe":
        return False, "not chrome.exe"
    if not re.search(r"--remote-debugging-port=" + str(int(port)) + r"(\s|$)", cmd):
        return False, "not this debugging port"
    got = user_data_dir_of(cmd)
    if not got or norm_profile_path(got) != norm_profile_path(profile):
        return False, "not this profile"
    return True, "the dedicated browser"


def teardown_preclose(pid: int, port: int, profile: str, read: Optional[tuple[str, str]],
                      owners: Optional[set[int]]) -> tuple[Optional[int], dict[str, Any]]:
    """The teardown's ``main`` up to the close, with its two OS reads passed in: ``read`` is the
    PID's ``command_line_of``, and ``owners`` is ``port_owners(port)``, every PID listening on the
    port, or None when that read failed.

    Returns ``(2, report)`` for a refusal, the report being the one the tool prints and exits 2 on,
    or ``(None, report)`` when the close may go ahead. Nothing is closed for any process but the
    judged one. The port's ONE listener must be that same PID (round 4's NIT-4, as ruled): another
    listener, two, or none, and nothing is closed or killed. A listener read that failed is a
    refusal too (round 5's NIT-6), never a traceback."""
    out: dict[str, Any] = {"pid": pid, "port": port}
    ok, why = judge_command_line(read, port, profile)
    out["judged"] = why
    if not ok:
        out["path"] = "refused"
        return 2, out
    if owners is None:
        out["path"] = "refused_listener_read_failed"
        return 2, out
    out["port_listeners"] = len(owners)
    out["port_owner_is_the_pid"] = owners == {pid}
    if owners != {pid}:
        out["path"] = "refused_port_held_by_another" if owners else "refused_no_listener_on_the_port"
        return 2, out
    return None, out


# ---------------------------------------------------------------------------------------------
# Which browser may be attached, and when load 1 may be made (the tabs check: r3, r3c NIT-3,
# r3e NIT-7).
# ---------------------------------------------------------------------------------------------

BLANK_PAGES = ("about:blank", "chrome://newtab/", "chrome://new-tab-page/")


def dedicated_listener(owners: Optional[set[int]], read_of: Callable[[int], Optional[tuple[str, str]]],
                       port: int, profile: str) -> tuple[bool, str, int]:
    """The runner's ``_dedicated_listener(port)`` with the teardown's two reads passed in:
    ``owners`` is ``port_owners(port)`` and ``read_of`` is ``command_line_of``. Returns
    ``(ok, why, listeners)``. ok only when the port has exactly ONE listening PID, on every
    address, and that PID is chrome.exe started with this port and EXACTLY the dedicated profile.
    A read that fails is not ok."""
    if owners is None:
        return False, "the listener read failed", -1
    if len(owners) != 1:
        return False, str(len(owners)) + " listening processes on the port", len(owners)
    ok, why = judge_command_line(read_of(next(iter(owners))), port, profile)
    return ok, why, 1


def browser_digest(version: Any) -> Optional[str]:
    """The runner's ``_browser_instance(port)`` with its read passed in: ``version`` is the parsed
    answer of the DevTools port's ``/json/version``, or None when the port did not answer. Returns
    a 16-hex digest of the browser endpoint it names, one value per launch of the browser, or None
    when it names none. The endpoint itself is never kept or returned."""
    ws = version.get("webSocketDebuggerUrl") if isinstance(version, dict) else None
    return hashlib.sha256(str(ws).encode("utf-8")).hexdigest()[:16] if ws else None


def tabs_reading(targets: Any, browser: Optional[str], dedicated: bool, listeners: int,
                 at: str) -> dict[str, Any]:
    """The reading ``tabs_check`` keeps, from the port's ``/json/list`` (``targets``), the browser
    digest and the listener's verdict: COUNTS only. No address, title or target is kept."""
    pages = [t for t in (targets if isinstance(targets, list) else []) if isinstance(t, dict) and t.get("type") == "page"]
    on_linkedin = sum(1 for t in pages if (urlsplit(str(t.get("url") or "")).hostname or "").endswith("linkedin.com"))
    blank = sum(1 for t in pages if str(t.get("url") or "") in BLANK_PAGES)
    return {"answered": True, "pages": len(pages), "on_linkedin": on_linkedin, "blank_or_new_tab": blank,
            "browser": browser, "dedicated": dedicated, "listeners": listeners, "at": at}


def unanswered_reading(at: str) -> dict[str, Any]:
    """The reading ``tabs_check`` keeps when the port did not answer: never a stale count."""
    return {"answered": False, "at": at}


def tabs_stop(reading: dict[str, Any], port: int, dedicated_why: str = "", error: str = "") -> Optional[str]:
    """``tabs_check``'s verdict on a reading: the STOP sentence it says (and exits 4 on), or None
    when load 1 may follow. Exactly one page, none on LinkedIn, a browser endpoint named, and the
    port's one listener the dedicated profile's browser: a tab the runner did not open (a restored
    session's, say) could load LinkedIn outside both ledgers. ``error`` names the failed read's
    type when the port did not answer; ``dedicated_why`` is ``dedicated_listener``'s why."""
    if reading.get("answered") is not True:
        return "STOP before load 1: the DevTools port " + str(port) + " did not answer (" + error + ")"
    if reading.get("browser") is None:
        return "STOP before load 1: the DevTools port " + str(port) + " names no browser endpoint"
    if not reading.get("dedicated"):
        return ("STOP before load 1: the DevTools port's listener is not the dedicated profile's browser ("
                + dedicated_why + ")")
    pages, on_linkedin = reading.get("pages"), reading.get("on_linkedin")
    if pages != 1 or on_linkedin:
        return ("STOP before load 1: " + ("not exactly one tab open" if pages != 1 else "")
                + (" and " if pages != 1 and on_linkedin else "")
                + ("a LinkedIn tab the runner did not open" if on_linkedin else ""))
    return None


def tabs_gate(reading: Any, reading_mtime: Optional[float], flag_mtime: Optional[float],
              now: Optional[str]) -> Optional[str]:
    """The runner's ``_tabs_gate()``, which the meter asks before load 1 of a session, with its
    reads passed in: ``reading`` is the kept tabs_check reading (anything else when there is none),
    ``reading_mtime`` its file's time (None when it cannot be read), ``flag_mtime`` the session
    flag's time (None when no flag stands), and ``now`` the ``browser_digest`` the port names now.

    None when THIS session's tabs_check passed -- answered, exactly one page, none on LinkedIn, the
    dedicated profile's browser -- was written after this session's flag was raised, and was taken
    on the browser launch the port names now; else why not."""
    if not isinstance(reading, dict):
        return "no tabs_check in this session (run tabs_check after flag_on)"
    if not (reading.get("answered") is True and reading.get("pages") == 1 and reading.get("on_linkedin") == 0
            and reading.get("dedicated") is True):
        return "this session's tabs_check did not pass"
    if flag_mtime is None:
        return "the tabs_check is older than this session's flag (run it again after flag_on)"
    if reading_mtime is None:
        return "the tabs_check's time cannot be read"
    if reading_mtime < flag_mtime:
        return "the tabs_check is older than this session's flag (run it again after flag_on)"
    if now is None:
        return "the DevTools port names no browser endpoint now"
    if reading.get("browser") != now:
        return "the tabs_check was taken on another launch of the browser (run it again)"
    return None
