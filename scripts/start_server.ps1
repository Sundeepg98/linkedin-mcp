<#
.SYNOPSIS
    Start the LinkedIn MCP server on HTTP, in CDP-attach mode. Never touches Chrome.

.DESCRIPTION
    Starts `linkedin.py --http` detached, with LINKEDIN_CDP_ATTACH=1 so the
    server attaches to a Chrome something else started instead of launching and
    locking the persistent profile itself.

    IT CONFIRMS BY SPEAKING MCP, not by watching a socket. A bound port proves a
    process called bind(); it does not prove an MCP server is answering, and the
    two come apart exactly when a server has crashed during startup with the
    listener already up. `scripts/mcp_probe.py` performs a real `initialize` and
    that is what this script waits for.

    IT REFUSES TO START WITHOUT A BROWSER TO ATTACH TO, unless -AllowNoBrowser
    is passed. A server that starts happily and then fails every browser-backed
    tool call is worse than one that will not start: the first is diagnosed at
    the call site, minutes later, by somebody reading a tool error.

    IT NEVER STARTS OR STOPS CHROME. That is scripts\start_chrome.ps1's job, and
    keeping them apart is what makes this script safe to run repeatedly.

.PARAMETER Port
    HTTP port. Default 8322.

.PARAMETER CdpPort
    The DevTools port to attach to. Default 9224.

.PARAMETER EnableWrites
    Pass LINKEDIN_ENABLE_WRITES=1 to the server. Off by default: writes are
    opt-in per process and this script will not turn them on silently. The
    live .mcp.json entry sets it, so the cutover passes it.

.PARAMETER Token
    Require this bearer token on every request. Strongly recommended when
    writes are enabled -- see linkedin_server/transport.py for why a loopback
    port is a surface stdio did not have.

.PARAMETER AllowNoBrowser
    Start even when no DevTools endpoint answers on -CdpPort.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_server.ps1 -EnableWrites
#>
[CmdletBinding()]
param(
    [int]    $Port           = 8322,
    [int]    $CdpPort        = 9224,
    [string] $Python         = "",
    [switch] $EnableWrites,
    [string] $Token          = "",
    [switch] $AllowNoBrowser,
    [int]    $TimeoutSec     = 40
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $RepoRoot "venv\Scripts\python.exe" }
$Entry    = Join-Path $RepoRoot "linkedin.py"
$Probe    = Join-Path $PSScriptRoot "mcp_probe.py"
$LogDir   = Join-Path $RepoRoot "_state"
$OutLog   = Join-Path $LogDir "http-server.out.log"
$ErrLog   = Join-Path $LogDir "http-server.err.log"
$Url      = "http://127.0.0.1:$Port/mcp"

foreach ($required in @($Python, $Entry, $Probe)) {
    if (-not (Test-Path $required)) {
        Write-Error "missing $required"
        exit 3
    }
}
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

# --- Already serving? Then this is a no-op, and says so. ---------------------

$probeArgs = @($Probe, '--url', $Url, '--timeout', '5')
if ($Token) { $probeArgs += @('--token', $Token) }
& $Python @probeArgs 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    [pscustomobject]@{
        outcome = 'found'
        url     = $Url
        note    = 'an MCP server was already answering here; nothing was started'
    } | ConvertTo-Json
    exit 0
}

# --- Is there a browser to attach to? ----------------------------------------

$browser = $null
try {
    $browser = (Invoke-WebRequest -Uri "http://127.0.0.1:$CdpPort/json/version" `
        -UseBasicParsing -TimeoutSec 3).Content | ConvertFrom-Json
} catch { $browser = $null }

if (-not $browser -and -not $AllowNoBrowser) {
    Write-Error @"
REFUSING: nothing is serving DevTools on 127.0.0.1:$CdpPort, so an attach-mode
server would start and then fail every browser-backed tool call.

Start the browser first:
    .\scripts\start_chrome.ps1 -Port $CdpPort

Or pass -AllowNoBrowser if starting the server without one is what you meant.
"@
    exit 2
}

# --- Start it, and the how is not incidental. --------------------------------
#
# THE SERVER MUST INHERIT NOTHING FROM WHOEVER RAN THIS SCRIPT. A detached
# child that inherits the caller's console handles holds them for its entire
# life, and any shell waiting for end-of-input on one of them blocks until the
# server dies. Measured here, twice: `Start-Process` with stdout, stderr AND
# stdin all redirected to files STILL left a handle behind, and a Bash call
# that piped this script's output sat for two full minutes on a server that had
# come up in six seconds. Without the pipe the same call returned in one
# second, which is what dated the leak to handle inheritance rather than to the
# server being slow.
#
# `Win32_Process.Create` is the one launcher on Windows that inherits no
# handles at all. Measured: one second, with or without a pipe.
#
# ITS COST, AND WHY THE WRAPPER EXISTS. It also inherits no ENVIRONMENT -- it
# starts the process with the user's default block, not this one. That is not a
# cosmetic difference: on the first attempt it silently dropped
# LINKEDIN_CDP_ATTACH and LINKEDIN_HTTP_PORT, so the server came up in LAUNCH
# mode on the default port, pointed at the real persistent profile. Nothing was
# damaged -- a browser is launched lazily and no tool call was made -- but a
# launcher whose failure mode is "runs correctly against the wrong profile" is
# not one to leave in place.
#
# So the configuration is written into a wrapper .cmd first and the wrapper is
# what gets launched. It carries the environment explicitly, does its own
# redirection, and has the side benefit of being a readable record of exactly
# how the running server was started. It lives in _state, which is gitignored
# and already holds the Chrome profile -- a bearer token is a smaller secret
# than the live session cookies sitting beside it.
$Wrapper = Join-Path $LogDir "run-http-server.cmd"
$writes  = if ($EnableWrites) { "1" } else { "" }

$wrapperText = @"
@echo off
rem GENERATED by scripts\start_server.ps1 -- overwritten on every start.
rem This file is the exact configuration the running server was started with.
set "LINKEDIN_CDP_ATTACH=1"
set "LINKEDIN_CDP_PORT=$CdpPort"
set "LINKEDIN_HTTP_PORT=$Port"
set "LINKEDIN_ENABLE_WRITES=$writes"
set "LINKEDIN_HTTP_TOKEN=$Token"
set "PYTHONUNBUFFERED=1"
cd /d "$RepoRoot"
"$Python" -u "$Entry" --http > "$OutLog" 2> "$ErrLog"
"@
Set-Content -Path $Wrapper -Value $wrapperText -Encoding ASCII

$startup = ([wmiclass]'Win32_ProcessStartup').CreateInstance()
$startup.ShowWindow = 0
$created = ([wmiclass]'Win32_Process').Create("cmd.exe /c `"$Wrapper`"", $RepoRoot, $startup)
if ($created.ReturnValue -ne 0) {
    Write-Error "Win32_Process.Create refused to start the wrapper (ReturnValue=$($created.ReturnValue))."
    exit 1
}

# --- Confirm by speaking MCP, not by watching a socket. ----------------------

$probeArgs = @($Probe, '--url', $Url, '--timeout', '10', '--retries', "$TimeoutSec")
if ($Token) { $probeArgs += @('--token', $Token) }
$answer = & $Python @probeArgs 2>&1
$served = ($LASTEXITCODE -eq 0)

if (-not $served) {
    $tail = if (Test-Path $ErrLog) { (Get-Content $ErrLog -Tail 15) -join "`n" } else { '<no stderr log>' }
    Write-Error @"
the server did not answer MCP on $Url within $TimeoutSec seconds.
probe said: $answer

last lines of $ErrLog :
$tail
"@
    exit 1
}

$serverProc = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -like 'python*.exe' -and $_.CommandLine -match 'linkedin\.py' -and $_.CommandLine -match '--http'
} | Select-Object -First 1

[pscustomobject]@{
    outcome        = 'started'
    url            = $Url
    pid            = $(if ($serverProc) { $serverProc.ProcessId } else { $created.ProcessId })
    launcher_pid   = $created.ProcessId
    cdp_port       = $CdpPort
    browser        = $(if ($browser) { $browser.Browser } else { $null })
    writes_enabled = [bool]$EnableWrites
    auth           = $(if ($Token) { 'bearer' } else { 'none' })
    stdout_log     = $OutLog
    stderr_log     = $ErrLog
} | ConvertTo-Json
exit 0
