# Reproducing the system changes

## Two different image claims

There are two outputs, and they must not be confused:

* **Core reproduction:** the exact upstream `arm64_bgS` archive, the device fixes, overlays and wallpaper defaults. It retains the upstream Google app versions. The public builder was replayed offline successfully; its six central changed files matched the corresponding files in the live-tested final image byte for byte. Filesystem validation and vendor-policy compilation passed.
* **Owner's final personal image:** those core fixes **plus 16 Google app updates exported from the owner's Google Play installation**. Its complete physical flash readback was `43c10328b72a77514774cbc25e8e1a46cde454593654312c9d45a2fcdf41d883`. That image booted and passed the final live checks. It is not mirrored here because it includes proprietary Google binaries.

A rebuilt core image is not expected to have the personal image's hash. The app contents differ, and ordinary filesystem metadata can differ between rebuilds. Always use the receipt generated for your actual output. Do not copy a hash from an article into a receipt to make it pass.

## Exact core input and transformations

The input archive is publisher-hash pinned in [tested-profile.json](../evidence/tested-profile.json). Stock vendor is checked against `3d8cf8ffb3bedfb3edb3e90ee6aaaa7ffac0d19552730236e925e7dcedfb8f1d`; the builder never modifies the vendor backup.

The upstream `.img` inside the XZ archive is Android sparse. `image_utils.expand_sparse` handles the tested 4096-byte block format and RAW, FILL, DONT_CARE and CRC chunks, checking sizes, extent totals and truncation. The pinned archive checksum protects the input; sparse format expansion is not a substitute for checking it.

The builder extends the raw image and filesystem to the already measured **5,033,164,800-byte** system capacity. It does not enlarge a phone partition. It runs `resize2fs`, then `e2fsck -fy -E unshare_blocks`. Only after shared data blocks are removed does it replace files through offline `debugfs` operations.

Original shared ext4 blocks mattered. Writing an APK's physical blocks before unsharing could overwrite data shared by another file. The guide does not generalize the old diagnostic inode/block offsets into a new install recipe.

The builder then:

1. Extracts the original platform policy and applies the single ordered `sigcont` declaration change.
2. Extracts platform mapping 28, system_ext policy, and the actual vendor's `plat_pub_versioned.cil`/`vendor_sepolicy.cil`.
3. Compiles a policy-version-30 binary with the host `secilc`, using Android-init-style merged declaration/MLS/generated-attribute flags. The compile-time `-N` flag is not a runtime `setenforce 0`; global enforcement remains enabled.
4. Replaces platform CIL, preserving its original root ownership, mode and `sepolicy_file` context.
5. Applies the small `rw-system.sh` diff for the Keymaster wrappers, unsafe USB diagnostic guard, density and home fallback path; preserves root:shell, mode 0755 and `phhsu_exec` context.
6. Installs the two static overlays in `product/overlay`, with their tested labels/modes.
7. Installs the five native wallpaper files, initializer and post-fs-data init fragment.
8. Extracts and compares every injected file's complete content with its source.
9. Runs a final read-only filesystem check and writes an output SHA-256 receipt.

Neither the build tool nor the e2fsprogs tools access a phone or a mounted phone filesystem. Run them only against ordinary local image files. The guarded device tool is a separate explicit step.

## Overlay source and signing

The provided configuration-only APKs contain no DEX. Their manifest/resource sources are in `assets/wifi-compat` and `assets/touch-defaults`. The signing certificate belongs to this project's local configuration overlay, not Google, Oppo or the Android platform.

They are authorized by their system/product placement and the target's supported overlay rules. The Wi-Fi target exposes the `WifiCustomization` product policy; SettingsProvider in this Android 11 build has no overlayable set and permits a preinstalled overlay. Do not re-sign an APEX or install an arbitrary `/data/app` overlay and assume those are the same conditions.

If you rebuild overlays yourself, use a new local signing key and official AAPT2/SDK `apksigner` tools. Keep the private key private. Check `apksigner verify --verbose --min-sdk-version 30`; do not claim that a signature scheme unsupported by Android 11 was validated just because a newer desktop tool accepts it.

The supplied signed overlay binaries provide a convenient exact configuration input; their hashes are in `assets/SHA256.json`. Their private signing key is not required to use or inspect them and is not published.

## Optional: make official Play updates into local ROM defaults

Finish the core installation and native Wi-Fi/Google sign-in first. Let Play Store update itself, update the preinstalled apps, open the WebView listing separately, and wait for **All apps up to date**. The original Store's false “no updates” response is described in the installation guide.

Use official Android SDK Build Tools' `apksigner` with a suitable Java runtime. Android Studio/SDK tools are available from [Google's official tools page](https://developer.android.com/tools). Accept any SDK terms yourself through the normal SDK setup. The original session used Google's Build Tools 36 signing JAR with a local Corretto 17 runtime; no Google credentials were supplied to a script.

On the phone, enable the GSI's normal **Rooted debugging** switch temporarily if your own APK/native-library paths cannot be read as shell. `adb root` must succeed through that normal setting. Do not bypass the root service's UID checks or patch Settings permissions to enable it.

```sh
adb devices -l
adb root
.venv/bin/python tools/export_updates.py \
  --serial YOUR_OWN_ADB_SERIAL \
  --output work/app-export \
  --apksigner /YOUR/ANDROID/SDK/build-tools/36.0.0/apksigner
```

`YOUR_OWN_ADB_SERIAL` and the SDK path are the only reader-specific selectors in this command. They are not credentials. Use the serial shown by your own ADB inventory and an existing official signer executable.

The exporter selects **updated system apps**, finds their original product `app`/`priv-app` destination, captures the complete `pm path` APK set, verifies each APK for SDK 30, requires matching split signers, and copies only native `.so` code files actually extracted under that install's `lib/`. It does not export app databases, Google tokens, contacts, messages or account data.

The local manifest and binaries remain private. The [observed version table](../evidence/observed-app-versions.json) is a reference snapshot, not a list to download from third-party APK mirrors. Google Play may offer a newer compatible version, another language/density split set, or a different testing-track build to your account. The tested account was offered a beta-labeled Gboard; no reader is instructed to enroll in that beta.

Do not stop at `base.apk`. Messages, Chrome, Play Store, Play services and other packages can require splits. Text-to-speech in our capture had extracted native libraries. Copying only the base may appear to install but fail later.

### Static shared libraries and Trichrome

The initial Chrome/WebView 87 package set used an original Trichrome library. The updated set captured here did not require exporting a new separate data-based Trichrome package. The public exporter deliberately stops if an updated package declares a static shared-library dependency it has not captured; that is safer than baking an incomplete image.

Inspect an affected phone with:

```sh
adb shell dumpsys package libraries
adb shell dumpsys package com.android.chrome
adb shell dumpsys package com.google.android.webview
```

A static library may have an internal name such as `com.google.android.trichromelibrary_VERSION`. On Android 11, `pm path` on that internal name failed in our session. The workable inspection is `dumpsys package INTERNAL_NAME`, take its actual `codePath`, and enumerate/pull the APKs from that install directory. Verify the library's signature, min SDK and exact version required by the client. Keep distinct static-library versions in distinct system directories; do not replace a differently versioned original dependency blindly.

This public exporter/integrator supports the tested package set, not an arbitrary future static-library graph. If it stops on this condition, extend and validate dependency handling before proceeding. Do not delete the check just to force a build.

### Integrate and check the local image

```sh
.venv/bin/python tools/integrate_updates.py \
  --base work/cph1923-core.img \
  --base-receipt work/cph1923-core.img.json \
  --export work/app-export \
  --output work/cph1923-with-local-updates.img
```

It verifies the base receipt and every exported checksum before modification, refuses a still-shared filesystem, keeps original package directory/privilege location, removes old APK/split/native/oat contents from that package directory, installs the captured APK/native set with system labels/ownership, verifies full file readbacks and checks the filesystem again.

This includes Google binaries. Use the resulting image locally; do not add it to the repository, its ZIP or a public release without redistribution rights.

## Preserve the current setup when installing your local app build

The `update` subcommand does **not** format data. It requires an exact local copy of the current system image as `--prior-image`, and reads the physical system to confirm that prior image before writing. Keep the image and receipt that you actually installed; a similarly named upstream image is not an acceptable rollback.

Use a separate operation directory with a private copy of the verified original backup set/manifest, so existing readback filenames cannot be overwritten:

```sh
mkdir -p work/update-device
cp work/device/*-stock.bin work/device/backup-manifest.json work/update-device/
.venv/bin/python tools/device.py update \
  --workspace work/update-device \
  --prior-image work/cph1923-core.img \
  --image work/cph1923-with-local-updates.img \
  --receipt work/cph1923-with-local-updates.img.json
```

Enter boot ROM only after it is listening. It keeps your current vbmeta as the rollback reference, writes/verifies the selected system, and retains `userdata`, `metadata` and `cache`. On a write/readback failure it attempts to restore the exact prior system and current metadata. This is a same-Android-11 update route, not a promise that a data-preserving Android-version downgrade is safe.

After boot, compare both the active version and the system/bundled record in `dumpsys package PACKAGE`. An update living only in `/data/app` is not proof that the new version survives a reset. Our live checker found all 16 expected version codes at their actual system destination records.

Finally, turn **Rooted debugging off**, leave ordinary USB debugging available if still needed, run `adb unroot`, and restore any stay-awake setting you temporarily changed. The final phone's shell UID was 2000.
