from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json
root=Path(__file__).parent
src=root/'evidence'
out=root/'assets_prepared/q1'
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
  crops=[im.crop(b) for b in boxes]
  gap=14
  result=Image.new('RGB',(sum(c.width for c in crops)+gap,max(c.height for c in crops)),(235,235,235))
  result.paste(crops[0],(0,0));result.paste(crops[1],(crops[0].width+gap,0))
  dr=ImageDraw.Draw(result)
  x=crops[0].width+gap//2
  for y in range(0,result.height,12):dr.line((x,y,x,min(y+6,result.height)),fill=(125,125,125),width=2)
  kind='same_source_aligned_column_crops_with_disclosed_gap'
 target=out/(name+'.png');result.save(target)
 items.append(dict(file=str(target.relative_to(root)),source=str(p.relative_to(root)),source_sha256=sha(p),output_sha256=sha(target),source_size=list(im.size),output_size=list(result.size),method=kind,crop_boxes_xyxy=boxes,caption=caption))
ipboxes=[(45,190,470,560),(1100,190,1430,560)]
for n,c in [
 ('q1-lax-gw-empty','LAXpc 网关留空时的 IPv4 配置'),
 ('q1-lax-gw-correct','LAXpc 的正确 IPv4 配置：192.168.1.2/24，网关192.168.1.1'),
 ('q1-phx-ip','PHXpc 最终 IPv4 配置：192.168.2.2/24，网关192.168.2.1'),
 ('q1-atl-ip','ATLpc 最终 IPv4 配置：192.168.3.2/24，网关192.168.3.1'),
 ('q1-lax-gw-wrong','LAXpc 将网关设为本地不存在的192.168.1.254'),
 ('q1-lax-gw-offlink','LAXpc 将网关设为跨网段地址192.168.2.1'),
 ('q1-lax-final','LAXpc 恢复后的最终 IPv4 配置')]:
 add(n,ipboxes,c+'（同一原图左右字段列裁剪并排，虚线表示省略中间空白）')
for n,b,c in [
 ('q1-empty-pings',(50,220,650,790),'网关留空：本地目标4/4成功，远端目标0/4成功'),
 ('q1-correct-pings',(50,815,650,1415),'正确网关：本地目标4/4成功，远端目标3/4成功，保留首包超时'),
 ('q1-wrong-pings',(50,1370,650,1930),'不存在的本地网关：本地目标4/4成功，远端目标0/4成功'),
 ('q1-offlink-remote',(50,1660,650,1970),'跨网段网关补充测试：远端目标4/4成功'),
 ('q1-offlink-arp',(50,1480,650,1970),'跨网段网关补测的 ARP 表和本地4/4成功：两地址对应同一MAC'),
 ('q1-restored-remote',(50,1660,650,1970),'恢复正确网关192.168.1.1后复测远端，4/4成功')]:
 add(n,[b],c+'（连续矩形裁剪，保留该组完整命令与输出）')
add('q1-assessment',[(40,340,805,930)],'题1全部9项 Assessment Items 均为 Correct（连续矩形裁剪）')
add('q1-assessment-count',[(2815,270,3220,440)],'题1 Item Count 为9/9；此活动评分权重均为0，Score显示0/0（同一评分窗口右侧连续裁剪）','q1-assessment')
add('q1-completion',[(0,1595,600,1695)],'题1 Completion 为100%（活动窗口底部连续裁剪）')
add('q1-topology',[(1315,390,2455,975)],'题1三台主机、交换机和路由器拓扑（连续矩形裁剪）','q1-completion')
(out/'manifest.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print(json.dumps([(x['file'],x['output_size']) for x in items],ensure_ascii=False,indent=2))
