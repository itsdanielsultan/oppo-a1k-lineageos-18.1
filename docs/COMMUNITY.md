# Sharing the guide

The GitHub repository holds the complete instructions. A forum post should explain the result, give enough detail to help readers, and link to the full installation and recovery steps.

## Where it fits, checked October 12, 2026

* **r/AndroidAfterlife:** [posting guide](https://www.reddit.com/r/androidafterlife/wiki/index/community_guide/). The community welcomes guides for older phones. Its rules require useful information and prohibit posts primarily aimed at self-promotion. Share the phone's result and the fixes that mattered, rather than a bare link or an advertisement. A search for Oppo A1k did not show an existing guide covering this process.
* **XDA General Topics:** [forum](https://xdaforums.com/f/general-topics.256/) accepts guides for phones without a dedicated device section. However, [XDA rule 15](https://xdaforums.com/t/using-ai-to-generate-post-content-in-the-forums-is-not-permitted.4704287/) prohibits AI-generated forum posts. The owner must write the announcement in their own words; the AI-written draft is not suitable for submission. The in-app browser was also signed out of XDA at the time of checking.
* **r/AndroidRoms:** [community](https://www.reddit.com/r/AndroidRoms/) is relevant, but posting was restricted. An account must have posting access before submitting there.

Do not post the unofficial-build link in r/LineageOS, whose rules exclude unofficial builds and sites. r/Oppo also requires human-produced posts and restricts generated text and images. r/CustomRoms was restricted and prohibited download links, so it was not selected.

## Reddit post prepared for r/AndroidAfterlife

**Title:** I upgraded an old Oppo A1k from Android 9 to Android 11: the fixes that finally worked

I wanted to upgrade an old Oppo A1k rather than leave it sitting on Android 9. Mine is the CPH1923 with 2 GB of RAM and 32 GB of storage. Getting a working result took about twelve hours, so I wrote down the successful process for people with the same phone and original firmware.

It now runs Android 11 with normal colors, working Wi-Fi and Play Store. It is still a slow phone: changing Android does not replace the old processor, memory or storage. For me, this was about making it useful again.

The working release was Andy Yan's unofficial LineageOS 18.1 image, `lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz`, using the original Oppo kernel and hardware drivers. Android 14 started but its colors kept washing out; Android 12 did not finish starting. Android 11 with the fixes gave us the result I wanted.

The things the short tutorials missed were:

- MTKClient needed USB connection fixes on my Apple Silicon Mac.
- The phone has one `system` partition, but the working download uses the publisher's `b` image layout. Picking an A-only file just from the phone's partition description was not the right choice here.
- Android needed a missing SELinux permission and a fix for the old Oppo encryption software before startup would finish. Repeating the data wipe did not solve those problems.
- Wi-Fi was trying to change a saved WPA2 connection into WPA3, which the old phone's Wi-Fi software could not handle. The fix keeps WPA2 on a mixed WPA2/WPA3 network; it does not add WPA3-only support.

The order that worked was: check the exact phone and firmware, back up its original software, unlock it, build the specified Android 11 image with all the fixes, install and verify it, clear the old setup, then finish Android setup and update the apps. The first installation erases personal data. The guide includes the exact commands, button sequence, checks and recovery steps; this summary is not enough to flash from.

[Complete guide and build tools](https://github.com/itsdanielsultan/oppo-a1k-lineageos-18.1)

I also built in a smaller interface, system touch vibration off with supported tap sounds on, and new default wallpapers. I updated 16 Google packages through Play Store and included those in my personal image. The public download contains the fixes and tools, not a finished ROM containing Google app files; it explains how to make that version locally.

This was tested on one CPH1923 with specific firmware. Android's security patch is still January 2024, and calls, VoLTE, GPS, Bluetooth audio, every camera mode and payment apps have not had a complete test. I have not repeated the complete installation with the packaged public tools or factory-reset the finished setup; the wallpaper helper was tested separately. The guide was prepared with Codex and checked against the phone's logs, full system readbacks and actual behavior.

Has anyone else upgraded this model? I'd be interested in whether your original firmware matches the one in the guide.

## Facts for the owner to use when writing an XDA announcement

These notes are a reference for a human-written post, not text to submit as an AI-generated announcement:

- Goal: make an old Oppo A1k useful again by moving from Android 9 to Android 11.
- Tested phone: CPH1923, board `oppo6762_18540`, reported platform `mt6765`, MTKClient hardware code `0x766`, 2 GB RAM / 32 GB storage.
- Original driver interface: VNDK 28. Original Oppo 4.9.117-based kernel and hardware-driver files retained.
- Working image: `lineage-18.1-20240121-UNOFFICIAL-arm64_bgS.img.xz`.
- Computer: Apple Silicon Mac. Tested MTKClient revision: `cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3`.
- Needed fixes: macOS USB connection, ordered `sigcont` permission, all four VNDK28 Keymaster wrappers, unsafe USB diagnostic branch excluded, automatic WPA2-to-WPA3 promotion disabled.
- Result: Android 11 boots, normal colors, mixed-mode Wi-Fi through WPA2, official Google Play sign-in/updates, smaller layout, system touch defaults and wallpapers built into the system.
- Google apps: 16 updates included privately; public toolkit explains local integration and does not mirror the app files.
- Limits: one exact phone/firmware; initial data erase; January 2024 OS patch; no second complete installation with the public wrapper; no full factory reset of the finished setup; many radio/camera/payment features not comprehensively checked.
- Evidence: complete final system readback matched; wallpaper initializer separately tested with empty and existing settings; exact firmware hashes and redacted logs in the repository.
- Guide: https://github.com/itsdanielsultan/oppo-a1k-lineageos-18.1
- Credit: Andy Yan, LineageOS, AOSP, PHH/TrebleDroid, MTKClient and SELinuxProject.

Keep private firmware dumps, serial numbers, account information and unredacted logs out of any public report.
