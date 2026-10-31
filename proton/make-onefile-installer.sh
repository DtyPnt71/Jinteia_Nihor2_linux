#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: $0 Jinteia-Proton-0.2.tar.gz [output.run]" >&2
    exit 2
fi

RUNNER_TARBALL="$(realpath "$1")"
OUTPUT="${2:-$PWD/Jinteia-Proton-0.2-installer.run}"
[[ -f "$RUNNER_TARBALL" ]] || { echo "Runner archive not found: $RUNNER_TARBALL" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/payload/tools"
cp "$RUNNER_TARBALL" "$TMP/payload/Jinteia-Proton-0.2.tar.gz"
cp "$SCRIPT_DIR/setup-jinteia.sh" "$TMP/payload/setup-jinteia.sh"
cp "$SCRIPT_DIR/tools/create_lutris_entry.py" "$TMP/payload/tools/create_lutris_entry.py"
tar -czf "$TMP/payload.tar.gz" -C "$TMP" payload

cat > "$OUTPUT" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
MARKER="__JINTEIA_PAYLOAD_BELOW__"
PAYLOAD_LINE="$(awk -v m="$MARKER" '$0 == m { print NR + 1; exit }' "$0")"
[[ -n "$PAYLOAD_LINE" ]] || { echo "Installer payload marker not found." >&2; exit 1; }
TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

tail -n +"$PAYLOAD_LINE" "$0" | tar -xzf - -C "$TMP"
chmod +x "$TMP/payload/setup-jinteia.sh"
"$TMP/payload/setup-jinteia.sh" \
    --runner-archive "$TMP/payload/Jinteia-Proton-0.2.tar.gz" \
    --runner-name "Jinteia-Proton-0.2" \
    --entry-name "Jinteia Patcher 0.2" \
    --mode "${JINTEIA_LUTRIS_MODE:-auto}"
exit $?
__JINTEIA_PAYLOAD_BELOW__
STUB

cat "$TMP/payload.tar.gz" >> "$OUTPUT"
chmod +x "$OUTPUT"
(cd -- "$(dirname -- "$OUTPUT")" && sha256sum -- "$(basename -- "$OUTPUT")" > "$(basename -- "$OUTPUT").sha256")
printf 'Created:\n  %s\n  %s\n' "$OUTPUT" "${OUTPUT}.sha256"