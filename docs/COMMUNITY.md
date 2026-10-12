# Community announcement drafts and placement

These are **review drafts**, not messages already posted to Reddit or XDA. The canonical technical guide is the GitHub repository; a short announcement should link to it rather than duplicate an incomplete flashing recipe.

## Recommended placement, checked October 12, 2026

* **XDA General Topics:** [current forum](https://xdaforums.com/f/general-topics.256/). Its description explicitly includes guides for phones without a dedicated device forum. This is a suitable fallback for a CPH1923 device guide. If a moderator identifies a more specific Oppo/Treble section, use that section instead. An XDA login was not active in the browser used for this check; do not create an account/accept terms or post under another identity automatically.
* **r/AndroidAfterlife:** its [current rules](https://www.reddit.com/r/androidafterlife/about/rules/) allow revival/repurposing of older phones and related OS versions. This is the most natural Reddit framing for making an old A1k useful again. Check sidebar/pinned guidance and posting availability again before submission.
* **r/AndroidRoms:** [community](https://www.reddit.com/r/AndroidRoms/) is directly relevant, but its public metadata reported restricted posting. Use it only if the posting account is approved; don't send moderator mail without separate authorization.

Do **not** post this unofficial-build link in r/LineageOS: its [rules](https://www.reddit.com/r/LineageOS/about/rules/) exclude unofficial builds/sites. Do **not** submit this generated draft/artwork to r/Oppo: its [rules](https://www.reddit.com/r/Oppo/about/rules/) require human-produced posts and restrict generated text/images. r/CustomRoms was also a poor candidate: restricted posting, no download links, and a sidebar focused on emulator/game ROMs despite an inconsistent short description.

## Reddit draft

**Title:** Reviving an Oppo A1k CPH1923: my Android 9 → 11 upgrade took 12 hours, so I documented the exact fixes

I got my old 2 GB/32 GB Oppo A1k CPH1923 running Android 11 after roughly twelve hours of troubleshooting. I worked through it with Codex and put the logs, actual fixes, checks and failure history into a detailed guide so someone with the same firmware doesn't have to repeat the whole process.

The working result is a customized Andy Yan LineageOS 18.1 GSI, with the original Oppo kernel and vendor retained. Android 14 booted but the physical display kept turning washed out; an Android 12 attempt returned to recovery. Android 11 eventually booted with normal colors after extending the existing Keymaster compatibility handling to the VNDK28 wrappers.

Other details that mattered: macOS libusb/CDC-interface handling, the correct system-as-root GSI despite the phone being physically A-only, a missing `sigcont` policy permission, and a saved WPA2 profile getting promoted to unsupported SAE on a mixed WPA2/WPA3 network.

The guide includes the exact input hashes, private-backup and recovery steps, guarded tools, Wi-Fi fix, native smaller scale, touch defaults and reset-persistent wallpapers. I also updated the bundled Google apps locally. The public download is the fixes/toolkit and build process, **not a mirrored Google-app ROM**.

[Guide and source](https://github.com/itsdanielsultan/oppo-a1k-lineageos-18.1)

This was tested on one exact CPH1923 configuration. It is unofficial, requires an initial data reset, and the Android framework security patch is still January 2024. I haven't validated every camera/radio/banking/payment feature, so I'm not calling it “the only correct method” or claiming every issue is fixed.

If you've worked on the same model, which stock firmware did yours have, and do its boot/vendor hashes match the guide?

## XDA draft

**Title:** [GUIDE][CPH1923][GSI] Oppo A1k Android 9 → 11: tested macOS MTKClient path, Keymaster/Wi-Fi fixes and reset defaults

This documents one successful CPH1923 upgrade using Andy Yan's `lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz`, stock Oppo boot/vendor, and MTKClient on Apple Silicon macOS. It was prepared with AI assistance and checked against the physical phone's logs, partition readbacks, owner feedback and live verification.

**Tested profile:** CPH1923; board `oppo6762_18540`; reported platform `mt6765`; MTKClient hardware code `0x766`; 2 GB RAM / 32 GB storage; original Android 9 / VNDK28; physical A-only system-as-root; stock 4.9.117-based kernel; vendor SPL 2021-05-05. The repository contains the exact boot/vendor/GPT profile and rejects mismatches.

**Key changes:**

1. Pinned macOS MTKClient USB backend and specific CDC control-interface claim correction.
2. Fresh connection handling and verified seccfg unlock; no LK/preloader/boot replacement.
3. Ordered `sigcont` addition, compiled against the actual vendor CIL/mapping28/system_ext.
4. Existing fixSPL processing extended to all four VNDK28 soft/puresoft Keymaster wrappers. Fresh logs showed TEE Android9/202105, repeated successful UpgradeKey and `vold begin -62`.
5. Old-kernel-unsafe PHH USB diagnostic branch excluded on this hardware.
6. Static product RRO disabling automatic PSK-to-SAE promotion. This fixes the observed transition-network case, not WPA3-only support.
7. Native 320 density, system touch/charging defaults and bundled home/lock wallpaper initialization before zygote on a fresh setup.
8. Optional local official-Play APK/split/native-library integration; proprietary Google binaries are not mirrored.

**Observed final results:** Android11/SDK30 boot complete; FBE encrypted/file; global SELinux Enforcing; physical colors reported normal; mixed-mode Wi-Fi internet validated; Play sign-in/updates worked; all16 expected bundled app version codes verified in the personal build; full final5GB system readback matched. The wallpaper initializer was tested on empty/existing directories and preserved the completed setup after reboot.

**Limitations:** one exact unit/configuration; Android OS patch2024-01-05; upstream permissive superuser domains still present; no full factory-reset trial of the completed personal setup; public orchestration refactored/offline-tested rather than re-flashing the phone just to test packaging. Calls, VoLTE, GPS, Bluetooth audio, every camera mode, DRM and payment/integrity behavior are not comprehensively certified.

**Guide/source/toolkit:** https://github.com/itsdanielsultan/oppo-a1k-lineageos-18.1

It includes A–Z prerequisites, input hashes, private backups, build/flash checkpoints, failed attempts, recovery boundaries and redacted evidence. This is a patched unofficial GSI, not an official device-specific LineageOS release or a from-scratch OS build. Credits belong to Andy Yan, LineageOS/AOSP, PHH/TrebleDroid, MTKClient and SELinuxProject.

Please report the exact stock build hashes and failed checkpoint rather than removing guards or posting unredacted partition dumps. Independent confirmation on a matching CPH1923 would be useful.
