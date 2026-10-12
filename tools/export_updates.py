"""Export updated system apps from your own phone for a private local ROM build."""
from pathlib import Path
import argparse,json,re,subprocess
from image_utils import digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--serial',required=True);p.add_argument('--output',required=True,type=Path);p.add_argument('--apksigner',required=True,type=Path);a=p.parse_args()
    if a.output.exists():raise RuntimeError('Use a new export directory; preserve any prior snapshot')
    a.output.mkdir(parents=True);adb=['adb','-s',a.serial]
    def sh(*args):return subprocess.check_output(adb+['shell',*args],text=True).strip()
    if sh('getprop','ro.build.version.sdk')!='30':raise RuntimeError('This export is validated for Android 11 only')
    rows=[]
    for line in sh('pm','list','packages','-s').splitlines():
        package=line.removeprefix('package:')
        if not package.startswith(('com.google.','com.android.')):continue
        dump=sh('dumpsys','package',package);first=dump.split('Hidden system packages:')[0]
        if 'UPDATED_SYSTEM_APP' not in first:continue
        targets=re.findall(r'codePath=(/system/product/(?:app|priv-app)/[^\s]+)',dump)
        code=re.search(r'versionCode=(\d+) minSdk=(\d+)',first);version=re.search(r'versionName=(.*)',first)
        paths=[s.removeprefix('package:') for s in sh('pm','path',package).splitlines() if s.startswith('package:')]
        if not targets or not paths or not paths[0].startswith('/data/app/'):continue
        if not code or int(code[2])>30:raise RuntimeError('Incompatible update: '+package)
        local=a.output/package;local.mkdir();files=[];signers=[]
        for remote in paths:
            q=local/Path(remote).name;subprocess.run(adb+['pull',remote,str(q)],check=True)
            proof=subprocess.check_output([str(a.apksigner.resolve()),'verify','--verbose','--print-certs','--min-sdk-version','30',str(q)],text=True)
            (local/(q.name+'.signature.txt')).write_text(proof)
            certs=re.findall(r'certificate SHA-256 digest: (\w+)',proof);signers.append(certs)
            files.append(dict(name=q.name,bytes=q.stat().st_size,sha256=digest(q)))
        if not signers[0] or any(s!=signers[0] for s in signers):raise RuntimeError('Split signer mismatch: '+package)
        folder=str(Path(paths[0]).parent);r=subprocess.run(adb+['shell','find',folder+'/lib','-type','f'],capture_output=True,text=True);libs=[]
        if r.returncode and 'No such file or directory' not in r.stderr:raise RuntimeError(r.stderr)
        for remote in r.stdout.splitlines() if r.returncode==0 else []:
            if not remote.startswith(folder+'/lib/') or not remote.endswith('.so'):continue
            relative=Path(remote).relative_to(folder);q=local/relative;q.parent.mkdir(parents=True,exist_ok=True);subprocess.run(adb+['pull',remote,str(q)],check=True);libs.append(dict(name=str(relative),bytes=q.stat().st_size,sha256=digest(q)))
        # Static shared-library dependencies require separate capture, not guesswork.
        if re.search(r'usesStaticLibraries=\[[^\]]+',first):raise RuntimeError('Static shared libraries require additional export; see BUILD.md: '+package)
        rows.append(dict(package=package,target=targets[-1],version=version[1].strip(),version_code=int(code[1]),min_sdk=int(code[2]),files=files,native_libs=libs,signer_sha256=signers[0]))
    if not rows:raise RuntimeError('No updated system packages exported; do not call this an updated-ROM build')
    (a.output/'manifest.json').write_text(json.dumps(rows,indent=2));print('Exported',len(rows),'updated system packages. Keep this directory private.')
if __name__=='__main__':main()
