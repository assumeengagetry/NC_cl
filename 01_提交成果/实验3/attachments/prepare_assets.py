from pathlib import Path
import sys,json
sys.path.insert(0,'/Users/apple/Workspace/NC_cl/99_工作记录/实验2_工作记录_20261024/work/template/pythonlib')
import pymupdf as fitz
from PIL import Image,ImageOps,ImageDraw
w=Path(__file__).parent
s=w/'evidence/screenshots';a=w/'source/assets';c=w/'evidence/cropped';c.mkdir(exist_ok=True)
spec={
'udp-header':('02-udp-request.png',(115,1125,1350,1483)),
'udp-bytes':('02-udp-request.png',(1365,505,2600,675)),
'udp-ip':('02-udp-request.png',(115,588,1350,1095)),
'udp-response':('03-udp-response.png',(115,1125,1350,1445)),
'upload-success':('11-upload-zoom.png',(112,145,2750,1010)),
'syn-detail':('04-tcp-syn.png',(115,690,1320,1745)),
'synack-detail':('05-tcp-synack.png',(115,1123,1320,1595)),
'ack-window':('06-tcp-ack.png',(115,944,1320,1305)),
'follow-stream':('09-follow-stream.png',(160,160,1740,1430)),
'data-detail':('07-tcp-data.png',(115,690,1320,1635)),
'data-list':('07-tcp-data.png',(110,260,2600,545)),
'rtt-detail':('08-tcp-rtt.png',(115,690,1320,1630)),
'release-list':('12-release-columns.png',(113,255,1320,550)),
}
manifest=[];thumbs=[]
for name,(original,box) in spec.items():
 im=Image.open(s/original).convert('RGB').crop(box);im.save(c/(name+'.png'))
 doc=fitz.open();p=doc.new_page(width=im.width/2,height=im.height/2);p.insert_image(p.rect,filename=str(c/(name+'.png')));doc.save(a/(name+'.pdf'),deflate=True);doc.close()
 manifest.append({'asset':name+'.pdf','original':original,'crop_pixels':box,'size':im.size,'operations':'rectangular crop only; lossless PDF image embedding'})
 thumb=im.copy();thumb.thumbnail((440,380));cv=Image.new('RGB',(460,420),'white');cv.paste(thumb,(10,25));ImageDraw.Draw(cv).text((10,5),name,fill='black');thumbs.append(cv)
(s/'crop-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
canvas=Image.new('RGB',(460*3,420*5),'#ccc')
for n,t in enumerate(thumbs):canvas.paste(t,((n%3)*460,(n//3)*420))
canvas.save(w/'assets-contact.png')
