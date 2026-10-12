# Symptoms, evidence and next actions

Use the symptom's checkpoint, not another random ROM or wipe. Keep logs private until redacted. An operation's result file and complete readback are stronger evidence than a filename, a tool launch, a black screen or a single “success” message.

| Symptom | What it establishes | Next action |
|---|---|---|
| `adb devices` empty, Mac sees no USB phone | No usable connection yet | Reconnect the data cable; wait about ten seconds for enumeration; inspect again |
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
| Repeated TEE upgrade success then `vold begin -62` | The fresh Android 11 Keymaster version loop | Verify all four VNDK28 soft/puresoft wrappers are included in the existing fixSPL processing |
| `Failed to resolve permission sigcont` | Platform/vendor CIL mismatch | Apply the precise ordered process-class patch and compile against the actual vendor/mapping policies |
| PSK profile becomes SAE and cannot be saved | The observed mixed-mode Wi-Fi failure | Confirm the static Wi-Fi overlay is enabled and its SAE-upgrade resource is false |
| WPA3-only network still cannot connect | Outside this overlay's capability | Use a compatible WPA2/mixed network; do not claim the fix adds WPA3 |
| USB VPN validated but old Google sign-in says no network | Matches the temporary reverse-tethering limitation | Fix native Wi-Fi; the final route does not need gnirehtet |
| Old Play Store says no updates | Could be an obsolete update service, as here | Use its own version-update control first, then recheck from the newer Store |
| WebView not in Update all but its listing offers Update | Observed separately here | Update it from its own official Store page and check the active provider |
| Pending/restoring launcher icons; settings slow | Bulk restoration/app processing on a 2 GB phone | Let actual install/compile progress finish; stop assuming pending means already installed |
| Density changes disappear on reset | Likely only a user override | Inspect native `ro.sf.lcd_density`; remove just the override and verify physical 320 |
| Home wallpaper persists but separate lock default is absent | A home property alone is insufficient on Android 11 | Verify bundled lock files, native metadata and post-fs-data initializer |
| Initializer reports `preserved` | At least one existing wallpaper file/configuration was found | Expected on an already configured phone; it deliberately does not overwrite the user's choices |
| Google app version disappears on reset | Likely update only in `/data/app` | Check the actual system/bundled package record and complete APK split/native integration |
| Rooted debugging cannot be enabled by an ADB setting write | Root service deliberately checks caller identity | Use the normal phone UI; do not bypass UID checks or component permissions |

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

## Do not conflate these situations

* A correctly written image can still be incompatible with the vendor/kernel and fail boot.
* A successful Android boot can still have bad physical colors.
* A validated VPN can still be rejected by an old Google sign-in flow.
* An app's active update can be new while its bundled system APK remains old.
* A user density override can look correct while the factory ROM density is still 480.
* `Enforcing` can coexist with permissive upstream superuser domains.
* A tested first-start initializer is not an actual factory-reset trial.

That separation is the reason this guide contains checkpoints instead of asking the reader to repeat the same reset indefinitely.
