#!/usr/bin/env bash
# Jinteia-Proton source-readable installer preview — DtyPnt71.
# This preview uses the VERIFIED existing v0.2 .run as a transport archive,
# but NEVER EXECUTES the .run wrapper. The setup and Heap-Fix source lives here.
set -euo pipefail
umask 077

# Route interactive installs through the readable UI. Scripted checks and
# non-interactive callers retain the tested core behavior.
if [[ "${JINTEIA_UI_INTERNAL:-0}" != 1 ]]; then
  case "${1:-}" in
    --demo|--webview2-only)
      exec bash "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/scripts/installer-ui.sh" "$@" ;;
  esac
  if [[ -t 0 && -t 1 ]]; then
    case "${1:-}" in
      ''|--mode)
        exec bash "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/scripts/installer-ui.sh" "$@" ;;
    esac
  fi
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_NAME='Jinteia-Proton-0.2'
ASSET='Jinteia-Proton-0.2-installer.run'
EXPECTED_SHA256='e2d73e4c36266c4c07323bd73a318f9e52e5a805f4774ae1cab8c994df9b59e7'
EXPECTED_ORIGINAL_DLL_SHA256='ad0243384afa5fad82331dacfd7e45383b2a0c955fb8f99dd12e1cfd7d558438'
URL='https://github.com/DtyPnt71/Jinteia_Nihor2_linux/releases/download/v0.2/Jinteia-Proton-0.2-installer.run'
SETUP="$SCRIPT_DIR/proton/setup-jinteia.sh"
HEAP="$SCRIPT_DIR/heap/heap-test.py"
MODE='auto'
ACTION='install'
HEAP_RUNNER=''

say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }
usage() {
  cat <<'HELP'
Jinteia-Proton v0.2 — source-readable installation preview

Usage:
  bash install.sh                  Install runner, then apply matching Heap Fix
  bash install.sh --dry-run        Explain planned changes (NO downloads or writes)
  bash install.sh --check         Read-only status of the existing DLL and backup
  bash install.sh --verify-release Download/verify actual release archive only (no installation)
  bash install.sh --test-heap     Isolated test: patch, verify and restore in a temporary directory
  bash install.sh --heap-only     Apply the matching Heap Fix to existing runner
  bash install.sh --runner PATH   Choose the installed runner for Heap Fix explicitly
  bash install.sh --mode MODE     Native Lutris recommended; Flatpak not supported by the UI
  bash install.sh --demo          UI preview without downloads or changes
  bash install.sh --webview2-only Optional official Microsoft x64 download
  bash install.sh --help

Requires the game and Lutris to be closed. Never run with sudo.
This is a preview, NOT a fully tested replacement for the v0.2 release.
WebView2 and the official Jinteia patcher still need manual setup.
HELP
}
while (( $# )); do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --dry-run) ACTION='dry-run'; shift ;;
    --heap-only) ACTION='heap-only'; shift ;;
    --check) ACTION='check'; shift ;;
    --verify-release) ACTION='verify-release'; shift ;;
    --test-heap) ACTION='test-heap'; shift ;;
    --mode) (( $# >= 2 )) || die '--mode requires a value'; MODE="$2"; shift 2 ;;
    --runner) (( $# >= 2 )) || die '--runner requires a path'; HEAP_RUNNER="$2"; shift 2 ;;
    *) die "Unknown option: $1 (try --help)" ;;
  esac
done
case "$MODE" in auto|native|flatpak) ;; *) die "Invalid mode: $MODE" ;; esac
[[ -f "$SETUP" && -f "$SCRIPT_DIR/proton/tools/create_lutris_entry.py" && -f "$HEAP" && -f "$SCRIPT_DIR/heap/heap_core.py" && -f "$SCRIPT_DIR/heap/binary_patch.py" ]] || die 'Required public source files are missing.'

say 'What this installer will do'
printf '%s\n' \
  '  - Readable source code for the installation and Heap Fix is included.' \
  '  - Download the existing v0.2 release payload only from GitHub.' \
  '  - Verify the entire download with its published SHA-256 checksum.' \
  '  - Extract the runner WITHOUT executing the bundled .run script.' \
  '  - Use proton/setup-jinteia.sh to install runner and prepare Lutris.' \
  '  - Apply Heap Fix only if the ntdll.dll SHA-256 matches the known v0.2 build.' \
  '  - Keep the original DLL backup for later restoration.' \
  '  - Never require sudo or replace system Wine.' \
  '  - You still install WebView2 and select the official patcher manually.'

[[ "$ACTION" == 'dry-run' ]] && { say 'Dry run complete. No files downloaded or changed.'; exit 0; }
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || die 'Linux x86_64 is required.'
[[ "$ACTION" == 'check' || "$ACTION" == 'verify-release' || "${EUID:-$(id -u)}" != 0 ]] || die 'Do not run as root or with sudo.'
command -v python3 >/dev/null 2>&1 || die 'Python 3 is required.'

run_heap() {
  local args=(apply)
  if [[ -n "$HEAP_RUNNER" ]]; then args+=(--runner "$HEAP_RUNNER"); fi
  say 'Applying the exact-build Heap Fix (includes backup and post-write validation)'
  python3 "$HEAP" "${args[@]}" || die 'Heap Fix did not complete. See the message above. The installer will not patch an unknown DLL.'
}

if [[ "$ACTION" == 'check' ]]; then
  say 'Checking installed Heap Fix (read-only; no downloads or modifications)'
  check_args=(check)
  if [[ -n "$HEAP_RUNNER" ]]; then check_args+=(--runner "$HEAP_RUNNER"); fi
  python3 "$HEAP" "${check_args[@]}"
  exit $?
fi

if [[ "$ACTION" == 'heap-only' ]]; then
  run_heap
  say 'Heap Fix completed; restart Lutris and the game.'
  exit 0
fi

# Preserve existing installations: the v0.2 setup helper normally replaces
# an existing runner, which could erase a working hand-patched ntdll.dll.
if [[ "$ACTION" == install ]]; then
for root in "${XDG_DATA_HOME:-$HOME/.local/share}/lutris/runners/wine" \
            "$HOME/.var/app/net.lutris.Lutris/data/lutris/runners/wine"; do
  [[ ! -e "$root/$RUNNER_NAME" && ! -L "$root/$RUNNER_NAME" ]] ||
    die "Existing $RUNNER_NAME detected in $root. Keeping it unchanged. For a compatible existing install, use --heap-only."
done
fi

for cmd in sha256sum awk tail tar mktemp; do
  command -v "$cmd" >/dev/null 2>&1 || die "Missing command: $cmd"
done
command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 || die 'curl or wget is required.'

if [[ "$ACTION" == install ]]; then
  printf '\nBefore continuing: completely close Lutris, the game, and its patcher.\n'
  read -r -p 'Proceed with installation? [y/N] ' answer
  case "$answer" in y|Y|yes|YES) ;; *) say 'Cancelled; no changes made.'; exit 0 ;; esac
else
  if [[ "$ACTION" == test-heap ]]; then
    say 'Isolated Heap-Fix test: writes only to a temporary test runner (no Lutris/prefix changes).'
  else
    say 'Read-only release verification selected: no Lutris/runner/prefix changes.'
  fi
fi

TMP="$(mktemp -d "${TMPDIR:-/tmp}/jinteia-source-installer.XXXXXXXX")"
trap 'rm -rf -- "$TMP"' EXIT

if [[ "$ACTION" == test-heap ]]; then
  command -v df >/dev/null 2>&1 || die 'df is required for a safe temporary storage check.'
  free_kib="$(df -Pk "$TMP" | awk 'NR == 2 {print $4}')"
  [[ "$free_kib" =~ ^[0-9]+$ ]] || die 'Could not determine available temporary space.'
  (( free_kib >= 4194304 )) || die 'Isolated test needs at least 4 GiB free at TMPDIR. Choose a filesystem with sufficient space and retry.'
fi

download="$TMP/$ASSET"
say 'Downloading v0.2 release package (~540 MB)'
if command -v curl >/dev/null 2>&1; then
  curl --fail --location --retry 2 --proto '=https' --proto-redir '=https' --tlsv1.2 --output "$download" "$URL"
else
  wget --https-only --output-document="$download" "$URL"
fi
say 'Verifying published SHA-256'
( cd "$TMP" && printf '%s  %s\n' "$EXPECTED_SHA256" "$ASSET" | sha256sum --check --status ) || die 'Checksum mismatch. Installation stopped.'

# The historical onefile script adds a gzip tar after a text marker.
# We extract ONLY the inner runner archive and execute our checked-in setup.
marker='__JINTEIA_PAYLOAD_BELOW__'
line="$(awk -v marker="$marker" '$0 == marker { print NR + 1; exit }' "$download")"
[[ "$line" =~ ^[0-9]+$ ]] || die 'Unrecognized .run format. No code executed.'
runner_archive="$TMP/$RUNNER_NAME.tar.gz"
say 'Extracting verified runner payload without running the .run wrapper'
tail -n +"$line" "$download" | tar -xzOf - "payload/$RUNNER_NAME.tar.gz" > "$runner_archive" || die 'Cannot locate the expected nested runner archive.'
[[ -s "$runner_archive" ]] || die 'Empty runner archive.'

if [[ "$ACTION" == 'verify-release' || "$ACTION" == 'test-heap' ]]; then
  say 'Checking original 64-bit DLL inside verified release'
  member="$(tar -tzf "$runner_archive" | awk -v p="$RUNNER_NAME/files/lib/wine/x86_64-windows/ntdll.dll" '($0 == p || $0 == "./" p) && !found { print; found=1 }')"
  [[ -n "$member" ]] || die 'The released runner archive contains no matching 64-bit DLL path.'
  actual_dll_sha="$(tar -xzOf "$runner_archive" "$member" | sha256sum | awk '{print $1}')"
  if [[ "$actual_dll_sha" != "$EXPECTED_ORIGINAL_DLL_SHA256" ]]; then
    printf 'Observed original DLL SHA-256: %s\n' "$actual_dll_sha" >&2
    die 'The released runner DLL does not match the known v0.2 original. No changes made.'
  fi
  say 'RELEASE VERIFIED: asset checksum, nested runner archive, and original 64-bit DLL match.'
  printf 'SHA-256: %s\nOriginal DLL SHA-256: %s\n' "$EXPECTED_SHA256" "$actual_dll_sha"
  if [[ "$ACTION" == verify-release ]]; then
    say 'No installer scripts, Wine runner or Heap Fix were executed.'
    exit 0
  fi

  # Isolated real-binary verification: only the matched, verified archive is
  # extracted under the mktemp directory. No Lutris settings or runner roots.
  # Reject unsafe absolute/parent member paths before extraction, as the
  # regular installer helper already does.
  say 'Checking runner archive member paths before temporary extraction'
  local_members="$TMP/runner-members.txt"
  tar -tzf "$runner_archive" > "$local_members" || die 'Runner archive listing failed.'
  while IFS= read -r entry; do
    normalized="$entry"
    while [[ "$normalized" == ./* ]]; do normalized="${normalized#./}"; done
    [[ -z "$normalized" || "$normalized" == . ]] && continue
    case "/$normalized/" in */../*) die "Unsafe archive path: $entry" ;; esac
    [[ "$normalized" == "$RUNNER_NAME" || "$normalized" == "$RUNNER_NAME/"* ]] || die "Unexpected runner archive member: $entry"
  done < "$local_members"

  sandbox="$TMP/isolated-runner"
  mkdir -p "$sandbox"
  say 'Extracting released runner into private temporary test area'
  tar -xzf "$runner_archive" --no-same-owner -C "$sandbox" || die 'Temporary runner extraction failed.'
  test_runner="$sandbox/$RUNNER_NAME"
  test_dll="$test_runner/files/lib/wine/x86_64-windows/ntdll.dll"
  [[ -f "$test_runner/proton" && -f "$test_dll" && ! -L "$test_dll" ]] || die 'Expected test files are missing or the DLL is a symlink.'
  [[ "$(sha256sum "$test_dll" | awk '{print $1}')" == "$EXPECTED_ORIGINAL_DLL_SHA256" ]] || die 'Temporary test DLL does not match original build.'

  # The recovered Heap Fix saves diagnostics by default. Redirect its state
  # data inside TMP as well so the test leaves no personal-files changes.
  export XDG_STATE_HOME="$TMP/test-state"
  say 'Applying real Heap-Fix1+2 to the isolated test DLL'
  python3 "$HEAP" apply --runner "$test_runner" || die 'Real-binary isolated Heap Fix application failed.'
  [[ "$(sha256sum "$test_dll" | awk '{print $1}')" == '7b925e64a014111f80a1be831866f4d38f34c51abc35640ea87a6926716b021f' ]] || die 'Patched DLL checksum mismatch.'
  test_backup="$test_dll.jinteia-heap-test1.original"
  [[ -f "$test_backup" && "$(sha256sum "$test_backup" | awk '{print $1}')" == "$EXPECTED_ORIGINAL_DLL_SHA256" ]] || die 'Original DLL backup was not verified.'
  say 'Heap Fix installed with expected patch and backup hashes; testing restore'
  python3 "$HEAP" restore --runner "$test_runner" || die 'Real-binary isolated restore failed.'
  [[ "$(sha256sum "$test_dll" | awk '{print $1}')" == "$EXPECTED_ORIGINAL_DLL_SHA256" ]] || die 'Restored DLL checksum mismatch.'
  say 'ISOLATED HEAP TEST PASSED: real original DLL patched, backup verified, then restored byte-for-byte.'
  say 'Temporary test runner will be removed automatically; installed Lutris/runner/prefix remain unchanged.'
  exit 0
fi

say 'Installing runner and preparing Lutris using the public setup script'
bash "$SETUP" --runner-archive "$runner_archive" --runner-name "$RUNNER_NAME" --entry-name 'Jinteia Patcher 0.2' --mode "$MODE" --fail-if-existing-runner

# Read the exact installation target from this run's setup log. Never let
# auto-discovery pick a different compatible runner on a multi-runner system.
setup_log="${XDG_CACHE_HOME:-$HOME/.cache}/jinteia-proton/setup-v0.2.log"
[[ -f "$setup_log" ]] || die 'Installer setup log was not created; refusing to guess DLL target.'
installed_runner="$(sed -n 's/^.*Installed Proton runner: //p' "$setup_log" | tail -n 1)"
[[ "$installed_runner" == /* && "${installed_runner##*/}" == "$RUNNER_NAME" && -f "$installed_runner/proton" ]] || die 'Could not verify the exact installed runner path.'
if [[ -n "$HEAP_RUNNER" && "$HEAP_RUNNER" != "$installed_runner" ]]; then
  die "--runner does not match the newly installed runner: $installed_runner"
fi
HEAP_RUNNER="$installed_runner"
run_heap
say 'Runner and Heap Fix ready. Restart Lutris, select the official Patcher EXE, and install WebView2 x64 into the same prefix.'