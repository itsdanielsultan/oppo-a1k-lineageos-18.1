# Release contents, privacy and redistribution

## The public resource is a device-fix toolkit

The package contains documentation, source diffs, guarded Python/shell tools, two configuration-only overlay APKs with their sources, self-generated wallpapers/native crop assets, selected redacted evidence, and offline tests.

It does **not** contain Google's application APKs, a mirrored GApps-bearing system image, stock Oppo partition binaries, the owner's APK export, raw device logs, account databases, serial/IMEI, Wi-Fi identifiers, credentials or private signing keys.

The owner's final personally used raw image remains local. Its published SHA-256 identifies the observed tested result; it is not a download promise. The core builder lets a reader obtain the original upstream archive themselves and apply the documented fixes. Official app updates and optional incorporation are performed locally from that reader's phone/account.

## Why the exact final Google-bearing image is not mirrored

Google distinguishes AOSP from its proprietary apps. Its [Android Developers explanation](https://android-developers.googleblog.com/2009/09/note-on-google-apps-for-android.html) says those apps are not licensed for inclusion in developer-built system images; its [GMS page](https://www.android.com/intl/en_au/gms/) explains the separate licensing. The [Open GApps project](https://github.com/opengapps/opengapps#license) likewise distinguishes its open build system from the component licenses and restricts mirroring its prebuilt packages.

Downloading an update through an account does not give this project permission to redistribute that Google APK as part of a public ROM. This repository cannot grant such permission. The useful public contribution is therefore the reproducible device changes and process, not a renamed bundle of proprietary apps.

We also do not provide Oppo firmware binaries from the phone as public rescue downloads. The instructions use the reader's own device backups.

## The public and private version tables

The published table lists package/version/code/min-SDK information actually observed on the final phone. It omits private `/data/app` UUID paths, account identity and credentials. It records an October 12, 2026 offer to one account, including a beta-labeled Gboard; it does not imply those exact versions are the newest stable version for every account or in the future.

Native OS apps and the framework security patch remain the upstream Android 11 build. A Google-app version table is not a new Android security bulletin.

## Screenshots and images

The public artwork is labeled as generated wallpaper artwork, not a photograph taken by the Oppo or a representation of camera quality. Its native saved/cropped copies are the exact selected images in the wallpaper initializer.

The investigation had phone screenshots and a boot-stall photo. Some screens showed phone/account/network identifiers, notifications, installed personal apps or restoration state. Those are not automatically publishable just because a screenshot exists. This package uses the artwork and sanitized technical evidence; do not add raw screenshots/EXIF-bearing photos without reviewing them first.

## Hardware and software evidence boundaries

The final physical system was fully read back, the phone booted, and the live/default checks passed. An empty-directory reset-initialization test passed. A complete reset of the finished personal setup was not performed. The consolidated public wrapper is offline-tested but has not been used for a second cold install. Neither limitation should disappear in a Reddit/XDA announcement.

## Release integrity

The toolkit ZIP and its checksum should be uploaded as release assets, not a several-gigabyte image committed to Git. GitHub's [release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) currently limits each release file to under 2 GiB. The small toolkit avoids that limit and the licensing problem.

For every local image build, retain its own generated receipt and hash. For every phone write, retain the private full readback and completion result. Source reproducibility, a successful write and a successful physical boot are separate pieces of evidence.
