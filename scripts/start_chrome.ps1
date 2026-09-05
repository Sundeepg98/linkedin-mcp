<#
.SYNOPSIS
    Start the Chrome that the LinkedIn MCP server attaches to. Idempotent.

.DESCRIPTION
    In ATTACH mode the server owns no browser: it connects over CDP to a Chrome
    that something else started. This script is that something else.

    It is idempotent in the only sense that matters -- it asks the DevTools port
    whether a browser is already answering, and if one is it changes nothing and
    says so. It never starts a second Chrome on a profile, and it never touches
    the operator's own Chrome.

    THREE THINGS IT REFUSES, each because the failure is silent otherwise:

    1. A LIVE PROFILE LOCK. `_state/chrome-profile.lock` naming a running PID
       means the stdio MCP server has the profile open. Two processes on one
       Chromium user-data-dir corrupt it and the session is lost. The stdio
       server must stop BEFORE this script runs -- that ordering is the whole
       reason the cutover runbook has an order.

    2. A CHROME ALREADY ON THIS PROFILE WITHOUT THE PORT. Chrome's singleton
       hands the command line to the running instance and exits zero, so a
       second `chrome.exe --remote-debugging-port=...` against a profile Chrome
       already has open opens NO port and reports NO error. If the port does not
       come up, this script looks for that process and says which one it is
       rather than leaving a timeout to be misread as a slow start.

    3. A MISSING chrome.exe, named with the path it looked at.

    WHICH PROFILE, AND WHY IT IS THE SERVER'S OWN. The default is
    `_state/chrome-profile`, where his signed-in LinkedIn session already lives.
    A separate `--user-data-dir` is what keeps his everyday Chrome out of this:
    the singleton is per-profile, so his windows are untouched and this one is
    its own instance. A blank profile would also avoid the collision but would
    be signed into nothing, which is the opposite of the point.

    THE FLAG LIST IS TWO ENTRIES and matches the server's posture: the debugging
    port, and the profile to use. No automation flag is passed. Real Chrome
    started this way does not set `navigator.webdriver` -- measured, not
    assumed; see the cutover audit note.

.PARAMETER Port
    DevTools port. Default 9224, which is what config.CDP_PORT resolves to.

.PARAMETER ProfileDir
    Chrome user-data-dir. Default `<repo>/_state/chrome-profile`.

.PARAMETER ChromeExe
    Path to chrome.exe. Default is the standard 64-bit install location.

.PARAMETER TimeoutSec
    How long to wait for the DevTools port after launching. Default 30.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_chrome.ps1

.EXAMPLE
    # A throwaway profile on a throwaway port, for testing.
    .\scripts\start_chrome.ps1 -Port 9324 -ProfileDir C:\Temp\test-profile
#>
[CmdletBinding()]
param(
    [int]    $Port        = 9224,
    [string] $ProfileDir  = "",
    [string] $ChromeExe   = "C:\Program Files\Google\Chrome\Application\chrome.exe",
    [int]    $TimeoutSec  = 30
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not $ProfileDir) { $ProfileDir = Join-Path $RepoRoot "_state\chrome-profile" }
$LockFile = "$ProfileDir.lock"

function Read-DevToolsVersion {
    param([int] $P)
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$P/json/version" `
            -UseBasicParsing -TimeoutSec 3
        return ($response.Content | ConvertFrom-Json)
    } catch {
        return $null
    }
}

function Get-ChromeOnProfile {
    param([string] $Dir)
    # Chrome quotes the value it was given; match on the directory text so both
    # quoted and bare spellings are found.
    $needle = [regex]::Escape($Dir)
    Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match $needle }
}

# --- 1. Already up? Then there is nothing to do. -----------------------------

$existing = Read-DevToolsVersion -P $Port
if ($existing) {
    $owner = Get-ChromeOnProfile -Dir $ProfileDir | Select-Object -First 1
    [pscustomobject]@{
        outcome     = 'found'
        port        = $Port
        browser     = $existing.Browser
        profile_dir = $ProfileDir
        pid         = $(if ($owner) { $owner.ProcessId } else { $null })
        note        = 'a browser was already serving this port; nothing was started'
    } | ConvertTo-Json
    exit 0
}

# --- 2. Refuse if the MCP server has the profile open. -----------------------

if (Test-Path $LockFile) {
    $holder = (Get-Content $LockFile -TotalCount 1).Trim()
    $alive = $false
    if ($holder -match '^\d+$') {
        $alive = [bool](Get-Process -Id ([int]$holder) -ErrorAction SilentlyContinue)
    }
    if ($alive) {
        Write-Error @"
REFUSING: the persistent Chrome profile is locked by live PID $holder.
That is the stdio LinkedIn MCP server with its browser open. Starting Chrome on
the same user-data-dir would put two processes on one profile and cost the
signed-in session.

Stop that server first. Under the current stdio config it dies with its Claude
Code session, so: close the session (or remove the linkedin entry and reconnect),
confirm $LockFile is gone, then run this again.
"@
        exit 2
    }
    Write-Warning "stale lock at $LockFile (PID $holder is dead) -- ignoring it."
}

# --- 3. Is there a chrome.exe to start? --------------------------------------

if (-not (Test-Path $ChromeExe)) {
    Write-Error "no chrome.exe at $ChromeExe -- pass -ChromeExe with the right path."
    exit 3
}

# --- 3b. Warn if this Chrome will re-stamp the profile. ----------------------
#
# THIS IS THE ONE-WAY DOOR IN THE WHOLE CUTOVER, so it is said out loud before
# anything is started rather than discovered afterwards.
#
# Chromium writes its own version into `Last Version` and migrates the profile
# when it opens one stamped by a DIFFERENT build. Opening an older profile with
# a newer Chrome is an ordinary upgrade. The reverse is not: browser.py records
# a 2026-08-25 measurement in which playwright's older chromium met a
# newer-stamped profile, moved it aside, started clean, and cost the operator
# his signed-in session over and over -- which is the entire reason
# session_store.restore_into_context exists.
#
# So the moment real Chrome opens the server's persistent profile, that profile
# is stamped for real Chrome. The attach path is then fine forever, but FALLING
# BACK to the launch path puts playwright's chromium in front of a profile it
# considers from the future. Measured on this machine today: the profile reads
# 151.0.7922.34, playwright's chromium IS 151.0.7922.34, and the installed
# Chrome is 152.0.7977.77 -- so this is a live skew, not a hypothetical one.
#
# The fix is a copy taken BEFORE the first attach start, and the rollback step
# in the runbook restores it. This script does not take that copy itself: a
# hundreds-of-megabytes silent duplication is not a side effect a "start the
# browser" command should have.
$stampFile = Join-Path $ProfileDir "Last Version"
if (Test-Path $stampFile) {
    $stamp = (Get-Content $stampFile -TotalCount 1).Trim()
    $chromeVersion = (Get-Item $ChromeExe).VersionInfo.ProductVersion
    try {
        if ([version]$stamp -lt [version]$chromeVersion) {
            Write-Warning @"
This profile is stamped $stamp and Chrome $chromeVersion is about to open it.
Chrome will migrate it and re-stamp it to $chromeVersion. That is safe going
forward, but it makes the LAUNCH path (playwright chromium, $stamp) a DOWNGRADE
for this profile, which is the failure that cost the signed-in session on
2026-08-25.

If you have not already copied $ProfileDir, stop and do it now -- it is the
rollback.
"@
        }
    } catch {
        Write-Warning "could not compare profile stamp '$stamp' with Chrome '$chromeVersion'."
    }
}

# --- 4. Start it, detached, and wait for the port to answer. -----------------

if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
}

$arguments = @(
    "--remote-debugging-port=$Port"
    "--user-data-dir=`"$ProfileDir`""
)
$proc = Start-Process -FilePath $ChromeExe -ArgumentList $arguments -PassThru
$launchedPid = $proc.Id

$deadline = (Get-Date).AddSeconds($TimeoutSec)
$version = $null
while ((Get-Date) -lt $deadline) {
    $version = Read-DevToolsVersion -P $Port
    if ($version) { break }
    Start-Sleep -Milliseconds 400
}

if (-not $version) {
    # The singleton trap, or something like it. Say which.
    $onProfile = @(Get-ChromeOnProfile -Dir $ProfileDir)
    $launcherGone = -not (Get-Process -Id $launchedPid -ErrorAction SilentlyContinue)
    $diagnosis = if ($launcherGone -and $onProfile.Count -gt 0) {
        "the process this script started (PID $launchedPid) has already exited " +
        "while $($onProfile.Count) chrome.exe still hold this profile. That is " +
        "Chrome's singleton: the command line was handed to the running " +
        "instance and no port was opened. Quit every window on this profile " +
        "and run this again."
    } elseif ($launcherGone) {
        "the process this script started (PID $launchedPid) exited without " +
        "opening the port and nothing else holds this profile. Run the command " +
        "by hand to see what Chrome printed."
    } else {
        "PID $launchedPid is still running but has not opened the port after " +
        "$TimeoutSec seconds. Raise -TimeoutSec, or check whether another " +
        "process holds port $Port."
    }
    Write-Error "no DevTools endpoint on port $Port after $TimeoutSec seconds: $diagnosis"
    exit 4
}

$owner = Get-ChromeOnProfile -Dir $ProfileDir | Select-Object -First 1
[pscustomobject]@{
    outcome     = 'started'
    port        = $Port
    browser     = $version.Browser
    profile_dir = $ProfileDir
    pid         = $(if ($owner) { $owner.ProcessId } else { $launchedPid })
    note        = 'started by this script; leave it running for the MCP server to attach to'
} | ConvertTo-Json
exit 0
