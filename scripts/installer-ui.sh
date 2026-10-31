#!/usr/bin/env bash
# Jinteia Proton - interactive terminal front-end
# Source: DtyPnt71 / Burarion. Runs the existing tested installer unchanged.
set -Eeuo pipefail
umask 077

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
WEBVIEW_HELPER="$ROOT/scripts/webview2-download.sh"
VERSION='0.2'
MODE=native
DEMO=0
COLOR=0
[[ -t 1 && -z "${NO_COLOR:-}" && "${TERM:-dumb}" != dumb ]] && COLOR=1

if (( COLOR )); then
  R=$'\e[0m'; B=$'\e[1m'; MUTED=$'\e[2m'; BLUE=$'\e[38;5;75m'; OK=$'\e[38;5;114m'; WARN=$'\e[38;5;215m'; ERR=$'\e[38;5;203m'
else
  R=''; B=''; MUTED=''; BLUE=''; OK=''; WARN=''; ERR=''
fi

say()  { printf '%s\n' "$*"; }
info() { printf '  %s%s%s  %s\n' "$BLUE" 'i' "$R" "$*"; }
warn() { printf '  %s!%s  %s\n' "$WARN" "$R" "$*"; }
fail() { printf '  %sx%s  %s\n' "$ERR" "$R" "$*" >&2; }
done_() { printf '  %s✓%s  %s\n' "$OK" "$R" "$*"; }

header() {
  printf '\n%s' "$BLUE"
  say '  ╭──────────────────────────────────────────────────────╮'
  say '  │                                                      │'
  printf '  │   %s%-51s%s│\n' "$B" 'J I N T E I A   P R O T O N' "$BLUE"
  printf '  │   %-51s│\n' 'by DtyPnt71 / Burarion'
  say '  │                                                      │'
  say '  ╰──────────────────────────────────────────────────────╯'
  printf '%s\n' "$R"
  printf '  %sSETUP%s  •  Runner v%s  •  Native Lutris\n\n' "$B" "$R" "$VERSION"
}
section() { printf '\n  %s%s%s\n  %s\n' "$B" "$1" "$R" '────────────────────────────────────────────────────────'; }
confirm() {
  local answer=''
  [[ -t 0 ]] || return 1
  read -r -p "  $1 [j/N] " answer || return 1
  [[ "$answer" == j || "$answer" == J || "$answer" == ja || "$answer" == JA || "$answer" == y || "$answer" == Y || "$answer" == yes ]]
}

usage() {
  cat <<'EOF'
Jinteia Proton - interactive setup
  bash install.sh                 Open the installer UI in a terminal
  bash install.sh --demo          Preview UI with no downloads or changes
  bash install.sh --mode native   Select native Lutris (recommended)
  bash install.sh --webview2-only Optional official WebView2 x64 download

Other checks: --check, --verify-release, --test-heap, --dry-run, --help
EOF
}

for arg in "$@"; do
  case "$arg" in --demo) DEMO=1;; esac
done
while (( $# )); do
  case "$1" in
    --mode) (( $# >= 2 )) || { fail '--mode requires an argument'; exit 2; }; MODE="$2"; shift 2 ;;
    --demo) shift ;;
    --webview2-only) header; exec bash "$WEBVIEW_HELPER" ;;
    --help|-h) usage; exit 0 ;;
    *) fail "Unknown UI argument: $1"; exit 2 ;;
  esac
done

header
if [[ "$MODE" != native ]]; then
  warn 'Für Jinteia-Proton wird nur natives Lutris unterstützt.'
  warn 'Bitte nicht die Flatpak-Version für diese Einrichtung verwenden.'
  exit 2
fi

section '01  VORAUSSETZUNGEN'
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { fail 'Linux x86_64 ist erforderlich.'; exit 1; }
if [[ "$DEMO" != 1 ]]; then
  [[ "${EUID:-$(id -u)}" != 0 ]] || { fail 'Nicht mit sudo oder als root starten.'; exit 1; }
fi
done_ 'Linux x86_64'

if [[ "$DEMO" == 1 ]]; then
  info 'Vorschau: keine Downloads, Installationen oder Änderungen.'
  section '02  INSTALLATIONSABLAUF'
  done_ 'Native Lutris prüfen'
  done_ 'Runner herunterladen und SHA-256 prüfen'
  done_ 'Proton-Runner installieren'
  done_ 'Lutris-Eintrag einrichten'
  done_ 'Heap-Fix 1+2 mit Original-Backup installieren'
  section '03  ABSCHLUSS'
  done_ 'So sieht die Erfolgsmeldung später aus.'
  info 'WebView2 x64: optionaler Microsoft-Download + Lutris-Anleitung'
  exit 0
fi

# This tool supports native Lutris only. A Flatpak installation is not touched.
if command -v flatpak >/dev/null 2>&1 && flatpak info net.lutris.Lutris >/dev/null 2>&1; then
  warn 'Flatpak-Lutris erkannt. Für dieses Setup bitte natives Lutris nutzen.'
fi
if ! command -v lutris >/dev/null 2>&1; then
  warn 'Lutris ist nicht installiert.'
  distro_id=''; distro_like=''
  if [[ -r /etc/os-release ]]; then
    distro_id="$(. /etc/os-release; printf '%s' "${ID:-}")"
    distro_like="$(. /etc/os-release; printf '%s' "${ID_LIKE:-}")"
  fi
  package_cmd=()
  case " $distro_id $distro_like " in
    *' arch '*|*' cachyos '*|*' manjaro '*) package_cmd=(sudo pacman -S --needed lutris) ;;
    *' ubuntu '*|*' debian '*|*' linuxmint '*|*' pop '*|*' mint '*) package_cmd=(sudo apt-get install lutris) ;;
    *' fedora '*) package_cmd=(sudo dnf install lutris) ;;
    *' opensuse '*|*' suse '*) package_cmd=(sudo zypper install lutris) ;;
  esac
  if (( ${#package_cmd[@]} == 0 )); then
    warn 'Für diese Distribution gibt es keinen automatischen Installationsweg.'
    info 'Native Lutris-Pakete: https://lutris.net/downloads'
    exit 1
  fi
  info "Vorgeschlagener Befehl: ${package_cmd[*]}"
  if confirm 'Natives Lutris jetzt über den Paketmanager installieren?'; then
    if ! command -v sudo >/dev/null 2>&1; then
      fail 'sudo ist nicht vorhanden. Bitte Lutris manuell installieren.'; exit 1
    fi
    say ''
    "${package_cmd[@]}" || { fail 'Lutris-Installation fehlgeschlagen. Kein Proton wurde verändert.'; exit 1; }
    command -v lutris >/dev/null 2>&1 || { fail 'Lutris wurde nach der Paketinstallation nicht gefunden.'; exit 1; }
  else
    info 'Abgebrochen. Bitte natives Lutris installieren und Setup erneut starten.'
    exit 0
  fi
fi
done_ 'Natives Lutris gefunden'

runner_root="${XDG_DATA_HOME:-$HOME/.local/share}/lutris/runners/wine/Jinteia-Proton-0.2"
if [[ -e "$runner_root" || -L "$runner_root" ]]; then
  fail 'Jinteia-Proton-0.2 ist bereits installiert. Keine Dateien werden überschrieben.'
  info 'Status prüfen: bash install.sh --check --runner "$HOME/.local/share/lutris/runners/wine/Jinteia-Proton-0.2"'
  exit 1
fi

section '02  INSTALLATION'
info 'Installiert werden Proton-Runner, Lutris-Eintrag und Heap-Fix 1+2.'
info 'Spielclient und offizielle Patcher-Datei sind nicht enthalten.'
confirm 'Installation starten?' || { info 'Keine Änderungen vorgenommen.'; exit 0; }

log_dir="${XDG_STATE_HOME:-$HOME/.local/state}/jinteia-proton"
mkdir -p -- "$log_dir"
log_file="$log_dir/installer-ui-$(date +%Y%m%d-%H%M%S).log"
: > "$log_file"
chmod 600 "$log_file"

steps=(
  'Runner herunterladen'
  'SHA-256 prüfen'
  'Runner-Archiv entpacken'
  'System und Lutris prüfen'
  'Proton installieren'
  'Lutris-Eintrag anlegen'
  'Heap-Fix 1+2 anwenden'
)
phase=0
last_phase=0
start_time="$(date +%s)"

# The original, tested installer remains responsible for all file operations.
# Its verbose diagnostics go to the user-owned logfile, never to /dev/null.
( printf 'y\n' | JINTEIA_UI_INTERNAL=1 bash "$ROOT/install.sh" --mode native ) > "$log_file" 2>&1 &
worker=$!
trap 'kill "$worker" 2>/dev/null || true' INT TERM

get_phase() {
  if grep -Fq '==> Applying the exact-build Heap Fix' "$log_file"; then phase=7
  elif grep -Fq '[5/6] Jinteia folders and Lutris entry' "$log_file"; then phase=6
  elif grep -Fq '[4/6] Proton runner installation' "$log_file"; then phase=5
  elif grep -Fq '[1/6] System detection' "$log_file"; then phase=4
  elif grep -Fq '==> Extracting verified runner payload' "$log_file"; then phase=3
  elif grep -Fq '==> Verifying published SHA-256' "$log_file"; then phase=2
  elif grep -Fq '==> Downloading v0.2 release package' "$log_file"; then phase=1
  fi
}

while kill -0 "$worker" 2>/dev/null; do
  get_phase
  if (( phase > last_phase )); then
    if (( last_phase > 0 )); then
      printf '\r\033[K  %s✓%s  %s\n' "$OK" "$R" "${steps[last_phase-1]}"
    fi
    printf '  %s•%s  %s' "$BLUE" "$R" "${steps[phase-1]}"
    last_phase=$phase
  fi
  if (( last_phase > 0 )) && [[ -t 1 ]]; then
    elapsed=$(( $(date +%s) - start_time ))
    printf '\r\033[K  %s•%s  %-34s %s%3ds%s' "$BLUE" "$R" "${steps[last_phase-1]}" "$MUTED" "$elapsed" "$R"
  fi
  sleep 0.7
done
wait "$worker" && rc=0 || rc=$?
trap - INT TERM
get_phase
if (( rc != 0 )); then
  printf '\r\033[K\n'
  fail 'Installation fehlgeschlagen. Details stehen im Log.'
  printf '  %sLog:%s %s\n' "$MUTED" "$R" "$log_file"
  printf '\n  %sLetzte Meldungen:%s\n' "$B" "$R"
  tail -n 9 "$log_file" | sed 's/^/    /'
  exit "$rc"
fi
if (( last_phase > 0 )); then
  printf '\r\033[K  %s✓%s  %s\n' "$OK" "$R" "${steps[last_phase-1]}"
fi
# A zero exit status is not enough if the underlying helper unexpectedly
# skipped the critical installation stage; the real back-end reports success.
if ! grep -Fq '==> Runner and Heap Fix ready.' "$log_file"; then
  fail 'Das Backend meldete keinen vollständigen Abschluss. Bitte Log prüfen.'
  info "Log: $log_file"
  exit 1
fi

section '03  INSTALLATION ABGESCHLOSSEN'
done_ 'Jinteia-Proton-0.2 und Heap-Fix 1+2 sind eingerichtet.'
info "Log: $log_file"

if confirm 'Microsoft WebView2 Evergreen x64 von Microsoft herunterladen?'; then
  bash "$WEBVIEW_HELPER" --yes || warn 'WebView2-Download fehlgeschlagen; die Proton-Installation bleibt erhalten.'
fi

section '04  NÄCHSTE SCHRITTE'
say '  1  Lutris vollständig schließen und neu starten.'
say '  2  "Jinteia Patcher 0.2" öffnen und konfigurieren.'
say '  3  Ausführbare Datei: offizielle Nihor2-Patcher.exe wählen.'
say '  4  Arbeitsverzeichnis: ~/Games/Jinteia.'
say '  5  WebView2-x64-Datei in Lutris über'
say '     "EXE im Wine-Präfix ausführen" installieren.'
say '  6  Anschließend den offiziellen Patcher starten.'
say ''
info 'WebView2 (falls übersprungen): https://developer.microsoft.com/microsoft-edge/webview2'
info 'Der Spielclient wurde weder heruntergeladen noch verändert.'