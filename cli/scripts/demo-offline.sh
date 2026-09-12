#!/usr/bin/env bash
# Offline demo of the Adversaria CLI: the subset that works with NO cloud keys.
# Verified 2026-09-12 against a fresh --home. Run from anywhere:
#   bash cli/scripts/demo-offline.sh
# Each command is printed before it runs. `doctor` exits 1 without keys by design,
# so it is run with `|| true`; everything else must exit 0.
set -u
CLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="$(mktemp -d)"
cd "$CLI_DIR"

run() {
  printf '\n\033[1;36m$ adversaria --home %s %s\033[0m\n' "$HOME_DIR" "$*"
  uv run adversaria --home "$HOME_DIR" "$@"
}

echo "Adversaria CLI · offline demo · isolated home: $HOME_DIR"

# 1. Environment (doctor is non-zero without keys; that's expected here)
run doctor || true
run devices

# 2. Workspace: create, attach grounding context, set instructions
run workspace create Interviews
run workspace attach --workspace Interviews examples/adversaria-overview.txt
run workspace instructions --workspace Interviews \
  "Focus on hiring loop notes; keep answers short and cite attached files."
run workspace list

# 3. Replay a two-speaker transcript through the live detector.
#    Expect two CAUGHT lines (c1 visualize · by Monday, c2 research · before Friday).
#    Nothing is auto-approved; the transcript is saved as a meeting.
run replay --workspace Interviews examples/design-review.txt

# 4. Tasks queue locally; running them needs a provider key (see `adversaria setup`).
run task add --workspace Interviews --kind write \
  --details "One-page brief on the interview loop" "Draft interview loop brief"
run task list --workspace Interviews
run task show 1

# 5. Meeting history from the replay
run meetings list --workspace Interviews
run meetings show 1

printf '\nDone. Data lives in %s (delete it when finished).\n' "$HOME_DIR"
