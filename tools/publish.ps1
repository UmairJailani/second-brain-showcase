# Publishes the public Second Brain showcase (github.com/UmairJailani/second-brain-showcase).
# Run hourly by the Task Scheduler job "Second Brain - Showcase sync" (see install.ps1).
# Safe by design:
#   - builds only from COMMITTED vault content (a fresh local clone), never from unsaved edits,
#   - every note passes the privacy filter in sync.py, which fails closed: any leak stops the run,
#   - pushes only to the showcase repo, then verifies GitHub really has the commit.

$ErrorActionPreference = 'Stop'
$vault   = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$home2   = Join-Path $env:LOCALAPPDATA 'second-brain-showcase'
$build   = Join-Path $home2 'vault-snapshot'
$public  = Join-Path $home2 'public'
$log     = Join-Path $home2 'sync.log'
$remote  = 'https://github.com/UmairJailani/second-brain-showcase.git'
New-Item -ItemType Directory -Force $home2 | Out-Null

function Log($msg) {
    $line = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -Path $log -Value $line -Encoding utf8
    Write-Output $line
}
function Git-Run { $ErrorActionPreference = 'Continue'; & git.exe @args; if ($LASTEXITCODE -ne 0) { throw "git $($args -join ' ') failed (exit $LASTEXITCODE)" } }

try {
    # 1. Snapshot of committed vault content only
    if (Test-Path $build) { Remove-Item $build -Recurse -Force }
    Git-Run clone -q --no-hardlinks $vault $build | Out-Null

    # 2. Up-to-date copy of the public repo
    if (-not (Test-Path (Join-Path $public '.git'))) {
        Git-Run clone -q $remote $public | Out-Null
    } else {
        Git-Run -C $public fetch -q origin | Out-Null
        $hasRemoteMain = & git.exe -C $public rev-parse --verify -q origin/main
        if ($hasRemoteMain) { Git-Run -C $public reset -q --hard origin/main | Out-Null }
    }

    # 3. Build through the privacy filter (exit code 1 = possible leak, nothing is pushed)
    $ErrorActionPreference = 'Continue'
    $out = & python.exe (Join-Path $build 'scripts\showcase\sync.py') $public 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    $out | ForEach-Object { Log "  $_" }
    if ($code -ne 0) { Log 'ERROR privacy filter stopped the sync; nothing pushed.'; exit 1 }

    # 4. Commit only real content changes (ignore the "last synced" timestamp line)
    Git-Run -C $public add -A | Out-Null
    & git.exe -C $public diff --cached --quiet -I 'Last synced from the private vault'
    if ($LASTEXITCODE -eq 0) { Git-Run -C $public reset -q --hard | Out-Null; Log 'OK no content changes'; exit 0 }
    Git-Run -C $public -c user.name='Umair Jailani' -c user.email='95302478+UmairJailani@users.noreply.github.com' commit -q -m "Sync from private vault $(Get-Date -Format 'yyyy-MM-dd HH:mm')" | Out-Null
    Git-Run -C $public push -q origin HEAD:main | Out-Null

    # 5. Verify against GitHub, don't trust the exit code
    Git-Run -C $public fetch -q origin | Out-Null
    $local  = & git.exe -C $public rev-parse HEAD
    $remoteHead = & git.exe -C $public rev-parse origin/main
    if ($local -ne $remoteHead) { Log "ERROR push not confirmed (local $local, GitHub $remoteHead)"; exit 1 }
    Log "PUBLISHED $($local.Substring(0,7)) verified on GitHub"
} catch {
    Log "ERROR $($_.Exception.Message)"
    exit 1
}
