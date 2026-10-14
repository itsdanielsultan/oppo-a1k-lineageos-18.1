# Troubleshooting: what you see and what to do next

Find the problem in the table, then check the result file and log for that step. Keep logs private until you have removed personal details. A black screen or a single “success” line does not tell you whether the complete operation finished; the saved result and full readback do.

| Symptom | What it establishes | Next action |
|---|---|---|
| `adb devices` empty, Mac sees no USB phone | No usable connection yet | Reconnect the data cable; wait about ten seconds for the Mac to detect the phone; inspect again |
| Mac sees Oppo/Phh USB but no ADB interface | USB is present; debugging may be off/hidden | Enable Developer options and USB debugging, select File transfer if needed, approve the Mac |
| ADB says `unauthorized` | Android is present but this host is not approved | Unlock the phone and accept its normal debugging prompt |
| Android home screen visible | Framework/launcher reached a usable screen | Check release/SDK, boot complete, encryption, policy, density and network; do not declare every hardware feature tested |
| ColorOS recovery menu | Recovery is running, not boot ROM or Lineage setup | Do not run Android shell instructions against it; collect a new private diagnostic read and check the build-specific failure |
| Charging icon | Charging mode, not the expected DA connection | Start one listener first, then use the tested both-volume-buttons reset sequence |
| Black screen after buttons | Consistent with boot ROM, not proof of it | Require chip/GPT/DA detection in the tool log before proceeding |
| Waiting/handshake failure on Mac | Tool has not reached the guarded operation | Confirm interpreter/checkpoint/USB patch; avoid another simultaneous listener; enter the proven mode again |
| Orange unlocked warning then Android | Expected unlocked boot path on this unit | Keep the bootloader unlocked with this custom system |
| Oppo logo for a short first boot | Not sufficient evidence of failure | Allow the documented first-boot window; if persistent, collect current diagnostics |
| Logo persists well beyond first-boot window | Boot did not reach the expected screen | Check a fresh log snapshot; do not apply conclusions from an older build's log bank |
| Write or checksum mismatch | Image integrity has not passed | Leave the cable attached for the guarded rollback, inspect result/log; do not tell the reader to power up mid-write |
| USB timeout only after verified completion and shutdown | May be the observed close/disconnect behavior | Confirm result `verified: true`/complete checksum and that the writer exited before normal boot |
| Android 14 photos/icons wash out after motion stops | Similar to the observed graphics problem | Do not ship the failed color tweaks as fixes; use the documented Android 11 path for this configuration |
| Maximum brightness is too dim on this Android 11 build | The normal brightness setting may already be at maximum while the backlight scale is mismatched | Try the [tested PHH backlight-scale adjustment](#maximum-brightness-is-too-low) and check the physical screen |
| Repeated TEE upgrade success then `vold begin -62` | The fresh Android 11 Keymaster version loop | Verify all four VNDK28 soft/puresoft wrappers are included in the existing fixSPL processing |
| `Failed to resolve permission sigcont` | Platform/vendor CIL mismatch | Apply the precise ordered process-class patch and compile against the actual vendor/mapping policies |
| PSK profile becomes SAE and cannot be saved | The observed mixed-mode Wi-Fi failure | Confirm the static Wi-Fi overlay is enabled and its SAE-upgrade resource is false |
| WPA3-only network still cannot connect | Outside this overlay's capability | Use a compatible WPA2/mixed network; do not claim the fix adds WPA3 |
| USB VPN validated but old Google sign-in says no network | Matches the temporary reverse-tethering limitation | Fix native Wi-Fi; the final route does not need gnirehtet |
| Old Play Store says no updates | Could be an obsolete update service, as here | Use its own version-update control first, then recheck from the newer Store |
| Google apps or Store show “This device isn't Play Protect certified” | Google is blocking access on this custom installation | Follow [Google's custom-ROM registration route and the tested Store recovery](#google-play-is-blocked-by-a-certification-warning); do not relock this custom system |
| WebView not in Update all but its listing offers Update | Observed separately here | Update it from its own official Store page and check the active provider |
| Pending/restoring launcher icons; settings slow | Bulk restoration/app processing on a 2 GB phone | Let actual install/compile progress finish; stop assuming pending means already installed |
| Density changes disappear on reset | Likely only a user override | Inspect native `ro.sf.lcd_density`; remove just the override and verify physical 320 |
| Home wallpaper persists but separate lock default is absent | A home property alone is insufficient on Android 11 | Verify bundled lock files, native metadata and post-fs-data initializer |
| Initializer reports `preserved` | At least one existing wallpaper file/configuration was found | Expected on an already configured phone; it deliberately does not overwrite the user's choices |
| Google app version disappears on reset | Likely update only in `/data/app` | Check the actual system/bundled package record and complete APK split/native integration |
| Rooted debugging cannot be enabled by an ADB setting write | Root service deliberately checks caller identity | Use the normal phone UI; do not bypass UID checks or component permissions |

## Google Play is blocked by a certification warning

For this custom ROM, Google's [uncertified-device notice](https://www.google.com/android/uncertified/warningauto) directs users to register their own **Google Services Framework Android ID (GSF ID)**. This is an exception route for using Google apps. It does not make this GSI an officially certified Oppo build or establish a Play Integrity pass.

### 1. Read your own GSF ID privately

Use the phone's existing Google Services Framework installation. The ID is **not** `Settings.Secure.ANDROID_ID`, the USB serial, or an IMEI. Do not publish it, copy another phone's ID, or upload the GSF database.

On this build, the normal shell could not read the GSF provider. With the phone unlocked and your own Mac authorized for USB debugging, temporarily enable **Settings → System → Advanced → Developer options → Rooted debugging** through the normal phone UI. Then, on the Mac:

```sh
adb devices -l
adb root
adb wait-for-device
adb shell
```

Allow the USB connection to return if it briefly disconnects. Inside the phone's shell, run `id`; it must report `uid=0(root)` before the database read. Then run this read-only query in that same phone shell:

```sh
sqlite3 -readonly /data/user/$(cmd activity get-current-user)/com.google.android.gsf/databases/gservices.db \
  "SELECT value FROM main WHERE name = 'android_id';"
exit
```

Copy only the returned decimal value, privately. If access is denied or no ID is returned, stop and investigate the current installation; do not clear GSF storage to generate another ID or bypass the rooted-debugging checks.

Turn **Rooted debugging** off again on the phone immediately after reading the ID. Back on the Mac, run:

```sh
adb unroot
adb wait-for-device
adb shell id
```

After reconnection, the last command should report the ordinary shell UID `2000`. Restore any temporary stay-awake preference to its previous value.

### 2. Register with Google, then restart

1. Open [Google's official device-registration page](https://www.google.com/android/uncertified/) and sign in to your Google account.
2. Paste your GSF ID into **Google Services Framework Android ID**. `phonelink_setup`, if displayed beside the field, is an icon label rather than part of the ID.
3. Complete Google's CAPTCHA and select **Register**.
4. Confirm **Device registered** or that your ID appears in the registered-device list. A button click alone is not confirmation.
5. Restart the phone, reconnect to working Wi-Fi, and reopen Play Store.

Google's public registration instructions do not promise a processing deadline or formal certification. If the Store opens, continue with setup and app updates; a data reset is unnecessary in that case.

### 3. If the Store still blocks access, reset only its local data

Registration, rebooting, cache clearing and reinstalling the same Store version were insufficient on this phone. On October 14, 2026, the additional **Play Store-only** data reset below restored signed-in catalogue access.

This deletes the Store's local databases and preferences. Review the warning before proceeding: purchase/password protection and parental controls may need to be restored, and Google may ask you to accept its terms again. Installed apps and the device's Google account remain. This is separate from clearing **Google Play services** or **Google Services Framework** data, which was not needed for this recovery.

1. Open **Settings → Apps & notifications → Google Play Store**. Use **See all apps** if necessary.
2. Select **Storage & cache → Clear storage**.
3. Read **Delete app data?** and confirm only if you accept the Store-local reset.
4. Reopen Play Store. Complete any account or terms prompts yourself, and review purchase protection and parental controls before further use.
5. Verify the catalogue loads, then separately test an app download or update.

These steps follow [Google's Store troubleshooting](https://support.google.com/googleplay/answer/14121800?hl=en). Do not disable Play Protect scanning, relock the bootloader with this custom system, or factory-reset the phone as part of this procedure.

### What was actually verified

Google confirmed registration on October 13. After the Store-only reset on October 14, its signed-in catalogue and account menu opened without the blocking screen. We did **not** finish checking a new download/update or the Store's **Settings → About → Play Protect certification** result afterward. Working access, certification and Play Integrity are separate results. The [sanitized recovery record](../evidence/google-play-access-recovery.json) contains no private IDs or account information.

## Maximum brightness is too low

On October 13, 2026, the tested CPH1923 running this Android 11 build was still too dim with manual brightness already at `255` (maximum). Enabling PHH's alternative backlight scale made the screen noticeably brighter, as confirmed by the owner.

1. Open **Settings → Phh Treble Settings → Misc features**.
2. Under **Backlight**, enable **Force alternative backlight scale**.
3. Move the normal brightness slider slightly down and back to maximum. In our check, the setting was refreshed from `255` to `254` and back to `255`.
4. Check the phone's physical screen. A screenshot cannot establish its brightness.

Optional read-only checks over an already authorized ADB connection:

```sh
adb shell getprop persist.sys.phh.backlight.scale
adb shell getprop persist.sys.qcom-brightness
adb shell settings get system screen_brightness
adb shell settings get system screen_brightness_mode
```

On this phone, the first two values changed from `0` / `-1` to `1` / `2047`. The last two were `255` / `0`, meaning maximum manual brightness. The installed PHH handler reads the device's reported backlight maximum and selected `2047`; do not copy that number blindly to another device. Despite the property's `qcom` name, this result was observed on the tested MediaTek-based Oppo. **Use linear screen brightness slider** was left unchanged. Rooted debugging, reflashing and a data reset were not needed for this adjustment.

To undo, disable **Force alternative backlight scale** and move the brightness slider again. The installed handler restores `persist.sys.qcom-brightness` to `-1` when the option is disabled; this rollback path was inspected in the handler, rather than physically retested after the successful adjustment.

This is a setting change on the existing installation, not a new image build or an increase beyond the panel's reported range. Brightness was not measured in nits or compared instrumentally with stock firmware. Reboot persistence and factory-reset behavior were not tested after this change; do not assume the image builder applies it or that it survives a reset. See the [sanitized brightness check](../evidence/brightness-verification.json) and [upstream sources](SOURCES.md).

## Useful read-only checks

```sh
adb devices -l
adb shell getprop sys.boot_completed
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.crypto.state
adb shell getprop ro.crypto.type
adb shell getenforce
adb shell wm size
adb shell wm density
adb shell dumpsys connectivity
adb shell dumpsys webviewupdate
adb shell dumpsys package com.android.vending
adb shell getprop ro.config.wallpaper
adb shell getprop sys.phh.wallpaper_defaults
```

`dumpsys connectivity`, package diagnostics and screenshots can include account/network/device information. Inspect privately and redact before sharing. A GUI click accepted by a tool does not establish that the intended setting changed; read it back.

## Fresh private boot diagnostics

Use a new private directory:

```sh
.venv/bin/python tools/device.py logs --workspace work/diagnostic-attempt-01
```

Start it first, then enter boot ROM. It reads `expdb`, `para` and `cache` and does not write those partitions. Their contents can include old boots and private identifiers. Keep them out of public releases.

During the difficult Android 11 case, a timed startup snapshot was needed because the newest hang was not reliably represented in an old dump bank. The final production image does not retain that instrumentation. Recreating the old snapshots is not a normal install step, and the unsafe USB gadget teardown must not be re-enabled.

## Checks that answer different questions

* A correctly written image can still be incompatible with the vendor/kernel and fail boot.
* A successful Android boot can still have bad physical colors.
* A validated VPN can still be rejected by an old Google sign-in flow.
* An app's active update can be new while its bundled system APK remains old.
* A user density override can look correct while the factory ROM density is still 480.
* `Enforcing` can coexist with permissive upstream superuser domains.
* A tested first-start initializer is not an actual factory-reset trial.

That separation is the reason this guide contains checkpoints instead of asking the reader to repeat the same reset indefinitely.
