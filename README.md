<p align="center">
  <img src="banner.png" width="100%" alt="Jinteia Proton Fix">
</p>

# Jinteia / Nihor2 on Linux

> **New terminal UI (review branch):** preview the installer without making changes:

```bash
bash install.sh --demo --lang de  # Deutsch
bash install.sh --demo --lang en  # English
bash install.sh --simulate-install --lang de  # Echter Test im temporären Ordner
```

The redesigned installer offers **Deutsch / English at startup** (or `--lang de` / `--lang en`). Native Lutris setup, stage progress, logs and optional Microsoft WebView2 x64 download are documented in [Installer UI](docs/INSTALLER_UI.md). **This is not yet a published release.**

> **Under review: source-readable installer** — see [instructions and test status](docs/SOURCE_INSTALLER_PREVIEW.md). This feature branch has passed native CachyOS installation and repeat-install protection tests, but the new-user game launch and WebView2 setup are not verified. The published v0.2 release is unchanged.

Run **Nihor2 / Chronicles of Jinteia** on Linux with Lutris using a custom Proton build.

This setup uses the **Jinteia Patcher** as the main entry point.  
The patcher can be used both to **download/install the game** and to **launch an existing installation**.

---
This fix allows you running Metin2 (Jinteia) on Linux using a Wine environment.

Check out the releases for more information!
---

***You want Discord recognize Jinteia / Nihor2?*** 

Download Discord-RPC Bridge:

https://github.com/enderice2/rpc-bridge/releases

Unzip to your gamefolder -> Open Lutris and run "bridge.exe" as Wine-Prefix

Click "Install" 

Start Jinteia & enjoy!
---

### Important

The Jinteia client executable itself is **not modified**.

No Jinteia security checks are disabled or bypassed.

### Disclaimer & Copyright

All game files and logos belong to Jinteia / Nihor2.

This is an independent community project and is **not yet officially supported or endorsed by Jinteia / Nihor2**.

All rights to the original game and its content remain with their respective owners.

</details>

---

<details>
<summary><strong>Known test status</strong></summary>

### Confirmed working

- **CachyOS**
- **Linux Mint 22.3**
- Lutris
- UMU
- Jinteia-Proton-0.1, 0.2
- Microsoft Edge WebView2 Runtime x64
- Jinteia Patcher
- Jinteia Client
- Launching Jinteia through the patcher (not recommended)
- Optional direct client launch using the same prefix

### Not yet fully verified

- SteamOS
- Flatpak Lutris
- Other Linux distributions

Feedback and additional distribution tests are welcome.

</details>

---

<details>
<summary><strong>Credits / Notes</strong></summary>

This project uses a custom Proton build based on:

```text
GE-Proton 11-7
```

Jinteia, GE-Proton, Wine, Valve, Microsoft and Lutris are separate projects and trademarks of their respective owners.

This repository provides a Linux compatibility setup and is not an official Jinteia Linux release.

</details>
