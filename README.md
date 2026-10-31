<p align="center">
  <img src="banner.png" width="100%" alt="Jinteia-Proton">
</p>

# Jinteia-Proton

**Linux-Kompatibilität für Jinteia / Nihor2.** Ein angepasster Proton-Runner mit automatischer Lutris-Einrichtung und integriertem Heap-Fix.

**Jinteia-Proton for Linux.** A customized Proton runner with native Lutris setup and integrated Heap Fix.

## Installation

Voraussetzung: Linux (x86_64) und eine native Lutris-Installation. Falls Lutris fehlt, bietet das Setup die Installation über den Paketmanager an. **Flatpak-Lutris wird von diesem Installer nicht unterstützt.**

Requires Linux (x86_64) and native Lutris. The installer can offer to install native Lutris when needed. Flatpak Lutris is not supported by this setup.

```bash
git clone https://github.com/DtyPnt71/Jinteia_Nihor2_linux.git
cd Jinteia_Nihor2_linux
bash install.sh
```

Wähle beim Start **Deutsch** oder **English**. Der Installer lädt Proton herunter, prüft die Dateiintegrität und richtet den Runner einschließlich Heap-Fix automatisch ein. Bestehende Installationen werden nicht überschrieben.

Choose **Deutsch** or **English** at startup. The installer downloads and verifies Proton, prepares Lutris, and applies the Heap Fix. Existing runner installations are preserved.

### Nach der Installation / After installation

1. **Lutris neu starten / Restart Lutris.**
2. **Jinteia Patcher 0.2** auswählen / Select **Jinteia Patcher 0.2**.
3. Die offizielle **Nihor2-Patcher.exe** als ausführbare Datei auswählen / Select the official **Nihor2-Patcher.exe**.
4. **Microsoft Edge WebView2 Evergreen x64** in demselben Wine-Präfix installieren / Install WebView2 Evergreen x64 in the same Wine prefix. Der Installer kann die Datei optional herunterladen / The installer can optionally download the file.

**[Schritt-für-Schritt-Anleitung / Installation guide](docs/INSTALLATION.md)** · **[Fehlerbehebung / Troubleshooting](docs/TROUBLESHOOTING.md)**

## Repository

| Bereich / Component | Inhalt / Description |
| --- | --- |
| `install.sh` | Installer und Integritätsprüfung / Setup and integrity checks |
| `scripts/` | Zweisprachige Terminaloberfläche und WebView2-Hilfe / Bilingual setup UI and WebView2 helper |
| `proton/` | Runner- und Lutris-Einrichtung / Runner and Lutris setup |
| `heap/` | Heap-Fix mit Versionsprüfung und Sicherung / Version-checked Heap Fix with backup |
| `patches/` | Dokumentierte Wine-Anpassungen / Documented Wine patches |
| `docs/` | Anleitungen und technische Dokumentation / Guides and technical documentation |

### Downloads & Versions / Releases

Die Installationsskripte sind hier im Repository verfügbar. Der Runner wird aus dem bestehenden **[v0.2-Release](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/releases/tag/v0.2)** bezogen und anhand seiner SHA-256-Prüfsumme verifiziert.

The installation scripts are available in this repository. The runner is downloaded from the existing **v0.2 release** and verified using SHA-256. A new v0.3 release has **not** been published.

[Quellcode und Integrität / Source and integrity](docs/TRUST.md) · [Wine-Patches](docs/RECOVERED_PATCHES.md)

---

**by DtyPnt71 / Burarion**

Unabhängiges Community-Projekt; keine offizielle Unterstützung oder Verbindung zu Jinteia/Nihor2, Valve, Wine oder Lutris. Spielclient und Kontoprüfungen werden nicht verändert.

Independent community project; not officially supported or endorsed by Jinteia/Nihor2, Valve, Wine or Lutris. Game client files and account checks are not modified.
