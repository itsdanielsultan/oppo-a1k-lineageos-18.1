#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v brew >/dev/null || { echo 'Install Homebrew from https://brew.sh first.'; exit 1; }
xcode-select -p >/dev/null || { echo 'Install Apple Command Line Tools first: xcode-select --install'; exit 1; }
brew install uv libusb e2fsprogs libsepol android-platform-tools
mkdir -p work/tools
uv python install 3.12.12
uv venv --python 3.12.12 .venv
if [ ! -d work/mtkclient/.git ]; then git clone https://github.com/bkerler/mtkclient.git work/mtkclient; fi
git -C work/mtkclient checkout cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3
if git -C work/mtkclient apply --check ../../patches/mtkclient-darwin-usb.patch; then
    git -C work/mtkclient apply ../../patches/mtkclient-darwin-usb.patch
else
    git -C work/mtkclient apply --reverse --check ../../patches/mtkclient-darwin-usb.patch
fi
uv pip install --python .venv/bin/python pyusb==1.3.1 pycryptodome==3.24.1 pycryptodomex==3.24.1 colorama==0.4.6 pyserial==3.5
# The tested command-line environment did not require Qt or FUSE mounting.
uv pip install --python .venv/bin/python --no-deps -e work/mtkclient
if [ ! -d work/selinux/.git ]; then git clone https://github.com/SELinuxProject/selinux.git work/selinux; fi
git -C work/selinux checkout 2233a23a4d4f1bf29054037babec13f30d038e65
sepol_prefix="$(brew --prefix libsepol)"
clang -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -I"$sepol_prefix/include" -L"$sepol_prefix/lib" work/selinux/secilc/secilc.c -lsepol -o work/tools/secilc
echo 'Setup complete. Use .venv/bin/python tools/device.py --help; backups stay in ignored work/.'
