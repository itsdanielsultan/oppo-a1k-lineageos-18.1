import importlib.util,json,struct,tempfile,unittest,sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from image_utils import expand_sparse,digest
from device import Operation,PROFILE,lock_state

class SparseTests(unittest.TestCase):
    def test_raw_fill_skip(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);src=d/'in';out=d/'out'
            data=struct.pack('<I4H4I',0xed26ff3a,1,0,28,12,4096,3,3,0)
            data+=struct.pack('<2H2I',0xcac1,0,1,4108)+b'A'*4096
            data+=struct.pack('<2H2I',0xcac2,0,1,16)+b'1234'
            data+=struct.pack('<2H2I',0xcac3,0,1,12)
            src.write_bytes(data);expand_sparse(src,out)
            self.assertEqual(out.read_bytes(),b'A'*4096+b'1234'*1024+b'\0'*4096)
    def test_truncation_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'in';src.write_bytes(struct.pack('<I4H4I',0xed26ff3a,1,0,28,12,4096,1,1,0)+struct.pack('<2H2I',0xcac1,0,1,4108)+b'X')
            with self.assertRaises(ValueError):expand_sparse(src,Path(d)/'out')

class FakeDA:
    def __init__(self,layout,data,corrupt_new=False):self.layout=layout;self.data=data;self.formats=[];self.writes=[];self.corrupt_new=corrupt_new
    def name(self,addr):return next(n for n,p in self.layout.items() if p['offset']==addr)
    def readflash(self,addr,length,filename='',**kw):
        n=self.name(addr);b=self.data[n][:length]
        if self.corrupt_new and n=='system' and b.startswith(b'NEW'):b=b'BAD'+b[3:]
        if filename:Path(filename).write_bytes(b);return True
        return b
    def writeflash(self,addr,length,filename='',wdata=None,**kw):
        n=self.name(addr);b=Path(filename).read_bytes() if filename else wdata;self.writes.append(n);self.data[n]=b[:length];return True
    def formatflash(self,partitionname,**kw):self.formats.append(partitionname);return True

class DeviceTests(unittest.TestCase):
    def operation(self,d,corrupt=False):
        layout={n:dict(offset=i*100000,bytes=4096) for i,n in enumerate(['boot','system','vbmeta','seccfg','userdata','metadata','cache'])}
        cfg=struct.pack('<7I',0x4d4d4d4d,4,60,3,0,0,0x45454545)+b'\0'*(4096-28)
        vb=b'AVB0'+b'\0'*4092;old=b'OLD'+b'O'*4093;new=b'NEW'+b'N'*4093
        (d/'system-stock.bin').write_bytes(old);(d/'vbmeta-stock.bin').write_bytes(vb);img=d/'new.img';img.write_bytes(new)
        rec=d/'new.json';rec.write_text(json.dumps(dict(sha256=digest(img),bytes=4096,filesystem_validated=True)))
        da=FakeDA(layout,dict(boot=b'B'*4096,system=old,vbmeta=vb,seccfg=cfg,userdata=b'U'*4096,metadata=b'M'*4096,cache=b'C'*4096),corrupt)
        op=Operation.__new__(Operation);op.w=d;op.layout=layout;op.mtk=SimpleNamespace(daloader=da);op.result=dict(verified=False,userdata_erased=False)
        op.args=SimpleNamespace(action='flash',image=img,receipt=rec,erase_confirmation='ERASE MY CPH1923 DATA');op.load_backups=lambda:None
        def patch(meta,flags):out=bytearray(meta);out[0x78:0x7c]=flags.to_bytes(4,'big');return bytes(out)
        op.patcher=patch;return op,da
    def test_erase_only_after_full_readback(self):
        with tempfile.TemporaryDirectory() as d:
            op,da=self.operation(Path(d));op.flash();self.assertTrue(op.result['verified']);self.assertEqual(da.formats,['userdata','metadata','cache']);self.assertEqual(da.writes,['vbmeta','system'])
    def test_readback_failure_rolls_back_before_erasure(self):
        with tempfile.TemporaryDirectory() as d:
            op,da=self.operation(Path(d),True)
            with self.assertRaises(RuntimeError):op.flash()
            self.assertEqual(da.formats,[]);self.assertTrue(da.data['system'].startswith(b'OLD'));self.assertTrue(op.result['system_and_vbmeta_restored'])
    def test_missing_erase_confirmation_no_write(self):
        with tempfile.TemporaryDirectory() as d:
            op,da=self.operation(Path(d));op.args.erase_confirmation=''
            with self.assertRaises(RuntimeError):op.flash()
            self.assertEqual(da.writes,[]);self.assertEqual(da.formats,[])
    def test_bad_receipt_no_write(self):
        with tempfile.TemporaryDirectory() as d:
            op,da=self.operation(Path(d));op.args.image.write_bytes(b'changed')
            with self.assertRaises(RuntimeError):op.flash()
            self.assertEqual(da.writes,[])
    def test_data_preserving_update(self):
        with tempfile.TemporaryDirectory() as d:
            op,da=self.operation(Path(d));op.args.action='update';op.args.prior_image=op.w/'system-stock.bin';op.flash();self.assertEqual(da.formats,[]);self.assertFalse(op.result['userdata_erased'])
    def test_unexpected_chip_never_writes(self):
        da=SimpleNamespace(get_gpt=lambda:(b'',SimpleNamespace(partentries=[])))
        with tempfile.TemporaryDirectory() as d:
            mtk=SimpleNamespace(config=SimpleNamespace(hwcode=0,pagesize=512),daloader=da)
            with self.assertRaises(RuntimeError):Operation(mtk,SimpleNamespace(workspace=Path(d)),lambda x,y:x)
    def test_seccfg_unknown_format_rejected(self):
        with self.assertRaises(RuntimeError):lock_state(b'X'*512)

if __name__=='__main__':unittest.main()
