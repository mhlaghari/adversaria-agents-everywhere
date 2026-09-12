# Pull-and-run for Windows 10/11 (PowerShell). Checks the toolchain, installs
# what is missing with winget where that is safe, pulls the local models, starts
# the Python service, waits for it to be healthy, then launches the desktop app
# in dev mode (dev mode is what shows the Workspaces tab).
#
#   git clone https://github.com/mhlaghari/adversaria-agents-everywhere.git
#   cd adversaria-agents-everywhere; .\start.ps1
#
# Re-run any time; every step is idempotent. Set $env:SMALL_MODELS="0" to pull
# the 35B copilot model instead of the 4B one (needs 24 GB of disk and RAM).
# Rust needs the Visual Studio C++ Build Tools; rustup-init installs them if
# they are missing (one-time, a few minutes).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Say($m) { Write-Host "`n$m" -ForegroundColor White -BackgroundColor DarkBlue }
function Need($c) { $null -ne (Get-Command $c -ErrorAction SilentlyContinue) }
function Winget($id) { & winget.exe install --id $id -e --accept-source-agreements --accept-package-agreements }

Say "1/6 Toolchain"
if (-not (Need winget)) { Write-Host "winget (App Installer) is required from the Microsoft Store"; exit 1 }
if (-not (Need node))   { Winget "OpenJS.NodeJS.LTS" }
if (-not (Need git))    { Winget "Git.Git" }
if (-not (Need ffmpeg)) { Winget "Gyan.FFmpeg" }
if (-not (Need ollama)) { Winget "Ollama.Ollama" }
if (-not (Need cargo))  { Winget "Rustlang.Rustup" }
if (-not (Need uv))     { irm https://astral.sh/uv/install.ps1 | iex }
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:USERPROFILE\.local\bin;$env:LOCALAPPDATA\Programs\Ollama;" + $env:Path

Say "2/6 Python service dependencies"
$extra = @()
if (Need nvidia-smi) { $extra = @("--extra", "cuda"); Write-Host "NVIDIA GPU found: installing the CUDA extra" }
Push-Location python-service; uv sync @extra; Pop-Location

Say "3/6 Frontend dependencies"
npm install --no-audit --no-fund

Say "4/6 Local models (Ollama)"
try { Invoke-RestMethod -TimeoutSec 2 http://127.0.0.1:11434/api/tags | Out-Null } catch { Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 3 }
ollama pull bge-m3
if ($env:SMALL_MODELS -eq "0") { ollama pull qwen3.6:35b } else { ollama pull qwen3.5:4b }

Say "5/6 Python service"
$healthy = $false
try {
  # /health makes two sequential Ollama round-trips (backend_available +
  # the embedding-model check) — 2s was too tight right after `ollama pull`
  # just finished, so this timed out on an already-healthy service and
  # started a redundant (harmlessly failing) second uvicorn on the same port.
  $h = Invoke-RestMethod -TimeoutSec 15 http://127.0.0.1:9876/health
  $healthy = ($h.status -eq "ok" -or ($h.status -eq "degraded" -and $h.ollama_available))
} catch {}
if ($healthy) { Write-Host "service already running on 127.0.0.1:9876" }
else {
  Push-Location python-service
  Start-Process -WindowStyle Hidden -FilePath "uv" -ArgumentList "run","--no-sync","uvicorn","src.server:app","--host","127.0.0.1","--port","9876","--log-level","info" -RedirectStandardOutput "$env:TEMP\adversaria-service.log" -RedirectStandardError "$env:TEMP\adversaria-service.err"
  Pop-Location
  # V3 never auto-downloads a transcription model (Whisper or otherwise) —
  # that only happens from the in-app Welcome wizard / Settings, on an
  # explicit click. This just waits for the sidecar itself to come up.
  Write-Host "waiting for the service" -NoNewline
  for ($i = 0; $i -lt 240; $i++) {
    try {
      $h = Invoke-RestMethod -TimeoutSec 15 http://127.0.0.1:9876/health
      if ($h.status -eq "ok" -or ($h.status -eq "degraded" -and $h.ollama_available)) {
        $healthy = $true
        break
      }
    } catch {}
    Write-Host "." -NoNewline; Start-Sleep 5
  }
  Write-Host ""
}
if (-not $healthy) { Write-Host "service did not come up; see $env:TEMP\adversaria-service.err"; exit 1 }
if ($h.status -eq "degraded") {
  Write-Host "service is up; pick and download a transcription model from the Welcome wizard (or Settings > AI Model) once the app opens"
}

Say "6/6 Desktop app (dev mode: Meetings, Workspaces, Copilot)"
npm run tauri dev
