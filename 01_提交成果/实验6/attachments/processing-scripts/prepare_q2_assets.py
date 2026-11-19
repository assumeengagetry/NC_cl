from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json
root=Path(__file__).parent
src=root/'evidence'
out=root/'assets_prepared/q2'
out.mkdir(parents=True,exist_ok=True)
items=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(name,boxes,caption,source_name=None):
 p=src/((source_name or name)+'.png')
 if not p.exists():return
 im=Image.open(p).convert('RGB')
 if len(boxes)==1:
  result=im.crop(boxes[0]);kind='continuous_rectangle_crop'
 else:
  crops=[im.crop(b) for b in boxes];gap=14
  result=Image.new('RGB',(sum(c.width for c in crops)+gap,max(c.height for c in crops)),(235,235,235))
  result.paste(crops[0],(0,0));result.paste(crops[1],(crops[0].width+gap,0))
  dr=ImageDraw.Draw(result);x=crops[0].width+gap//2
  for y in range(0,result.height,12):dr.line((x,y,x,min(y+6,result.height)),fill=(125,125,125),width=2)
  kind='same_source_aligned_column_crops_with_disclosed_gap'
 target=out/(name+'.png');result.save(target)
 items.append(dict(file=str(target.relative_to(root)),source=str(p.relative_to(root)),source_sha256=sha(p),output_sha256=sha(target),source_size=list(im.size),output_size=list(result.size),method=kind,crop_boxes_xyxy=boxes,caption=caption))
ipboxes=[(45,190,470,560),(1100,190,1430,560)]
for n,ip in [(1,'172.16.3'),(2,'172.16.1'),(3,'192.168.2')]:
 add(f'q2-pc{n}-ip',ipboxes,f'PC{n}最终IPv4配置：{ip}.10/24，网关{ip}.1（同一原图左右字段列裁剪并排，虚线表示省略中间空白）')
 add(f'q2-r{n}-config',[(50,760,650,825)],f'R{n}的Fa0/0配置：{ip}.1/24及no shutdown（原截图配置命令区域连续裁剪）',f'q2-r{n}-interface')
 add(f'q2-r{n}-detail',[(50,1125,650,1185)],f'R{n}的Fa0/0实测状态up/up，地址{ip}.1/24（原截图show命令与输出区域连续裁剪）',f'q2-r{n}-interface')
 add(f'q2-pc{n}-ping',[(50,220,650,550)],f'PC{n} Ping本地网关{ip}.1，4/4响应（完整命令与输出连续裁剪）')
add('q2-assessment',[(40,340,805,1440)],'题2全部18项 Assessment Items 均为 Correct（连续矩形裁剪）')
add('q2-assessment-count',[(2815,270,3220,440)],'题2 Item Count 为18/18；此活动评分权重均为0，Score显示0/0（同一评分窗口右侧连续裁剪）','q2-assessment')
add('q2-completion',[(1105,1595,1300,1625)],'题2 Completion 为100%（活动窗口底部连续裁剪）')
add('q2-topology',[(1460,580,2830,1030)],'题2主机与路由器拓扑；本题仅配置并验证以太网接口（连续矩形裁剪）','q2-completion')
(out/'manifest.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print(json.dumps([(x['file'],x['output_size']) for x in items],ensure_ascii=False,indent=2))
