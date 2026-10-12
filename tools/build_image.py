"""Build the tested core fixes locally from the pinned publisher GSI and own vendor backup."""
from pathlib import Path
import argparse,json,lzma,shutil,subprocess
from image_utils import Ext4,digest,expand_sparse

ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'evidence/tested-profile.json').read_text())
def main():
    p=argparse.ArgumentParser();p.add_argument('--publisher',required=True,type=Path);p.add_argument('--vendor',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--secilc',required=True,type=Path);p.add_argument('--e2fsprogs',type=Path,default=Path('/opt/homebrew/opt/e2fsprogs/sbin'));a=p.parse_args()
    for q in [a.publisher,a.vendor,a.output,a.secilc,a.e2fsprogs]:
        if '\n' in str(q):raise ValueError('Invalid path')
    assert digest(a.publisher)==PROFILE['publisher_sha256'],'Wrong upstream archive; no image produced'
    assert digest(a.vendor)==PROFILE['stock_vendor_sha256'],'Untested vendor firmware; stop and investigate'
    assert not a.output.exists(),'Do not overwrite a prepared image'
    work=a.output.resolve().parent/(a.output.name+'.build');work.mkdir(parents=True,exist_ok=False)
    sparse=work/'publisher.sparse.img'
    with lzma.open(a.publisher,'rb') as i,sparse.open('xb') as o:shutil.copyfileobj(i,o,8*1024*1024)
    expand_sparse(sparse,a.output)
    with a.output.open('r+b') as f:f.truncate(PROFILE['partitions']['system']['bytes'])
    subprocess.run([str(a.e2fsprogs/'resize2fs'),str(a.output)],check=True)
    r=subprocess.run([str(a.e2fsprogs/'e2fsck'),'-fy','-E','unshare_blocks',str(a.output)],capture_output=True,text=True)
    (work/'unshare.log').write_text(r.stdout+r.stderr);assert r.returncode in (0,1),'Filesystem unsharing failed'
    fs=Ext4(a.output,a.e2fsprogs,work/'ext4');vendor=Ext4(a.vendor,a.e2fsprogs,work/'vendor-extract')
    plat=fs.extract('/system/etc/selinux/plat_sepolicy.cil',work/'plat.cil')
    subprocess.run(['patch','--batch','--fuzz=0',str(plat),str(ROOT/'patches/selinux-sigcont.patch')],check=True)
    mapping=fs.extract('/system/etc/selinux/mapping/28.0.cil',work/'mapping28.cil')
    ext=fs.extract('/system/system_ext/etc/selinux/system_ext_sepolicy.cil',work/'system_ext.cil')
    vpub=vendor.extract('/etc/selinux/plat_pub_versioned.cil',work/'vendor_pub.cil')
    vc=vendor.extract('/etc/selinux/vendor_sepolicy.cil',work/'vendor.cil')
    # Same policy version and Android-init style CIL flags, including merged declarations.
    subprocess.run([str(a.secilc.resolve()),'-m','-M','true','-G','-N','-c','30',str(plat),str(mapping),str(ext),str(vpub),str(vc),'-o',str(work/'checked.policy'),'-f',str(work/'checked.contexts')],check=True)
    fs.put(plat,'/system/etc/selinux/plat_sepolicy.cil',replace=True)
    helper=fs.extract('/system/bin/rw-system.sh',work/'rw-system.sh')
    subprocess.run(['patch','--batch','--fuzz=0',str(helper),str(ROOT/'patches/rw-system.patch')],check=True)
    subprocess.run(['bash','-n',str(helper)],check=True)
    fs.put(helper,'/system/bin/rw-system.sh',replace=True)
    for name in ['OppoWifiCompat','OppoTouchDefaults']:
        dst='/system/product/overlay/'+name;fs.mkdir(dst);fs.put(ROOT/'assets'/(name+'.apk'),dst+'/'+name+'.apk',context='u:object_r:vendor_overlay_file:s0' if name=='OppoTouchDefaults' else 'u:object_r:system_file:s0')
    fs.mkdir('/system/etc/cph-wallpaper-defaults')
    for q in (ROOT/'assets/wallpaper-defaults').iterdir():
        if q.is_file():fs.put(q,'/system/etc/cph-wallpaper-defaults/'+q.name)
    fs.put(ROOT/'assets/cph-wallpaper-defaults.sh','/system/bin/cph-wallpaper-defaults.sh',mode='0100755',gid=2000,context='u:object_r:phhsu_exec:s0')
    fs.put(ROOT/'assets/cph-wallpaper-defaults.rc','/system/etc/init/cph-wallpaper-defaults.rc')
    r=subprocess.run([str(a.e2fsprogs/'e2fsck'),'-fn',str(a.output)],capture_output=True,text=True);(work/'final-filesystem.log').write_text(r.stdout+r.stderr);assert r.returncode==0,'Final filesystem validation failed'
    receipt=dict(image=str(a.output.resolve()),bytes=a.output.stat().st_size,sha256=digest(a.output),upstream_sha256=PROFILE['publisher_sha256'],vendor_sha256=PROFILE['stock_vendor_sha256'],filesystem_validated=True,policy_compiled=True,google_updates_integrated=False)
    a.output.with_suffix(a.output.suffix+'.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
