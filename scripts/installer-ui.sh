#!/usr/bin/env bash
# Jinteia Proton — human-facing terminal setup. DtyPnt71 / Burarion.
# Tested, checksum-pinned installer logic stays in ../install.sh.
set -Eeuo pipefail
umask 077

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
WEBVIEW="$ROOT/scripts/webview2-download.sh"
RUNNER='Jinteia-Proton-0.2'
MODE=native
ACTION=install
LANG_CHOICE=''
COLOR=0
[[ -t 1 && -z "${NO_COLOR:-}" && "${TERM:-dumb}" != dumb ]] && COLOR=1
if (( COLOR )); then
  RESET=$'\033[0m'; BOLD=$'\033[1m'; DIM=$'\033[2m'
  ACCENT=$'\033[38;5;81m'; GREEN=$'\033[38;5;114m'
  GOLD=$'\033[38;5;215m'; RED=$'\033[38;5;203m'
else
  RESET=''; BOLD=''; DIM=''; ACCENT=''; GREEN=''; GOLD=''; RED=''
fi

# Small, dependency-free bilingual catalogue: all installer-facing strings live
# here, not mixed into the version-pinned installation backend.
declare -A DE=(
  [mode]='INSTALLATION' [native]='Natives Lutris' [preview]='DESIGNVORSCHAU'
  [requirements]='VORBEREITUNG' [install]='INSTALLATION' [finish]='FERTIG'
  [linux]='Linux x86_64' [requires_linux]='Linux x86_64 ist erforderlich.'
  [no_root]='Bitte nicht als root oder mit sudo starten.'
  [native_found]='Natives Lutris erkannt' [missing_lutris]='Natives Lutris ist nicht installiert.'
  [flatpak]='Flatpak-Lutris wird von diesem Installer nicht unterstützt. Verwende das native Paket.'
  [not_supported]='Für diese Distribution ist keine automatische Lutris-Installation eingerichtet.'
  [lutris_link]='Native Lutris-Pakete: https://lutris.net/downloads'
  [offer_lutris]='Natives Lutris über den Paketmanager installieren?'
  [package_command]='Paketmanager-Befehl' [needs_sudo]='sudo ist für die Paketinstallation erforderlich.'
  [package_failed]='Lutris konnte nicht installiert werden. Proton bleibt unverändert.'
  [not_found_after]='Lutris wurde nach der Installation nicht gefunden.'
  [lutris_cancel]='Lutris wurde nicht installiert. Setup beendet.'
  [already]='Jinteia-Proton-0.2 ist bereits vorhanden und wird nicht überschrieben.'
  [check_hint]='Installationsstatus: bash install.sh --check --runner PFAD'
  [about]='Installiert werden Proton v0.2, der Lutris-Eintrag und Heap-Fix 1+2.'
  [not_included]='Der Spielclient und der offizielle Patcher sind nicht enthalten.'
  [offer_install]='Installation starten?' [cancelled]='Abgebrochen. Keine Installation gestartet.'
  [download]='Proton herunterladen' [verify]='SHA-256 prüfen'
  [extract]='Runner-Archiv auspacken' [preflight]='System und Lutris prüfen'
  [runner]='Proton-Runner installieren' [entry]='Lutris-Eintrag erstellen'
  [heap]='Heap-Fix 1+2 anwenden' [progress]='Installationsschritte'
  [running]='Läuft' [seconds]='Sek.'
  [failed]='Installation fehlgeschlagen. Keine weiteren Schritte ausgeführt.'
  [log]='Diagnoseprotokoll' [recent]='Letzte Fehlermeldungen'
  [incomplete]='Der Installer meldete keinen vollständigen Abschluss. Protokoll prüfen.'
  [complete]='Proton, Lutris-Eintrag und Heap-Fix sind eingerichtet.'
  [offer_webview]='Microsoft WebView2 Evergreen x64 herunterladen?'
  [webview_failed]='WebView2 konnte nicht heruntergeladen werden; Proton bleibt installiert.'
  [next]='NÄCHSTE SCHRITTE' [restart]='Lutris vollständig neu starten.'
  [select]='In Lutris „Jinteia Patcher 0.2“ auswählen.'
  [executable]='Ausführbare Datei: offizielle Nihor2-Patcher.exe auswählen.'
  [directory]='Arbeitsverzeichnis: ~/Games/Jinteia einstellen.'
  [webview_step]='WebView2 über „EXE im Wine-Präfix ausführen“ installieren.'
  [start_game]='Anschließend den offiziellen Patcher starten.'
  [unchanged]='Keine Spieldateien verändert. WebView2 wird nie automatisch ausgeführt.'
  [demo_info]='Nur Vorschau: keine Downloads oder Änderungen.'
  [demo_done]='Vorschau abgeschlossen. Installationsdateien wurden nicht verändert.'
  [invalid_mode]='Nur natives Lutris wird unterstützt. Flatpak bitte nicht verwenden.'
  [bad_lang]='Sprache: de oder en auswählen.'
)
declare -A EN=(
  [mode]='SETUP' [native]='Native Lutris' [preview]='DESIGN PREVIEW'
  [requirements]='PREPARATION' [install]='INSTALLATION' [finish]='COMPLETE'
  [linux]='Linux x86_64' [requires_linux]='Linux x86_64 is required.'
  [no_root]='Do not run as root or with sudo.'
  [native_found]='Native Lutris detected' [missing_lutris]='Native Lutris is not installed.'
  [flatpak]='Flatpak Lutris is not supported by this installer. Use the native package.'
  [not_supported]='Automatic native Lutris installation is not configured for this distribution.'
  [lutris_link]='Native Lutris packages: https://lutris.net/downloads'
  [offer_lutris]='Install native Lutris using the package manager?'
  [package_command]='Package manager command' [needs_sudo]='sudo is required to install the package.'
  [package_failed]='Lutris installation failed. Proton was not changed.'
  [not_found_after]='Lutris was not detected after package installation.'
  [lutris_cancel]='Lutris was not installed. Setup stopped.'
  [already]='Jinteia-Proton-0.2 already exists and will not be overwritten.'
  [check_hint]='Check installation: bash install.sh --check --runner PATH'
  [about]='Installs Proton v0.2, the Lutris entry and Heap Fix 1+2.'
  [not_included]='The game client and official patcher are not included.'
  [offer_install]='Start installation?' [cancelled]='Cancelled. No installation started.'
  [download]='Download Proton' [verify]='Verify SHA-256'
  [extract]='Extract runner archive' [preflight]='Check system and Lutris'
  [runner]='Install Proton runner' [entry]='Create Lutris entry'
  [heap]='Apply Heap Fix 1+2' [progress]='Installation stages'
  [running]='Working' [seconds]='sec'
  [failed]='Installation failed. No further steps were run.'
  [log]='Diagnostic log' [recent]='Recent error details'
  [incomplete]='The installer did not report successful completion. Check the log.'
  [complete]='Proton, Lutris entry and Heap Fix are installed.'
  [offer_webview]='Download Microsoft WebView2 Evergreen x64?'
  [webview_failed]='WebView2 download failed; Proton is still installed.'
  [next]='NEXT STEPS' [restart]='Restart Lutris completely.'
  [select]='Select “Jinteia Patcher 0.2” in Lutris.'
  [executable]='Set executable to the official Nihor2-Patcher.exe.'
  [directory]='Set working directory to ~/Games/Jinteia.'
  [webview_step]='Install WebView2 using “Run EXE inside Wine prefix”.'
  [start_game]='Then launch the official patcher.'
  [unchanged]='No game files changed. WebView2 is never executed automatically.'
  [demo_info]='Preview only: no downloads or changes.'
  [demo_done]='Preview complete. Installation files were not modified.'
  [invalid_mode]='Only native Lutris is supported. Do not use Flatpak here.'
  [bad_lang]='Choose language de or en.'
)
tr() { if [[ "$LANG_CHOICE" == en ]]; then printf '%s' "${EN[$1]}"; else printf '%s' "${DE[$1]}"; fi; }

usage() {
  cat <<'TEXT'
Jinteia Proton | by DtyPnt71 / Burarion
  bash install.sh                 Language selection + interactive setup
  bash install.sh --lang de       Deutsch
  bash install.sh --lang en       English
  bash install.sh --demo          UI preview; no changes
  bash install.sh --webview2-only Official Microsoft WebView2 x64 download
  bash install.sh --mode native   Native Lutris (required)

Read-only diagnostics: --check, --verify-release, --dry-run
Isolated real-binary test: --test-heap
TEXT
}
while (( $# )); do
  case "$1" in
    --lang|--language) (( $# >= 2 )) || { printf 'Missing language.\n' >&2; exit 2; }; LANG_CHOICE="$2"; shift 2 ;;
    --mode) (( $# >= 2 )) || { printf 'Missing Lutris mode.\n' >&2; exit 2; }; MODE="$2"; shift 2 ;;
    --demo) ACTION=demo; shift ;;
    --webview2-only) ACTION=webview; shift ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown UI option: %s\n' "$1" >&2; exit 2 ;;
  esac
done
if [[ -n "$LANG_CHOICE" && "$LANG_CHOICE" != de && "$LANG_CHOICE" != en ]]; then
  printf 'Language / Sprache: de | en\n' >&2; exit 2
fi

choose_language() {
  [[ -n "$LANG_CHOICE" ]] && return
  if [[ -t 0 && -t 1 ]]; then
    printf '\n  %sLANGUAGE / SPRACHE%s\n' "$BOLD" "$RESET"
    printf '  %s1%s  Deutsch\n  %s2%s  English\n\n' "$ACCENT" "$RESET" "$ACCENT" "$RESET"
    local answer=''
    read -r -p '  Auswahl / Choice [1]: ' answer || answer=''
    case "$answer" in 2|en|EN|english|English) LANG_CHOICE=en ;; *) LANG_CHOICE=de ;; esac
  else
    case "${LC_ALL:-${LC_MESSAGES:-${LANG:-de}}}" in de*) LANG_CHOICE=de ;; *) LANG_CHOICE=en ;; esac
  fi
}
choose_language

line() { printf '  %s────────────────────────────────────────────────────────%s\n' "$DIM" "$RESET"; }
brand() {
  printf '\n'
  printf '  %s▌%s  %s%sJINTEIA%s  %sPROTON%s\n' "$ACCENT" "$RESET" "$BOLD" "$ACCENT" "$RESET" "$BOLD" "$RESET"
  printf '  %s   by DtyPnt71 / Burarion%s\n' "$DIM" "$RESET"
  line
  printf '  %s%s%s  /  v0.2  /  %s\n\n' "$BOLD" "$(tr mode)" "$RESET" "$(tr native)"
}
section() { printf '\n  %s%s%s\n' "$BOLD" "$(tr "$1")" "$RESET"; line; }
message() { printf '  %s%s%s  %s\n' "$ACCENT" '·' "$RESET" "$1"; }
warning() { printf '  %s!%s  %s\n' "$GOLD" "$RESET" "$1"; }
error() { printf '  %s×%s  %s\n' "$RED" "$RESET" "$1" >&2; }
success() { printf '  %s✓%s  %s\n' "$GREEN" "$RESET" "$1"; }
confirm() {
  [[ -t 0 ]] || return 1
  local answer=''
  if [[ "$LANG_CHOICE" == de ]]; then
    read -r -p "  $1 [j/N]: " answer || return 1
  else
    read -r -p "  $1 [y/N]: " answer || return 1
  fi
  case "$answer" in j|J|ja|Ja|JA|y|Y|yes|Yes|YES) return 0 ;; *) return 1 ;; esac
}

brand
if [[ "$MODE" != native ]]; then error "$(tr invalid_mode)"; exit 2; fi
if [[ "$ACTION" == webview ]]; then
  exec bash "$WEBVIEW" --lang "$LANG_CHOICE"
fi
section requirements
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { error "$(tr requires_linux)"; exit 1; }
if [[ "$ACTION" != demo ]]; then
  [[ "${EUID:-$(id -u)}" != 0 ]] || { error "$(tr no_root)"; exit 1; }
fi
success "$(tr linux)"

steps=(download verify extract preflight runner entry heap)
# This is *stage progress*, never a made-up download percentage.
progress_bar() {
  local completed="$1" bars=28 i filled out=''
  filled=$((completed * 28 / 7))
  for ((i=0;i<bars;i++)); do
    if ((i < filled)); then out+='━'; else out+='─'; fi
  done
  printf '%s' "$out"
}
show_demo() {
  message "$(tr demo_info)"
  section install
  local i=0
  for key in "${steps[@]}"; do
    ((i+=1))
    printf '  %s✓%s  %02d  %-37s %s%d/7%s\n' "$GREEN" "$RESET" "$i" "$(tr "$key")" "$DIM" "$i" "$RESET"
  done
  printf '\n  %s%s%s  %s7 / 7%s\n' "$ACCENT" "$(progress_bar 7)" "$RESET" "$DIM" "$RESET"
  section finish
  success "$(tr complete)"
  section next
  print_next
  message "$(tr demo_done)"
}
print_next() {
  local keys=(restart select executable directory webview_step start_game) i=0
  for key in "${keys[@]}"; do
    ((i+=1))
    printf '  %s%02d%s  %s\n' "$ACCENT" "$i" "$RESET" "$(tr "$key")"
  done
  printf '\n'
  message "$(tr unchanged)"
}
if [[ "$ACTION" == demo ]]; then show_demo; exit 0; fi

# Native Lutris only: never install or launch Flatpak as a fallback.
if command -v flatpak >/dev/null 2>&1 && flatpak info net.lutris.Lutris >/dev/null 2>&1; then
  warning "$(tr flatpak)"
fi
if ! command -v lutris >/dev/null 2>&1; then
  warning "$(tr missing_lutris)"
  id=''; like=''
  if [[ -r /etc/os-release ]]; then
    id="$(. /etc/os-release; printf '%s' "${ID:-}")"
    like="$(. /etc/os-release; printf '%s' "${ID_LIKE:-}")"
  fi
  package_cmd=()
  case " $id $like " in
    *' arch '*|*' cachyos '*|*' manjaro '*) package_cmd=(sudo pacman -S --needed lutris) ;;
    *' ubuntu '*|*' debian '*|*' linuxmint '*|*' pop '*|*' mint '*) package_cmd=(sudo apt-get install lutris) ;;
    *' fedora '*) package_cmd=(sudo dnf install lutris) ;;
    *' opensuse '*|*' suse '*) package_cmd=(sudo zypper install lutris) ;;
  esac
  if (( ${#package_cmd[@]} == 0 )); then
    warning "$(tr not_supported)"
    message "$(tr lutris_link)"
    exit 1
  fi
  message "$(tr package_command): ${package_cmd[*]}"
  if confirm "$(tr offer_lutris)"; then
    command -v sudo >/dev/null 2>&1 || { error "$(tr needs_sudo)"; exit 1; }
    "${package_cmd[@]}" || { error "$(tr package_failed)"; exit 1; }
    command -v lutris >/dev/null 2>&1 || { error "$(tr not_found_after)"; exit 1; }
  else
    message "$(tr lutris_cancel)"
    exit 0
  fi
fi
success "$(tr native_found)"
runner_path="${XDG_DATA_HOME:-$HOME/.local/share}/lutris/runners/wine/$RUNNER"
if [[ -e "$runner_path" || -L "$runner_path" ]]; then
  error "$(tr already)"
  message "$(tr check_hint)"
  exit 1
fi
section install
message "$(tr about)"
message "$(tr not_included)"
confirm "$(tr offer_install)" || { message "$(tr cancelled)"; exit 0; }

log_dir="${XDG_STATE_HOME:-$HOME/.local/state}/jinteia-proton"
mkdir -p -- "$log_dir"
log_file="$log_dir/installer-ui-$(date +%Y%m%d-%H%M%S).log"
: > "$log_file"
chmod 600 "$log_file"
( printf 'y\n' | JINTEIA_UI_INTERNAL=1 bash "$ROOT/install.sh" --mode native ) > "$log_file" 2>&1 &
worker=$!
trap 'kill "$worker" 2>/dev/null || true' INT TERM

phase=0
last=0
spin=('◐' '◓' '◑' '◒')
tick=0
start_time="$(date +%s)"
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
paint_active() {
  (( phase > 0 )) || return 0
  local elapsed=$(( $(date +%s) - start_time ))
  local txt="$(tr "${steps[phase-1]}")"
  if [[ -t 1 ]]; then
    printf '\r\033[2K  %s%s%s  %02d / 07  %-31.31s  %s%3ds%s' \
      "$ACCENT" "${spin[tick%4]}" "$RESET" "$phase" "$txt" "$DIM" "$elapsed" "$RESET"
  elif (( tick % 20 == 0 )); then
    printf '  %02d / 07  %s\n' "$phase" "$txt"
  fi
}
complete_through() {
  local target="$1"
  while ((last < target)); do
    if ((last > 0)); then
      if [[ -t 1 ]]; then printf '\r\033[2K'; fi
      printf '  %s✓%s  %02d  %s\n' "$GREEN" "$RESET" "$last" "$(tr "${steps[last-1]}")"
    fi
    ((last+=1))
  done
}
while kill -0 "$worker" 2>/dev/null; do
  get_phase
  if ((phase > last)); then complete_through "$phase"; fi
  paint_active
  ((tick+=1))
  sleep 0.4
done
wait "$worker" && rc=0 || rc=$?
trap - INT TERM
get_phase
if [[ -t 1 ]]; then printf '\r\033[2K'; fi
if ((rc != 0)); then
  error "$(tr failed)"
  message "$(tr log): $log_file"
  printf '\n  %s%s%s\n' "$BOLD" "$(tr recent)" "$RESET"
  tail -n 8 "$log_file" | sed 's/^/    /'
  exit "$rc"
fi
if ! grep -Fq '==> Runner and Heap Fix ready.' "$log_file"; then
  error "$(tr incomplete)"
  message "$(tr log): $log_file"
  exit 1
fi
complete_through 8
printf '\n  %s%s%s  %s7 / 7%s\n' "$ACCENT" "$(progress_bar 7)" "$RESET" "$DIM" "$RESET"
section finish
success "$(tr complete)"
message "$(tr log): $log_file"
if confirm "$(tr offer_webview)"; then
  bash "$WEBVIEW" --yes --lang "$LANG_CHOICE" || warning "$(tr webview_failed)"
fi
section next
print_next