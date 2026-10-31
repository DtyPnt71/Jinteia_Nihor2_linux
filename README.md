<p align="center">
  <img src="banner.png" width="100%" alt="Jinteia Proton">
</p>

# Jinteia-Proton

Community-maintained Linux compatibility setup for **Jinteia / Nihor2**, using Lutris and a customized Proton runner.

**Unofficial project** by DtyPnt71 / Burarion. Not affiliated with Jinteia, Nihor2, Valve, GE-Proton, Microsoft or Lutris. Game files and account checks are not bypassed.

## Installation / Installation

The source-readable installer is available **directly in this repository**. On Linux, install or use **native Lutris**; this installer does not support Flatpak Lutris.

```bash
git clone https://github.com/DtyPnt71/Jinteia_Nihor2_linux.git
cd Jinteia_Nihor2_linux
bash install.sh
```

Choose **1 Deutsch** or **2 English** when prompted. No `sudo` is needed for the Proton setup. If native Lutris is missing, the installer can offer to install its system package with your approval; only that package-management operation may require `sudo`.

What happens:
1. Download the **existing v0.2 Proton runner** from the project's GitHub release and verify the pinned SHA-256.
2. Extract the embedded archive **without executing the old `.run` wrapper**.
3. Install the runner, prepare the Lutris entry and apply **Heap Fix 1+2** only to the matching DLL, with an original-file backup.
4. Offer an optional download of **Microsoft WebView2 Evergreen x64**; the `.exe` is **not executed automatically**.

**After setup:** Restart Lutris. Select **Jinteia Patcher 0.2**, choose your official **Nihor2-Patcher.exe** and configure WebView2 x64 in the *same* Wine prefix. The installer does not distribute the game or install WebView2 unattended.

[Complete installation steps](docs/INSTALLATION.md) · [Terminal UI (Deutsch / English)](docs/INSTALLER_UI.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

## Test without installing

```bash
bash install.sh --demo --lang de             # Interface only, no changes
bash install.sh --demo --lang en             # English preview
bash install.sh --simulate-install --lang de # Real release, temporary runner + Heap Fix test
```

The isolated simulation downloads the real release, verifies and patches a **temporary copy** and restores it afterwards. It requires at least **4 GiB** of free temporary storage, but does not modify Lutris, existing prefixes or installed runners. A diagnostic log remains.

An existing `Jinteia-Proton-0.2` runner is **never silently overwritten**. Do not delete an existing working prefix just to reinstall.

## Source and release status

- **Readable installation code:** `install.sh`, `scripts/`, `proton/`, `heap/` and tests are tracked in GitHub.
- **Wine patch review:** [Recovered source diffs](patches/) and [provenance / limitations](docs/RECOVERED_PATCHES.md).
- **Binary runner:** still supplied from the **[published v0.2 release](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/releases/tag/v0.2)**. The archive is checksum-verified, but a **fully reproducible build has not been established**.
- **Latest published release:** v0.2. The new source-readable installer on `main` does **not** mean a v0.3 binary release has been published.
- **Verified:** native Lutris installation on CachyOS, automatic Heap Fix and repeat-install protection, plus 41 passing offline tests. **Not verified:** a fresh-prefix game/WebView2 launch through the redesigned installer, Flatpak installation, and rollback after an interrupted install.

[Transparency and checksums](docs/TRUST.md) · [Detailed installation audit](docs/INSTALLER_AUDIT.md) · [Historical v0.2 instructions](docs/RELEASE_NOTES_v0.2.md)

## Optional Discord Rich Presence

Community bridge: [Discord RPC Bridge](https://github.com/enderice2/rpc-bridge/releases). Third-party software; review its instructions and source before installing.

All game assets and marks belong to their respective owners. Jinteia-Proton is an independent compatibility project.
