# Fehlerbehebung / Troubleshooting

[Overview](../README.md) · [Installation](INSTALLATION.md) · [Trust and integrity](TRUST.md)

## Installation bricht ab / Installation stops

**`Existing Jinteia-Proton-0.2 detected`:** Der Überschreibschutz funktioniert. Verwende deine vorhandene Installation oder prüfe den Status, statt Ordner unüberlegt zu löschen:

```bash
bash install.sh --check --runner "$HOME/.local/share/lutris/runners/wine/Jinteia-Proton-0.2"
```

**Lutris missing:** Install native Lutris using your distribution package manager or accept the installer's optional package offer. The current installer **does not support Flatpak Lutris**.

**Vulkan / dependencies missing:** Verify 64-bit and 32-bit graphics/Vulkan drivers. Install missing host dependencies through your distribution's package manager. Do not run the entire Proton installer as root.

**Checksum mismatch or unsupported DLL:** Stop. Do not bypass the version check or modify DLLs manually. Download only from the official GitHub release and share the relevant diagnostic message when asking for support.

## Wo liegen die Logs? / Log locations

```text
~/.local/state/jinteia-proton/installer-ui-*.log
~/.cache/jinteia-proton/setup-v0.2.log
```

To read the latest UI log:

```bash
ls -lt "$HOME/.local/state/jinteia-proton/"
```

If setup stops with an error, keep the log and check for a partial runner or Lutris entry before trying again. Do not delete or overwrite a working game prefix.

## Patcher / WebView2

If the **official Patcher** does not start, confirm that:
1. Lutris uses `Jinteia-Proton-0.2`.
2. Its executable points to your actual `Nihor2-Patcher.exe`.
3. The working directory contains the patcher.
4. Microsoft **WebView2 Evergreen x64** was installed via **Run EXE inside Wine prefix** for that exact Lutris entry, typically using `~/Games/jinteia-prefix`.

The source installer **downloads WebView2 optionally but does not run it**. Do not create new game accounts to diagnose compatibility when the game's rules prohibit them.

## Updating or removing

Re-running `bash install.sh` will **refuse to replace an existing runner**. To assess an existing runner or restore a backup, use the included documented Heap Fix tools with the correct version. **Never replace system Wine or delete your working game prefix to experiment.**

For advanced diagnostics: [Developer reference](DEVELOPMENT.md). Source provenance: [Recovered patches](RECOVERED_PATCHES.md) and [transparency](TRUST.md).
