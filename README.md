<p align="center">
  <img src="banner.png" width="100%" alt="Jinteia Proton Fix">
</p>

# Jinteia / Nihor2 on Linux

**Community-maintained Linux compatibility setup** for Nihor2 / Chronicles of Jinteia using Lutris and a customized GE-Proton build.

The goal is simple: install the runner, configure the official patcher, and launch Jinteia from Lutris.

> [!IMPORTANT]
> This is an **unofficial community project**. It is not affiliated with or endorsed by Jinteia / Nihor2, Valve, Lutris, Wine, or GE-Proton. The original game files and security checks are not intentionally modified or disabled by this compatibility setup.

## Get started — v0.2

**[Download the latest release (v0.2)](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/releases/tag/v0.2)** · **[Full installation guide](docs/INSTALLATION.md)** · **[Troubleshooting](docs/TROUBLESHOOTING.md)**

1. Download **Jinteia-Proton-0.2-installer.run** from the release's **Assets** section.
2. Open a terminal in the download folder and run:

   ~~~bash
   chmod +x Jinteia-Proton-0.2-installer.run
   ./Jinteia-Proton-0.2-installer.run
   ~~~

3. Follow the **[installation guide](docs/INSTALLATION.md)** to configure the patcher in Lutris and install WebView2 and the separately distributed Heap Fix.

**Do not launch the patcher before completing the required setup.** The installer alone is not the entire installation.

### What you will download

| Asset | Purpose |
| --- | --- |
| **Jinteia-Proton-0.2-installer.run** | Contains and installs the customized Proton runner, checks host requirements, and creates a Lutris entry |
| **Jinteia-HeapFix1+2.zip** | Separate manual compatibility patch used in the current v0.2 instructions |

The official Jinteia patcher and Microsoft Edge WebView2 x64 are **not included** in these two release assets.

## Documentation

- **[Installation, step by step](docs/INSTALLATION.md)** — download → installer → Lutris → WebView2 → Heap Fix → launch
- **[Troubleshooting and logs](docs/TROUBLESHOOTING.md)** — common setup mistakes and information for bug reports
- **[Trust, checksums and future installer format](docs/TRUST.md)** — what can currently be inspected and how we intend to improve it

## Compatibility and status

Reported as working in the project's previous testing: **CachyOS**, **Linux Mint 22.3**, native **Lutris**, and Jinteia-Proton **v0.1/v0.2**. SteamOS, Flatpak Lutris, and other distributions have **not** been fully verified. Additional reports are welcome.

This build is based on **GE-Proton 11-7** and is intended for Linux. It does not replace system Wine.

## Optional: Discord Rich Presence

For Discord game detection, see the third-party [Discord RPC Bridge](https://github.com/enderice2/rpc-bridge/releases). This is an optional, separate project and is **not required** to play Jinteia.

## Help and feedback

If installation fails, follow the [troubleshooting guide](docs/TROUBLESHOOTING.md) and include the relevant setup log **after checking it for personal data**. Please mention your distribution, Lutris installation type, and the exact stage that failed.

## Transparency and credits

The current v0.2 release ships a large **.run** installer. Its **full installer source and build process are not yet published in this repository**; changing the extension to **.sh** would not itself make the bundled payload auditable. See [Trust and installer plans](docs/TRUST.md).

Jinteia / Nihor2 content and trademarks belong to their respective owners. GE-Proton, Wine, Valve, Microsoft, and Lutris are independent projects.
