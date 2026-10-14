# Upstream sources and attribution

The original session is the primary evidence for the actual phone results. Public upstream sources explain the mechanisms and tools; they do not substitute for testing another unit.

| Component/reference | Source | Use here |
|---|---|---|
| MTKClient | [bkerler/mtkclient](https://github.com/bkerler/mtkclient), pinned commit `cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3` | Boot-ROM connection, DA extensions, seccfg unlock, GPT and partition I/O; GPL-3.0 |
| GSI publisher | [Andy Yan Lineage 18.x files](https://sourceforge.net/projects/andyyan-gsi/files/lineage-18.x/) | Exact Android 11 archive, publisher checksums and original system content |
| GSI source ecosystem | [Andy Yan's LineageOS GSI project](https://github.com/AndyCGYan/lineage_build_unified) | Upstream build context and credits; do not imply this repository compiled a full OS |
| LineageOS Android framework | [lineage-18.1 framework](https://github.com/LineageOS/android_frameworks_base/tree/lineage-18.1) | Android 11 framework/WMS behavior and CIL context |
| PHH Treble | [phhusson/device_phh_treble](https://github.com/phhusson/device_phh_treble) | Publisher's helper/fixSPL approach, init integration and generic device support |
| PHH Android 11 backlight handler | [phh-prop-handler.sh](https://github.com/phhusson/device_phh_treble/blob/android-11.0/phh-prop-handler.sh) | Alternative backlight scale reads the device's reported maximum; disabling restores `-1`. The installed phone's handler was also inspected |
| PHH brightness troubleshooting | [Common Issues and fixes](https://github.com/phhusson/treble_experimentations/wiki/Common-Issues-and-fixes#maximum-brightness-is-too-low) | Community-contributed upstream guidance; the alternative-scale setting alone was tested on this CPH1923, with owner feedback |
| SELinux compiler | [SELinuxProject/selinux](https://github.com/SELinuxProject/selinux), commit `2233a23a4d4f1bf29054037babec13f30d038e65` | Host secilc compiled against local libsepol for validation |
| Runtime resource overlays | [AOSP RRO documentation](https://source.android.com/docs/core/runtime/rros) | Static product placement, overlayable policy and SettingsProvider target rules |
| Wi-Fi client source | [Lineage 18.1 ClientModeImpl](https://github.com/LineageOS/android_frameworks_opt_net_wifi/blob/lineage-18.1/service/java/com/android/server/wifi/ClientModeImpl.java) | `config_wifiSaeUpgradeEnabled`-controlled promotion |
| Android Keymaster | [Android 11 keymaster implementation](https://android.googlesource.com/platform/system/keymaster/+/refs/heads/android11-release/android_keymaster/android_keymaster.cpp) | OS/patch version checks and key-upgrade behavior |
| Keymaster wrapper | [AndroidKeymaster3Device](https://android.googlesource.com/platform/system/keymaster/+/refs/heads/android11-release/ng/AndroidKeymaster3Device.cpp) | VNDK/legacy wrapper context |
| Android 11 wallpaper client | [WallpaperManager.java](https://github.com/LineageOS/android_frameworks_base/blob/lineage-18.1/core/java/android/app/WallpaperManager.java) | Separate lock default unsupported by `openDefaultWallpaper` in this build |
| Android 11 wallpaper service | [WallpaperManagerService.java](https://github.com/LineageOS/android_frameworks_base/blob/lineage-18.1/services/core/java/com/android/server/wallpaper/WallpaperManagerService.java) | Native file names, metadata tags, ownership and load behavior |
| Init sequencing | [Lineage 18.1 init.rc](https://github.com/LineageOS/android_system_core/blob/lineage-18.1/rootdir/init.rc) | post-fs-data before zygote; the actual image's rc was also inspected |
| Similar display report | [TrebleDroid issue 91](https://github.com/TrebleDroid/treble_experimentations/issues/91) | Corroborating symptom report; not an exact diagnosed defect |
| USB reverse tethering | [Genymobile/gnirehtet](https://github.com/Genymobile/gnirehtet) | Historical temporary workaround, not a final dependency |
| Google app licensing | [Android Developers note](https://android-developers.googleblog.com/2009/09/note-on-google-apps-for-android.html), [GMS](https://www.android.com/intl/en_au/gms/) | Why Google app binaries are not mirrored |
| APK signing tools | [Android SDK tools](https://developer.android.com/tools) | Official AAPT2/apksigner validation |

The source diffs keep the actual changes visible. The complete stock/vendor/raw logs are private and not redistributed. This is a documented adaptation of other developers' work; the successful hardware result does not justify claiming authorship of LineageOS, PHH, MTKClient or Google's apps.
