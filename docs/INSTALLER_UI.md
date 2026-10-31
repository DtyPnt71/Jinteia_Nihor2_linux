# Jinteia Proton — Terminal Installer

**Review version only.** The published v0.2 release and `main` stay unchanged.

## Deutsch

### So funktioniert das Setup

```bash
bash install.sh
```

Beim Start **1 Deutsch** oder **2 English** wählen, oder direkt `bash install.sh --lang de` ausführen. Die Oberfläche zeigt Vorbereitung, Installation und Abschluss mit einem Fortschrittsbalken für die **abgeschlossenen Schritte** – nicht für den Download in Prozent.

Wenn natives Lutris fehlt, bietet das Setup nach Bestätigung einen Paketmanager-Befehl für Arch/CachyOS, Debian/Ubuntu, Fedora oder openSUSE an. Nur die Betriebssystem-Paketinstallation benötigt eventuell `sudo`. **Für die Proton-Installation niemals `sudo` verwenden.** Flatpak-Lutris ist für diesen Installer **nicht unterstützt**; nutze die native Version.

Anschließend werden Proton v0.2, der Lutris-Eintrag und Heap-Fix 1+2 eingerichtet. Die technischen Ausgaben bleiben als Log unter `~/.local/state/jinteia-proton/installer-ui-*.log` verfügbar. Ein bereits installierter Runner wird nicht überschrieben.

### WebView2 nach dem Setup

Nach der Installation kannst du den offiziellen **Microsoft WebView2 Evergreen Standalone x64** optional herunterladen. Das Setup lädt lediglich eine `.exe` herunter und **führt sie nie automatisch aus**. Wegen der laufend wechselnden Evergreen-Version ist kein unveränderlicher Microsoft-SHA-256 in diesem Projekt hinterlegt.

1. Lutris schließen und neu starten.
2. Den Eintrag `Jinteia Patcher 0.2` auswählen.
3. Runner `Jinteia-Proton-0.2` und Präfix `~/Games/jinteia-prefix` prüfen.
4. Rechtsklick → **EXE im Wine-Präfix ausführen**.
5. `~/Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe` auswählen und den Microsoft-Installer abschließen.
6. `Nihor2-Patcher.exe` (offizielle Datei) als ausführbare Datei und `~/Games/Jinteia` als Arbeitsverzeichnis einstellen.
7. Lutris erneut starten und den offiziellen Patcher verwenden.

**Ohne Installation anschauen:** `bash install.sh --demo --lang de`. **Nur WebView2-Download:** `bash install.sh --webview2-only --lang de`.

## English

### Setup

```bash
bash install.sh
```

Choose **1 Deutsch** or **2 English** at startup, or use `bash install.sh --lang en`. The UI shows preparation, installation and completion with **stage-based** progress, not a fabricated download percentage.

If native Lutris is missing, setup offers to install it via the distro package manager (Arch/CachyOS, Debian/Ubuntu, Fedora or openSUSE) **only with confirmation**. The system package manager may need `sudo`; **do not run the Proton installer with `sudo`**. Flatpak Lutris is **unsupported by this installer**; install native Lutris.

It then sets up Proton v0.2, the Lutris entry, and Heap Fix 1+2 with its original-DLL backup. Full technical output is kept at `~/.local/state/jinteia-proton/installer-ui-*.log`. The script refuses to replace an existing runner.

### WebView2 after setup

You may optionally download the official **Microsoft WebView2 Evergreen Standalone x64**. The helper only downloads the Windows `.exe`; it **does not execute it**. Evergreen versions change over time, so this project cannot claim a fixed Microsoft SHA-256 checksum.

1. Close and restart Lutris.
2. Select `Jinteia Patcher 0.2`.
3. Verify runner `Jinteia-Proton-0.2` and prefix `~/Games/jinteia-prefix`.
4. Right-click → **Run EXE inside Wine prefix**.
5. Select `~/Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe` and finish the Microsoft installer.
6. Configure the official `Nihor2-Patcher.exe` as executable and `~/Games/Jinteia` as working directory.
7. Restart Lutris and run the official patcher.

**Safe UI preview:** `bash install.sh --demo --lang en`. **WebView2 download only:** `bash install.sh --webview2-only --lang en`.

## Validation

Previously tested: release checksum; original DLL patch and restore; native Lutris installation with Heap Fix on a separate CachyOS user; repeated-install refusal. The *new UI* and both languages have passed offline checks. **Not yet tested:** a real full installation through the newly redesigned UI, the live Microsoft WebView2 download, or a fresh game launch in the separate user. The game launch is deliberately excluded to respect the maintainer's reported account restrictions.

Microsoft's WebView2 downloads: https://developer.microsoft.com/microsoft-edge/webview2

Independent community project by **DtyPnt71 / Burarion**. No game files are redistributed or security checks bypassed.