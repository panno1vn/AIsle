$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $here
$node = Get-Command node -ErrorAction SilentlyContinue
$bundledNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
if (-not $node -and (Test-Path $bundledNode)) { $node = Get-Item $bundledNode }
if (-not $node) { Write-Host 'Không tìm thấy Node.js 22+.' -ForegroundColor Red; exit 1 }
$nodePath = if ($node.Path) { $node.Path } else { $node.FullName }
Start-Process 'http://127.0.0.1:8765'
& $nodePath server.mjs
