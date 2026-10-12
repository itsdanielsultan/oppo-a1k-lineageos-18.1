"""CPH1923-only MTKClient workflow, derived from the session's guarded operations.

The public orchestration is refactored and offline-tested; do not describe it as a
second end-to-end hardware install. No operation starts while printing --help.
"""
from pathlib import Path
import argparse,hashlib,json,os,struct,sys
from image_utils import digest

ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'evidence/tested-profile.json').read_text())
BACKUPS=['seccfg','lk','lk2','boot','vbmeta','dtbo','recovery','vendor','system']

def lock_state(data):
    if len(data)<512:raise RuntimeError('Incomplete seccfg')
    magic,version,size,lock,verity,runtime,end=struct.unpack('<7I',data[:28])
    if magic!=0x4d4d4d4d or version!=4 or end!=0x45454545 or lock not in (1,3) or not 60<=size<=len(data):raise RuntimeError('Untested seccfg structure')
    return lock

class Operation:
    def __init__(self,mtk,args,patcher):
        self.mtk=mtk;self.args=args;self.patcher=patcher;self.w=args.workspace.resolve();self.w.mkdir(parents=True,exist_ok=True)
        _,gpt=mtk.daloader.get_gpt()
        if mtk.config.hwcode!=PROFILE['chip_code'] or not gpt:raise RuntimeError('Untested chip/GPT')
        self.layout={p.name:dict(offset=p.sector*mtk.config.pagesize,bytes=p.sectors*mtk.config.pagesize) for p in gpt.partentries}
        if self.layout!=PROFILE['partitions']:raise RuntimeError('GPT differs from tested profile. Do not edit the guard to force a flash.')
        boot=self.read_bytes('boot')
        if hashlib.sha256(boot).hexdigest()!=PROFILE['stock_boot_sha256']:raise RuntimeError('Untested stock boot image')
        self.result=dict(action=args.action,chip=mtk.config.hwcode,userdata_erased=False,verified=False)
        if args.action in ('unlock','flash','update','restore'):
            vendor=self.w/(args.action+'-vendor-confirmation.bin');self.read_file('vendor',vendor)
            if digest(vendor)!=PROFILE['stock_vendor_sha256']:raise RuntimeError('Connected vendor image differs; no write attempted')
    def read_bytes(self,name):
        p=self.layout[name];data=self.mtk.daloader.readflash(addr=p['offset'],length=p['bytes'],filename='',parttype='user',display=False)
        if not isinstance(data,(bytes,bytearray)) or len(data)!=p['bytes']:raise RuntimeError('Incomplete read: '+name)
        return bytes(data)
    def read_file(self,name,dest,length=None):
        p=self.layout[name];n=p['bytes'] if length is None else length;dest=Path(dest)
        if dest.exists():raise RuntimeError('Refusing to overwrite '+str(dest))
        if not self.mtk.daloader.readflash(addr=p['offset'],length=n,filename=str(dest),parttype='user',display=True) or not dest.is_file() or dest.stat().st_size!=n:raise RuntimeError('Read failed: '+name)
    def write_file(self,name,path):
        p=self.layout[name];path=Path(path)
        if path.stat().st_size>p['bytes']:raise RuntimeError('Image exceeds '+name)
        if not self.mtk.daloader.writeflash(addr=p['offset'],length=path.stat().st_size,filename=str(path),parttype='user',display=True):raise RuntimeError('Write failed: '+name)
    def write_bytes(self,name,data):
        p=self.layout[name]
        if len(data)>p['bytes']:raise RuntimeError('Data exceeds partition')
        if not self.mtk.daloader.writeflash(addr=p['offset'],length=len(data),wdata=data,parttype='user',display=True):raise RuntimeError('Write failed: '+name)
        if self.read_bytes(name)!=data:raise RuntimeError('Full byte readback failed: '+name)
    def checked_backup(self):
        manifest=self.w/'backup-manifest.json'
        if manifest.exists():raise RuntimeError('Backup manifest already exists; use a fresh private workspace')
        rows={}
        for name in BACKUPS:
            p=self.w/(name+'-stock.bin');self.read_file(name,p)
            second=self.w/(name+'-second-read.bin');self.read_file(name,second)
            if digest(p)!=digest(second):raise RuntimeError('Independent backup checksum failed: '+name)
            second.unlink();rows[name]=dict(file=p.name,bytes=p.stat().st_size,sha256=digest(p))
        if rows['vendor']['sha256']!=PROFILE['stock_vendor_sha256'] or rows['system']['sha256']!=PROFILE['stock_system_sha256']:raise RuntimeError('Backed-up firmware differs from tested stock configuration; no write was attempted')
        manifest.write_text(json.dumps(dict(profile=PROFILE,partitions=rows),indent=2));self.result['verified']=True
    def load_backups(self):
        rows=json.loads((self.w/'backup-manifest.json').read_text())['partitions']
        for name,row in rows.items():
            p=self.w/row['file']
            if p.stat().st_size!=row['bytes'] or digest(p)!=row['sha256']:raise RuntimeError('Backup changed: '+name)
        if rows['vendor']['sha256']!=PROFILE['stock_vendor_sha256']:raise RuntimeError('Untested backup vendor')
        return rows
    def unlock(self):
        self.load_backups();before=self.read_bytes('seccfg')
        if lock_state(before)!=1 or before!=(self.w/'seccfg-stock.bin').read_bytes():raise RuntimeError('Locked state differs from own verified backup')
        ok,msg=self.mtk.daloader.seccfg('unlock',critical=False)
        if not ok:raise RuntimeError(str(msg))
        after=self.read_bytes('seccfg')
        if lock_state(after)!=3:raise RuntimeError('Unlock readback remains locked')
        (self.w/'seccfg-unlocked.bin').write_bytes(after);self.result['verified']=True
    def full_verify(self,name,path,out):
        self.read_file(name,out,Path(path).stat().st_size)
        if digest(out)!=digest(path):raise RuntimeError('Full image readback mismatch: '+name)
    def rollback(self,old_image,old_vbmeta):
        self.write_file('system',old_image);self.full_verify('system',old_image,self.w/'rollback-system-readback.bin');self.write_bytes('vbmeta',old_vbmeta)
        self.result['system_and_vbmeta_restored']=True
    def flash(self):
        self.load_backups()
        if lock_state(self.read_bytes('seccfg'))!=3:raise RuntimeError('Bootloader is not unlocked')
        image=self.args.image.resolve();receipt=json.loads(self.args.receipt.read_text())
        if digest(image)!=receipt['sha256'] or image.stat().st_size!=receipt['bytes'] or not receipt['filesystem_validated']:raise RuntimeError('Image/receipt mismatch')
        if self.args.action=='flash':
            if self.args.erase_confirmation!='ERASE MY CPH1923 DATA':raise RuntimeError('Initial flash requires explicit data-erasure confirmation')
            old=self.w/'system-stock.bin';old_meta=(self.w/'vbmeta-stock.bin').read_bytes()
            # Confirm the connected phone still has the exact saved current system.
            before=self.w/'before-flash-system.bin';self.full_verify('system',old,before)
        else:
            old=self.args.prior_image.resolve();before=self.w/'before-update-system.bin';self.full_verify('system',old,before);old_meta=self.read_bytes('vbmeta')
        if old_meta[:4]!=b'AVB0':raise RuntimeError('Unrecognized verification metadata')
        patched=self.patcher(old_meta,3)
        if patched is None or int.from_bytes(patched[0x78:0x7c],'big')!=3:raise RuntimeError('vbmeta preparation failed')
        attempted=False
        try:
            attempted=True;self.write_bytes('vbmeta',patched);self.write_file('system',image);self.full_verify('system',image,self.w/'system-flash-readback.bin')
            self.result['system_sha256']=digest(image)
            if self.args.action=='flash':
                self.result['erasure_started']=True
                for name in ['userdata','metadata','cache']:
                    p=self.layout[name]
                    if not self.mtk.daloader.formatflash(addr=p['offset'],length=p['bytes'],partitionname=name,parttype='user',display=True):raise RuntimeError('Approved format failed: '+name)
                    self.result.setdefault('cleared_partitions',[]).append(name)
                    if name=='userdata':self.result['userdata_erased']=True
            self.result['verified']=True
        except Exception:
            if attempted:self.rollback(old,old_meta)
            raise
    def restore(self):
        self.load_backups()
        if self.args.erase_confirmation!='ERASE MY CPH1923 DATA':raise RuntimeError('Returning to stock needs explicit reset consent')
        self.write_file('system',self.w/'system-stock.bin');self.full_verify('system',self.w/'system-stock.bin',self.w/'stock-restoration-readback.bin');self.write_bytes('vbmeta',(self.w/'vbmeta-stock.bin').read_bytes())
        self.result['erasure_started']=True
        for name in ['userdata','metadata','cache']:
            p=self.layout[name]
            if not self.mtk.daloader.formatflash(addr=p['offset'],length=p['bytes'],partitionname=name,parttype='user',display=True):raise RuntimeError('Stock reset failed: '+name)
            if name=='userdata':self.result['userdata_erased']=True
        self.result['verified']=True
    def logs(self):
        for name in ['expdb','para','cache']:self.read_file(name,self.w/(name+'-diagnostic.bin'))
        self.result['verified']=True

def arguments():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['backup','unlock','flash','update','restore','logs']);p.add_argument('--workspace',required=True,type=Path);p.add_argument('--mtkclient',type=Path,default=ROOT/'work/mtkclient');p.add_argument('--image',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--prior-image',type=Path);p.add_argument('--erase-confirmation',default='');a=p.parse_args()
    if a.action in ('flash','update') and (not a.image or not a.receipt):p.error('flash/update require --image and --receipt')
    if a.action=='update' and not a.prior_image:p.error('update requires an exact --prior-image')
    if a.action in ('flash','restore') and a.erase_confirmation!='ERASE MY CPH1923 DATA':p.error('Use --erase-confirmation "ERASE MY CPH1923 DATA" only after backing up personal data')
    return a

def main():
    a=arguments();os.umask(0o077);a.workspace=a.workspace.resolve();a.mtkclient=a.mtkclient.resolve()
    if not (a.mtkclient/'mtkclient').is_dir():raise RuntimeError('Pinned MTKClient checkout missing; run setup first')
    sys.path.insert(0,str(a.mtkclient))
    from mtkclient.Library.DA.mtk_da_handler import DaHandler
    from mtkclient.mtk import main as mtk_main
    completed={'verified':False}
    def connect(self,mtk,directory=None):
        if not mtk.preloader.init(directory=directory or '.'):return None
        return mtk if mtk.config.target_config is not None else None
    def action(self,mtk,command,args):
        if command!='printgpt':raise RuntimeError('Unexpected MTK entry command')
        op=Operation(mtk,a,self.patch_vbmeta)
        try:
            {'backup':op.checked_backup,'unlock':op.unlock,'flash':op.flash,'update':op.flash,'restore':op.restore,'logs':op.logs}[a.action]()
            (op.w/(a.action+'-result.json')).write_text(json.dumps(op.result,indent=2));print('VERIFIED:',a.action,flush=True)
            completed['verified']=op.result['verified']
        except Exception as error:
            op.result['error']=str(error);(op.w/(a.action+'-result.json')).write_text(json.dumps(op.result,indent=2));raise
        finally:mtk.daloader.shutdown(bootmode=0)
    DaHandler.connect=connect;DaHandler.handle_da_cmds=action
    os.chdir(a.mtkclient);sys.argv=['mtk','printgpt'];mtk_main()
    if not completed['verified']:raise RuntimeError('No operation completed and verified; do not assume success')
if __name__=='__main__':main()
