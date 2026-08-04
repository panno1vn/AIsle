$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $here
$node = Get-Command node -ErrorAction SilentlyContinue
$bundledNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
if (-not $node -and (Test-Path $bundledNode)) { $node = Get-Item $bundledNode }
if (-not $node) { Write-Host 'Không tìm thấy Node.js 22+.' -ForegroundColor Red; exit 1 }
$nodePath = if ($node.Path) { $node.Path } else { $node.FullName }
try { Invoke-WebRequest 'http://127.0.0.1:8765/health' -UseBasicParsing -TimeoutSec 1 | Out-Null }
catch { Start-Process $nodePath -ArgumentList 'server.mjs' -WorkingDirectory $here -WindowStyle Hidden; Start-Sleep -Milliseconds 700 }
$edge = @("$env:ProgramFiles`(x86`)\Microsoft\Edge\Application\msedge.exe", "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($edge) { Start-Process $edge -ArgumentList '--app=http://127.0.0.1:8765','--start-maximized' }
else { Start-Process 'http://127.0.0.1:8765' }
