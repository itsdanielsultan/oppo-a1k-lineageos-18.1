# What was actually verified

The evidence concerns **one physical CPH1923** and its recorded firmware. It is a useful successful case, not a compatibility certification.

## Live hardware observations

| Check | Evidence type | Outcome |
|---|---|---|
| Unlocked seccfg | Independent partition read | v4 lock state 3 |
| Orange warning then Android | Owner observation | Confirmed |
| Android version/SDK | ADB property reads | 11 / 30 |
| Boot complete | ADB property | 1 |
| Encryption | ADB properties | encrypted / file |
| SELinux global mode | `getenforce` | Enforcing |
| Native density | Property + cleared override + `wm density` | Physical 320 |
| Font scale | Settings read | 1.0 |
| Physical colors | Owner comparison/feedback | Reported perfectly fine on Android 11 |
| Mixed-mode Wi-Fi | Live resource lookup + network state | SAE upgrade false, connected and internet validated |
| Play Store | Owner sign-in + Store UI | Sign-in complete; All apps up to date |
| WebView | Live update-service state | Valid active Google WebView 153, completed relro setup |
| 16 bundled versions | System package records | Expected version codes at system destinations |
| Tap defaults | Overlay lookups + current settings | Haptics false/off, sounds true/on, charging vibration false/off |
| Gboard current preferences | Phone UI | Key sound on; keyboard vibration off |
| Home/lock wallpapers | Android picker + actual screenshots + service IDs | Midnight glass / blue-hour lake; IDs 3 / 4 |
| ROM wallpaper assets | Five full file hashes | Matched captured native files |
| Wallpaper startup hook | Post-boot marker | `preserved`, existing configuration retained |
| Maintenance runtime | ADB UID after completion | shell UID 2000 |
| Temporary stay-awake | Settings read | Restored to 0 for this owner |

The final wallpaper/system readback was the complete **5,033,164,800-byte** image, SHA-256 `43c10328b72a77514774cbc25e8e1a46cde454593654312c9d45a2fcdf41d883`. Its wallpaper patch changed 12 checked ranges totaling **1,257,472 bytes**. All original changed ranges matched before writes; each new range was read back; the entire final system hash then matched.

The preceding default-app image was also fully verified, SHA-256 `8bf498db72417cdf2584795ef5de673a260e43c848cf87f25992915954a46032`. Later default/wallpaper updates did not format user data.

The source session's first Android 14 basic checks detected two camera devices, but that is **not** a completed Android 11 camera-function test. Do not turn device detection from an earlier build into a final feature claim.

## Reset-default evidence without erasing the completed setup

We ran the wallpaper initializer on an empty test directory **on the actual Android phone**, checked all five complete hashes, ran it again and observed no changes, and tested a directory containing an existing choice. A production-path guard run preserved the actual user wallpaper files. The actual ROM init trigger order was inspected: post-fs-data occurs before zygote-start. The installed image then booted with the nonpersistent `preserved` marker set by that hook.

**A full factory reset of the finished personal setup was not performed.** Density was tested with `wm density reset`, which clears an override rather than user data. Both wallpaper assets and the initialization mechanism are system-resident. This is the factual basis for their reset-default behavior; it must not be described as a video of a fresh reset we never did.

Gboard's separate sound preference remains a user-data setting. The system haptic/sound defaults are the ones bundled in the SettingsProvider overlay.

## Public package replay and software tests

The public core builder was run offline against the exact publisher archive and actual stock vendor backup. Sparse expansion, filesystem resizing/unsharing, policy-version-30 compilation, full injected-file readbacks and final filesystem check passed. Its central helper, platform CIL, both overlays and wallpaper script/init fragment matched the live-tested final files byte for byte.

The public device wrapper consolidates the underlying operations into a new CLI. Its offline tests cover:

* unexpected chip rejection;
* unrecognized seccfg rejection;
* bad image receipt rejection before writes;
* missing data-erasure consent rejection;
* full verification before a data format;
* restoring system/vbmeta after a simulated readback failure, with no data format;
* a data-preserving same-version update;
* sparse RAW/FILL/DONT_CARE handling and truncated-input rejection.

These software tests do not constitute a second physical unlock/clean install with the refactored wrapper. The physical phone was not erased again merely to test publication packaging. A future independent tester should report their exact matching configuration and checkpoints rather than saying “works on all A1k.”

## Not established

Calls, SMS sending/receiving, cellular data/VoLTE, GPS, Bluetooth audio, every camera mode, microphone recording, sensors, SD cards, USB OTG, standby/battery behavior, DRM/Widevine, hardware codecs, banking apps, payments, Play Integrity and long-term stability were not comprehensively validated as final Android 11 features here.

The unlocked/custom/root-capable image is not equivalent to locked official Oppo firmware. It is not current on OS security patches. The 2 GB phone showed slow controls during large application restores. A future Store offer, different Google account, region, language/split delivery, beta-track membership, vendor build or different physical unit may change the result.

## Small evidence files suitable for public review

* [Tested hardware/profile and partition boundaries](../evidence/tested-profile.json)
* [Sanitized live check results](../evidence/live-verification.json)
* [Observed bundled package versions](../evidence/observed-app-versions.json)
* [Wallpaper defaults result](../evidence/wallpaper-defaults.json)
* [Keymaster excerpt](../evidence/keymaster-redacted-excerpt.txt)
* [Wi-Fi excerpt](../evidence/wifi-redacted-excerpt.txt)
* [SELinux excerpt](../evidence/selinux-redacted-excerpt.txt)

No private partition backups, APK exports, account databases or full raw logs are published.
