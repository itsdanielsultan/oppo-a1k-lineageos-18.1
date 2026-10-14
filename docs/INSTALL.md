# Install Android 11 on the tested Oppo A1k CPH1923

Follow these steps in order. They combine the operations that worked on our phone; you do not need to repeat the failed Android 14 and Android 12 attempts.

The process is: check the phone → save its original software → unlock it → build the Android 11 image with the fixes → install it and clear the old setup → check the result → update the apps.

The public tools have tests for their phone checks and recovery handling. The individual steps were used on the phone, but we have not repeated a complete installation with the repackaged tools. Read [what was tested](VALIDATION.md) and [recovery](RECOVERY.md) before starting.

## 0. Check your exact model and original firmware

This guide is for the tested **32 GB Oppo A1k CPH1923**. The tools stop unless all of these match:

- Boot-ROM chip code `0x766`.
- The complete recorded storage layout, called the GPT.
- The original `boot` image's hash.
- The exact tested `vendor` firmware, which contains the Oppo hardware drivers.

A hash, or checksum, identifies the contents of a file. Matching the model name alone is not enough. **If a check fails, stop and find out why. Do not remove it.**

The original phone ran Android 9, SDK 28, VNDK 28, with Treble and system-as-root enabled. Its board was `oppo6762_18540`, platform `mt6765`, screen 720 × 1560 and RAM 2 GB. The original kernel and vendor drivers were kept. We could not confirm the complete original firmware build name, so the exact boot/vendor/system hashes in the recorded profile identify the tested software.

Do not use these commands on an A1, A1s, A5, another Oppo model, or a CPH1923 with different firmware hashes without separate work. The Android image in this guide is a **GSI**: a generic system image adapted here for this phone. Do not choose one from the marketing chipset name alone.

## 1. Gather the equipment and back up your data

You need the phone and access to unlock its screen, an Apple Silicon Mac, a reliable data-capable USB cable, and internet for downloads. Reserve approximately **50 GB free** on the Mac for downloads, converted images, backups, verification copies and an optional build with updated apps. Keep the Mac awake during transfers and plug in a laptop's power supply.

**The first installation clears `userdata`, `metadata` and `cache`.** That removes apps, settings, accounts and personal files. Back up what you need before unlocking or installing. The original owner chose to preserve nothing; that is not a recommendation for another person. Copying `/sdcard` does not save all private app data, authenticator information or account credentials. Export those through the relevant apps first.

Keep the original-software backups private and make a second copy in another safe local location. Do not upload calibration, seccfg, NVRAM/NV data, partition dumps, account databases or raw logs to GitHub. The repository excludes `work/` from Git.

Expect transfers to take minutes. Our final 5 GB write ran near 7–8 MB/s, with verification near 12–14 MB/s. Follow the progress log to distinguish an active transfer from a failed one.

## 2. Install the Mac tools and check the Android connection

Install Apple's Command Line Tools and Homebrew through their official setup instructions if they are missing. Do not disable SIP, install random “MTK drivers,” or load an unknown kernel extension.

```sh
git clone https://github.com/itsdanielsultan/oppo-a1k-lineageos-18.1.git
cd oppo-a1k-lineageos-18.1
bash tools/setup_macos.sh
```

The script installs Python **3.12.12** through `uv` and creates a Python environment inside the project. It also installs the Homebrew USB, filesystem, SELinux and Android tools: libusb, e2fsprogs, libsepol and ADB. It downloads the tested MTKClient revision and applies the macOS USB fix.

Only the command-line Python dependencies are needed. Qt and FUSE mounting are not required. The working sessions printed `fuse library not installed`; that message did not prevent these steps.

Check that Python is using this project's MTKClient copy, with the expected revision and USB changes:

```sh
.venv/bin/python -c 'import mtkclient; print(mtkclient.__file__)'
git -C work/mtkclient rev-parse HEAD
git -C work/mtkclient diff -- mtkclient/Library/Connection/usblib.py
.venv/bin/python tools/device.py --help
```

The revision must be `cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3`. Stop if Python points to an unrelated installed copy or the revision differs. The last command only prints help; it does not connect to a phone.

**ADB** is the tool used to inspect Android over USB. Enable Developer options and USB debugging on the phone, approve your own Mac, and select File transfer if debugging is hidden by the current USB mode. `adb devices -l` must show an authorized phone. Use your own phone's serial when needed; this guide does not hardcode the owner's serial.

Check the original Android setup:

```sh
adb shell getprop ro.product.model
adb shell getprop ro.product.cpu.abi
adb shell getprop ro.vndk.version
adb shell getprop ro.treble.enabled
adb shell getprop ro.build.system_root_image
```

The expected values, in order, are `CPH1923`, `arm64-v8a`, `28`, `true`, `true`. If they differ, investigate before continuing. ADB is separate from the boot-ROM connection used to write the phone's storage. Rooted debugging is not needed for the initial backup, unlock or installation.

## 3. Learn the button sequence before starting a transfer

**Boot ROM**, also called **BROM**, is the low-level connection MTKClient uses for backups and writes. Start the requested tool command first, then enter this mode:

1. Leave the command waiting for the phone.
2. Keep USB attached.
3. Hold **Volume Up + Volume Down + Power** until the screen resets or goes black.
4. Release **Power**; keep **both volume buttons** held for about 20 seconds.
5. Release both volume buttons and leave USB connected.

The expected screen is black. Recovery, the charging icon or the Oppo logo means you have not reached the required mode. A black screen alone is not proof: the tool's log must identify the expected chip, accept the DA extensions—the transfer software loaded into the phone—and start the requested operation after its checks pass. Do not continue on a failed connection.

This route did not require opening the phone, using a test point, shorting pins, installing TWRP, or replacing LK, the preloader or the original kernel. Do not add those steps.

## 4. Save and verify the phone's original software

Run:

```sh
.venv/bin/python tools/device.py backup --workspace work/device
```

Then use the button sequence in step 3. The tool checks the chip, storage layout and original boot image. It reads each selected partition—a section of the phone's storage—twice and compares complete SHA-256 hashes. It keeps the first copy and deletes only the temporary second copy used for verification.

The backup contains `seccfg`, `lk`, `lk2`, `boot`, `vbmeta`, `dtbo`, `recovery`, `vendor` and `system`, plus `backup-manifest.json`, which records the files and checksums. This command does not unlock or write to the phone. The recorded original system is 5,033,164,800 bytes and vendor 964,689,920 bytes.

**Continue only after `VERIFIED: backup` and a manifest recording every complete file.** Stop on an incomplete file or a firmware hash mismatch. Keep the originals untouched. If you need a new backup attempt, use a new workspace rather than overwrite the previous files.

Make a separate private copy of `work/device` before unlocking. Never write another owner's seccfg or calibration partitions to your phone.

## 5. Unlock and check that Android still starts

Run:

```sh
.venv/bin/python tools/device.py unlock --workspace work/device
```

Use the button sequence while the command is waiting. The current locked v4 `seccfg` must match your saved original bytes. MTKClient uses `seccfg('unlock', critical=False)`, then reads the partition back and requires lock state **3**. It does not change LK, the preloader or the original boot image.

**Wait for `VERIFIED: unlock` and for the tool to finish.** If verification fails, stop. Then unplug USB, release both volume buttons and hold Power to start the phone. The expected result is an **Orange State / unlocked** warning followed by Android. Reconnect USB and approve debugging again if needed.

Do not relock the bootloader while a custom system or modified verification metadata is installed. This guide leaves it unlocked.

## 6. Download and check the exact Android 11 image

Download [the image used in this guide](https://sourceforge.net/projects/andyyan-gsi/files/lineage-18.x/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz/download) and save it here:

```text
work/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz
```

Check its SHA-256 checksum:

```sh
shasum -a 256 work/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz
```

It must match this exactly. Stop if it does not:

```text
7bb7c4ebd336ad1615ce9f078d6a455e2c524d736578571ac41671b36d23415a
```

Use `arm64_bgS`. This phone has one physical system partition, often called **A-only**, but needs the publisher's `b` system-as-root image layout. The letter does not mean the phone has A/B slots. Do not substitute `arm64_agS`, 32-bit `arm`, `a64`, vndklite, a random TWRP ZIP, or Android 12/14 because the name looks similar.

Unpacking the archive still leaves an **Android sparse image**, a compact storage format. The builder converts it to the raw ext4 filesystem image needed for installation and checks the lengths before editing. Do not flash the unpacked file directly with this workflow.

## 7. Build the Android image with the phone's fixes

Run:

```sh
.venv/bin/python tools/build_image.py \
  --publisher work/lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz \
  --vendor work/device/vendor-stock.bin \
  --output work/cph1923-core.img \
  --secilc work/tools/secilc
```

For an Intel Mac with a different Homebrew prefix, pass `--e2fsprogs "$(brew --prefix e2fsprogs)/sbin"`. We did not test the physical installation on that Mac configuration.

The builder checks the download and vendor hashes, converts the sparse image and expands its filesystem to fit the existing system partition. It separates shared ext4 file blocks before changing files. It adds and checks the `sigcont` SELinux permission, patches the Keymaster encryption helper, adds the Wi-Fi and touch-settings overlays, and includes the wallpapers and their first-start helper. It preserves required SELinux file labels and checks the complete filesystem.

The output is `work/cph1923-core.img` with `work/cph1923-core.img.json`, a receipt containing the full hash and size. **Stop if SELinux policy compilation or the final filesystem check fails. Do not install that image.**

This core image still has the publisher's original Google app versions. Update those after the first boot; the later optional build can include those updates. [BUILD](BUILD.md) records every input and change. The tools do not edit raw storage sectors underneath a mounted filesystem.

## 8. Install Android 11 and clear the old setup

This is the first installation and it will clear your data. Run:

```sh
.venv/bin/python tools/device.py flash \
  --workspace work/device \
  --image work/cph1923-core.img \
  --receipt work/cph1923-core.img.json \
  --erase-confirmation "ERASE MY CPH1923 DATA"
```

Use the button sequence while the command is waiting. Leave USB connected and do not press buttons during writing or verification.

The tool performs these steps:

1. Rechecks the chip, GPT storage layout, original boot image and connected vendor firmware.
2. Checks that your verified backups match the current original system.
3. Confirms that seccfg reports the unlocked state.
4. Prepares your own `vbmeta` verification header with flags **3**. It requires `AVB0`, uses no borrowed vbmeta, and reads back all written metadata.
5. Writes the prepared raw image to the single partition named `system`.
6. Reads the complete written image back and compares its SHA-256 checksum.
7. Only after that passes, formats **`userdata`, `metadata`, `cache`** for the first Android 9 → 11 installation.
8. Records completion and closes the DA transfer connection.

The script leaves `boot`, `vendor`, LK, recovery, DTBO, TEE, radio, calibration and preloader partitions untouched. It does not repartition storage, write `system_a`/`system_b`, or install another phone's original firmware.

If a write or readback fails, the tool attempts to restore the original system and vbmeta from your verified backup, then checks that restoration. A disconnected cable can prevent recovery. Restoring firmware cannot recover data that has already been erased. Follow [RECOVERY](RECOVERY.md) if a step fails.

**Continue only when the saved result says `verified: true`.** An `Operation timed out` message sometimes appeared during final USB shutdown after successful verification. Check the saved result, transfer stage and process exit: a shutdown timeout after success is different from a write, read or checksum failure.

## 9. Start the phone and finish setup

After the tool has finished:

1. Unplug USB and release both volume buttons.
2. Hold Power until the phone starts.
3. Reconnect USB and let the orange unlocked warning pass.
4. Allow up to approximately three minutes for the first boot.
5. Finish setup, including your PIN, Wi-Fi and Google sign-in choices, on the phone. Keep credentials out of logs and issue reports.

The expected result is **LineageOS setup**, then the home screen. If the phone stays at the logo after that wait or returns to ColorOS recovery, follow [TROUBLESHOOTING](TROUBLESHOOTING.md). Do not repeatedly format data or use a log from an earlier Android build to explain the current boot.

The phone may show the generic name `Phh-Treble with GApps`. Check the Android version and SDK in the next step to confirm what is installed.

## 10. Check Android, colors, Wi-Fi and the defaults

Enable USB debugging and approve your Mac again after the reset. Give the Mac several seconds to detect the phone; one immediate empty `adb devices` result does not prove the phone is broken.

Run these checks. The comments show the expected results:

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

Stop and investigate if these do not match before restoring lots of apps. `Enforcing` is the expected global SELinux mode; the upstream GSI still contains permissive superuser domains, as explained in [VALIDATION](VALIDATION.md).

If an old user scale override is present, `adb shell wm density reset` removes only that override. It does **not** factory-wipe the phone. The remaining physical density—the interface scale supplied by the system—should still be 320.

Check colorful icons and photos on the phone itself. A screenshot cannot show whether its physical display is hazy. Colors looked normal on the owner's Android 11 setup.

Also check maximum brightness on the phone. If it is too dim, follow [the tested backlight-scale adjustment](TROUBLESHOOTING.md#maximum-brightness-is-too-low). This is a setting to apply after installation; the image builder does not enable it for you.

If you use a mixed WPA2/WPA3 network, connect to it and check the Wi-Fi configuration:

```sh
adb shell cmd overlay list com.android.wifi.resources
adb shell cmd overlay lookup com.android.wifi.resources \
  com.android.wifi.resources:bool/config_wifiSaeUpgradeEnabled
```

The configuration overlay should be enabled and the value should be `false`. Confirm the phone actually connects and has working internet. This change addresses the mixed-network problem through WPA2; it does not add WPA3-only support.

Check touch and wallpaper defaults:

```sh
adb shell cmd overlay lookup com.android.providers.settings \
  com.android.providers.settings:bool/def_haptic_feedback       # false
adb shell cmd overlay lookup com.android.providers.settings \
  com.android.providers.settings:bool/def_sound_effects_enabled # true
adb shell getprop ro.config.wallpaper
adb shell getprop sys.phh.wallpaper_defaults
```

The home wallpaper property should reference `/system/etc/cph-wallpaper-defaults/wallpaper`. A fresh setup should report `initialized`; a setup with existing wallpaper choices should report `preserved`. Normal setup or backup restoration can replace those choices afterward.

## 11. Register with Google if needed, then update Play Store and the bundled apps

If Google apps or Play Store show **This device isn't Play Protect certified**, complete [the custom-ROM device-registration steps](TROUBLESHOOTING.md#google-play-is-blocked-by-a-certification-warning) before continuing. They explain how to read your own Google Services Framework ID, register it on Google's official page, and reset only the Store's local data if access remains blocked. Do not use the owner's ID or post your own ID publicly.

The app-update steps below worked during the original setup. A later certification block appeared on October 13, 2026; registration followed by a Store-only data reset restored signed-in catalogue access on October 14. Downloads/updates were not retested after that recovery, and formal certification remains unverified. See [the follow-up validation](VALIDATION.md#october-14-2026-google-play-access-recovery); do not assume sign-in, updates or certification will work on every installation.

Connect through working Wi-Fi and sign in to Play Store privately on the phone. Our temporary USB internet connection worked, but the old Google sign-in screen still reported no network. The Wi-Fi fix allowed sign-in to complete.

The original Play Store said “no updates” even though the apps were old, and its service returned errors. First update the Store itself using **Settings → About / Play Store version → Update**. In the older interface, tapping the version row started the update. Our phone downloaded a newer Store and then another current Store update.

Once the newer Store is running, open **Manage apps & device → Updates → Update all**. Wait for installation to finish. Also open Android System WebView's Store page; it offered an additional Update in our session. Play services updated automatically. Confirm that Manage apps & device says **All apps up to date**.

Expect delays while this 2 GB phone installs large apps or restores a backup. Follow actual installation progress before interrupting it. A pending restored launcher icon does not mean the display is broken. The phone will still load apps slowly and have limited multitasking, whichever Android version it runs.

These are the newest versions Play Store offers for this phone. Android itself remains version 11. If you want the updates to remain after a reset, follow [the optional app-integration steps](BUILD.md). Those steps copy the APK app files into your local system image. An update left only in `/data/app` disappears after a reset. Do not upload Google's proprietary app files as your own GitHub release.

## 12. Turn off temporary maintenance access

The initial backup, unlock and installation do not require rooted Android debugging. The optional app export and integration may use **Developer options → Rooted debugging**, which gives maintenance tools elevated access. Turn it on through the normal phone settings only when needed. When finished, turn that switch off and use `adb unroot`. Keep ordinary USB debugging on if you still need final checks.

Do **not** turn off the Developer-options master switch or delete its enabled setting while trying to keep debugging available. Changing that setting while the screen was active contributed to losing our debugging connection, which had to be enabled again on the phone.

Restore any temporary stay-awake preference to its previous value. The owner's original value was 0; another reader's may differ.

## 13. Understand what remains after a factory reset

A normal data reset removes personal apps, settings, accounts and updates stored in `/data/app`. It does not erase the files and settings built into the system image. That is where the smaller interface scale and touch defaults are stored. The first-start wallpaper helper can recreate both wallpapers when there are no existing choices.

The owner's final local image also contained the 16 updated Google packages. Resetting the **core** image built in step 7 returns the publisher's original app versions unless you completed the optional build with updated apps. Gboard's per-user sound setting and other apps' personal preferences are not system defaults.

We tested the wallpaper helper with an empty directory and checked that it preserved existing choices. We did **not** factory-reset the completed phone again. Read [what was tested](VALIDATION.md) and the recorded evidence before assuming the same result on different firmware.
