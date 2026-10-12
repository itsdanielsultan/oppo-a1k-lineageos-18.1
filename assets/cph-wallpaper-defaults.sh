#!/system/bin/sh
# Initialize reset defaults before zygote starts; never replace a user's choices.
src=/system/etc/cph-wallpaper-defaults
dst=/data/system/users/0
if [ "$1" = --test ]; then
    case "$2" in /data/local/tmp/cph-wallpaper-test-*) dst="$2";; *) exit 2;; esac
    case "$3" in /data/local/tmp/cph-wallpaper-test-*) src="$3";; *) exit 2;; esac
elif [ -n "$1" ]; then
    exit 2
fi

for name in wallpaper_info.xml wallpaper_info.xml.tmp wallpaper_orig wallpaper wallpaper_lock_orig wallpaper_lock; do
    if [ -e "$dst/$name" ]; then
        [ "$1" = --test ] || setprop sys.phh.wallpaper_defaults preserved
        echo 'Existing wallpaper choices preserved'
        exit 0
    fi
done
for name in wallpaper_orig wallpaper wallpaper_lock_orig wallpaper_lock wallpaper_info.xml; do
    [ -s "$src/$name" ] || exit 1
done

# Existing user directories keep their ownership and permissions.
if [ ! -d "$dst" ]; then
    mkdir -p "$dst" || exit 1
    chown 1000:1000 "$dst" || exit 1
    chmod 0700 "$dst" || exit 1
    restorecon "$dst" || exit 1
fi
stage="$dst/.cph-wallpaper-seed"
mkdir "$stage" || exit 1
chmod 0700 "$stage"
for name in wallpaper_orig wallpaper wallpaper_lock_orig wallpaper_lock wallpaper_info.xml; do
    if ! cp "$src/$name" "$stage/$name"; then
        for cleanup in wallpaper_orig wallpaper wallpaper_lock_orig wallpaper_lock wallpaper_info.xml; do
            rm -f "$stage/$cleanup"
        done
        rmdir "$stage"
        exit 1
    fi
    chown 1000:1000 "$stage/$name" || exit 1
    chmod 0600 "$stage/$name" || exit 1
done
# Commit metadata last; Android's normal wallpaper service reads these files.
for name in wallpaper_orig wallpaper wallpaper_lock_orig wallpaper_lock wallpaper_info.xml; do
    mv "$stage/$name" "$dst/$name" || exit 1
    restorecon "$dst/$name" || exit 1
done
rmdir "$stage"
[ "$1" = --test ] || setprop sys.phh.wallpaper_defaults initialized
echo 'Home and lock wallpaper defaults initialized'
