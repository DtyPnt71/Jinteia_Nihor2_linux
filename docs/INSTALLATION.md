# Install Jinteia-Proton v0.2

[Back to overview](../README.md) · [Troubleshooting](TROUBLESHOOTING.md) · [Trust and checksums](TRUST.md)

This guide follows the **existing v0.2 release workflow**. It is written for people who are new to Lutris: complete each step **in order**.

## Before you start

You will need:

- A Linux PC and **Lutris** (the native version is better tested than Flatpak).
- Working 64-bit and 32-bit Vulkan support and any dependencies requested by the installer.
- The **official Jinteia/Nihor2 patcher** (Nihor2-Patcher.exe), saved in your Jinteia folder.
- The two assets from **[Jinteia-Proton v0.2](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/releases/tag/v0.2)**: **Jinteia-Proton-0.2-installer.run** and **Jinteia-HeapFix1+2.zip**.
- Microsoft **Edge WebView2 Evergreen Runtime x64**, installed later in the same Wine prefix as the patcher.

> [!CAUTION]
> Do **not** remove an existing working Wine prefix to start over. Jinteia uses Discord verification; changing prefixes can trigger a new session verification or lockout. If you already have a working installation, back it up before experimenting.

## Step 1 — Download and install the runner

Download **Jinteia-Proton-0.2-installer.run** under the **Assets** heading of the [v0.2 release](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/releases/tag/v0.2).

Open a terminal in the folder where the file was downloaded. Run:

~~~bash
chmod +x Jinteia-Proton-0.2-installer.run
./Jinteia-Proton-0.2-installer.run
~~~

Follow the on-screen assistant. It detects your distribution, session, Lutris type and dependencies, checks Vulkan, installs the runner and prepares the Lutris entry.

**Do not run this installer with sudo.** If a host package is missing, install that dependency using your distribution's normal package manager instead.

> [!NOTE]
> The **.run** file contains a binary runner payload. It is not equivalent to a plain, readable shell script. For integrity information and the planned source-readable installation format, see [Trust](TRUST.md).

## Step 2 — Restart Lutris

**Completely close Lutris**, then open it again. You should now see:

- A game entry named **Jinteia Patcher 0.2**
- A Wine version named **Jinteia-Proton-0.2**

Do not launch the game yet.

## Step 3 — Point Lutris at the official patcher

In Lutris, right-click **Jinteia Patcher 0.2** and choose **Configure → Game options**.

Set:

| Setting | Value |
| --- | --- |
| Executable | The **full path** to your official **Nihor2-Patcher.exe** |
| Working directory | The folder containing **Nihor2-Patcher.exe** |
| Wine prefix | **~/Games/jinteia-prefix** (unless you deliberately use an existing prefix) |

The installer normally prepares **~/Games/Jinteia** as the game folder, but you may have placed the patcher elsewhere. Select the actual file from your system rather than copying an example path literally.

In **Configure → Runner options**, confirm the Wine version is **Jinteia-Proton-0.2**. Save.

**Do not start the patcher yet.**

## Step 4 — Install Microsoft Edge WebView2

The patcher requires **Microsoft Edge WebView2 Evergreen Runtime x64**.

1. Check the installer output first: it may already report that WebView2 is present in the prefix. If so, do not reinstall it unnecessarily.
2. Otherwise, download the **x64 Evergreen Runtime** from [Microsoft's WebView2 download page](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).
3. In Lutris, select **Jinteia Patcher 0.2**.
4. Open the Wine menu for this entry and choose **Run EXE inside Wine prefix**.
5. Select and complete the WebView2 installer.

**Important:** Install WebView2 inside the **same prefix** selected in Step 3. Do not create a second prefix for it.

Completely close Lutris after the installation.

## Step 5 — Apply the separately supplied Heap Fix

Download **Jinteia-HeapFix1+2.zip** from the same [v0.2 release](https://github.com/DtyPnt71/Jinteia_Nihor2_linux/releases/tag/v0.2) and extract the ZIP file.

While **Lutris and all Jinteia processes are closed**, open a terminal in the extracted folder containing **START.sh** and run:

~~~sh
sh START.sh
~~~

According to the release's existing installation instructions:

1. Select **1** when the script asks for the installation action.
2. Confirm with **y** when prompted.
3. Look for **[SUCCESS] HEAP FIX INSTALLED** before proceeding.

**This step patches two addresses in the runner's Wine ntdll.dll to change memory-management behavior.** It is not a cosmetic setting. Only use the release's matching files and do not apply them to your system Wine or an unrelated runner. For the trust limitations of these files, see [Trust](TRUST.md).

## Step 6 — Launch Jinteia

Open Lutris and launch **Jinteia Patcher 0.2**. The official patcher can install or update Jinteia and start the game.

**Done.** If something fails, use [Troubleshooting](TROUBLESHOOTING.md) rather than deleting the Wine prefix.

---

## Installation at a glance

| Order | Action | Expected result |
| --- | --- | --- |
| 1 | Run the v0.2 installer | Runner and Lutris entry created |
| 2 | Fully restart Lutris | New runner appears |
| 3 | Configure official patcher | Correct executable, folder and prefix |
| 4 | Install WebView2 x64 if missing | Runtime in **same prefix** |
| 5 | Run the separate Heap Fix | Success confirmation |
| 6 | Start the patcher | Game downloads/updates/launches |

## Avoid these common mistakes

- **Never launch before WebView2 and the documented Heap Fix steps are finished.**
- **Do not use a separate prefix** for WebView2 or a second game entry without deliberately sharing the same prefix.
- **Do not install or replace system Wine.**
- **Do not delete an existing prefix** merely because the runner is missing in the Lutris menu.
- **Do not confuse the optional Discord RPC Bridge with a required part of installation.**

## Need help?

The installer writes a log to:

~~~text
~/.cache/jinteia-proton/setup-v0.2.log
~~~

See [Troubleshooting](TROUBLESHOOTING.md) for what to include in a support request.
