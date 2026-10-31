# Jinteia-Proton — Terminal Setup

Das Installationsprogramm bietet eine einheitliche Oberfläche in **Deutsch** und **Englisch**. Beim Start erscheint die Sprachauswahl.

The setup provides a consistent interface in **German** and **English**, with language selection at startup.

## Deutsch

### Einrichtung starten

```bash
bash install.sh
```

Alternativ mit festgelegter Sprache:

```bash
bash install.sh --lang de
```

Die Installation zeigt die aktuellen Arbeitsschritte, einen Fortschrittsbalken und beim Herunterladen die tatsächliche Downloadgeschwindigkeit. Die technischen Ausgaben werden automatisch unter `~/.local/state/jinteia-proton/` protokolliert.

Wenn natives Lutris fehlt, bietet das Setup die Installation über den Paketmanager an. Dafür ist eine Bestätigung erforderlich. Der Proton-Installer selbst darf **nicht mit `sudo`** gestartet werden. Flatpak-Lutris wird von diesem Installer nicht unterstützt.

Proton wird automatisch eingerichtet, der Lutris-Eintrag vorbereitet und der **Heap-Fix 1+2** für die passende DLL-Version angewendet. Ein bereits vorhandener Runner wird nicht überschrieben.

### WebView2 einrichten

WebView2 Evergreen x64 kann am Ende des Setups optional direkt von Microsoft heruntergeladen werden. Alternativ:

```bash
bash install.sh --webview2-only --lang de
```

Der Download wird **nicht automatisch ausgeführt**.

1. Lutris vollständig schließen und neu starten.
2. **Jinteia Patcher 0.2** auswählen und den Runner `Jinteia-Proton-0.2` prüfen.
3. Rechtsklick → **EXE im Wine-Präfix ausführen**.
4. `~/Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe` auswählen und die Installation abschließen.
5. Die offizielle `Nihor2-Patcher.exe` und ihr Arbeitsverzeichnis konfigurieren.
6. Lutris neu starten und den Patcher verwenden.

## English

### Start setup

```bash
bash install.sh
```

Or select English directly:

```bash
bash install.sh --lang en
```

The installer shows each stage, a progress bar, and the measured download speed during transfer. Technical logs are saved under `~/.local/state/jinteia-proton/`.

If native Lutris is missing, the installer can offer to install it through your distribution's package manager, after confirmation. **Do not launch the Proton installer with `sudo`.** Flatpak Lutris is unsupported by this installer.

Setup automatically installs the Proton runner, prepares the Lutris entry and applies the version-checked **Heap Fix 1+2**. An existing runner is not overwritten.

### Configure WebView2

The installer can optionally download WebView2 Evergreen x64 from Microsoft. To download it separately:

```bash
bash install.sh --webview2-only --lang en
```

The downloaded file is **never automatically executed**.

1. Close Lutris and restart it.
2. Select **Jinteia Patcher 0.2** and check runner `Jinteia-Proton-0.2`.
3. Right-click → **Run EXE inside Wine prefix**.
4. Select `~/Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe` and complete the installer.
5. Configure the official `Nihor2-Patcher.exe` and its working directory.
6. Restart Lutris and launch the official patcher.

[Installation guide / Installationsanleitung](INSTALLATION.md) · [Troubleshooting / Fehlerbehebung](TROUBLESHOOTING.md)

Independent community project by **DtyPnt71 / Burarion**. The official game client is not distributed with this installer.
