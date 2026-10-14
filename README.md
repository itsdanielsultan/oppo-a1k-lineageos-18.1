# Oppo A1k CPH1923: Android 9 to Android 11, step by step

I wanted to upgrade an old Oppo A1k and make it useful again. It was running Android 9, and getting a working upgrade took about twelve hours over October 11–12, 2026. The instructions I found left out several fixes this phone needed. This guide brings the successful steps together, including the checks, exact files and recovery instructions.

The phone now runs Android 11 with working Wi-Fi and normal display colors. Play Store sign-in and app updates worked during the original setup; a later certification warning is recorded below. I also added a smaller interface, turned off system touch vibration, enabled supported tap sounds, updated the bundled Google apps in my own build, and added new home and lock-screen wallpapers.

**For a CPH1923 with the same original firmware, this is the route I would follow for the best results we achieved.** Start with the checks in the installation guide. A matching model number alone is not enough; the tools also check the phone's original software before changing it.

It is still a slow phone with **2 GB of RAM and 32 GB of storage**. A different Android version can change how it runs and which apps work, but it cannot replace the old processor, add memory or make the storage new. Expect slow app loading and limited multitasking.

The working system is based on **Andy Yan's unofficial LineageOS 18.1 release**, with fixes for this Oppo. This guide was written in 2026, but Android's security patch is still **January 5, 2024**. Updating Google apps does not update the whole operating system.

## The process in plain language

1. **Check the phone and save its original software.** Confirm it matches the tested CPH1923, save your personal files, and make a private backup for recovery.
2. **Prepare the Mac.** Install the tools and the USB connection fix used here.
3. **Unlock the bootloader.** This allows the phone to start a replacement Android system. The guide gives the exact button sequence and checks that unlocking worked.
4. **Build the Android 11 system.** Download the specified release and add the startup, Wi-Fi, interface and wallpaper changes before installing it.
5. **Install it and clear the old Android setup.** The tool writes the system and checks the complete result. The first upgrade erases personal data.
6. **Set up the phone and check it.** Confirm it reaches Android, Wi-Fi connects, colors look normal and the smaller layout is active.
7. **Update the bundled apps.** Use Play Store for the newest versions it offers this phone. If you want those versions to remain after a reset, follow the extra steps for including them in your local system image.

**Begin with [the full installation guide](docs/INSTALL.md).** Read [the recovery instructions](docs/RECOVERY.md) before unlocking or installing anything. The overview above explains the route; the installation guide contains the commands and the points where you must stop if a check fails.

## What works on the finished phone

| Feature | What we checked |
|---|---|
| Android | Android 11 starts and reaches the home screen |
| Display | Colors look normal; the Android 14 attempt looked washed out |
| Maximum brightness | Owner confirmed a brighter screen after the [PHH backlight-scale adjustment](docs/TROUBLESHOOTING.md#maximum-brightness-is-too-low) |
| Interface size | Smaller layout, set in the system rather than only in user settings |
| Wi-Fi | Internet works on a mixed WPA2/WPA3 network by connecting through WPA2 |
| Google Play | Sign-in and official updates worked during the original setup; Store access was blocked by a certification warning on October 13, 2026 |
| Bundled apps | 16 Google packages updated and included in my personal system image |
| Touch feedback | System touch vibration off, supported tap sounds on, charging vibration off |
| Wallpapers | Home and lock-screen files included in the system, with setup code that preserves later choices |
| Original Oppo drivers | Original kernel and hardware drivers retained |

The Wi-Fi fix does not add support for a WPA3-only network. Individual apps can have their own sound and vibration settings; Gboard's sound preference was set separately.

The brightness adjustment was applied after installation on October 13, 2026. It uses an existing PHH setting and is not bundled by this repository's image builder. The owner confirmed that the screen became brighter; stock-firmware brightness equivalence was not measured. Google accepted custom-ROM device registration during the same follow-up, but the Play Store certification warning remained after a restart and cache refresh. Registration is not a verified certification or Play Integrity pass.

The smaller layout, system touch settings and wallpapers are built into the customized system. We tested wallpaper setup with both empty and existing settings. We have **not reset the finished phone again** to test the whole setup from scratch. The core build starts with the original release's app versions unless you complete the optional app-update build.

This was tested on **one phone and its exact original firmware**. Calls, VoLTE, GPS, Bluetooth audio, every camera mode and payment apps still need a full check. [What we tested](docs/VALIDATION.md) records these limits and links to the evidence.

## Why Android 11?

I tried newer releases first. Android 14 started, but photos and colors kept turning washed out. Android 12 did not finish starting. Android 11, with the fixes in this guide, gave us the working result with normal colors and Wi-Fi.

That is why the instructions use this exact release. Installing the newest-looking file was not enough for the old Oppo drivers. The [failed-attempts page](docs/FAILURE-HISTORY.md) explains what happened, so you can go straight to the successful route instead of repeating those experiments.

## Read the guide in order, or look up a specific problem

| Page | What you will find |
|---|---|
| [Installation](docs/INSTALL.md) | Equipment, Mac setup, backups, unlocking, building, installing and first boot |
| [Building your system image](docs/BUILD.md) | Every change applied to Android and how to include your own official app updates |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Connection problems, recovery screens, a stuck logo, dim maximum brightness and failed checks |
| [Recovery](docs/RECOVERY.md) | Restoring your own backups and what a failed installation can leave behind |
| [Why the fixes were needed](docs/TECHNICAL.md) | The code changes and the problems they addressed |
| [Failed attempts](docs/FAILURE-HISTORY.md) | What failed and which experiments to skip |
| [What we tested](docs/VALIDATION.md) | Phone results, separate tool tests and features still needing checks |
| [Downloads and licenses](docs/DISTRIBUTION.md) | What is included in the public download |
| [Sources and credits](docs/SOURCES.md) | The upstream software and documentation used |

## What the download contains

The [GitHub release](https://github.com/itsdanielsultan/oppo-a1k-lineageos-18.1/releases) contains the guide, fixes, build tools, two small settings packages and wallpapers. It is a toolkit for building the customized system on your Mac.

Download the original Android image from [Andy Yan's release page](https://sourceforge.net/projects/andyyan-gsi/files/lineage-18.x/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz/download). The installation guide checks that file and explains how to add the fixes.

My final image contains Google apps updated through my Play account. Those app files and the phone's private Oppo backups are not included in this repository. [The app-update instructions](docs/BUILD.md#optional-make-official-play-updates-into-local-rom-defaults) explain how to include updates from your own phone in your own local build. The two APK files in `assets/` only change settings; they are not Google apps and contain no app code. See [downloads and licenses](docs/DISTRIBUTION.md).

## Exact phone and software used

These details matter when comparing another phone with ours. The installation tools check the full partition layout and original boot/vendor files, not just the names in this table.

| Item | Tested value |
|---|---|
| Model / board | `CPH1923` / `oppo6762_18540` |
| Reported platform / hardware code | `mt6765` / `0x766` |
| Memory / storage / screen | 2 GB / 32 GB / 720 × 1560 |
| Original Android | Android 9 / SDK 28 |
| Original hardware-driver interface | VNDK 28 |
| Android layout | Treble and system-as-root enabled |
| Phone partitions | One physical `system` partition; no `system_a` or `system_b` |
| Original kernel | Oppo's 4.9.117-based kernel |
| Android image | `lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz` |
| Archive SHA-256 checksum | `7bb7c4ebd336ad1615ce9f078d6a455e2c524d736578571ac41671b36d23415a` |
| MTKClient version | 2.1.4, commit `cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3` |

A **GSI** is a generic Android system image intended for compatible phones. The `b` in the required `arm64_bgS` filename describes the image's internal layout. **It does not mean this phone has A/B slots.** We installed it on the single partition named `system`. Do not choose a different download just because the phone is described as A-only.

A **checksum** is a fingerprint of a file's contents. Matching checksums let the tools confirm that your original firmware matches ours and that the complete installation was written correctly. The measured layout and firmware checksums are in [the tested phone profile](evidence/tested-profile.json). If a check fails, stop and investigate; do not remove it to force the installation.

The final phone reported file-based storage encryption and global SELinux `Enforcing`. Its complete 5,033,164,800-byte system was read back and matched its SHA-256 checksum. The original hardware-driver security patch is May 5, 2021, and the upstream system contains permissive superuser domains. The full details are in [the technical notes](docs/TECHNICAL.md) and [test results](docs/VALIDATION.md).

## Credits

The Android system and tools come from **Andy Yan, LineageOS, AOSP, phhusson/PHH Treble, TrebleDroid, Bjoern Kerler and MTKClient contributors, and SELinuxProject**. This project's contribution is the fixes for the tested CPH1923, the chosen defaults, and the instructions and checks needed to repeat the work. The guide was prepared with Codex and checked against the phone's logs, complete partition readbacks and actual behavior.

Source changes are under GPL-3.0, with the upstream notices and component licenses retained. See [NOTICE](NOTICE.md) for the settings packages and wallpapers. The repository's license does not grant rights to Google's apps or Oppo's firmware.
