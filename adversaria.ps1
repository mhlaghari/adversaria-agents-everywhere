$ErrorActionPreference = "Stop"
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "Install uv first: https://docs.astral.sh/uv/getting-started/installation/"
}
& uv run --project (Join-Path $PSScriptRoot "cli") adversaria @args
exit $LASTEXITCODE
