"""Offline Android sparse/ext4 helpers. Never opens a phone or block device."""
from pathlib import Path
import hashlib,re,struct,subprocess

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while b:=f.read(8*1024*1024):h.update(b)
    return h.hexdigest()

def expand_sparse(src,dst):
    with Path(src).open('rb') as i,Path(dst).open('xb') as o:
        head=i.read(28)
        if len(head)!=28:raise ValueError('Incomplete sparse header')
        magic,major,minor,fhs,chs,block,total,chunks,crc=struct.unpack('<I4H4I',head)
        if magic!=0xed26ff3a or major!=1 or fhs<28 or chs<12 or block!=4096:raise ValueError('Unexpected sparse format')
        i.read(fhs-28);written=0
        for _ in range(chunks):
            raw=i.read(12)
            if len(raw)!=12:raise ValueError('Truncated chunk header')
            kind,res,n,size=struct.unpack('<2H2I',raw);i.read(chs-12)
            length=n*block;payload=size-chs
            if kind==0xcac1:
                if payload!=length:raise ValueError('Bad raw chunk length')
                remaining=length
                while remaining:
                    b=i.read(min(8*1024*1024,remaining))
                    if not b:raise ValueError('Truncated raw chunk')
                    o.write(b);remaining-=len(b)
            elif kind==0xcac2:
                if payload!=4:raise ValueError('Bad fill chunk')
                fill=i.read(4)
                if len(fill)!=4:raise ValueError('Truncated fill chunk')
                b=fill*(2*1024*1024);remaining=length
                while remaining:z=min(remaining,len(b));o.write(b[:z]);remaining-=z
            elif kind==0xcac3:
                if payload:raise ValueError('Bad skip chunk')
                o.seek(length,1)
            elif kind==0xcac4:
                if payload!=4 or n:raise ValueError('Bad CRC chunk')
                if len(i.read(4))!=4:raise ValueError('Truncated CRC chunk')
            else:raise ValueError('Unknown sparse chunk')
            written+=n
        if written!=total or i.read(1):raise ValueError('Sparse extent totals differ')
        o.truncate(total*block)

def quote(s):
    s=str(s)
    if '\n' in s or '\r' in s:raise ValueError('Invalid debugfs path')
    return '"'+s.replace('\\','\\\\').replace('"','\\"')+'"'

class Ext4:
    def __init__(self,image,bin_dir,work):
        self.image=Path(image);self.debugfs=str(Path(bin_dir)/'debugfs');self.work=Path(work);self.work.mkdir(parents=True,exist_ok=True);self.serial=0
    def run(self,command,write=False):
        r=subprocess.run([self.debugfs,*(['-w'] if write else []),'-R',command,str(self.image)],capture_output=True,text=True,check=True)
        if re.search(r'File not found|Could not allocate|No space|already exists|while writing|Usage:',r.stderr,re.I):raise RuntimeError(r.stderr)
        return r.stdout
    def extract(self,target,dest):
        dest=Path(dest)
        if dest.exists():dest.unlink()
        self.run('dump '+quote(target)+' '+quote(dest))
        if not dest.is_file():raise RuntimeError('Extraction failed: '+target)
        return dest
    def metadata(self,target):
        s=self.run('stat '+quote(target));mode=re.search(r'Mode:\s+(\d+)',s);ug=re.search(r'User:\s+(\d+)\s+Group:\s+(\d+)',s)
        self.serial+=1;c=self.work/('context-'+str(self.serial));self.run('ea_get -f '+quote(c)+' '+quote(target)+' security.selinux')
        if not mode or not ug or not c.is_file():raise RuntimeError('Missing metadata: '+target)
        return ('010'+mode[1].zfill(4),int(ug[1]),int(ug[2]),c.read_bytes())
    def label(self,target,context):
        self.serial+=1;p=self.work/('label-'+str(self.serial));p.write_bytes(context if isinstance(context,bytes) else context.encode()+b'\0')
        self.run('ea_set -f '+quote(p)+' '+quote(target)+' security.selinux',True)
    def put(self,local,target,replace=False,mode='0100644',uid=0,gid=0,context='u:object_r:system_file:s0'):
        if replace:
            mode,uid,gid,context=self.metadata(target);self.run('rm '+quote(target),True)
        self.run('write '+quote(local)+' '+quote(target),True)
        for field,val in [('mode',mode),('uid',uid),('gid',gid)]:self.run('set_inode_field '+quote(target)+' '+field+' '+str(val),True)
        self.label(target,context)
        check=self.work/'file-readback';self.extract(target,check)
        if digest(check)!=digest(local):raise RuntimeError('Content mismatch: '+target)
    def mkdir(self,target,context='u:object_r:system_file:s0'):
        self.run('mkdir '+quote(target),True)
        for f,v in [('mode','040755'),('uid',0),('gid',0)]:self.run('set_inode_field '+quote(target)+' '+f+' '+str(v),True)
        self.label(target,context)

