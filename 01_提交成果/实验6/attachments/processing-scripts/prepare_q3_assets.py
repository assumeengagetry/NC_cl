from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(__file__).parent;src=root/'evidence';out=root/'assets_prepared/q3';out.mkdir(parents=True,exist_ok=True)
items=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(name,boxes,caption,source_name=None):
 p=src/((source_name or name)+'.png')
 if not p.exists():return
 im=Image.open(p).convert('RGB');crops=[im.crop(b) for b in boxes]
 if len(crops)==1:result=crops[0];method='continuous_rectangle_crop'
 else:
  gap=12;result=Image.new('RGB',(max(c.width for c in crops),sum(c.height for c in crops)+gap*(len(crops)-1)),(245,245,245));d=ImageDraw.Draw(result);y=0
  for i,c in enumerate(crops):
   result.paste(c,(0,y));y+=c.height
   if i<len(crops)-1:
    for x in range(0,result.width,12):d.line((x,y+gap//2,min(x+6,result.width),y+gap//2),fill=(125,125,125),width=1)
    y+=gap
  method='same_source_separated_title_hostname_interface_regions_with_disclosed_gaps'
 target=out/(name+'.png');result.save(target)
 items.append(dict(file=str(target.relative_to(root)),source=str(p.relative_to(root)),source_sha256=sha(p),output_sha256=sha(target),source_size=list(im.size),output_size=list(result.size),method=method,crop_boxes_xyxy=boxes,caption=caption))
for n,host,yy in [(3,'Branch1',1343),(4,'HQ',1183),(5,'Branch2',1343)]:
 yname=540 if n==4 else 700
 add(f'q3-router{n}-config',[(1400,0,1850,55),(50,yname,500,yname+21),(50,yy,500,yy+325)],f'题3 Router{n}（{host}）四接口实际地址及掩码（同一原图标题、hostname及接口区域分块裁剪，虚线表示省略内容）')
add('q3-assessment',[(40,340,805,1600)],'题3三台路由器12个接口的地址及掩码，24项均为Correct（连续矩形裁剪）')
add('q3-assessment-count',[(2815,270,3220,440)],'题3Item Count为24/24；Score0/0表示评分权重为0（评分窗口右侧连续裁剪）','q3-assessment')
add('q3-completion',[(1105,1595,1300,1625)],'题3Completion为100%（活动窗口底部连续裁剪）')
add('q3-topology',[(1495,430,2825,1115)],'题3 HQ、Branch1、Branch2及六个LAN、三条串行链路（连续矩形裁剪）','q3-completion')
(out/'manifest.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print(json.dumps([(m['file'],m['output_size']) for m in items],ensure_ascii=False,indent=2))
