#!/usr/bin/env bash
# Download helper for Microsoft's official WebView2 Evergreen x64 standalone.
# This helper deliberately NEVER executes the downloaded Windows program.
set -Eeuo pipefail
umask 077

URL='https://go.microsoft.com/fwlink/?linkid=2124701'
FILE='MicrosoftEdgeWebView2RuntimeInstallerX64.exe'
TARGET_DIR="${XDG_DOWNLOAD_DIR:-$HOME/Downloads}/Jinteia-Proton"

confirm() {
    local answer=''
    [[ -t 0 ]] || return 1
    read -r -p '  WebView2 Evergreen x64 von Microsoft herunterladen? [j/N] ' answer || return 1
    [[ "$answer" == j || "$answer" == J || "$answer" == ja || "$answer" == y || "$answer" == Y || "$answer" == yes ]]
}

if [[ "${1:-}" != --yes ]]; then
    confirm || { printf '  Übersprungen.\n'; exit 0; }
fi
if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
    printf '  Fehler: curl oder wget benötigt.\n' >&2
    exit 1
fi
mkdir -p -- "$TARGET_DIR"
target="$TARGET_DIR/$FILE"
if [[ -e "$target" || -L "$target" ]]; then
    printf '  Datei existiert bereits: %s\n' "$target"
    printf '  Keine vorhandene Datei wird überschrieben.\n'
    exit 0
fi
tmp="$(mktemp "$TARGET_DIR/.webview2.XXXXXXXX")"
trap 'rm -f -- "$tmp"' EXIT
printf '  Quelle: Microsoft WebView2 Evergreen Standalone x64\n'
if command -v curl >/dev/null 2>&1; then
    curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.2 \
        --retry 2 --progress-bar --output "$tmp" "$URL"
else
    wget --https-only --output-document="$tmp" "$URL"
fi
# The stable Microsoft link returns a PE executable. Do not accept an HTML
# error or an empty response. The Evergreen version changes over time; there
# is deliberately no fabricated pinned checksum here.
magic="$(LC_ALL=C head -c 2 "$tmp")"
size="$(wc -c < "$tmp")"
if [[ "$magic" != MZ || "$size" -lt 102400 ]]; then
    printf '  Fehler: Download ist kein plausibler Windows-Installer. Datei verworfen.\n' >&2
    exit 1
fi
chmod 600 "$tmp"
# Creating the destination as a hard link refuses to clobber it even if
# another process created it while the download was running.
if ! ln -- "$tmp" "$target"; then
    printf '  Fehler: Zieldatei existiert schon oder ist nicht beschreibbar.\n' >&2
    exit 1
fi
rm -f -- "$tmp"
trap - EXIT
printf '\n  Download abgeschlossen: %s\n' "$target"
printf '  Größe: %s Bytes\n' "$size"
printf '\n  WebView2 in Lutris installieren:\n'
printf '  1. Lutris neu starten und "Jinteia Patcher 0.2" auswählen.\n'
printf '  2. Prüfen: Wine-Version Jinteia-Proton-0.2.\n'
printf '  3. Rechtsklick: "EXE im Wine-Präfix ausführen".\n'
printf '  4. Diese Datei auswählen: %s\n' "$target"
printf '  5. Microsoft-Installation abschließen und Lutris danach neu starten.\n'
printf '\n  Hinweis: Die Datei wurde nur heruntergeladen, NICHT gestartet.\n'