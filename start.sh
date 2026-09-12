#!/usr/bin/env bash
# Pull-and-run for macOS (Apple Silicon). Checks the toolchain, installs what is
# missing where that is safe, pulls the local models, starts the Python service,
# waits for it to be healthy, then launches the desktop app in dev mode
# (dev mode is what shows the Workspaces tab).
#
#   git clone https://github.com/mhlaghari/adversaria-agents-everywhere.git
#   cd adversaria-agents-everywhere && ./start.sh
#
# Re-run any time; every step is idempotent. Set SMALL_MODELS=0 to pull the
# 35B copilot model instead of the 4B one (needs 24 GB of disk and RAM).
set -euo pipefail
cd "$(dirname "$0")"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1; }

say "1/6 Toolchain"
if ! need brew; then echo "Homebrew is required: https://brew.sh"; exit 1; fi
need node   || { echo "installing node";   brew install node; }
need git    || { echo "installing git";    brew install git; }
need ffmpeg || { echo "installing ffmpeg"; brew install ffmpeg; }
need ollama || { echo "installing ollama"; brew install ollama; }
if ! need cargo; then
  echo "installing Rust (rustup)"; curl -sSf https://sh.rustup.rs | sh -s -- -y
fi
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
if ! need uv; then
  echo "installing uv"; curl -LsSf https://astral.sh/uv/install.sh | sh
fi
node -e 'const v=+process.versions.node.split(".")[0]; if(v<20){console.error("node 20+ required");process.exit(1)}'

say "2/6 Python service dependencies"
( cd python-service && uv sync )

say "3/6 Frontend dependencies"
npm install --no-audit --no-fund

say "4/6 Local models (Ollama)"
if ! curl -s -m 2 http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "starting ollama"; (ollama serve >/tmp/ollama-adversaria.log 2>&1 &) ; sleep 3
fi
ollama pull bge-m3
if [ "${SMALL_MODELS:-1}" = "1" ]; then ollama pull qwen3.5:4b; else ollama pull qwen3.6:35b; fi

say "5/6 Python service"
if curl -s -m 2 http://127.0.0.1:9876/health >/dev/null; then
  echo "service already running on 127.0.0.1:9876"
else
  ( cd python-service && HF_HUB_DISABLE_XET=1 nohup uv run --no-sync uvicorn src.server:app \
      --host 127.0.0.1 --port 9876 --log-level info >/tmp/adversaria-service.log 2>&1 & )
  printf 'waiting for the service (first run downloads the Whisper model, a few minutes)'
  for _ in $(seq 1 240); do
    if curl -s -m 2 http://127.0.0.1:9876/health | grep -q '"status":"ok"'; then echo; break; fi
    printf '.'; sleep 5
  done
fi
curl -s -m 2 http://127.0.0.1:9876/health || { echo "service did not come up; see /tmp/adversaria-service.log"; exit 1; }
echo

say "6/6 Desktop app (dev mode: Meetings, Workspaces, Copilot)"
echo "macOS will ask for Microphone and System Audio Recording the first time you record."
# The dev config drops the frozen-sidecar resource (a PyInstaller build product that
# is never in git); in dev mode the app talks to the source service started above.
npm run tauri dev -- --config src-tauri/tauri.dev.conf.json
