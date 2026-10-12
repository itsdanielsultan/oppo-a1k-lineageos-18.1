# Oppo A1k CPH1923: a tested Android 9 → Android 11 upgrade

An unusually detailed record of taking **one Oppo A1k CPH1923** from stock Android 9 to a working, customized **Andy Yan LineageOS 18.1 Android 11 GSI**, using **MTKClient on an Apple Silicon Mac**. The work ran across October 11–12, 2026. The owner estimates at least twelve hours of troubleshooting.

This repository exists because “unlock, flash a GSI, wipe data, reboot” omitted the details that actually determined whether this phone booted. The missing pieces included a macOS USB backend fix, the correct GSI layout, a vendor SELinux permission, a legacy Keymaster wrapper mismatch, and WPA2 profiles being automatically upgraded to an unsupported SAE connection.

**This is an unofficial, device-specific result, not an official LineageOS device build, not a new OS compiled from scratch, and not evidence that every A1k variant or every phone feature works.** It is a documented method that worked on the exact configuration below. It is not “the only right way.” Different firmware may need different fixes.

## What was achieved

| Item | Result on the test phone |
|---|---|
| Bootloader | Unlocked; orange warning followed by Android |
| OS | Android 11 / SDK 30 / LineageOS 18.1 GSI |
| Stock kernel and vendor drivers | Retained |
| Storage encryption | `encrypted`, `file` |
| SELinux global mode | `Enforcing` |
| Display | Owner reported colors “perfectly fine” on Android 11; Android 14 had visibly washed-out colors |
| Density | Native 320, no user override required |
| Mixed WPA2/WPA3 network | Connected through WPA2-PSK; internet validated |
| Google Play | Sign-in and official updates worked |
| Bundled Google apps | 16 updated packages incorporated into the owner's local system image |
| Touch feedback | System haptics off, supported tap sounds on; charging vibration off |
| Wallpapers | Home and lock assets bundled with a first-start initializer; current settings preserved |
| Final image | Full 5,033,164,800-byte flash readback matched its SHA-256 |

**Android's framework security patch remains `2024-01-05`. Updating Play Store, Chrome, WebView or other apps does not turn this into a 2026-patched Android OS.** The stock vendor advertises `2021-05-05`. Global SELinux enforcement also does not mean that every domain is enforcing: the upstream GSI already contains permissive superuser domains.

## Start here

1. [The complete installation guide](docs/INSTALL.md) — prerequisites, exact macOS setup, private backups, unlock, build, flash, first boot and checkpoints.
2. [Reproducing the customized image](docs/BUILD.md) — pinned input, modifications, overlays, SELinux validation, optional app integration and hashes.
3. [Why each fix exists](docs/TECHNICAL.md) — the mechanisms, precise paths and limitations.
4. [Failures and discarded attempts](docs/FAILURE-HISTORY.md) — what we tried, what failed and what should not become a tutorial step.
5. [Troubleshooting](docs/TROUBLESHOOTING.md) — distinguish Android, recovery, charging, boot ROM, an inactive ADB interface, a write failure and a normal disconnect after verified shutdown.
6. [Recovery](docs/RECOVERY.md) — your own backups, rollback boundaries, and what was versus was not tested.
7. [Validation and unresolved items](docs/VALIDATION.md) — measured, owner-observed, inferred and untested results.
8. [Distribution and source attribution](docs/DISTRIBUTION.md).
9. [Community announcement drafts](docs/COMMUNITY.md).

Read the installation and recovery documents before running a write command. A first Android 9 → 11 installation clears apps, settings, credentials and files. Later changes in our session preserved the existing Android 11 setup; that does not make an initial upgrade data-preserving.

## Exact tested configuration

| Field | Observed value |
|---|---|
| Model | `CPH1923` |
| Board | `oppo6762_18540` |
| Reported platform | `mt6765` |
| MTKClient hardware code | `0x766` |
| RAM / storage | 2 GB / 32 GB |
| Display | 720 × 1560 |
| Original Android | 9 / SDK 28 |
| Vendor API | VNDK 28 |
| Treble / system-as-root | Both true |
| Partition scheme | Physical A-only `system`, no `system_a` or `system_b` |
| Kernel | Original 4.9.117-based Oppo kernel |
| GSI input | `lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz` |
| Publisher SHA-256 | `7bb7c4ebd336ad1615ce9f078d6a455e2c524d736578571ac41671b36d23415a` |
| Tested MTKClient commit | `cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3` / 2.1.4 |

The marketing chipset name and the bootloader's reported platform are not interchangeable selectors. Use the actual hardware code, boot hash, vendor hash and GPT checks. The complete measured partition layout is in [tested-profile.json](evidence/tested-profile.json). Do not remove a guard to force a different phone through this workflow.

The `b` in the publisher's `arm64_bgS` filename describes the GSI's A/B-style/system-as-root image layout. **It does not mean this physical phone has A/B slots.** Our working image was flashed to the single GPT partition named `system`.

## What you can download from this repository

This repository distributes the **device-specific source changes, configuration overlays, wallpaper assets, guarded workflow tools and evidence**. Obtain the original GSI from [Andy Yan's publisher page](https://sourceforge.net/projects/andyyan-gsi/files/lineage-18.x/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz/download), then build the customized image locally.

The owner's exact final image contains Google Play binaries installed from their Play account. Those Google app binaries and stock Oppo firmware backups are **not mirrored here**. The build/update process documents how to produce a local version, including installing official Play updates and capturing all necessary APK splits and extracted native libraries. See [distribution](docs/DISTRIBUTION.md) for the reason and the distinction between the tested personal image and the reproducible core image.

The two small APKs in `assets/` are our **configuration-only overlays**, not Google apps. They have no DEX code and are accompanied by their manifest/resource sources.

## Credits

The upstream work is essential: **Andy Yan**, **LineageOS**, **AOSP**, **phhusson/PHH Treble**, **TrebleDroid**, **Bjoern Kerler and MTKClient contributors**, and **SELinuxProject**. Our contribution is documenting and packaging the CPH1923-specific compatibility work, defaults and verification workflow. See [sources](docs/SOURCES.md).

The technical source changes are provided under GPL-3.0, with upstream notices and component licenses retained. Configuration-only overlay artwork and the generated wallpaper assets are provided for reuse under the terms in [NOTICE](NOTICE.md). No license in this repository grants rights to Google's apps or Oppo's firmware.
