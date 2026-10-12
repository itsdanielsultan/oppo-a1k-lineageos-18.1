# The exact fixes and why they mattered

This document separates observed evidence from hypotheses. It is not a list of settings to try randomly.

## 1. macOS could enumerate the USB device without usable boot-ROM communication

The tested MTKClient version grouped Darwin with Linux and selected `libusb-1.0.so`. That is the wrong shared-library name for this Mac. The tested patch uses PyUSB's native `libusb1.get_backend()` discovery on Darwin, retains the Linux/FreeBSD path, and limits the Windows-specific `libusb_set_option` call to Windows.

A second problem affected the Mediatek boot-ROM device `0x0e8d:0x0003`. On this configuration, macOS owned CDC control interface 0. The working data endpoints were on interface 1. PyUSB's endpoint-zero/control handling tried to claim interface 0 even when the data interface was explicitly selected.

The patch skips that claim only when all of these conditions match:

* Darwin;
* vendor `0x0e8d`, product `0x0003`;
* selected interface 1;
* interface 0 exists and is CDC class 2.

Normal data-interface claims remain in place. This is not a general instruction to skip every interface claim or detach arbitrary Mac kernel drivers. The exact source diff is [mtkclient-darwin-usb.patch](../patches/mtkclient-darwin-usb.patch).

Every standalone session also uses a fresh `DaHandler.connect` implementation which actually calls `preloader.init`. A stale saved DA state is not proof that a newly connected phone is in the expected mode. Keep one listener/writer active at a time.

## 2. The boot-ROM sequence was specific, and recovery was not boot ROM

The reliable sequence on this unit was: keep the cable attached, hold **Volume Up + Volume Down + Power** until the screen resets/goes black, release **Power**, keep **both volume buttons** held for about 20 seconds, then release them.

The software must already be listening. A black screen alone is not proof of a successful connection; the log must identify the hardware and accept the DA extensions.

Volume Down alone led to ColorOS recovery. Volume Up alone led to a charging screen. Reconnecting without buttons and trying `adb reboot bootloader`/EDL did not produce a reliable usable fastboot/boot-ROM workflow on this phone. The guide does not rely on those routes.

## 3. `sigcont` had to be present in the platform policy's ordered process class

The stock vendor policy referenced `sigcont`, while the newer GSI platform CIL did not declare it. The captured failure included:

```text
Failed to resolve permission sigcont
```

The change was narrowly scoped to the platform CIL declaration:

```diff
-(class process (fork transition sigchld sigkill sigstop signull signal ...))
+(class process (fork transition sigchld sigkill sigstop sigcont signull signal ...))
```

The full exact diff is [selinux-sigcont.patch](../patches/selinux-sigcont.patch). `sigcont` belongs **after `sigstop` and before `signull`**, matching the stock process permission order. Appending it at an arbitrary location is not equivalent.

The modified platform policy was compiled against the actual stock vendor CIL, its versioned vendor public policy, platform mapping 28 and the GSI's system_ext policy before it was installed. No global `setenforce 0`, permissive boot argument, or encryption-disable change was used to make Android 11 boot. After boot, `getenforce` reported `Enforcing`.

The upstream GSI already has permissive superuser domains. We retained those upstream definitions; `Enforcing` is a global-mode observation, not a claim that the GSI has stock Oppo's complete security posture.

## 4. The successful Android 11 encryption fix was a VNDK 28 wrapper fix

The useful fresh Android 11 snapshot showed the Trustonic TEE reading:

```text
os_version = 90000
os_patchlevel = 202105
TEE_UpgradeKey exiting with 0
vold: begin failed, code -62
```

The important pattern was repeated successful key upgrade followed by `KEY_REQUIRES_UPGRADE` (`-62`) on the next operation. Repeating a data format did not resolve that version disagreement.

The publisher's existing `fixSPL()` code already redirected property reads in selected vendor Keymaster libraries. It made temporary copies, performed same-length substitutions such as the ROM version/patch property names to dedicated Keymaster compatibility properties, restored labels and bind-mounted the copies. The **VNDK 28 soft/puresoft wrapper libraries were omitted** on this MediaTek path.

For `ro.boot.hardware=mt6765`, we appended these four existing files to that same `additional` list:

```text
/apex/com.android.vndk.v28/lib/libsoftkeymasterdevice.so
/apex/com.android.vndk.v28/lib64/libsoftkeymasterdevice.so
/apex/com.android.vndk.v28/lib/libpuresoftkeymasterdevice.so
/apex/com.android.vndk.v28/lib64/libpuresoftkeymasterdevice.so
```

That extension—not a global fake Android version, not deleting Keymaster, and not disabling FBE—was followed by a successful Android 11 setup/home screen. The phone still reported Android 11/SDK 30 while storage reported `encrypted`/`file`.

Keep the original stock `boot`, `vendor` and TEE partitions. The compatibility values are derived by the publisher's helper from the retained boot image. A different kernel/vendor/SPL combination must be investigated separately.

## 5. A publisher USB diagnostic branch was unsafe on this old kernel

An early diagnostic attempt enabled the publisher's `/cache/phh-adb` branch. That branch recursively removed and rebuilt `/config/usb_gadget`. On this old MediaTek kernel, the captured failure implicated `mtp_free_inst` during MTP/configfs teardown.

We removed the diagnostic activation and guarded the existing branch with:

```sh
if [ -f /cache/phh-adb ] && [ "$(getprop ro.boot.hardware)" != mt6765 ];then
```

This prevented that branch from running on the tested hardware. The final helper does not include the temporary forced ADB gadget setup, cache tracing or timed snapshot instrumentation used during diagnosis.

**Do not recreate the failure to gather logs.** In particular, do not create `/cache/phh-adb` and then recursively delete configfs USB gadgets. The successful guide uses the normal Android USB configuration and the tested boot-ROM connection.

## 6. Android 14 booted but had physical display washout

On Android 14, photos and colorful icons looked white/hazy. The owner observed normal colors for milliseconds during fast swipes, followed by the entire screen washing out. ColorOS had looked clearer.

We tried, and restored, GPU composition, unmanaged/native color output, an Oppo vivid mode, contrast/saturation changes, lower brightness, AAL bypass, legacy GLES, hardware color-processing bypass, gamma/idle/buffer-path changes. The owner continued reporting the same problem. Brightness reduction dimmed the screen but did not remove the haze.

The strongest interpretation was incompatibility between the old MediaTek/PowerVR display stack and the newer Android graphics behavior. The exact defect was not isolated. [TrebleDroid issue 91](https://github.com/TrebleDroid/treble_experimentations/issues/91) was a useful similar report, not proof that every variant has the same defect.

After the Android 11 boot fix, the owner explicitly reported that colors were “perfectly fine.” No failed Android 14 color/renderer tweak was carried into the final Android 11 image. We did not objectively calibrate the panel or validate color accuracy with an instrument.

## 7. Mixed WPA2/WPA3 Wi-Fi was failing in automatic SAE promotion

The saved profile was WPA2-PSK, and scan results advertised PSK+SAE transition mode. Android's Wi-Fi client automatically promoted the saved configuration to SAE; the retained vendor supplicant rejected saving that configuration:

```text
Failed to save variables for: "EXAMPLE-TRANSITION-SSID"SAE
Failed to add/save network configuration: "EXAMPLE-TRANSITION-SSID"SAE
```

The fix is a static, configuration-only product RRO:

| Field | Value |
|---|---|
| Package | `local.cph1923.wificompat` |
| Target | `com.android.wifi.resources` |
| Target name | `WifiCustomization` |
| Resource | `bool/config_wifiSaeUpgradeEnabled` |
| Value | `false` |
| Installed path | `/system/product/overlay/OppoWifiCompat/OppoWifiCompat.apk` |
| Static priority | 999 |

This keeps a mixed-mode network's PSK profile as PSK. It **does not add WPA3 support** and cannot make a WPA3-only network compatible. The router was not reconfigured. Live verification found a connected, internet-validated Wi-Fi network and the resource lookup returned `false`.

We did not edit or re-sign Google's Wi-Fi resources APEX. Its original APK data was shared in the ext4 image; overwriting those sectors could have changed another file too. A supported product overlay avoided both the signing problem and the shared-data problem.

## 8. The small scale became a ROM default

`wm density 320` is a user override; a data reset removes it. We added a guarded `resetprop_phh ro.sf.lcd_density 320` to the existing early `rw-system.sh` helper. That helper is executed from the original `vndk.rc` at `post-fs`, before the Android interface starts. The existing property trigger restarts SurfaceFlinger when the density changes.

After installation, we ran **`wm density reset`**, which removes only the override, and verified:

```text
Physical density: 320
```

Font scale remained 1.0. We did not factory-wipe the owner's setup to test density.

## 9. Tap sound and haptic defaults are a separate overlay

`local.cph1923.touchdefaults` targets `com.android.providers.settings` from `/system/product/overlay/OppoTouchDefaults/`. It sets:

```xml
<bool name="def_haptic_feedback">false</bool>
<bool name="def_sound_effects_enabled">true</bool>
<bool name="def_dtmf_tones_enabled">true</bool>
<bool name="def_charging_vibration_enabled">false</bool>
```

The live settings were adjusted too. Gboard's current Preferences → Key tap → Sound was enabled and Keyboard vibration disabled through its UI. Those Gboard preferences live in user data; the newer Gboard's obfuscated resource names did not provide a reliable separate reset-default overlay.

Do not promise that every third-party long press becomes an audible click. The system enables supported click sounds and disables normal system touch haptics. Apps can implement their own feedback. The Gboard sound preference may need setting again after a reset; the system haptic default remains off.

## 10. Both wallpapers needed system assets and first-start initialization

Android 11's `WallpaperManager.openDefaultWallpaper()` supports the normal `ro.config.wallpaper` path but returns `null` for a separate factory-default lock wallpaper. Merely placing two JPEGs in the ROM or setting a `ro.config.lock_wallpaper` property would not have implemented both defaults.

We bundled Android's native saved/cropped files for the selected home and lock images, plus its native `wallpaper_info.xml`, in `/system/etc/cph-wallpaper-defaults/`. The home fallback property is set by the same early helper. A new init fragment runs a small initializer at **`post-fs-data`, before `zygote-start`**.

The initializer checks for existing wallpaper metadata or images. If any are present, it preserves them and reports `sys.phh.wallpaper_defaults=preserved`. If none exist after a reset, it stages the five ROM files, assigns system ownership/mode 0600, restores their normal SELinux contexts and commits the metadata last. It reports `initialized` in that case.

An empty-directory test on the actual phone produced all five expected hashes. Re-running it made no changes. An existing-choice fixture stayed unchanged, and a production-path guard check preserved all five actual wallpaper hashes. After the installed ROM booted, the marker was `preserved`, home ID 3 and lock ID 4 remained, and all five public ROM asset hashes matched.

We did **not** erase the current setup to perform a full factory-reset trial. The evidence is the tested initialization logic, verified init ordering, system-resident files, full flash readback and observed post-boot execution. Restoring a cloud backup can deliberately replace wallpaper choices, just as it can on a stock ROM.

## 11. Updated APKs alone would not survive a factory reset

Play Store normally installs system-app updates under `/data/app`; those updates disappear with a data reset. We captured each installed update's base APK, all delivered splits, and any native `.so` files actually extracted by PackageManager. We verified Android 11 compatibility/signatures and incorporated them into the original `app` or `priv-app` system directories, keeping package identities and privilege location intact and removing obsolete `oat` directories.

The final local image contains 16 updated Google packages. [Observed versions](../evidence/observed-app-versions.json) describe what Google Play offered this phone/account on October 12, 2026. They are not a promise about another account, a future date, a testing-track membership or a newer OS-specific APK. In particular, the offered Gboard version was marked beta; we did not deliberately enroll another account into a beta.

Native LineageOS framework apps were retained from the Android 11 build. Arbitrarily copying a newer Android Settings, SystemUI or launcher into an old framework is not a safe substitute for a supported OS build.
