<#
.SYNOPSIS
    Stop the LinkedIn MCP HTTP server. Never touches Chrome.

.DESCRIPTION
    Finds the server by what it IS -- a python interpreter running
    `linkedin.py --http` -- rather than by whatever is holding the port, and
    stops it.

    THE MATCH IS ON THE PROCESS NAME AS WELL AS THE COMMAND LINE, and that is
    not belt-and-braces. The shell that launched the server has the whole
    command line inside its own, so a command-line match alone selects the
    caller's own shell and kills the session running the script. Measured
    during this script's own development: a cmdline-only sweep matched a
    bash.exe wrapper.

    IT WILL NOT KILL A BROWSER. chrome.exe is excluded explicitly, over and
    above the name filter, because an image-wide browser kill has already
    reached the operator's own Chrome once on this machine. In ATTACH mode the
    browser is not the server's child and must outlive it -- that is the point
    of the whole arrangement.

    Safe to run when nothing is up: it reports `stopped: 0` and exits 0.

.PARAMETER Port
    Only used to verify afterwards that nothing is still listening. Default 8322.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop_server.ps1
#>
[CmdletBinding()]
param(
    [int] $Port = 8322
)

$ErrorActionPreference = 'Stop'

function Get-ServerProcesses {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -ne 'chrome.exe' -and
        (
            # The interpreter itself. On a Windows venv this matches TWO
            # processes -- the venv shim and the base interpreter it re-execs --
            # and both are stopped, because stopping only the shim leaves the
            # one actually holding the port.
            (
                $_.Name -like 'python*.exe' -and
                $_.CommandLine -match 'linkedin\.py' -and
                $_.CommandLine -match '--http'
            ) -or
            # ...and the generated wrapper that start_server.ps1 launches it
            # through. It normally exits by itself when its child dies; it is
            # matched by that exact generated filename so that a wrapper left
            # behind by a killed child does not survive as an orphan.
            (
                $_.Name -eq 'cmd.exe' -and
                $_.CommandLine -match 'run-http-server\.cmd'
            )
        )
    }
}

$targets = @(Get-ServerProcesses)
$killed = @()

foreach ($t in $targets) {
    try {
        Stop-Process -Id $t.ProcessId -Force -ErrorAction Stop
        $killed += $t.ProcessId
    } catch {
        # A child dying with its parent is the normal case, not a failure.
        if (Get-Process -Id $t.ProcessId -ErrorAction SilentlyContinue) {
            Write-Warning "could not stop PID $($t.ProcessId): $_"
        } else {
            $killed += $t.ProcessId
        }
    }
}

if ($killed.Count -gt 0) { Start-Sleep -Milliseconds 800 }

$survivors = @(Get-ServerProcesses)
$listening = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)

[pscustomobject]@{
    stopped          = $killed.Count
    stopped_pids     = $killed
    still_running    = $survivors.Count
    port             = $Port
    still_listening  = $listening.Count
} | ConvertTo-Json

if ($survivors.Count -gt 0) {
    Write-Error "$($survivors.Count) server process(es) survived the stop."
    exit 1
}
if ($listening.Count -gt 0) {
    Write-Error @"
port $Port is still being listened on by PID(s) $(($listening | ForEach-Object { $_.OwningProcess }) -join ', ')
after every matching server process was stopped. Something OTHER than this
server holds that port -- do not assume the next start will get it.
"@
    exit 1
}
exit 0
