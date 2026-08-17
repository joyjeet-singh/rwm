#!/usr/bin/env bash
# Fetch the two upstream repositories at the commits this reproduction was
# verified against, and check the two reference artifacts against the hashes
# recorded in the ledger.
#
# The upstreams are NOT vendored here. Neither is installed: their setup.py
# pins torch>=2.7 with CUDA, which would replace the pins in requirements.txt.
# Only their source is read.
#
# Usage:  ./setup.sh [target-dir]      (default: the parent of this repository)

set -euo pipefail

LITE_COMMIT="13a798e9d35dabf12c0e6e02977b25ec64dfb2bd"
RSL_COMMIT="18eebcdd7145284c8d5eed5d8ed1a4b96c649693"
CSV_SHA256="1b2e00b8a2bc10dc9b5f62840de72410adb448a57a9a2f6adbcd735be9e78921"
CKPT_SHA256="2ac8686c8c7736287853c0fe1438c379320068adf97be71609b5f1afb52c6e5a"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$(dirname "$HERE")}"
cd "$TARGET"
echo "==> fetching upstreams into $TARGET"

clone_at() {
  local url="$1" dir="$2" commit="$3"
  if [ -d "$dir/.git" ]; then
    echo "--> $dir already present"
  else
    git clone --quiet "$url" "$dir"
  fi
  git -C "$dir" fetch --quiet origin "$commit" 2>/dev/null || true
  git -C "$dir" checkout --quiet "$commit"
  echo "--> $dir at $(git -C "$dir" rev-parse HEAD)"
}

clone_at https://github.com/leggedrobotics/robotic_world_model_lite \
         robotic_world_model_lite "$LITE_COMMIT"
clone_at https://github.com/leggedrobotics/rsl_rl_rwm \
         rsl_rl_rwm "$RSL_COMMIT"

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else shasum -a 256 "$1" | cut -d' ' -f1; fi
}

check() {
  local path="$1" expected="$2" label="$3"
  if [ ! -f "$path" ]; then
    echo "FAIL: $label missing at $path" >&2; return 1
  fi
  local got; got="$(sha256_of "$path")"
  if [ "$got" = "$expected" ]; then
    echo "--> $label sha256 OK"
  else
    echo "FAIL: $label sha256 mismatch" >&2
    echo "      expected $expected" >&2
    echo "      got      $got" >&2
    return 1
  fi
}

echo "==> verifying reference artifacts"
rc=0
check robotic_world_model_lite/assets/data/state_action_data_0.csv \
      "$CSV_SHA256"  "state_action_data_0.csv" || rc=1
check robotic_world_model_lite/assets/models/pretrain_rnn_ens.pt \
      "$CKPT_SHA256" "pretrain_rnn_ens.pt"     || rc=1

if [ "$rc" -ne 0 ]; then
  echo
  echo "One or more artifacts do not match the pinned hashes. Every number in"
  echo "FINDINGS_LEDGER.md was measured against those exact bytes, so results"
  echo "produced from different artifacts are not comparable. Stopping." >&2
  exit 1
fi

echo
echo "==> upstreams ready and artifacts verified"
echo "    next:  python3.11 -m venv .venv && . .venv/bin/activate"
echo "           pip install -r \"$HERE/requirements.txt\""
