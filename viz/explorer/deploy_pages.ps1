# Publish viz/explorer/site to the GitHub Pages repo. Dry run unless -Push.
param([switch]$Push)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$remote = 'https://github.com/apalikodath-cloud/pollen-shot-explorer.git'
$email = (git -C $here config user.email)
if (-not $email) { throw 'repo-local user.email not set' }
$site = Join-Path $here 'site'
if (-not (Test-Path (Join-Path $site 'index.html'))) { throw 'site/ missing: run python build_site.py first' }
# Persistent work repo so reruns add a normal commit on top of prior history.
$work = Join-Path $env:LOCALAPPDATA 'pollen-shot-explorer-deploy'
if (-not (Test-Path (Join-Path $work '.git'))) {
    New-Item -ItemType Directory -Force $work | Out-Null
    git -C $work init -b main | Out-Null
}
git -C $work config user.name 'apalikodath-cloud'
git -C $work config user.email $email
# Byte-exact mirror; also keeps Windows PowerShell 5.1 from turning git's CRLF warning into an error.
git -C $work config core.autocrlf false
$remotes = git -C $work remote
if ($remotes -contains 'origin') { git -C $work remote set-url origin $remote } else { git -C $work remote add origin $remote }
# Mirror site/ into the work repo (keep .git).
Get-ChildItem -Force $work | Where-Object { $_.Name -ne '.git' } | Remove-Item -Recurse -Force
Copy-Item -Recurse -Force (Join-Path $site '*') $work
Copy-Item -Force (Join-Path $site '.nojekyll') $work
git -C $work add -A
$changes = git -C $work status --porcelain
if ($changes) {
    git -C $work commit -q -m 'Update POLLEN shot explorer site'
    if ($LASTEXITCODE -ne 0) { throw 'commit failed' }
    Write-Host 'Committed on main.'
} else {
    Write-Host 'No changes to commit.'
}
if ($Push) {
    git -C $work push -u origin main:gh-pages
    if ($LASTEXITCODE -ne 0) { throw 'push failed' }
} else {
    Write-Host "DRY RUN: would push main to gh-pages on $remote (use -Push)"
    git -C $work log --oneline -3
    Write-Host ("{0} files tracked" -f @(git -C $work ls-files).Count)
}
