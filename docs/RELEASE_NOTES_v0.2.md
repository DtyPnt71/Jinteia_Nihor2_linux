# Jinteia-Proton v0.2

Run **Nihor2 / Chronicles of Jinteia on Linux** with Lutris and our customized Proton runner.

> **Read this first:** The runner installer is only the first step. You must also configure the official patcher and complete the WebView2 and Heap Fix steps before playing.

## Download

Under **Assets** below, download both files:

- **Jinteia-Proton-0.2-installer.run** — runner and Lutris setup assistant
- **Jinteia-HeapFix1+2.zip** — separately applied Wine compatibility patch

## Installation — in the correct order

1. **Install the runner:** Open a terminal in your downloads folder and run:

   ~~~bash
   chmod +x Jinteia-Proton-0.2-installer.run
   ./Jinteia-Proton-0.2-installer.run
   ~~~

2. **Restart Lutris completely** so the runner appears.
3. **Configure Jinteia Patcher 0.2:** Select the official **Nihor2-Patcher.exe**, its working directory and the prepared prefix **~/Games/jinteia-prefix**. Confirm runner **Jinteia-Proton-0.2**.
4. **Install WebView2 Evergreen x64**, if missing, by selecting **Run EXE inside Wine prefix** for that **same Lutris entry**. Close Lutris again.
5. **Apply the Heap Fix:** Extract the ZIP, open a terminal in the folder containing **START.sh** and run **sh START.sh**. Choose **1**, confirm **y**, and check for the success message.
6. **Launch Jinteia Patcher 0.2** in Lutris.

### Detailed help

- **[Complete step-by-step installation guide](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/blob/main/docs/INSTALLATION.md)**
- **[Troubleshooting and setup logs](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/blob/main/docs/TROUBLESHOOTING.md)**
- **[Checksums, installer transparency and future .sh plans](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/blob/main/docs/TRUST.md)**

### What v0.2 addresses

- Jinteia security violation associated with Wine's permanent 64 KiB RWX import-stub region
- Patcher crash involving Wine ole32.dll / RevokeDragDrop()
- Automated native/Flatpak Lutris detection, host dependency and Vulkan checks, prefix preparation and Lutris entry creation

### Notes

- No need to replace system Wine.
- Keep existing working prefixes; changing one can trigger a new Discord verification.
- The game client itself is not patched by this runner release.
- The distributed **.run** and Heap Fix assets are **not yet fully source-auditable in this repository**. See the transparency documentation.

---

**Maintainer note:** This file is proposed **replacement text** for the existing v0.2 GitHub Release description. It does **not** modify the published release automatically. Update the release description **after** the linked documentation is merged to main.
