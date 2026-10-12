"""Integrate a private, signature-checked export into an unshared core ext4 image."""
from pathlib import Path
import argparse,json,re,subprocess
from image_utils import Ext4,digest

def remove_tree(fs,target):
    for line in fs.run('ls -p '+target).splitlines():
        bits=line.split('/')
        if len(bits)<7 or bits[1]=='0' or bits[5] in ('.','..'):continue
        child=target+'/'+bits[5];mode=int(bits[2],8)
        if mode&0o170000==0o040000:remove_tree(fs,child);fs.run('rmdir '+child,True)
        else:fs.run('rm '+child,True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',required=True,type=Path);p.add_argument('--base-receipt',required=True,type=Path);p.add_argument('--export',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--e2fsprogs',type=Path,default=Path('/opt/homebrew/opt/e2fsprogs/sbin'));a=p.parse_args()
    receipt=json.loads(a.base_receipt.read_text());assert digest(a.base)==receipt['sha256'] and receipt['filesystem_validated'],'Unverified base'
    assert not a.output.exists(),'Output exists';rows=json.loads((a.export/'manifest.json').read_text());assert rows
    # Integrity and path checks happen before changing the local image.
    for r in rows:
        assert re.fullmatch(r'com\.(?:google|android)\.[A-Za-z0-9_.]+',r['package'])
        assert re.fullmatch(r'/system/product/(?:app|priv-app)/[A-Za-z0-9_]+',r['target']) and r['min_sdk']<=30
        for f in r['files']+r['native_libs']:
            rel=Path(f['name']);assert not rel.is_absolute() and '..' not in rel.parts
            assert digest(a.export/r['package']/rel)==f['sha256']
    subprocess.run(['cp','-c',str(a.base),str(a.output)],check=True)
    work=a.output.resolve().parent/(a.output.name+'.build');fs=Ext4(a.output,a.e2fsprogs,work)
    # The core builder already removed shared_blocks; never use this on the original GSI.
    if 'shared_blocks' in fs.run('stats'):raise RuntimeError('Base still has shared data blocks')
    for r in rows:
        target=r['target'];remove_tree(fs,target);fs.run('rmdir '+target,True);fs.mkdir(target)
        for f in r['files']:fs.put(a.export/r['package']/f['name'],target+'/'+f['name'])
        dirs=set()
        for f in r['native_libs']:
            rel=Path(f['name']);assert str(rel).startswith('lib/')
            for i in range(1,len(rel.parts)):
                name=target+'/'+str(Path(*rel.parts[:i]))
                if name not in dirs:fs.mkdir(name);dirs.add(name)
            fs.put(a.export/r['package']/rel,target+'/'+str(rel))
    r=subprocess.run([str(a.e2fsprogs/'e2fsck'),'-fn',str(a.output)],capture_output=True,text=True);(work/'final-filesystem.log').write_text(r.stdout+r.stderr);assert r.returncode==0,'Updated image filesystem failed'
    out=dict(image=str(a.output.resolve()),bytes=a.output.stat().st_size,sha256=digest(a.output),filesystem_validated=True,google_updates_integrated=True,packages=[{k:r[k] for k in ['package','version','version_code','min_sdk','target']} for r in rows])
    a.output.with_suffix(a.output.suffix+'.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
