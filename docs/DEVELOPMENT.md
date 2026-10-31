# Development and validation

Technical reference for maintainers and contributors. **Not part of the normal end-user installation.**

The regular install is described in [INSTALLATION.md](INSTALLATION.md). This project installs the published **v0.2** binary runner; no v0.3 binary release has been published.

## Available commands

Run these from the cloned repository.

```bash
bash install.sh --demo --lang de
bash install.sh --demo --lang en
bash install.sh --simulate-install --lang de
bash install.sh --verify-release
bash install.sh --test-heap
bash install.sh --dry-run
bash install.sh --check --runner "$HOME/.local/share/lutris/runners/wine/Jinteia-Proton-0.2"
```

- `--demo`: UI demonstration only; does not modify installations or download files.
- `--simulate-install`: downloads the pinned published release, verifies the checksum, extracts a runner into a temporary directory, applies and restores the real Heap Fix to the temporary DLL, then deletes the runner. At least 4 GiB free temporary storage is required. A diagnostic log is retained. It **does not test the actual Lutris installation or game launch**.
- `--verify-release`: checks the published asset and original DLL without installing the runner.
- `--test-heap`: command-line isolated patch, hash and restoration test.
- `--dry-run`: describes what installation would change without performing it.
- `--check`: examines the selected installed runner's DLL and backup without modifying them.

## Automated checks

```bash
bash -n install.sh scripts/installer-ui.sh scripts/webview2-download.sh proton/setup-jinteia.sh
python3 -m unittest discover -s proton/tests -p 'test_*.py' -q
python3 -m unittest tests_bootstrap.py tests_bootstrap_integration.py tests_ui.py -q
```

GitHub Actions runs 41 offline tests on the merged installer implementation, including unit/integration fixtures and bilingual UI tests.

## Release verification and limitations

- Native Lutris 0.5.22: runner setup and integrated Heap Fix succeeded on CachyOS in an isolated Linux test account.
- Repeated installation was refused without overwriting the existing runner.
- The published v0.2 release SHA-256 and temporary original / patched DLL checksums matched, and restoration of the temporary original passed.
- **Not established:** a complete game/WebView2 launch in a new prefix through the redesigned UI, full recovery of an interrupted installation, Flatpak Lutris integration or independently reproducible Wine/Proton builds.
- No second game-account login was attempted because the maintainer reported that doing so would violate game rules.

Sources and detailed verification:
- [Audit trail](INSTALLER_AUDIT.md)
- [Recovered Wine patch provenance](RECOVERED_PATCHES.md)
- [Download integrity and trust](TRUST.md)

Do not claim reproducible builds or a validated new-user game launch until independently demonstrated. Never delete or patch a maintainer's live Wine prefix while running installation checks.
