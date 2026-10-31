# Jinteia-Proton v0.2 — original binary release

**Historical release notes.** The existing [v0.2 release](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/releases/tag/v0.2) and its asset files have **not** been replaced or modified by the source-installer merge.

## Original v0.2 assets

- **`Jinteia-Proton-0.2-installer.run`**: original packaged Proton runner and setup script.
- **`Jinteia-HeapFix1+2.zip`**: separately distributed legacy compatibility fix.

Those files are kept for compatibility with existing installations. Their published checksums are listed in [TRUST.md](TRUST.md).

## Recommended new installation workflow

For a new Linux user, use the source-readable script now available on `main` instead:

```bash
git clone https://github.com/DtyPnt71/Jinteia_Nihor2_linux.git
cd Jinteia_Nihor2_linux
bash install.sh
```

This **downloads and verifies the same published v0.2 binary**, extracts its runner without executing the old `.run` wrapper, configures native Lutris and applies Heap Fix 1+2 automatically when the DLL matches exactly.

The official `Nihor2-Patcher.exe` and Microsoft WebView2 Evergreen x64 still require manual game-prefix setup. See the [German/English installation guide](INSTALLATION.md).

## Compatibility and remaining caveats

Native Lutris setup and automatic Heap Fix were tested on CachyOS, and the installer refuses to overwrite an existing runner. Full game launch through a newly created prefix, exact binary build reproducibility and incomplete-install rollback are **not proven**.

The version of the distributed binary remains **v0.2**. Merging the repository scripts is not a new v0.3 release.
