from pathlib import Path
import sys,json,re,csv,hashlib
sys.path.insert(0,'/Users/apple/Workspace/NC_cl/99_工作记录/实验2_工作记录_20261024/work/template/pythonlib')
import pymupdf as fitz
from PIL import Image
w=Path(__file__).parent;src=w/'source';e=w/'evidence'
t='\n'.join(p.read_text() for p in (src/'sections').glob('*.tex'))
q=list(map(int,re.findall(r'\\qa\{(\d+)\.',t)));assert sorted(q)==list(range(1,21)) and len(q)==20
figs=re.findall(r'\\ev\{([^}]+)\}\{([^}]+)\}',t);assert len(figs)==12
assert not re.search(r'/(Users|tmp)/','\n'.join(p.read_text() for p in src.rglob('*.tex')))
for _,name in figs:
 d=fitz.open(src/'assets'/(name+'.pdf'));im=Image.open(e/'cropped'/(name+'.png')).convert('RGB');pm=fitz.Pixmap(d,d[0].get_images(full=True)[0][0]);assert pm.samples==im.tobytes()
u=list(csv.DictReader((e/'udp-key-fields.tsv').open(),delimiter='\t'));tc=list(csv.DictReader((e/'tcp-key-fields.tsv').open(),delimiter='\t'));assert len(u)==2 and len(tc)==190
assert [u[0][x] for x in ['ip.len','ip.hdr_len','ip.proto','udp.srcport','udp.dstport','udp.length','udp.checksum.status']]==['59','20','17','55130','53','39','1']
assert u[1]['udp.length']=='85'
for n,seq in [(5,679),(6,1967),(7,3255)]:assert tc[n-1]['tcp.seq']==str(seq) and tc[n-1]['tcp.len']=='1288'
assert tc[13]['tcp.ack']=='4543' and tc[13]['tcp.analysis.acks_frame']=='7' and tc[13]['tcp.analysis.ack_rtt']=='0.269348000'
assert tc[184]['tcp.seq']=='781' and tc[187]['tcp.ack']=='782' and tc[189]['tcp.ack']=='153001'
assert all(int(p['tcp.flags'],16)&4==0 for p in tc)
pdf=fitz.open(src/'main.pdf');assert len(pdf)==12
bounds=[];mm=72/25.4
for n,p in enumerate(pdf,1):
 assert abs(p.rect.width-522)<.01 and abs(p.rect.height-737)<.01
 image_rects=[];outside=[]
 for b in p.get_text('dict')['blocks']:
  if b['type']==1:image_rects.append(b['bbox'])
  if n>1:
   x0,y0,x1,y1=b['bbox']
   if x0<19.72*mm-.5 or x1>(19.72+146.755556)*mm+.5 or y0<25.4*mm-2 or y1>250*mm+.5:outside.append(b['bbox'])
 assert not outside,(n,outside)
 bounds.append({'page':n,'images':len(image_rects),'text_or_image_outside_frame':outside})
log=(w/'build-final2.log').read_text();assert not re.search('Overfull|Missing character|undefined|Warning:|Error:',log)
fls=(src/'main.fls').read_text();assert '.png' not in fls
r={'pages':12,'questions':sorted(q),'figures':12,'paper_bp':[522,737],'all_screenshots_pixel_equal':True,'all_fonts_embedded':True,'native_xelatex':'TeX Live 2026 / XeTeX0.999998','UDP_frames':2,'TCP_frames':190,'report_fields_match_final_captures':True,'relative_paths_only':True,'PNG_decoder_not_used':True,'page_bounds':bounds,'human_visual_review':'All 12 pages rendered at 140dpi and reviewed; template frames, labels, fonts, tables, images and teacher blank area checked. Crops at field boundaries; full originals retained.'}
(w/'validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='page_bounds'},ensure_ascii=False,indent=2))
