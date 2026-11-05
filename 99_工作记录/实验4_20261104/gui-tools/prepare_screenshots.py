from pathlib import Path
import shutil, hashlib, json
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
W=Path(__file__).resolve().parent.parent
S=W/'evidence/screenshots';O=S/'originals';O.mkdir(exist_ok=True)
DEBUG=W/'gui-tools/debug';DEBUG.mkdir(exist_ok=True)
selected=['01-ping-request','02-ping-reply','03-large-first','04-large-reassembly','05-ttl3-request','06-ttl3-outer','07-ttl3-quote','08-trace-probe','09-trace-third-probe','10-trace-error-outer','11-trace-error','12-trace-final','13-trace-list','14-ttl4-request','15-ttl4-reply','16-ttl2-list','17-ttl1-list','18-ping-commands','19-ttl12-commands','20-ttl34-commands','21-trace-command']
for p in list(S.glob('*.png')):
 if p.stem in selected: shutil.move(p,O/p.name)
 else: shutil.move(p,DEBUG/p.name)
C={
 'ping-request':('01-ping-request',(0,105,1260,1230)),
 'ping-reply':('02-ping-reply',(0,105,1260,1265)),
 'large-first':('03-large-first',(0,105,1260,905)),
 'large-reassembly':('04-large-reassembly',(0,105,1260,1440)),
 'ttl3-request':('05-ttl3-request',(0,105,1260,1120)),
 'ttl3-outer':('06-ttl3-outer',(0,105,1260,975)),
 'ttl3':('07-ttl3-quote',(0,105,1260,1300)),
 'trace-probe':('08-trace-probe',(0,105,1260,1190)),
 'trace-third-probe':('09-trace-third-probe',(0,105,1260,1190)),
 'trace-error-outer':('10-trace-error-outer',(0,105,1260,975)),
 'trace-error':('11-trace-error',(0,105,1260,1405)),
 'trace-final':('12-trace-final',(0,105,1260,1160)),
 'trace-list':('13-trace-list',(0,105,2510,835)),
 'ttl4-request':('14-ttl4-request',(0,180,1260,720)),
 'ttl4-reply':('15-ttl4-reply',(0,105,1260,1140)),
 'ttl2-list':('16-ttl2-list',(0,105,2510,330)),
 'ttl1-list':('17-ttl1-list',(0,105,2510,330)),
 'ping-time':('18-ping-commands',(0,140,1180,760)),
 'large-command':('18-ping-commands',(0,780,1180,1375)),
 'ttl-commands':('19-ttl12-commands',(0,140,1180,1200)),
 'ttl34-commands':('20-ttl34-commands',(0,140,1180,1305)),
 'trace-command':('21-trace-command',(0,140,1180,590)),
}
A=W/'source/assets';old=W/'gui-tools/old-typeset-assets';old.mkdir(exist_ok=True)
for p in A.glob('*.pdf'):shutil.copy2(p,old/p.name)
records=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,(orig,box) in C.items():
 p=O/(orig+'.png');im=Image.open(p);im.crop(box).save(S/(name+'.png'))
 png=S/(name+'.png');crop=Image.open(png).convert('RGB')
 pdf=A/(name+'.pdf')
 if name not in ['ttl1-list','ttl2-list']:
  cv=canvas.Canvas(str(pdf),pagesize=crop.size,pageCompression=1,invariant=1)
  cv.drawImage(ImageReader(crop),0,0,width=crop.width,height=crop.height)
  cv.showPage();cv.save()
 records.append({'asset':name,'original':'originals/'+p.name,'original_sha256':sha(p),'original_size':list(im.size),'crop_box_pixels':list(box),'cropped_png':png.name,'cropped_sha256':sha(png),'crop_size':list(crop.size),'software':'Terminal (saved measurement log replay)' if int(orig[:2])>=18 else 'Wireshark 4.6.7','capture_method':'macOS screencapture -x -o -l <observed window ID>','editing':'Rectangular crop only; no pixel content replaced.'})
(S/'crop-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps([{'asset':r['asset'],'size':r['crop_size']} for r in records],indent=2))
