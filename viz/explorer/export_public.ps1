# Build the clean public source tree for github.com/apalikodath-cloud/pollen-shot-explorer (main).
# Dry run unless -Push. Takes the COMMITTED project tree (HEAD), leaves out internal tooling, scans
# for personal paths and secrets, and commits it on a local main on top of the fetched remote main.
# -Push does a normal push to main (never a force push). The built site lives on gh-pages
# (deploy_pages.ps1); this script never touches that branch.
param(
    [switch]$Push,
    [string[]]$Trailer = @()
)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$proj = (Resolve-Path (Join-Path $here '..\..')).Path
$remote = 'https://github.com/apalikodath-cloud/pollen-shot-explorer.git'
$work = Join-Path $env:LOCALAPPDATA 'pollen-shot-explorer-public'

# Internal tooling and private notes that never go public (paths relative to the project root).
$exclude = @('.af', '.claude', 'CLAUDE.md', 'docs/handoff', 'viz/team', 'data/_spec_run.log')   # run log: gitignored, may hold local paths
# Text that must not appear in the public tree (personal paths, account e-mail, session links, keys).
$forbidden = @(
    '[A-Za-z]:[\\/]Users[\\/]',
    '[A-Za-z]:[\\/]Dev[\\/]',
    'AppData[\\/]Local[\\/]Temp',
    '@gmail\.com',
    'claude\.ai/code/session',
    'TYPESAFE_API_KE[Y]',   # bracket keeps this script from matching itself
    'ghp_[A-Za-z0-9]{20,}',
    'github_pat_[A-Za-z0-9_]{20,}',
    'sk-[A-Za-z0-9]{20,}',
    'AKIA[0-9A-Z]{16}',
    # Internal tooling names (brackets keep this script from matching itself).
    '\bJe[v]\b',
    'DevLoade[r]',
    'AgentFusio[n]',
    'Sthir[a]',
    '\bRevi[t]\b',
    'Auto-IT[M]'
)
# Commit trailers that must not reach the public history (private session links).
$trailerForbidden = 'claude\.ai/code/sessio[n]|Claude-Sessio[n]:'

# Native stderr (git progress) must not become a terminating error in Windows PowerShell 5.1:
# run git with 'Continue' and judge it by its exit code.
function Invoke-Git {
    $old = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { & git @args 2>&1 | ForEach-Object { "$_" } } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "git $args failed" }
}

$name = (git -C $proj config user.name)
$email = (git -C $proj config user.email)
if (-not $name -or -not $email) { throw 'repo-local user.name / user.email not set' }
$prefix = (git -C $proj rev-parse --show-prefix).Trim()
$top = (git -C $proj rev-parse --show-toplevel).Trim()
$head = (git -C $proj rev-parse --short HEAD).Trim()
$dirty = git -C $proj status --porcelain -- .
if ($dirty) { Write-Host 'Note: uncommitted changes in the project are NOT exported (HEAD only).' }

# 1. Committed subtree -> staging folder.
$stage = Join-Path $env:TEMP ('pollen-public-stage-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Force $stage | Out-Null
$tarFile = Join-Path $env:TEMP ('pollen-public-' + $head + '.tar')
$treeish = if ($prefix) { "HEAD:$($prefix.TrimEnd('/'))" } else { 'HEAD' }
Invoke-Git -C $top archive --format=tar -o $tarFile $treeish
tar -xf $tarFile -C $stage
if ($LASTEXITCODE -ne 0) { throw 'tar extract failed' }
Remove-Item -Force $tarFile

# 2. Exclusions.
foreach ($e in $exclude) {
    $p = Join-Path $stage $e
    if (Test-Path -LiteralPath $p) { Remove-Item -Recurse -Force -LiteralPath $p }
}

# 3. Scan for personal paths and secrets (text files only), and for oversized files.
$hits = @()
$files = Get-ChildItem -Recurse -File -Force $stage
foreach ($f in $files) {
    if ($f.Length -gt 50MB) { $hits += "over 50 MB: $($f.FullName.Substring($stage.Length + 1))" }
    if ($f.Extension -match '^\.(png|jpg|jpeg|gif|mp4|pdf|npz|bin|zip)$') { continue }
    $rel = $f.FullName.Substring($stage.Length + 1)
    foreach ($pat in $forbidden) {
        $m = Select-String -LiteralPath $f.FullName -Pattern $pat -List
        if ($m) { $hits += "${rel}:$($m.LineNumber): matches /$pat/" }
    }
}
if ($hits) {
    $hits | ForEach-Object { Write-Host "BLOCKED $_" }
    Remove-Item -Recurse -Force $stage
    throw 'public tree failed the scan; fix the source and commit, then rerun'
}

# 4. Work repo on top of the remote main.
if (-not (Test-Path (Join-Path $work '.git'))) {
    New-Item -ItemType Directory -Force $work | Out-Null
    Invoke-Git -C $work init -q -b main
}
Invoke-Git -C $work config user.name $name
Invoke-Git -C $work config user.email $email
Invoke-Git -C $work config core.autocrlf false
$remotes = @(git -C $work remote)
if ($remotes -contains 'origin') { Invoke-Git -C $work remote set-url origin $remote } else { Invoke-Git -C $work remote add origin $remote }
$hasRemoteMain = [bool](Invoke-Git -C $work ls-remote --heads origin main)   # throws if the remote is unreachable
if ($hasRemoteMain) { Invoke-Git -C $work fetch -q origin main | Out-Null }
if ($hasRemoteMain) {
    # The work dir is a disposable mirror: rebuild main from the remote tip every run.
    Invoke-Git -C $work checkout -q -f -B main FETCH_HEAD
    $remoteTip = (git -C $work rev-parse --short FETCH_HEAD).Trim()
    Write-Host "Based on remote main $remoteTip."
} else {
    Write-Host 'Remote main not found: the first push creates it.'
}

# 5. Mirror the staging tree into the work repo (keep .git) and commit.
Get-ChildItem -Force $work | Where-Object { $_.Name -ne '.git' } | Remove-Item -Recurse -Force
Copy-Item -Recurse -Force (Join-Path $stage '*') $work
Get-ChildItem -Force $stage | Where-Object { $_.Name -like '.*' } | ForEach-Object { Copy-Item -Recurse -Force $_.FullName $work }
Remove-Item -Recurse -Force $stage
Invoke-Git -C $work add -A
$changes = git -C $work status --porcelain
if ($changes) {
    $kept = @($Trailer | Where-Object { $_ -notmatch $trailerForbidden })
    if ($kept.Count -ne @($Trailer).Count) { Write-Host 'Dropped a session-link trailer from the public commit message.' }
    $msg = @("Update project source (from $head)", '') + $kept
    $msgFile = Join-Path $env:TEMP ('pollen-public-msg-' + $head + '.txt')
    [IO.File]::WriteAllText($msgFile, ($msg -join "`n") + "`n", (New-Object Text.UTF8Encoding $false))
    Invoke-Git -C $work commit -q -F $msgFile
    Remove-Item -Force $msgFile
    Write-Host 'Committed on local main.'
} else {
    Write-Host 'No changes against the remote main.'
}

$tracked = @(git -C $work ls-files)
$bytes = 0
foreach ($t in $tracked) { $bytes += (Get-Item -LiteralPath (Join-Path $work $t)).Length }
Write-Host ("{0} files, {1:N1} MB in {2}" -f $tracked.Count, ($bytes / 1MB), $work)

if ($Push) {
    Invoke-Git -C $work push origin main
    Write-Host "Pushed main to $remote."
} else {
    Write-Host "DRY RUN: would push local main to main on $remote (use -Push)."
    git -C $work log --oneline -3
}
