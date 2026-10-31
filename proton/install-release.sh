#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SETUP="$SCRIPT_DIR/setup-jinteia.sh"

usage() {
    cat <<EOF
Usage:
  $0 Jinteia-Proton-0.2.tar.gz [auto|native|flatpak]

The integrated setup helper will detect the system, check Lutris and
required runtime components, install the runner, create the Jinteia
folders/prefix folder and prepare the Lutris entry.
EOF
}

[[ $# -ge 1 && $# -le 2 ]] || { usage; exit 2; }
ARCHIVE="$(realpath "$1")"
MODE="${2:-auto}"
[[ -f "$ARCHIVE" ]] || { echo "Runner archive not found: $ARCHIVE" >&2; exit 1; }
[[ -x "$SETUP" ]] || chmod +x "$SETUP"

exec "$SETUP" \
    --runner-archive "$ARCHIVE" \
    --runner-name "Jinteia-Proton-0.2" \
    --entry-name "Jinteia Patcher 0.2" \
    --mode "$MODE"