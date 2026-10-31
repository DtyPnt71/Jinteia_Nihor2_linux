#!/usr/bin/env bash
set -euo pipefail

BASE_TAG="GE-Proton11-7"
BUILD_NAME="Jinteia-Proton-0.2"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WORK_ROOT="${JINTEIA_BUILD_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/jinteia-proton-v0.2}"
SRC_DIR="$WORK_ROOT/proton-ge-custom"
BUILD_DIR="$WORK_ROOT/build"
OUTPUT_DIR="${JINTEIA_OUTPUT_DIR:-$SCRIPT_DIR}"
LUTRIS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/lutris/runners/wine"

say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nFEHLER: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "'$1' fehlt. Bitte zuerst installieren."; }

[[ "$(uname -m)" == "x86_64" ]] || die "Dieser Build ist aktuell nur für x86_64 gedacht."

for cmd in git make python3 tar sha256sum; do need "$cmd"; done

ENGINE=""
if command -v podman >/dev/null 2>&1; then
    ENGINE="podman"
elif command -v docker >/dev/null 2>&1; then
    ENGINE="docker"
else
    die "Podman oder Docker fehlt. Für den GE-Proton-Build wird eine Container-Engine benötigt."
fi

cat <<EOF
Jinteia-Proton v0.2 – Build + Lutris-Installation
Basis: $BASE_TAG
Container: $ENGINE
Build-Verzeichnis: $WORK_ROOT
Lutris-Ziel: $LUTRIS_DIR/$BUILD_NAME

Fixes:
  - Wine import stubs: W^X statt dauerhaft RWX
  - ole32 RevokeDragDrop: kein Release eines fremden Prozess-Pointers

Der erste Build lädt die GE-Proton-Quellen und kann lange dauern.
EOF

say "Frischen Quellstand vorbereiten"
rm -rf "$SRC_DIR" "$BUILD_DIR"
mkdir -p "$WORK_ROOT" "$OUTPUT_DIR"
git clone --branch "$BASE_TAG" --recurse-submodules     https://github.com/GloriousEggroll/proton-ge-custom.git "$SRC_DIR"

say "Offizielle GE-Proton-Patches vorbereiten"
cd "$SRC_DIR"
./patches/protonprep-valve-staging.sh 2>&1 | tee "$WORK_ROOT/protonprep.log"

say "Jinteia-Kompatibilitätsfixes anwenden"
python3 "$SCRIPT_DIR/tools/apply_jinteia_fixes.py" "$SRC_DIR/wine"

git -C "$SRC_DIR/wine" diff -- dlls/ntdll/loader.c dlls/ole32/ole2.c     > "$WORK_ROOT/jinteia-wine-v0.2.diff"

say "Jinteia-Proton konfigurieren"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
"$SRC_DIR/configure.sh" --build-name="$BUILD_NAME" --container-engine="$ENGINE"

say "Jinteia-Proton bauen"
make redist

TARBALL="$BUILD_DIR/$BUILD_NAME.tar.gz"
[[ -f "$TARBALL" ]] || die "Build war fertig, aber $TARBALL wurde nicht gefunden."

say "Release-Tarball kopieren"
cp -f "$TARBALL" "$OUTPUT_DIR/$BUILD_NAME.tar.gz"
(cd "$OUTPUT_DIR" && sha256sum "$BUILD_NAME.tar.gz" > "$BUILD_NAME.tar.gz.sha256")

say "Runner installieren und Jinteia vorbereiten"
"$SCRIPT_DIR/install-release.sh" "$TARBALL" auto

cat <<EOF

============================================================
BUILD FERTIG
============================================================

Release-Dateien:
  $OUTPUT_DIR/$BUILD_NAME.tar.gz
  $OUTPUT_DIR/$BUILD_NAME.tar.gz.sha256

Der integrierte Setup-Assistent hat danach Lutris, Ordner, Prefix
und den Eintrag "Jinteia Patcher 0.2" vorbereitet.
============================================================
EOF