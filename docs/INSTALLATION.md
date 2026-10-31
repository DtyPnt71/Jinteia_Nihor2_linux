# Jinteia-Proton installieren / Install Jinteia-Proton

[Übersicht / Overview](../README.md) · [Fehlerbehebung / Troubleshooting](TROUBLESHOOTING.md) · [Transparenz / Trust](TRUST.md)

## Deutsch

### 1. Vorbereitung

- Linux x86_64 mit 64- und 32-Bit-Vulkan-Unterstützung.
- **Natives Lutris**, kein Flatpak-Lutris für diesen Installer. Falls Lutris fehlt, bietet das Setup eine Installation über den Paketmanager an.
- Offizieller `Nihor2-Patcher.exe` vom Spielebetreiber. **Das Spiel wird nicht mitgeliefert.**

**Bestehende Installation?** Ein vorhandener Runner `Jinteia-Proton-0.2` wird nicht überschrieben. Behalte dein funktionierendes Wine-Präfix und deine Spieldaten.

### 2. Installer herunterladen und starten

```bash
git clone https://github.com/DtyPnt71/Jinteia_Nihor2_linux.git
cd Jinteia_Nihor2_linux
bash install.sh
```

- Im Menü **1 Deutsch** oder **2 English** wählen.
- Vor dem Start die angezeigten Schritte lesen und bestätigen.
- Das Setup lädt das **bestehende Release v0.2** (~515 MiB), prüft die SHA-256-Summe und entpackt den Proton-Runner **ohne den alten `.run`-Wrapper auszuführen**.
- Es legt den Lutris-Eintrag an und aktiviert **Heap Fix 1+2** für die exakt erkannte DLL-Version. Das Original wird gesichert.
- `sudo` **nicht** für `bash install.sh` nutzen. Nur die optionale Paketmanager-Installation von Lutris kann separat nach Bestätigung `sudo` benötigen.

### 3. Lutris konfigurieren

Lutris vollständig beenden und neu öffnen. In **Jinteia Patcher 0.2 → Konfigurieren** prüfen:

| Option | Einstellung |
| --- | --- |
| Wine-Version | `Jinteia-Proton-0.2` |
| Wine-Präfix | `~/Games/jinteia-prefix` (Standard) |
| Ausführbare Datei | Dein **offizieller** `Nihor2-Patcher.exe` |
| Arbeitsverzeichnis | Ordner mit dem offiziellen Patcher, standardmäßig `~/Games/Jinteia` |

Die ausführbare Datei wird vom Installer **absichtlich nicht automatisch eingetragen**.

### 4. WebView2 Evergreen x64 installieren

Das Setup kann die offizielle Microsoft-Datei optional herunterladen. Alternativ:

```bash
bash install.sh --webview2-only --lang de
```

Nach Download liegt sie normalerweise unter:

```text
~/Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe
```

In Lutris den Eintrag **Jinteia Patcher 0.2** auswählen und über Rechtsklick **EXE im Wine-Präfix ausführen** die WebView2-Datei starten. Microsofts Installationsdialog abschließen. **Wichtig:** dasselbe Wine-Präfix verwenden wie für den Patcher. Der `.exe`-Download wird vom Linux-Setup **niemals automatisch gestartet**.

Danach Lutris neu starten und den offiziellen Patcher verwenden. Beachte die Accountregeln des Spielbetreibers; führe keine zusätzlichen Spielkonten allein für Tests aus.

### Vorher anschauen oder isoliert testen

```bash
bash install.sh --demo --lang de
bash install.sh --simulate-install --lang de
```

Die **Demo** verändert nichts. Die **Simulation** lädt das echte Release herunter und überprüft den Heap-Fix an einer temporären Kopie. Sie verändert keine installierten Lutris-Runner oder Präfixe, braucht aber mindestens **4 GiB temporären Speicher**. Diagnoseprotokolle verbleiben unter `~/.local/state/jinteia-proton/`.

---

## English

### 1. Requirements

Linux x86_64, working 64-/32-bit Vulkan drivers and **native Lutris**. Flatpak Lutris is not supported by this installer. The installer can offer to install a native Lutris package, with confirmation. Obtain the official `Nihor2-Patcher.exe` separately.

Never remove a working prefix merely to retry installation; existing `Jinteia-Proton-0.2` runners are protected.

### 2. Install

```bash
git clone https://github.com/DtyPnt71/Jinteia_Nihor2_linux.git
cd Jinteia_Nihor2_linux
bash install.sh
```

Select **2 English**. The setup downloads the existing v0.2 binary release, verifies its SHA-256, extracts the Proton runner without executing the downloaded wrapper, creates the Lutris entry and applies the verified Heap Fix with an original-DLL backup. Do **not** run the Proton setup with `sudo`; an optional system-package installation might request it separately.

### 3. Configure Lutris and WebView2

Restart Lutris and open **Jinteia Patcher 0.2 → Configure**. Confirm Wine version `Jinteia-Proton-0.2`, Wine prefix `~/Games/jinteia-prefix`, select your official `Nihor2-Patcher.exe` and its working directory (default `~/Games/Jinteia`).

Choose the optional Microsoft **WebView2 Evergreen x64** download, or run `bash install.sh --webview2-only --lang en`. In Lutris right-click the Jinteia entry → **Run EXE inside Wine prefix** → select `~/Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe`, complete setup and restart Lutris. WebView2 is **downloaded only**, never automatically executed.

Safe preview: `bash install.sh --demo --lang en`. Real temporary binary-and-Heap-Fix test (no Lutris/prefix changes; at least 4 GiB free): `bash install.sh --simulate-install --lang en`.

## Test and release status

The source-readable installer is merged into the repository, but the latest **published binary release is still v0.2**. A new-user game/WebView2 launch through this UI, interrupted-install rollback and Flatpak setup are **not verified**. See [audit details](INSTALLER_AUDIT.md) and [source provenance notes](RECOVERED_PATCHES.md).
