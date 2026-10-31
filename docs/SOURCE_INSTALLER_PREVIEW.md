# Source-readable Jinteia-Proton installer (draft)

**Review branch only — not a stable release.**

The readable `install.sh` downloads the published v0.2 release, validates its SHA-256, extracts the runner without executing the downloaded wrapper, prepares a Lutris entry, and applies the version-checked Heap Fix with an original DLL backup.

## Check before installing

```bash
git clone --depth 1 --branch installer/source-readable-v0.2-preview https://github.com/DtyPnt71/Jinteia_Nihor2_linux.git
cd Jinteia_Nihor2_linux
bash install.sh --dry-run
```

For a clean Linux user with native Lutris installed:

```bash
bash install.sh --mode native
```

Do not use sudo. Close Lutris and the game first. Existing `Jinteia-Proton-0.2` runners are preserved; the script refuses to overwrite them.

For inspections, `--check --runner PATH` checks installed Heap Fix status, `--verify-release` verifies the public asset without installing, and `--test-heap` applies and restores the fix on a disposable temporary copy (requires 4 GiB free).

## Manual setup still required

Restart Lutris, select `Jinteia-Proton-0.2`, select the official `Nihor2-Patcher.exe`, and install Microsoft Edge WebView2 Evergreen Runtime x64 in the same Wine prefix. No game client is included.

## Verified on CachyOS, 2026-10-31

The real release checksum and original DLL hash matched. The actual Heap Fix and restoration succeeded on a temporary runner. Fresh native Lutris 0.5.22 installation succeeded in a separate test user and the Lutris GUI settings were confirmed. A second installer run refused to overwrite the existing runner.

**Not yet verified:** fresh-prefix game launch and WebView2 setup; Flatpak Lutris; interrupted-install recovery; reproducible binary build. The second test account was not used to launch the game due to the maintainer's reported game-account rules.

Refer to [the audit record](INSTALLER_AUDIT.md) and [Wine patch review](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/pull/5). Keep the original release and production runner unchanged until remaining checks are complete.
