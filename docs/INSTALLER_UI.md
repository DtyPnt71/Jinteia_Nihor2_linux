# Jinteia Proton — Terminal-Installer (Entwurf)

**Status:** Test-Branch. Das bestehende Release v0.2 und `main` werden nicht verändert.

## Installation

```bash
git clone https://github.com/DtyPnt71/Jinteia_Nihor2_linux.git
cd Jinteia_Nihor2_linux
bash install.sh
```

Der Befehl wird **erst nach Zusammenführung** auf `main` den neuen Installer enthalten. Bis dahin kann man die Vorschau aus dem entsprechenden Feature-Branch auschecken.

Die interaktive Oberfläche zeigt die Phasen des Setups. Der ursprüngliche, geprüfte Installer erledigt weiterhin Download, SHA-256-Prüfung, Installation und den versiongebundenen Heap-Fix. Die vollständige Ausgabe bleibt als Log unter `~/.local/state/jinteia-proton/installer-ui-*.log` erhalten.

## Optionen

| Befehl | Funktion |
| --- | --- |
| `bash install.sh` | Interaktiver Installer im Terminal |
| `bash install.sh --demo` | Vorschau der Oberfläche, ohne Downloads oder Änderungen |
| `bash install.sh --webview2-only` | Optionales WebView2-x64-Downloadmenü |
| `bash install.sh --check --runner PFAD` | Installierten Heap-Fix und Backup prüfen |
| `bash install.sh --verify-release` | Original-Release ohne Installation prüfen |
| `bash install.sh --test-heap` | Heap-Fix auf temporärer Kopie anwenden und rückgängig machen |

Ohne interaktives Terminal verwendet `install.sh` die bisherige, protokollierbare Skriptschnittstelle.

## Lutris

Der normale Installer benötigt die **native** Lutris-Installation. Ist sie nicht vorhanden, schlägt das Setup — abhängig von der Distribution — einen Befehl mit `pacman`, `apt-get`, `dnf` oder `zypper` vor und fragt **vor jeder Paketinstallation** nach. Nur dafür kann eine `sudo`-Passwortabfrage des Betriebssystems erforderlich sein. Proton selbst wird **nie mit sudo** installiert.

**Flatpak-Lutris ist in diesem Installationsablauf nicht unterstützt.** Nutze für Jinteia-Proton die native Version. Das bedeutet nicht, dass Lutris als Flatpak grundsätzlich fehlerhaft ist.

Offizielle Lutris-Installationshinweise: https://lutris.net/downloads

## WebView2 Evergreen x64

Nach erfolgreichem Proton-Setup kann der Nutzer optional den offiziellen **Evergreen-Standalone-Installer (x64)** von Microsoft herunterladen. Die Datei wird unter `~/Downloads/Jinteia-Proton/MicrosoftEdgeWebView2RuntimeInstallerX64.exe` gespeichert. Sie wird **nicht automatisch ausgeführt**, nicht im Repository mitgeliefert und bei einem erneuten Download nicht überschrieben.

WebView2 wird bei Microsoft fortlaufend aktualisiert. Die Downloadhilfe prüft den Transport über HTTPS sowie eine grundlegende Windows-EXE-Dateisignatur, hat aber **keinen festen Hersteller-SHA-256** für das wechselnde Installationsprogramm. Keine Aussage über eine vollständige Authentizitätsprüfung.

Quelle: https://developer.microsoft.com/microsoft-edge/webview2

### WebView2 in Lutris installieren

1. **Lutris schließen und neu starten.**
2. Den neuen Eintrag **Jinteia Patcher 0.2** auswählen.
3. Unter **Konfigurieren → Runner-Optionen** sicherstellen, dass `Jinteia-Proton-0.2` ausgewählt ist.
4. Unter **Spieloptionen** das Wine-Präfix `~/Games/jinteia-prefix` kontrollieren.
5. Per Rechtsklick **EXE im Wine-Präfix ausführen** wählen.
6. Die heruntergeladene Datei **MicrosoftEdgeWebView2RuntimeInstallerX64.exe** auswählen und den Microsoft-Installer durchlaufen.
7. Den Spieleintrag mit der **offiziellen Nihor2-Patcher.exe** als ausführbare Datei und `~/Games/Jinteia` als Arbeitsverzeichnis konfigurieren.
8. Lutris erneut starten und den offiziellen Patcher ausführen.

Der Installationsassistent verteilt keine Spieldateien und umgeht keine Spiel- oder Accountregeln.

## Prüfumfang vor Veröffentlichung

Die Kerninstallation auf CachyOS und der Überschreibschutz wurden bereits getestet. Die **neue Terminaloberfläche, das Paketmanager-Angebot und der WebView2-Download** sind separat zu prüfen. Der Start des Spielclients aus einem frischen zweiten Konto ist aus Rücksicht auf die gemeldeten Accountregeln nicht Teil dieser Tests.