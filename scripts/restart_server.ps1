<#
.SYNOPSIS
    Reload the LinkedIn MCP server's code. Stop, start, confirm. Never touches Chrome.

.DESCRIPTION
    THIS IS THE COMMAND THE CUTOVER EXISTS TO CREATE. Under stdio, loading
    changed code needed the operator to type `/mcp` in his own session. Under
    HTTP the client reconnects a dropped server by itself, so reloading the code
    is this script and nothing else.

    It is a thin composition of stop_server.ps1 and start_server.ps1 on purpose:
    the safety properties live in those two, and duplicating them here is how
    they would drift apart.

    SAFE TO RUN REPEATEDLY. stop is a no-op when nothing is running; start is a
    no-op when something already answers -- which is why -Force exists. Without
    it, "restart" on a healthy server would stop it and then decline to start
    it. With it, the stop always happens first.

    IT DOES NOT TOUCH THE BROWSER. Chrome is a separate process with a separate
    lifetime and the browser session is the thing being protected; if the
    browser is gone, start_server.ps1 refuses rather than starting a server that
    would fail every call.

.PARAMETER Port
    HTTP port. Default 8322.

.PARAMETER CdpPort
    DevTools port to attach to. Default 9224.

.PARAMETER EnableWrites
    Pass through to start_server.ps1.

.PARAMETER Token
    Pass through to start_server.ps1.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\restart_server.ps1 -EnableWrites
#>
[CmdletBinding()]
param(
    [int]    $Port         = 8322,
    [int]    $CdpPort      = 9224,
    [string] $Python       = "",
    [switch] $EnableWrites,
    [string] $Token        = "",
    [int]    $TimeoutSec   = 40
)

$ErrorActionPreference = 'Stop'
$Stop  = Join-Path $PSScriptRoot "stop_server.ps1"
$Start = Join-Path $PSScriptRoot "start_server.ps1"

Write-Host "-- stopping --"
& $Stop -Port $Port
if ($LASTEXITCODE -ne 0) {
    Write-Error "stop failed; not starting a second server on top of whatever is there."
    exit 1
}

Write-Host "-- starting --"
$startArgs = @{ Port = $Port; CdpPort = $CdpPort; TimeoutSec = $TimeoutSec }
if ($Python)       { $startArgs['Python'] = $Python }
if ($EnableWrites) { $startArgs['EnableWrites'] = $true }
if ($Token)        { $startArgs['Token'] = $Token }

& $Start @startArgs
exit $LASTEXITCODE
