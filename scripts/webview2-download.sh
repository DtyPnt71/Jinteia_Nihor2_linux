#!/usr/bin/env bash
# Optional Microsoft WebView2 Evergreen x64 downloader.
# Downloads only, never executes the Microsoft .exe.
set -Eeuo pipefail
umask 077

URL='https://go.microsoft.com/fwlink/?linkid=2124701'
FILE='MicrosoftEdgeWebView2RuntimeInstallerX64.exe'
TARGET_DIR="${XDG_DOWNLOAD_DIR:-$HOME/Downloads}/Jinteia-Proton"
LANG_CHOICE=''
AUTO=0
while (( $# )); do
  case "$1" in
    --yes) AUTO=1; shift ;;
    --lang|--language) (( $# >= 2 )) || { printf 'Missing language.\n' >&2; exit 2; }; LANG_CHOICE="$2"; shift 2 ;;
    --help) printf 'WebView2 downloader: [--lang de|en] [--yes]\n'; exit 0 ;;
    *) printf 'Unsupported option: %s\n' "$1" >&2; exit 2 ;;
  esac
done
if [[ -z "$LANG_CHOICE" ]]; then
  case "${LC_ALL:-${LC_MESSAGES:-${LANG:-de}}}" in de*) LANG_CHOICE=de ;; *) LANG_CHOICE=en ;; esac
fi
[[ "$LANG_CHOICE" == de || "$LANG_CHOICE" == en ]] || { printf 'Invalid language: de | en\n' >&2; exit 2; }

say() { printf '  %s\n' "$1"; }
t() {
  local key="$1"
  if [[ "$LANG_CHOICE" == de ]]; then
    case "$key" in
      ask) printf 'WebView2 Evergreen x64 von Microsoft herunterladen?' ;;
      skip) printf 'Übersprungen.' ;;
      missing) printf 'curl oder wget wird benötigt.' ;;
      existing) printf 'Datei ist bereits vorhanden; sie wird nicht überschrieben:' ;;
      source) printf 'Quelle: Microsoft WebView2 Evergreen Standalone x64' ;;
      invalid) printf 'Download ist kein plausibler Windows-Installer. Datei verworfen.' ;;
      conflict) printf 'Zieldatei existiert bereits oder ist nicht beschreibbar.' ;;
      completed) printf 'Download abgeschlossen:' ;;
      size) printf 'Dateigröße:' ;;
      guide) printf 'WebView2 in Lutris installieren' ;;
      a) printf 'Lutris vollständig schließen und neu starten.' ;;
      b) printf '„Jinteia Patcher 0.2“ auswählen; Wine-Version prüfen: Jinteia-Proton-0.2.' ;;
      c) printf 'Rechtsklick → „EXE im Wine-Präfix ausführen“.' ;;
      d) printf 'Die unten angegebene Datei auswählen:' ;;
      e) printf 'Den Microsoft-Installer abschließen, danach Lutris neu starten.' ;;
      notice) printf 'Nur heruntergeladen. Die Datei wurde NICHT ausgeführt.' ;;
    esac
  else
    case "$key" in
      ask) printf 'Download Microsoft WebView2 Evergreen x64?' ;;
      skip) printf 'Skipped.' ;;
      missing) printf 'curl or wget is required.' ;;
      existing) printf 'File already exists and will not be overwritten:' ;;
      source) printf 'Source: Microsoft WebView2 Evergreen Standalone x64' ;;
      invalid) printf 'Download is not a plausible Windows installer. File discarded.' ;;
      conflict) printf 'Destination already exists or is not writable.' ;;
      completed) printf 'Download complete:' ;;
      size) printf 'File size:' ;;
      guide) printf 'Install WebView2 in Lutris' ;;
      a) printf 'Close Lutris completely and restart it.' ;;
      b) printf 'Select “Jinteia Patcher 0.2”; verify Wine version: Jinteia-Proton-0.2.' ;;
      c) printf 'Right-click → “Run EXE inside Wine prefix”.' ;;
      d) printf 'Choose the downloaded file below:' ;;
      e) printf 'Complete Microsoft setup, then restart Lutris.' ;;
      notice) printf 'Downloaded only. The file was NOT executed.' ;;
    esac
  fi
}

if (( !AUTO )); then
  [[ -t 0 ]] || { say "$(t skip)"; exit 0; }
  answer=''
  if [[ "$LANG_CHOICE" == de ]]; then
    read -r -p "  $(t ask) [j/N]: " answer || exit 0
  else
    read -r -p "  $(t ask) [y/N]: " answer || exit 0
  fi
  case "$answer" in j|J|ja|JA|y|Y|yes|YES) ;; *) say "$(t skip)"; exit 0 ;; esac
fi
if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
  say "$(t missing)" >&2; exit 1
fi
mkdir -p -- "$TARGET_DIR"
target="$TARGET_DIR/$FILE"
if [[ -e "$target" || -L "$target" ]]; then
  say "$(t existing) $target"
  exit 0
fi
tmp="$(mktemp "$TARGET_DIR/.webview2.XXXXXXXX")"
trap 'rm -f -- "$tmp"' EXIT
say "$(t source)"
if command -v curl >/dev/null 2>&1; then
  curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.2 \
       --retry 2 --progress-bar --output "$tmp" "$URL"
else
  wget --https-only --output-document="$tmp" "$URL"
fi
# Evergreen changes over time: HTTPS + PE magic + plausible size are basic
# integrity screening, NOT an authenticated fixed-version hash or signature.
magic="$(LC_ALL=C head -c 2 "$tmp")"
size="$(wc -c < "$tmp")"
if [[ "$magic" != MZ || "$size" -lt 102400 ]]; then
  say "$(t invalid)" >&2; exit 1
fi
chmod 600 "$tmp"
# Atomic no-clobber link; a concurrent invocation cannot replace an .exe.
if ! ln -- "$tmp" "$target"; then
  say "$(t conflict)" >&2; exit 1
fi
rm -f -- "$tmp"
trap - EXIT
printf '\n'
say "$(t completed) $target"
say "$(t size) $size bytes"
printf '\n  %s\n' "$(t guide)"
for k in a b c d e; do
  case "$k" in a) n=1 ;; b) n=2 ;; c) n=3 ;; d) n=4 ;; e) n=5 ;; esac
  say "$n. $(t "$k")"
  [[ "$k" == d ]] && say "   $target"
done
printf '\n'
say "$(t notice)"