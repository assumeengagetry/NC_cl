from pathlib import Path
from PIL import Image
import json
root=Path('/Users/apple/Workspace/NC_cl/实验2_交付_20261024')
src=root/'attachments/screenshots/full'; dest=root/'work/report-stage/images';dest.mkdir(exist_ok=True)
crops={
 'A01-topology.png':('A01-final-topology.png',(390,390,2110,1390)),
 'A02-initial-client.png':('A02-client-initial.png',(980,312,2385,960)),
 'A03-records.png':('A03-DNS-records.png',(400,200,2900,900)),
 'A04-normal-ip.png':('A04-normal-ip.png',(1028,985,1650,1250)),
 'A05-normal-A.png':('A05-normal-A.png',(1028,1263,1650,1565)),
 'A06-normal-CNAME.png':('A06-normal-CNAME.png',(1028,1298,1650,1603)),
 'A07-A-PDU.png':('A07-sim-A-response-RR.png',(255,390,2230,1910)),
 'A08-alias-PDU.png':('A09-sim-CNAME-response-RR.png',(255,390,2230,1910)),
 'A09-fault-client.png':('A13-fault-client-DNS.png',(430,220,2940,845)),
 'A10-fault-tests.png':('A12-fault-CNAME.png',(482,1310,1400,1697)),
 'A11-restored-client.png':('A14-restored-client-DNS.png',(430,220,2940,845)),
 'A13-reopened-PC.png':('A18-reopened-PC-config.png',(430,220,2940,855)),
 'A14-reopened-records.png':('A19-reopened-DNS-records.png',(360,200,2870,900)),
 'A15-reopened-DNS-IP.png':('A20-reopened-DNS-IP.png',(360,200,2870,760)),
 'A12-restored-tests.png':('A17-restored-CNAME.png',(482,835,1110,1660)),
}
manifest=[]
for name,(original,box) in crops.items():
 im=Image.open(src/original);im.crop(box).save(dest/name)
 manifest.append({'image':name,'original':'attachments/screenshots/full/'+original,'crop_box_xyxy':box,'source_pixels':list(im.size),'modification':'rectangular crop only; no field edits'})
(root/'work/report-stage/qa/crop-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
