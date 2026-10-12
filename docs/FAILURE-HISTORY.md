# What the twelve-hour path actually contained

This is the historical appendix, not the order to follow for a new install. The install guide consolidates the final fixes into the image before the first write. The chronology below records why the simpler-looking advice did not work in this session.

The owner estimates at least twelve hours. We did not independently reconstruct a stopwatch duration from every interaction; the available saved operations span October 11–12, 2026. Source/log dates near January 1 or January 2024 often reflect the phone's unsynchronized first-boot clock, not the date of our work.

## Connection and unlock

| Attempt or state | Observed result | What changed |
|---|---|---|
| Phone connected in ordinary Android | ADB repeatedly disappeared or the Mac saw a non-debug interface | File transfer, Developer options and USB debugging had to be enabled; the Mac had to be approved |
| MTKClient on Mac through the initial USB backend | Enumeration/claim/handshake failures | Darwin library discovery and the specific CDC interface-0 claim were corrected |
| Native serial-interface listening, reconnect without buttons | Did not yield a dependable working unlock session | The proven attached-cable, both-volume-buttons + Power reset sequence was used |
| Volume Down only | ColorOS recovery | Recovery was not treated as boot ROM |
| Volume Up only | Charging screen | Charging was not treated as a DA connection |
| ADB reboot-to-bootloader/EDL and conventional fastboot assumptions | Normal Android or unusable/unstable connection | No fastboot-only recipe was relied on |
| Single guarded unlock session | Stock partition backups, v4 seccfg readback state 3 | Owner then saw the orange unlocked warning and Android |

Several requests to repeat the button sequence were real connection attempts; they were not evidence that every repetition changed the phone. The final guide requires software detection before a write and a verification result afterward.

## Android 14: boot success was not a display success

The initial newer LineageOS GSI path was Android 14. Platform/vendor SELinux compatibility and encryption compatibility changes were investigated. A Google-apps build and signed-package migration were prepared, checked and installed while retaining the setup. The phone reached Android; Google framework packages were present.

However, the display looked washed out across photos and colorful icons. The owner compared it with the clearer stock ColorOS display and described normal colors briefly appearing while swiping before the screen became hazy again.

Unsuccessful display tests included:

* forced GPU composition and hardware-overlay bypass;
* native/unmanaged output and an Oppo vivid color mode;
* contrast/saturation adjustment;
* lower backlight, which dimmed the screen but did not remove the haze;
* adaptive contrast/AAL bypass;
* legacy OpenGL/GLES rendering, alone and with forced GPU composition;
* bypassing the hardware color-processing block;
* neutral gamma, delaying/disabling display idle switching, and buffer-path optimization changes.

Those tests were restored. We did not find a single proven color-processing defect or ship a global saturation workaround. Android 14's ability to boot was not enough to recommend it as the successful result.

## Android 12: newer did not mean bootable here

With the owner's explicit permission to downgrade/reset, a checked LineageOS 19.1 Android 12 Google-apps build was written and fully read back, then the approved data partitions were cleared. The first boot returned to ColorOS recovery.

Fresh logs showed Android 12 platform policy loading and userdata mounting, followed by `vdc cryptfs enablefilecrypto` failure. Older `-62` messages in a shared log bank belonged to another build; it would have been wrong to label them as the new Android 12 failure without fresh evidence.

We tried a guarded startup-order adjustment to the stock Trustonic `mobicore` daemon and vendor Keymaster service, retaining encryption and enforcement. Another recovery boot followed. A full recovery data format also returned to recovery.

The owner was offered a stock ColorOS restoration and chose to continue with a custom ROM. Stock restoration was prepared/checked locally, but was not the final route taken. This history does not prove that Android 12 is impossible on every CPH1923; it records that this particular build/path did not succeed.

## Android 11: the first attempts still hung

The pinned LineageOS 18.1 Android 11 `arm64_bgS` image was selected and sparse-expanded. The `sigcont` policy change was prepared and compiled with the stock vendor policy. The system was written, fully read back, and the already approved failed setup was reset.

The phone stalled at the Oppo/orange-warning logo. The owner supplied a photo after approximately ten minutes. Several early log reads contained older recovery/Android 12 banks, rather than an unambiguous new Android 11 failure. A logo and an old log were not enough to diagnose the current boot.

### The diagnostic USB mistake

To expose early startup and save helper traces, an existing publisher USB diagnostic branch was activated. That branch tore down configfs/MTP and caused a kernel panic involving `mtp_free_inst` on this old kernel. This was an avoidable diagnostic mistake, was acknowledged during the session, and was corrected.

The unsafe diagnostic activation was removed, and the final helper excludes the `/cache/phh-adb` branch on `mt6765`. Do not include recursive USB gadget teardown in a public “fix” recipe.

### Snapshot timing and stale interpretations

Short, timed startup snapshots were used to capture properties/logcat before a stalled boot lost its normal interface. Some early snapshots were partial or taken before a relevant bind-mount state was complete. Source filenames explicitly marked `partial-overlay-unverified` are not final success evidence.

A later fresh Android 11 snapshot showed the actual storage-encryption loop: the TEE reported Android 9 / May 2021, key upgrade returned success, then `vold` begin returned `-62` again. Inspection linked the stock vendor Keymaster implementation with VNDK 28's puresoft wrapper and its property reads.

### The real successful correction

The existing publisher `fixSPL` processing was extended to all four VNDK 28 soft/puresoft Keymaster wrappers on the tested MediaTek hardware. The patch was locally checked, original phone sectors were compared, and the changed content was read back.

The phone subsequently reached LineageOS setup. Live checks found Android 11/SDK 30, boot complete, FBE and global SELinux enforcement. The owner later said the colors were “perfectly fine.” A waiting plan to restore the previously booting Android 14 custom ROM was canceled before writing, because the working Android 11 state was observed. Do not use a stale “return to 14” script just because it exists in a troubleshooting folder.

The final helper removed automatic startup tracing, forced USB properties and timed snapshots, while retaining the successful Keymaster extension and the diagnostic-branch exclusion.

## Defaults, Wi-Fi and current apps

After setup, the owner wanted a smaller native interface and the latest compatible preinstalled app versions, not merely auto-update turned on.

The scale was first a user override. It was moved into the early ROM helper and later verified as the physical 320 default after `wm density reset`.

Mixed WPA2/WPA3 Wi-Fi then blocked sign-in/app updates. A saved PSK profile was being promoted to SAE and rejected by the vendor supplicant. A signed, static product overlay disabled that promotion. This did not change the router and did not add native WPA3 support.

### USB internet was a partial success, not the Wi-Fi fix

The official Genymobile `gnirehtet` reverse-tethering project was tried. An older client needed a directly started activity because a background start was blocked. The older Rust relay was unstable, so the current Java relay and a workspace-local Corretto runtime were used. A phone HTTP connectivity check returned 204, the VPN became validated, and network time corrected the clock.

Despite that actual connectivity, the old Google sign-in UI reported no network. The owner continued seeing no usable Wi-Fi/setup path. The temporary helper was uninstalled, the relay stopped, and native Wi-Fi compatibility was fixed instead. The successful install does not require a VPN helper, an old Rust relay or Google credentials handled by a script.

### Play Store needed to update itself

The old upstream Store was version 23 and initially showed no updates while logs contained service errors. Its own version-update control downloaded a newer Store, then the current offered Store. The newer UI presented a real update queue. Android System WebView offered an update separately; Play services updated automatically.

The installed updates were captured with base APKs, all delivered splits and text-to-speech's extracted native libraries. All captured signatures were checked for SDK 30. A full unshared system image was prepared and written/read back without erasing the current setup. Live system package records—not just `/data/app` paths—then matched all 16 expected versions.

## Haptics and wallpapers

The owner disliked the physical vibration motor. Current system haptics were disabled, supported sounds enabled, and Gboard's current Sound/Vibration controls adjusted. A static SettingsProvider overlay makes the general touch/charging preferences ROM defaults. No reliable obfuscated Gboard resource override was claimed as a reset-safe keyboard-sound default.

Two wallpapers were generated and applied through Android's normal picker. Concurrent phone use and a slow restoration workload interfered with the picker; the owner then left it untouched and both selections were applied/verified. A shortcut-removal toast appeared after an earlier wake-up swipe; Undo was tapped. This was a UI-side interaction issue, not a ROM modification.

When the owner asked for reset persistence, the wallpapers were captured in Android's native saved/cropped form and bundled. The separate lock default required a post-fs-data initializer; a home fallback property alone was insufficient on Android 11. The initializer was tested on empty/existing directories, a small checked sector update was applied, and the entire 5 GB system readback matched. After boot, its `preserved` marker and the existing home/lock IDs proved it ran without replacing the current setup.

## What is deliberately absent from the clean route

No repeated recovery formats to chase the same unknown failure. No Android 14 graphics tuning carried into Android 11. No unsafe configfs teardown. No global encryption/SELinux disable. No guessed A/B partitions. No foreign boot, vendor, TEE or calibration images. No stale automatic return-to-14 job. No Google sign-in through our temporary USB VPN. No assumption that “Store says no updates” means its old update service is healthy.

For the concrete final recipe, return to [INSTALL](INSTALL.md). For symptoms and checkpoints, use [TROUBLESHOOTING](TROUBLESHOOTING.md).
