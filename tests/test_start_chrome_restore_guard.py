"""scripts/start_chrome.ps1 never lets a crashed profile offer its session back.

WHY. The operator saw a "Restore pages?" bubble on the dedicated Chrome after every live
session (2026-11-28). Measured that day on a throwaway Chromium: a RUNNING profile reads
``exit_type: Crashed``; Chrome's own orderly shutdown (CDP ``Browser.close``) rewrites it
``Normal``; a kill leaves ``Crashed``, and the next start offers the crashed session back --
tabs that could load LinkedIn outside both ledgers. So the script, ONLY while no Chrome has the
profile open, sets two values back -- ``profile.exit_type`` (Crashed to Normal) and
``profile.exited_cleanly`` (false to true) -- and nothing else. It is JSON-AWARE: the file is
parsed; each value changes by its one literal, which must occur exactly once; the result is parsed
again and compared with the original, every other key included, before anything is written; it is
written beside the file without a BOM and swapped in, and reported before and after. It passes
``--hide-crash-restore-bubble``, READS the startup setting from both ``Preferences`` and ``Secure
Preferences`` (never edits either), refuses to start under ``-RefuseSessionRestore`` when the
profile would reopen pages or cannot be read to rule that out, and reports the browser's own PID.

The script is PowerShell and starts a real Chrome, so CI cannot run it. These tests read the
script's own CODE (its comment lines stripped, so a comment can neither satisfy nor trip them),
where its structure lives; the live lane ran the guard itself behaviourally on synthetic profiles
(``_audit/2026-11-27-live-session-14.md``, section 11).
"""
from __future__ import annotations

import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "start_chrome.ps1"


def _text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _code(text: str) -> str:
    """The text without its whole-line comments."""
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _arguments(text: str) -> list[str]:
    block = re.search(r"\$arguments = @\((.*?)\n\)", text, flags=re.S)
    assert block, "the argument list is not drawn as one @( ... ) block"
    return [ln.strip().strip('"') for ln in block.group(1).splitlines() if ln.strip()]


def _guard() -> str:
    """The restore guard's CODE: from its section marker to the argument list."""
    text = _text()
    return _code(text[text.index("# --- 3c."):text.index("$arguments = @(")])


def test_the_argument_list_is_the_port_the_profile_and_the_restore_bubble_switch() -> None:
    args = _arguments(_text())
    assert len(args) == 3, args
    assert args[0].startswith("--remote-debugging-port=")
    assert args[1].startswith("--user-data-dir=")
    assert args[2] == "--hide-crash-restore-bubble"
    assert not any("automation" in a or "webdriver" in a for a in args), args


def test_only_the_two_values_are_changed_each_by_one_exact_literal_while_no_chrome_has_the_profile() -> None:
    text = _text()
    guard = _guard()
    write = guard.index("WriteAllText($tmpFile")
    edits = re.findall(r"\$edits \+= ,@\(('[^']*'), ('[^']*')\)", guard)
    assert edits == [("'\"exit_type\":\"Crashed\"'", "'\"exit_type\":\"Normal\"'"),
                     ("'\"exited_cleanly\":false'", "'\"exited_cleanly\":true'")], edits
    assert guard.count("$edits +=") == 2, "no third edit"
    assert guard.rfind("Get-ChromeOnProfile -Dir $ProfileDir", 0, write) != -1, "no Chrome-on-this-profile check first"
    assert guard.rfind("(Get-LiteralCount -Text $fixed -Needle $e[0]) -ne 1", 0, write) != -1, (
        "each literal must occur exactly once to be changed")
    assert text.index("Start-Process -FilePath $ChromeExe") > text.index("# --- 3c."), "the guard runs before the launch"


def test_the_change_is_parsed_again_and_compared_with_the_original_before_anything_is_written() -> None:
    guard = _guard()
    write = guard.index("WriteAllText($tmpFile")
    for needle in ("$prefs = $prefsText | ConvertFrom-Json", "$after = $fixed | ConvertFrom-Json",
                   "$origCopy = $prefsText | ConvertFrom-Json",
                   "$o.profile.PSObject.Properties.Remove('exit_type')",
                   "$o.profile.PSObject.Properties.Remove('exited_cleanly')",
                   "($origCopy | ConvertTo-Json -Depth 100 -Compress) -ne ($after | ConvertTo-Json -Depth 100 -Compress)"):
        at = guard.find(needle)
        assert at != -1 and at < write, needle
    assert "catch { $prefs = $null }" in guard and "$exitAfter = 'left: unparsable'" in guard, (
        "a Preferences that does not parse is left as it is")


def test_the_write_keeps_chromes_encoding_and_swaps_the_file_in() -> None:
    guard = _guard()
    assert "New-Object System.Text.UTF8Encoding($false)" in guard, "Preferences must be written without a BOM"
    assert "Set-Content" not in guard and "Out-File" not in guard, "either would write Windows PowerShell's encoding"
    assert "[System.IO.File]::Replace($tmpFile, $prefsFile, [NullString]::Value)" in guard, (
        "written beside it and swapped in; $null would reach .NET as an empty backup name")


def test_a_startup_that_would_reopen_pages_is_read_never_edited_and_refused_under_the_switch() -> None:
    text = _text()
    guard = _guard()
    assert "[switch] $RefuseSessionRestore" in text
    assert "restore_on_startup" in guard and "startup_urls" in guard
    assert "if ($prefsUnreadable -or $restoreAsks -or $startupUrlsOnLinkedin -gt 0) {" in guard
    assert guard.count("$prefsUnreadable = $true") == 2, (
        "neither preferences file that cannot be read can rule a reopen out")
    branch = guard[guard.index("if ($RefuseSessionRestore) {"):]
    branch = branch[:branch.index("}") + 1]
    assert "exit 5" in branch and "Write-Error" not in branch, (
        "under the file's 'Stop', Write-Error would end the script as exit 1 before exit 5")
    assert not re.search(r"\.restore_on_startup\s*=[^=]", guard), (
        "the startup setting is a protected pref: read it, never edit it")


def test_the_startup_setting_is_read_from_secure_preferences_too_and_that_file_is_never_written() -> None:
    """On Windows Chrome keeps a tracked pref's VALUE in Secure Preferences, not Preferences (the
    review's round 5, read on the operator's profile: 12 of 12 tracked values that hold one hold it
    there). A read of Preferences alone records "absent" exactly when the setting is set."""
    guard = _guard()
    assert '$securePrefsFile = Join-Path $ProfileDir "Default\\Secure Preferences"' in guard
    assert "[System.IO.File]::ReadAllText($securePrefsFile) | ConvertFrom-Json" in guard
    assert "$sources += ,@('secure', $secure)" in guard and "$sources += ,@('preferences', $prefs)" in guard
    assert "if ($value -eq 1) { $restoreAsks = $true }" in guard, "a value of 1 in EITHER file asks to reopen"
    uses = [ln.strip() for ln in guard.splitlines() if "$securePrefsFile" in ln]
    assert len(uses) == 3, uses  # defined, tested for, read: never written or replaced
    assert not any("Write" in ln or "Replace" in ln or "Move" in ln for ln in uses), uses


def test_what_changed_and_what_was_read_are_reported() -> None:
    text = _text()
    report = text[text.rindex("outcome            = 'started'"):]
    for key in ("exit_type_before   = $exitBefore", "exit_type_after    = $exitAfter",
                "restore_on_startup = $restoreOnStartup", "restore_on_startup_in = $restoreOnStartupIn",
                "startup_urls       = $startupUrls", "startup_urls_on_linkedin = $startupUrlsOnLinkedin"):
        assert key in report, key


def test_the_reported_pid_is_the_browser_never_a_helper() -> None:
    text = _text()
    helper = text[text.index("function Get-BrowserOnProfile"):]
    helper = helper[:helper.index("\n}\n") + 3]
    assert "--remote-debugging-port=$P" in helper and "-notmatch '--type='" in helper
    assert text.count("$owner = Get-BrowserOnProfile -Dir $ProfileDir -P $Port") == 2
    assert "$owner = Get-ChromeOnProfile" not in text
