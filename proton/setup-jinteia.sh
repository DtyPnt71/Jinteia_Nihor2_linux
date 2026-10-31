#!/usr/bin/env bash
set -euo pipefail

RUNNER_NAME="Jinteia-Proton-0.2"
ENTRY_NAME="Jinteia Patcher 0.2"
PREFIX_DIR="${HOME}/Games/jinteia-prefix"
GAME_DIR="${HOME}/Games/Jinteia"
RUNNER_ARCHIVE=""
LUTRIS_MODE="${JINTEIA_LUTRIS_MODE:-auto}"
CREATE_ENTRY=1
FAIL_IF_EXISTING_RUNNER=0
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENTRY_HELPER="${SCRIPT_DIR}/tools/create_lutris_entry.py"
LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/jinteia-proton"
LOG_FILE="${LOG_DIR}/setup-v0.2.log"
mkdir -p "$LOG_DIR"

if [[ -t 1 ]]; then
    RESET=$'\033[0m'; BOLD=$'\033[1m'; RED=$'\033[31m'; GREEN=$'\033[32m'
    YELLOW=$'\033[33m'; BLUE=$'\033[34m'; MAGENTA=$'\033[35m'; CYAN=$'\033[36m'
else
    RESET=""; BOLD=""; RED=""; GREEN=""; YELLOW=""; BLUE=""; MAGENTA=""; CYAN=""
fi

exec > >(tee "$LOG_FILE") 2>&1

usage() {
    cat <<EOF
Jinteia-Proton setup helper

Usage:
  $0 [options]

Options:
  --runner-archive FILE   Install Proton runner from FILE.
  --runner-name NAME      Runner name. Default: $RUNNER_NAME
  --mode MODE             auto, native or flatpak. Default: auto
  --prefix PATH           Prefix folder. Default: $PREFIX_DIR
  --game-dir PATH         Jinteia folder. Default: $GAME_DIR
  --entry-name NAME       Lutris entry name. Default: $ENTRY_NAME
  --no-entry              Skip automatic Lutris entry creation.
  --fail-if-existing-runner    Do not replace any existing runner.
  -h, --help              Show this help.

Environment:
  JINTEIA_LUTRIS_MODE=flatpak
      Force Flatpak Lutris when native and Flatpak are both installed.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --runner-archive) RUNNER_ARCHIVE="${2:?Missing archive}"; shift 2 ;;
        --runner-name) RUNNER_NAME="${2:?Missing runner name}"; shift 2 ;;
        --mode) LUTRIS_MODE="${2:?Missing mode}"; shift 2 ;;
        --prefix) PREFIX_DIR="${2:?Missing prefix}"; shift 2 ;;
        --game-dir) GAME_DIR="${2:?Missing game dir}"; shift 2 ;;
        --entry-name) ENTRY_NAME="${2:?Missing entry name}"; shift 2 ;;
        --fail-if-existing-runner) FAIL_IF_EXISTING_RUNNER=1; shift ;;
        --no-entry) CREATE_ENTRY=0; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    esac
done

section() {
    printf "\n%s%s[%s] %s%s\n" "$BOLD" "$BLUE" "$1" "$2" "$RESET"
    printf '%s\n' '------------------------------------------------------------'
}
ok()     { printf '  %s[ OK ]%s %s\n' "$GREEN" "$RESET" "$*"; }
info()   { printf '  %s[INFO]%s %s\n' "$CYAN" "$RESET" "$*"; }
warn()   { printf '  %s[WARN]%s %s\n' "$YELLOW" "$RESET" "$*"; }
fail()   { printf '  %s[FAIL]%s %s\n' "$RED" "$RESET" "$*"; }
manual() { printf '  %s[MANUAL]%s %s\n' "$MAGENTA" "$RESET" "$*"; }
fatal()  { fail "$*"; printf '\n%sSetup stopped.%s Log: %s\n' "$RED" "$RESET" "$LOG_FILE"; exit 1; }
have()   { command -v "$1" >/dev/null 2>&1; }

native_lutris_installed() { have lutris; }
flatpak_lutris_installed() { have flatpak && flatpak info net.lutris.Lutris >/dev/null 2>&1; }

load_os_release() {
    OS_PRETTY="Unknown Linux"; OS_ID="unknown"; OS_LIKE=""
    if [[ -r /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release
        OS_PRETTY="${PRETTY_NAME:-${NAME:-Unknown Linux}}"
        OS_ID="${ID:-unknown}"
        OS_LIKE="${ID_LIKE:-}"
    fi
}

detect_lutris_mode() {
    local native=0 flat=0
    native_lutris_installed && native=1
    flatpak_lutris_installed && flat=1
    case "$LUTRIS_MODE" in
        native)
            (( native == 1 )) || fatal "Native Lutris was requested but was not found."
            DETECTED_MODE="native" ;;
        flatpak)
            (( flat == 1 )) || fatal "Flatpak Lutris was requested but was not found."
            DETECTED_MODE="flatpak" ;;
        auto)
            if (( native == 1 && flat == 1 )); then
                DETECTED_MODE="native"
                warn "Both native and Flatpak Lutris are installed."
                warn "Native Lutris will be configured automatically."
                info "To force Flatpak: JINTEIA_LUTRIS_MODE=flatpak ./Jinteia-Proton-0.2-installer.run"
            elif (( native == 1 )); then
                DETECTED_MODE="native"
            elif (( flat == 1 )); then
                DETECTED_MODE="flatpak"
            else
                fatal "Lutris was not found. Install Lutris first and run the installer again."
            fi ;;
        *) fatal "Invalid Lutris mode '$LUTRIS_MODE'. Use auto, native or flatpak." ;;
    esac
}

runner_root_for_mode() {
    local detected=""
    if [[ "$DETECTED_MODE" == "native" ]] && have python3; then
        detected="$(python3 - <<'PY2' 2>/dev/null || true
import os
from lutris import settings
print(getattr(settings, "WINE_DIR", None) or os.path.join(settings.RUNNER_DIR, "wine"))
PY2
)"
    elif [[ "$DETECTED_MODE" == "flatpak" ]]; then
        detected="$(flatpak run --command=python3 net.lutris.Lutris - <<'PY2' 2>/dev/null || true
import os
from lutris import settings
print(getattr(settings, "WINE_DIR", None) or os.path.join(settings.RUNNER_DIR, "wine"))
PY2
)"
    fi

    if [[ -n "$detected" ]]; then
        printf '%s' "$detected"
    elif [[ "$DETECTED_MODE" == "native" ]]; then
        printf '%s' "${XDG_DATA_HOME:-$HOME/.local/share}/lutris/runners/wine"
    else
        printf '%s' "$HOME/.var/app/net.lutris.Lutris/data/lutris/runners/wine"
    fi
}

vulkan_64_present() {
    local p
    for p in /usr/lib/libvulkan.so.1 /usr/lib64/libvulkan.so.1 /usr/lib/x86_64-linux-gnu/libvulkan.so.1; do
        [[ -e "$p" ]] && return 0
    done
    if have ldconfig; then
        ldconfig -p 2>/dev/null | grep -E 'libvulkan\.so\.1.*(x86-64|x86_64)' >/dev/null 2>&1 && return 0
    fi
    return 1
}

vulkan_32_present() {
    local p
    for p in /usr/lib32/libvulkan.so.1 /usr/lib/i386-linux-gnu/libvulkan.so.1; do
        [[ -e "$p" ]] && return 0
    done
    case "${OS_ID} ${OS_LIKE}" in
        *fedora*|*rhel*|*centos*|*suse*|*opensuse*) [[ -e /usr/lib/libvulkan.so.1 ]] && return 0 ;;
    esac
    if have ldconfig; then
        ldconfig -p 2>/dev/null | grep -E 'libvulkan\.so\.1.*(x86-32|i386|i686)' >/dev/null 2>&1 && return 0
    fi
    return 1
}

vulkan_icd_present() {
    compgen -G '/usr/share/vulkan/icd.d/*.json' >/dev/null 2>&1 && return 0
    compgen -G '/etc/vulkan/icd.d/*.json' >/dev/null 2>&1 && return 0
    return 1
}

print_vulkan_hint() {
    case "${OS_ID} ${OS_LIKE}" in
        *arch*|*cachyos*|*manjaro*) info "Arch-based: check vulkan-icd-loader, lib32-vulkan-icd-loader and the matching 64/32-bit GPU driver packages." ;;
        *ubuntu*|*debian*|*linuxmint*) info "Debian/Ubuntu/Mint: check libvulkan1, libvulkan1:i386 and the matching 64/32-bit GPU driver packages." ;;
        *fedora*|*rhel*|*centos*) info "Fedora/RHEL: check vulkan-loader, vulkan-loader.i686 and the matching Vulkan driver packages." ;;
        *suse*|*opensuse*) info "openSUSE: check libvulkan1, libvulkan1-32bit and the matching Vulkan driver packages." ;;
        *) info "Install both 64-bit and 32-bit Vulkan loader/driver support for this distribution." ;;
    esac
}

probe_lutris_python_api() {
    [[ "$CREATE_ENTRY" -eq 0 ]] && return 0
    if [[ "$DETECTED_MODE" == "native" ]]; then
        have python3 || return 1
        python3 - <<'PY' >/dev/null 2>&1
from lutris import settings
from lutris.database import schema
from lutris.config import LutrisConfig, write_game_config
from lutris.database.games import add_game, get_game_by_field, get_games_by_slug, update_existing
from lutris.util.strings import slugify
assert getattr(settings, "WINE_DIR", None) or settings.RUNNER_DIR
PY
    else
        flatpak run --command=python3 net.lutris.Lutris - <<'PY' >/dev/null 2>&1
from lutris import settings
from lutris.database import schema
from lutris.config import LutrisConfig, write_game_config
from lutris.database.games import add_game, get_game_by_field, get_games_by_slug, update_existing
from lutris.util.strings import slugify
assert getattr(settings, "WINE_DIR", None) or settings.RUNNER_DIR
PY
    fi
}

install_runner() (
    if [[ -z "$RUNNER_ARCHIVE" ]]; then
        info "No runner archive supplied; checking an existing installation."
        return 0
    fi
    [[ -f "$RUNNER_ARCHIVE" ]] || fatal "Runner archive not found: $RUNNER_ARCHIVE"
    have tar || fatal "The 'tar' command is required."

    local root stage="" backup="" target committed=0
    root="$(runner_root_for_mode)"
    case "$RUNNER_NAME" in
        ''|.|..|*/*) fatal "Invalid runner folder name: $RUNNER_NAME" ;;
    esac
    mkdir -p "$root"
    target="$root/$RUNNER_NAME"
    if [[ "${FAIL_IF_EXISTING_RUNNER:-0}" == 1 ]] && [[ -e "$target" || -L "$target" ]]; then
        fatal "Existing runner will not be replaced: $target"
    fi
    cleanup_install() {
        local status=$?
        trap - EXIT HUP INT TERM
        if [[ -n "$backup" && ( -e "$backup/runner" || -L "$backup/runner" ) ]]; then
            if (( committed )); then
                rm -rf -- "$backup" || warn "Old runner backup remains at $backup"
            elif [[ ! -e "$target" && ! -L "$target" ]]; then
                mv -- "$backup/runner" "$target" || {
                    fail "Restore failed. Your original runner is safe at $backup/runner"
                    status=1
                }
            fi
        fi
        [[ -z "$stage" ]] || rm -rf -- "$stage"
        [[ -z "$backup" ]] || rmdir -- "$backup" 2>/dev/null || true
        exit "$status"
    }
    trap cleanup_install EXIT
    trap 'exit 129' HUP
    trap 'exit 130' INT
    trap 'exit 143' TERM

    # Work on the same filesystem so replacing the directory uses rename.
    # Never remove the working runner before validating the replacement.
    stage="$(mktemp -d "$root/.jinteia-install.XXXXXXXX")"
    tar -tzf "$RUNNER_ARCHIVE" > "$stage/members" || fatal "Runner archive is damaged or unreadable."
    local member normalized
    while IFS= read -r member; do
        normalized="$member"
        while [[ "$normalized" == ./* ]]; do normalized="${normalized#./}"; done
        [[ -z "$normalized" || "$normalized" == . ]] && continue
        case "/$normalized/" in
            */../*) fatal "Archive contains an unsafe path: $member" ;;
        esac
        [[ "$normalized" == "$RUNNER_NAME" || "$normalized" == "$RUNNER_NAME/"* ]] ||
            fatal "Archive must contain only the folder '$RUNNER_NAME': $member"
    done < "$stage/members"
    mkdir "$stage/extracted"
    tar -xzf "$RUNNER_ARCHIVE" --no-same-owner -C "$stage/extracted" || fatal "Could not extract runner archive."
    [[ -d "$stage/extracted/$RUNNER_NAME" && ! -L "$stage/extracted/$RUNNER_NAME" &&
       -s "$stage/extracted/$RUNNER_NAME/proton" && ! -L "$stage/extracted/$RUNNER_NAME/proton" ]] ||
        fatal "Runner archive is incomplete: a non-empty proton launcher is required."
    chmod +x "$stage/extracted/$RUNNER_NAME/proton" || fatal "Could not set launcher permissions."

    if [[ -e "$target" || -L "$target" ]]; then
        backup="$(mktemp -d "$root/.jinteia-backup.XXXXXXXX")"
        mv -- "$target" "$backup/runner" || fatal "Could not back up the existing runner."
    fi
    mv -- "$stage/extracted/$RUNNER_NAME" "$target" || fatal "Could not activate the new runner."
    committed=1
    ok "Installed Proton runner: $target"
)

create_directories() {
    mkdir -p "$GAME_DIR" "$PREFIX_DIR"
    ok "Jinteia folder: $GAME_DIR"
    ok "Wine/Proton prefix folder: $PREFIX_DIR"
}

create_lutris_entry() {
    [[ "$CREATE_ENTRY" -eq 1 ]] || { warn "Automatic Lutris entry creation was disabled."; return 0; }
    [[ -f "$ENTRY_HELPER" ]] || fatal "Lutris entry helper is missing: $ENTRY_HELPER"
    if [[ "$DETECTED_MODE" == "native" ]]; then
        python3 "$ENTRY_HELPER" "$ENTRY_NAME" "$RUNNER_NAME" "$PREFIX_DIR" "$GAME_DIR"
    else
        flatpak run --command=python3 net.lutris.Lutris - "$ENTRY_NAME" "$RUNNER_NAME" "$PREFIX_DIR" "$GAME_DIR" < "$ENTRY_HELPER"
    fi
    ok "Lutris entry prepared: $ENTRY_NAME"
}

webview2_installed() {
    local base="$PREFIX_DIR/drive_c" directory found
    [[ -d "$base" ]] || return 1
    for directory in "$base/Program Files (x86)/Microsoft/EdgeWebView/Application" \
                     "$base/Program Files/Microsoft/EdgeWebView/Application"; do
        [[ -d "$directory" ]] || continue
        found="$(find "$directory" -maxdepth 4 -type f -iname 'msedgewebview2.exe' -print -quit 2>/dev/null)" || continue
        [[ -z "$found" ]] || return 0
    done
    return 1
}

final_dialog() {
    printf '\n%s%s╔════════════════════════════════════════════════════════════╗%s\n' "$BOLD" "$GREEN" "$RESET"
    printf '%s%s║              JINTEIA SETUP COMPLETED                     ║%s\n' "$BOLD" "$GREEN" "$RESET"
    printf '%s%s╚════════════════════════════════════════════════════════════╝%s\n' "$BOLD" "$GREEN" "$RESET"

    printf '\n%sPrepared automatically:%s\n' "$BOLD" "$RESET"
    printf '  • Proton runner: %s\n' "$RUNNER_NAME"
    printf '  • Lutris entry:  %s\n' "$ENTRY_NAME"
    printf '  • Prefix:        %s\n' "$PREFIX_DIR"
    printf '  • Game folder:   %s\n' "$GAME_DIR"

    printf '\n%s%sNEXT STEPS IN LUTRIS%s\n' "$BOLD" "$YELLOW" "$RESET"
    printf '%s\n' '------------------------------------------------------------'
    printf '  1. Fully close Lutris and start it again.\n'
    printf '  2. Open the entry: %s%s%s\n' "$BOLD" "$ENTRY_NAME" "$RESET"
    printf '  3. Open %sConfigure → Game options%s.\n' "$BOLD" "$RESET"
    printf '  4. Set %sExecutable%s to your %sNihor2-Patcher.exe%s.\n' "$BOLD" "$RESET" "$BOLD" "$RESET"
    printf '  5. Set %sWorking directory%s to the Jinteia main folder.\n' "$BOLD" "$RESET"
    printf '     Prepared default folder: %s\n' "$GAME_DIR"
    printf '  6. Save the configuration.\n'
    printf '  7. Select %s and choose %sRun EXE inside Wine prefix%s.\n' "$ENTRY_NAME" "$BOLD" "$RESET"
    printf '  8. Install %sMicrosoft Edge WebView2 Evergreen Runtime x64%s.\n' "$BOLD" "$RESET"
    printf '  9. Start the Jinteia Patcher.\n'

    if webview2_installed; then
        ok "WebView2 was detected in the prefix."
    else
        manual "WebView2 is not installed yet. Complete step 8 before starting the patcher."
    fi

    if [[ "$DETECTED_MODE" == "flatpak" ]]; then
        printf '\n%s%sFLATPAK NOTE%s\n' "$BOLD" "$YELLOW" "$RESET"
        printf '  Flatpak Lutris is supported by this helper, but sandbox and\n'
        printf '  filesystem permissions can cause path or runner-detection issues.\n'
        printf '  Native Lutris is preferred when troubleshooting.\n'
    fi

    printf '\nSetup log:\n  %s\n\n' "$LOG_FILE"
}

clear 2>/dev/null || true
printf '%s%sJinteia-Proton 0.2 Setup%s\n' "$BOLD" "$CYAN" "$RESET"
printf 'Automated preflight, runner installation and Lutris preparation.\n'

section '1/6' 'System detection'
load_os_release
info "Distribution: $OS_PRETTY"
info "Distribution ID: $OS_ID${OS_LIKE:+ (ID_LIKE: $OS_LIKE)}"
info "Kernel: $(uname -sr)"
info "Architecture: $(uname -m)"
info "Desktop: ${XDG_CURRENT_DESKTOP:-unknown}"
info "Session: ${XDG_SESSION_TYPE:-unknown}"
[[ "$(uname -s)" == 'Linux' ]] || fatal "This installer is for Linux only."
[[ "$(uname -m)" == 'x86_64' ]] || fatal "Jinteia-Proton 0.2 currently requires x86_64."
ok "Linux x86_64 detected."

section '2/6' 'Lutris detection'
detect_lutris_mode
if [[ "$DETECTED_MODE" == 'native' ]]; then
    ver="$(lutris --version 2>/dev/null | head -n 1 || true)"
    ok "Native Lutris detected${ver:+: $ver}"
    flatpak_lutris_installed && warn "Flatpak Lutris is also installed but will not be modified."
else
    ver="$(flatpak info --show-version net.lutris.Lutris 2>/dev/null || true)"
    ok "Flatpak Lutris detected${ver:+: $ver}"
    warn "Flatpak can work, but sandbox/file-access differences may cause problems."
    warn "Native Lutris is recommended when troubleshooting."
fi

section '3/6' 'Dependency checks'
have bash && ok "Bash is available." || fatal "Bash is required."
have tar && ok "tar is available." || fatal "tar is required."
have tee && ok "tee is available." || fatal "tee is required."
if [[ "$DETECTED_MODE" == 'native' ]]; then
    have python3 && ok "Python 3 is available." || fatal "Python 3 is required for automatic native Lutris configuration."
else
    ok "Flatpak provides the Python environment used for Lutris configuration."
fi
probe_lutris_python_api && ok "Lutris configuration API is available." || fatal "The Lutris configuration API could not be loaded safely."

if vulkan_64_present; then ok "64-bit Vulkan loader detected."; else warn "64-bit Vulkan loader was not detected by the generic probe."; print_vulkan_hint; fi
if vulkan_32_present; then ok "32-bit Vulkan loader detected."; else warn "32-bit Vulkan loader was not detected."; warn "Lutris/Wine compatibility is more reliable with 64-bit and 32-bit Vulkan support."; print_vulkan_hint; fi
if vulkan_icd_present; then ok "Vulkan ICD manifest(s) detected."; else warn "No host Vulkan ICD manifest was found in standard locations."; fi
if have vulkaninfo; then
    vulkaninfo --summary >/dev/null 2>&1 && ok "vulkaninfo completed successfully." || warn "vulkaninfo is installed but could not query Vulkan successfully."
else
    info "vulkaninfo is not installed. This diagnostic tool is optional."
fi
if have lspci; then
    gpu="$(lspci 2>/dev/null | grep -Ei 'VGA|3D controller|Display controller' | head -n 2 || true)"
    if [[ -n "$gpu" ]]; then info "Detected GPU:"; while IFS= read -r line; do printf '       %s\n' "$line"; done <<< "$gpu"; fi
else
    info "lspci is not installed; GPU model was not probed."
fi
manual "Microsoft Edge WebView2 Runtime x64 must be installed into the Jinteia prefix after this setup."

section '4/6' 'Proton runner installation'
install_runner
runner_root="$(runner_root_for_mode)"
[[ -f "$runner_root/$RUNNER_NAME/proton" ]] && ok "Runner verified: $RUNNER_NAME" || fatal "Runner '$RUNNER_NAME' is not installed in the selected Lutris installation."

section '5/6' 'Jinteia folders and Lutris entry'
create_directories
create_lutris_entry

section '6/6' 'Final instructions'
final_dialog