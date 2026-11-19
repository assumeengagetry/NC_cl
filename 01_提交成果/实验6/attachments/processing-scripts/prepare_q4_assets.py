from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(__file__).parent;src=root/'evidence';out=root/'assets_prepared/q4';out.mkdir(parents=True,exist_ok=True)
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
specs=[
 ('q4-hq-config','q4-hq-config-final','HQ',700,(50,1343,500,1728)),
 ('q4-east-config','q4-east-config-final','East',700,(50,1343,500,1588)),
 ('q4-west-config','q4-west-config-final','West',700,(50,1343,500,1608)),
 ('q4-router2-config','q4-router2-config','Router2 / hostname Router',660,(50,1583,500,1648))]
for name,source,host,yname,body in specs:
 add(name,[(1400,0,1850,55),(50,yname,500,yname+21),body],f'题4 {host} 最终接口地址及掩码（同一原图标题、hostname及接口区域分块裁剪，虚线表示省略内容）',source)
add('q4-hq-clock',[(50,1380,650,1465)],'HQ Serial0/2/0控制器：DCE V.35、clock rate64000（连续矩形裁剪）')
add('q4-hq-status',[(50,1660,850,1805)],'HQ最终五个已编址接口均为up/up，包含Serial0/2/0=172.16.71.5（连续矩形裁剪）','q4-hq-status-final')
add('q4-assessment',[(40,340,805,1480)],'题4全部20项均为Correct；活动未评估的HQ S0/2/0和East S0/0/0由接口配置图补充（连续矩形裁剪）')
add('q4-assessment-count',[(2815,270,3220,440)],'题4Item Count为20/20；Score0/0表示评分权重为0（评分窗口右侧连续裁剪）','q4-assessment')
add('q4-completion',[(1105,1595,1300,1625)],'题4Completion为100%（活动窗口底部连续裁剪）')
add('q4-topology',[(1390,350,2760,960)],'题4四路由器、六个LAN与三条串行链路实际拓扑（连续矩形裁剪）','q4-completion')
(out/'manifest.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print(json.dumps([(m['file'],m['output_size']) for m in items],ensure_ascii=False,indent=2))
