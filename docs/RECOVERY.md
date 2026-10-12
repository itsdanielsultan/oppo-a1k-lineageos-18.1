# Recovery: restore your own original software

Read this before the first installation. **Rollback** means restoring the previous system after a failed write. It depends on your verified backups and a working USB connection. It cannot recover personal data that has already been erased.

## Keep the original hardware software and make backups first

The tested phone retained stock preloader, LK, kernel, vendor, recovery, DTBO, TEE and radio/calibration partitions. Only the unlock configuration, custom-ROM vbmeta metadata and system image were changed for the main upgrade; the initial installation also cleared the three approved data partitions.

That boundary matters. The boot-ROM entry method remained available throughout. Do not replace boot/LK/preloader as an attempted fix for a system-image compatibility problem. Do not erase calibration, FRP, OTP, NVRAM/NV data, whole eMMC regions or the entire partition table.

Your rescue inputs must be **your own independently verified backups**. A matching model number is not permission to use somebody else's seccfg or calibration data. This repository contains hashes/profile information, not stock partition binaries or a borrowed scatter-package “rescue.”

## If the public flash tool reports a write or readback error

The guarded path attempts to restore the exact previous system and vbmeta using the private images already checked. It reads that restoration back. Keep USB attached while it is doing this. The result records `system_and_vbmeta_restored` only after the corresponding checks succeed.

If USB disconnects, rollback may be unable to run. The script cannot guarantee recovery through a physically missing connection. Re-enter the proven boot-ROM mode with one fresh listener and inspect the private result/log first.

Initial data formatting happens only after system verification. If formatting has begun, some or all user data may already be gone. Restoring firmware cannot restore erased personal data or recreate an old encryption key. The separate `erasure_started`, `userdata_erased` and cleared-partition fields exist to avoid describing a firmware rollback as a data recovery.

Do not delete a mismatching readback or modify a receipt to make the check pass. Preserve the file and investigate the discrepancy.

## Deliberate return to the original stock system

The source session had verified original ColorOS backups and prepared a restoration path, but the owner chose to continue to Android 11. **A completed post-restoration stock boot was not the final hardware result demonstrated here.** The public recovery command is a prepared, guarded route; do not label it a separately proven stock-restoration test.

Copy the original private backup set and manifest into a new private operation directory:

```sh
mkdir -p work/restore-device
cp work/device/*-stock.bin work/device/backup-manifest.json work/restore-device/
.venv/bin/python tools/device.py restore \
  --workspace work/restore-device \
  --erase-confirmation "ERASE MY CPH1923 DATA"
```

Enter boot ROM after the command is listening. This verifies the same stock kernel/vendor/GPT, writes and fully verifies the stock system, restores/verifies the original vbmeta, and performs the explicitly requested data reset for the Android-version return. It does not relock the bootloader or write the stock kernel over a foreign kernel. If your boot/vendor/GPT differs, it stops.

Do not run `restore` just because a tool close emitted a timeout after a successful flash. Do not run an abandoned “return to Android 14” script against a currently working Android 11 phone. This happened as a planned fallback in our investigation, and it was canceled before writes when the new working state was observed.

## Recovery menu versus boot ROM

The ColorOS recovery menu was useful to recognize a failed boot and, during the already approved failed setup, to try a full data format. Repeating that format did not fix the missing compatibility changes. It is not the interface used by the guarded MTKClient writer.

For BROM, start a single listener, keep USB connected, hold both volume buttons and Power until reset, release Power, hold both volume buttons for approximately 20 seconds, release them, and require tool detection. For normal boot after the operation has finished, unplug USB, release volume buttons, hold Power and reconnect USB.

There was no validated fastboot rescue, no tested custom recovery installation, no opened-phone/test-point procedure, and no vendor-wide guarantee. The purpose of keeping the hardware firmware untouched and verifying backups is to avoid needing those untested routes.

## If a profile guard rejects your phone

Stop. Collect only the non-identifying configuration needed to compare: model/board/platform, original Android/VNDK, stock boot/vendor hashes, and the measured partition layout. Do not publish serial/IMEI/account data or raw calibration/partition dumps. A different build needs a separately checked policy/Keymaster/graphics assessment. Editing a hash constant to silence the guard is not that assessment.
