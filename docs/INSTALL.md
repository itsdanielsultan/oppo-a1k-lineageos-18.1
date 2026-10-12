# Complete installation: stock CPH1923 → customized Android 11

This is the clean route assembled from the successful operations. **Do not repeat the Android 14/12 experiments first.** The refactored public tools have offline guard/rollback tests; their individual underlying operations were used on the phone, but a second cold installation with the public wrapper has not been performed. The precise validation boundary is in [VALIDATION](VALIDATION.md).

## 0. Confirm scope before downloading anything

This workflow stops unless the boot-ROM chip is `0x766`, the entire GPT matches the recorded 32 GB CPH1923 layout, the stock boot hash matches, and the retained vendor is the exact tested firmware. A mismatch is a request for investigation, not an invitation to remove a check.

The unit had Android 9, SDK 28, VNDK 28, Treble enabled, system-as-root enabled, board `oppo6762_18540`, platform `mt6765`, a 720 × 1560 screen and 2 GB RAM. The kernel and vendor stayed stock throughout the successful custom installation. We did not recover a trustworthy complete stock marketing build string; the boot/vendor/system digests in the profile are the exact identifiers used instead.

Do not use these commands on an A1, A1s, A5, a differently numbered Oppo, or a CPH1923 with a different firmware hash without separate work. Do not choose a GSI using only a marketing chipset name.

## 1. Equipment, time and backups

You need the phone, its normal screen-unlock access, an Apple Silicon Mac, a stable data-capable USB cable, internet for downloads, and ample local storage. Reserve approximately **50 GB free** for the archive, sparse/raw images, private stock backups, verification reads and an optional updated-app build. Keep the Mac awake during transfers. If it is a laptop, connect its power supply.

The first flash explicitly clears `userdata`, `metadata` and `cache`. Back up personal data before unlocking/flashing. The original owner chose to preserve nothing, which is not a recommendation for another person. A copy of `/sdcard` does not include all private app data, authenticator state or account credentials. Export those through the relevant apps before erasure.

Keep device backups private and in a second safe local location. Do not upload calibration, seccfg, NVRAM/NV data, partition dumps, account databases or raw logs to GitHub. Our repository's `work/` is ignored.

Transfers are not instant. The final 5 GB write in this session ran near 7–8 MB/s, and verification near 12–14 MB/s. Backups and full readbacks therefore take minutes. “Still busy” and “failed” are different conditions; use the phase and progress log.

## 2. Clone the guide and set up the Mac

Install Apple's Command Line Tools and Homebrew through their normal official flows if missing. Do not disable SIP, install random “MTK drivers,” or load an unknown kernel extension.

```sh
git clone https://github.com/itsdanielsultan/oppo-a1k-lineageos-18.1.git
cd oppo-a1k-lineageos-18.1
bash tools/setup_macos.sh
```

The setup script uses Python **3.12.12** through `uv`, a project-local virtual environment, native Homebrew libusb/e2fsprogs/libsepol/ADB, the tested MTKClient commit and the checked macOS USB diff. It installs the **headless** Python dependencies. Qt and FUSE mounting are unnecessary for this command-line workflow. `fuse library not installed` was printed by the working sessions; it did not prevent the operations used here.

The editable MTKClient checkout is the one Python imports. Do not patch a clone but accidentally run an unrelated installed package from another interpreter. Check:

```sh
.venv/bin/python -c 'import mtkclient; print(mtkclient.__file__)'
git -C work/mtkclient rev-parse HEAD
git -C work/mtkclient diff -- mtkclient/Library/Connection/usblib.py
.venv/bin/python tools/device.py --help
```

The commit must be `cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3`; the last command prints help without opening a phone.

For normal Android inspection, enable Developer options and USB debugging on the phone, approve your own Mac, and choose File transfer if its USB configuration hides debugging. `adb devices -l` must list an authorized device. Use your phone's serial if needed; this guide does not hardcode the owner's serial.

```sh
adb shell getprop ro.product.model
adb shell getprop ro.product.cpu.abi
adb shell getprop ro.vndk.version
adb shell getprop ro.treble.enabled
adb shell getprop ro.build.system_root_image
```

Expected original values are `CPH1923`, `arm64-v8a`, `28`, `true`, `true`. ADB is useful for ordinary Android inspection. **It is not the boot-ROM connection used to write partitions.** Rooted debugging is not required for this initial stock backup/unlock/flash route.

## 3. Enter boot ROM only after the tool is listening

Use the same sequence for every requested BROM session:

1. Start the specific tool command and leave it waiting.
2. Keep USB attached to the phone.
3. Hold **Volume Up + Volume Down + Power** until the screen resets or goes black.
4. Release **Power**; keep **both volume buttons** held for about 20 seconds.
5. Release both volume buttons and leave USB connected.

Recovery, the charging icon, or the Oppo logo is not the expected result. A black screen is necessary on this unit, but is not sufficient proof. Confirm the log identifies the expected chip, loads/accepts the DA extensions and enters the requested guarded operation.

We did not need a test point, opened casing, shorted pins, a TWRP recovery image, a replacement LK, a replacement preloader or a replacement stock kernel. Do not add those steps to this route.

## 4. Read and verify your own stock partitions

```sh
.venv/bin/python tools/device.py backup --workspace work/device
```

Then perform the boot-ROM sequence. The command checks the chip, GPT and stock boot image, and independently reads each selected partition twice. It compares complete SHA-256 hashes, saves the first copy, and removes only the temporary second verification copy.

The private backup set is `seccfg`, `lk`, `lk2`, `boot`, `vbmeta`, `dtbo`, `recovery`, `vendor` and `system`, plus `backup-manifest.json`. No unlock or flash occurs in this command. The recorded stock system is 5,033,164,800 bytes and vendor 964,689,920 bytes.

Proceed only after `VERIFIED: backup` and a manifest recording every complete file. An incomplete file or a mismatching firmware hash is a stop. Leave all originals untouched; use a new workspace for a genuinely new backup attempt rather than overwriting evidence.

Make a separate private copy of `work/device` before the next step. Do not copy another owner's seccfg or calibration partitions into your phone.

## 5. Unlock, then independently check the result

```sh
.venv/bin/python tools/device.py unlock --workspace work/device
```

Enter boot ROM again while the command is listening. The tool requires the current locked v4 seccfg to match your saved original bytes. It uses MTKClient's `seccfg('unlock', critical=False)`, reads the partition back and requires lock state **3**. It does not patch LK, preloader or the stock boot image.

After `VERIFIED: unlock`, wait for the tool to finish. Unplug USB, release both volume buttons and hold Power to start the phone. An **Orange State / unlocked** warning was the expected result on this unit, followed by Android. Reconnect USB and re-approve debugging if needed.

Do not use a “relock” command while a custom system or modified verification metadata is installed. This guide deliberately leaves the bootloader unlocked.

## 6. Download the exact GSI, not the newest-looking filename

Download [the pinned upstream archive](https://sourceforge.net/projects/andyyan-gsi/files/lineage-18.x/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz/download) to:

```text
work/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz
```

Verify:

```sh
shasum -a 256 work/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz
```

The result must be:

```text
7bb7c4ebd336ad1615ce9f078d6a455e2c524d736578571ac41671b36d23415a
```

`arm64_bgS` is the specific working upstream choice here. The A-only physical phone still uses the publisher's `b` system-as-root layout. Do not substitute `arm64_agS`, 32-bit `arm`, `a64`, vndklite, a random TWRP ZIP, or Android 12/14 based on a similar-looking name.

Decompression alone yields an **Android sparse image**, not the raw ext4 image expected by this workflow. The builder expands and validates its chunk lengths before editing it.

## 7. Build all the core device fixes before the first flash

```sh
.venv/bin/python tools/build_image.py \
  --publisher work/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz \
  --vendor work/device/vendor-stock.bin \
  --output work/cph1923-core.img \
  --secilc work/tools/secilc
```

For an Intel Mac with a different Homebrew prefix, pass `--e2fsprogs "$(brew --prefix e2fsprogs)/sbin"`; that machine configuration was not the physical installation tested in this session.

The builder verifies the archive/vendor hashes, expands sparse ext4, expands the filesystem within the existing system partition, unshares ext4 data blocks, adds/validates `sigcont`, patches the original Keymaster helper, adds the two static overlays and the wallpaper files/initializer, preserves required labels and checks the complete filesystem.

It produces `work/cph1923-core.img` and `work/cph1923-core.img.json`. The receipt includes its full hash and size. **Do not flash if policy compilation or the final filesystem check fails.** The core build keeps the publisher's original Google app versions; official updates and optional incorporation follow after first boot.

See [BUILD](BUILD.md) for every input and transformation. No direct mounted-filesystem sector editing is used.

## 8. Initial flash and the explicitly approved reset

```sh
.venv/bin/python tools/device.py flash \
  --workspace work/device \
  --image work/cph1923-core.img \
  --receipt work/cph1923-core.img.json \
  --erase-confirmation "ERASE MY CPH1923 DATA"
```

Enter boot ROM while the command is waiting. Do not unplug or press buttons during writing or verification.

The write path:

1. Rechecks chip/GPT/stock boot and the connected vendor image.
2. Confirms your own verified backups and the current stock system match.
3. Confirms seccfg reports the unlocked state.
4. Prepares your own vbmeta header with flags **3**; requires `AVB0`, saves no borrowed vbmeta, and reads back the full written metadata.
5. Writes the prepared raw system image to the single partition named `system`.
6. Reads the complete written image back and compares SHA-256.
7. Only then formats **`userdata`, `metadata`, `cache`** for the initial Android 9 → 11 installation.
8. Records completion and shuts down the DA connection.

The script leaves `boot`, `vendor`, LK, recovery, DTBO, TEE, radio, calibration and preloader partitions untouched. There is no repartitioning, no `system_a`/`system_b` write, and no flashing of another phone's stock image.

If a write/readback fails, the tool attempts to restore the original system and vbmeta from your own verified backup and verifies that restoration. A disconnected cable can prevent rollback; data already erased cannot be recovered by restoring firmware. See [RECOVERY](RECOVERY.md).

Proceed only when the result file says `verified: true`. In this session, an `Operation timed out` message sometimes appeared only during the final USB shutdown after successful verification. That is different from a write/read/checksum failure. Read the saved result, phase and actual process exit rather than interpreting one line in isolation.

## 9. First boot: wait for the right evidence

After the tool has finished:

1. Unplug USB and release both volume buttons.
2. Hold Power until the phone starts.
3. Reconnect USB and let the orange unlocked warning pass.
4. Allow up to approximately three minutes for first boot before declaring a logo stall.
5. Finish setup and any PIN/Wi-Fi/Google sign-in choices on the phone. Do not put credentials into logs or issue reports.

The expected result is **LineageOS setup**, then the home screen. If ColorOS recovery returns, use the troubleshooting/log path. Do not repeat data formats indefinitely or assume an old log from a previous Android build describes the current boot.

The custom ROM presents a generic `Phh-Treble with GApps` name. Confirm the OS by its release and SDK, not that generic product name.

## 10. Validate the basics before restoring dozens of apps

Enable USB debugging and approve your Mac again after the initial reset. Wait several seconds for USB enumeration; an instant empty `adb devices` result is not proof of a broken phone.

```sh
adb shell getprop ro.build.version.release       # 11
adb shell getprop ro.build.version.sdk           # 30
adb shell getprop sys.boot_completed             # 1
adb shell getprop ro.crypto.state                # encrypted
adb shell getprop ro.crypto.type                 # file
adb shell getenforce                             # Enforcing
adb shell getprop ro.sf.lcd_density              # 320
adb shell wm density                            # Physical density: 320
adb shell settings get system font_scale         # 1.0
```

If an old user density override is present, `adb shell wm density reset` removes that override only. It does **not** factory-wipe the phone. The remaining physical density should still be 320.

Check colorful icons/photos on the physical panel. A screenshot cannot prove the absence of a panel/display-path haze. The owner reported normal colors on this Android 11 configuration.

Connect to a mixed WPA2/WPA3 network if that was your previous problem:

```sh
adb shell cmd overlay list com.android.wifi.resources
adb shell cmd overlay lookup com.android.wifi.resources \
  com.android.wifi.resources:bool/config_wifiSaeUpgradeEnabled
```

The overlay should be enabled and the value `false`. Verify an actual connection and validated internet. A WPA3-only network is a different case and is not fixed by this overlay.

Check defaults:

```sh
adb shell cmd overlay lookup com.android.providers.settings \
  com.android.providers.settings:bool/def_haptic_feedback       # false
adb shell cmd overlay lookup com.android.providers.settings \
  com.android.providers.settings:bool/def_sound_effects_enabled # true
adb shell getprop ro.config.wallpaper
adb shell getprop sys.phh.wallpaper_defaults
```

The home property should reference `/system/etc/cph-wallpaper-defaults/wallpaper`. A truly fresh initial setup should report `initialized`; an existing wallpaper configuration should report `preserved`. Normal setup/backup restoration can subsequently replace wallpaper choices.

## 11. Google sign-in and official app updates

Use actual Wi-Fi internet and sign in privately to Play Store. Our temporary USB internet workaround validated connectivity but the old Google sign-in UI still said no network; the native Wi-Fi fix removed the practical blocker.

The upstream Store initially reported “no updates” despite obsolete apps. Its service was returning errors. We used the Store's own **Settings → About / Play Store version → Update** control; the older UI was a simple tap on the version row. It downloaded a newer Store, then a further current Store update.

After the newer Store is running, open **Manage apps & device → Updates → Update all**. Let installation finish, not just download. Open Android System WebView's own Store page too; it still offered Update separately in our session. Play services updated automatically. Verify that Manage apps & device reports **All apps up to date**.

On 2 GB RAM, large app processing and bulk backup restoration made controls slow and downloads look pending. Waiting for real install progress was preferable to interrupting active compilation. Do not mistake a pending restored launcher icon for a ROM display failure. The old framework is still Android 11 even when app versions are current.

If you want the downloaded versions to survive a reset, follow the **optional local APK integration** procedure in [BUILD](BUILD.md). A Store update in `/data/app` alone is not a ROM default. Do not upload those proprietary binaries as your own GitHub release.

## 12. Return temporary maintenance settings to normal

The backup/unlock/initial flash route does not require rooted Android debugging. The optional export/integration workflow may use the GSI's normal **Developer options → Rooted debugging** switch. Enable it through the normal UI only when needed; turn that switch off when finished and use `adb unroot`. Leave USB debugging on if you still need final checks.

Do **not** turn off the Developer-options master switch or delete its enabled setting while trying to preserve debugging. In our session, changing that setting while the screen was active contributed to losing the debugging interface and required re-enabling it on the phone.

Restore any temporary stay-awake preference to its prior value. The owner's original value was 0. Never guess that every reader's original setting is the same.

## 13. What a factory reset means afterward

A normal data reset removes personal apps, settings, accounts and downloaded `/data/app` updates. It does not erase these system-resident assets, overlays or early-init defaults. The native density and system touch defaults therefore come from the customized system image; the first-start wallpaper initializer can recreate both wallpapers when no configuration exists.

The owner's final local image also included the 16 updated Google packages. A reset of the **core** image built here returns the original upstream app versions unless you completed the optional app-integration build. Gboard's per-user sound setting and arbitrary third-party app preferences are not system defaults.

We tested initialization on an empty directory and verified it did not overwrite existing choices. We did not perform another factory reset on the completed personal phone. See the validation boundary and the exact evidence before treating this as a guarantee for a different firmware.
