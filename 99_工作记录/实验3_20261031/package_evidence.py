from pathlib import Path
import shutil,hashlib,json,subprocess,csv
w=Path(__file__).parent;e=w/'evidence';out=w/'delivery-evidence';out.mkdir(exist_ok=True)
for p in [*e.glob('2024141460445*.pcapng'),e/'tcp-upload-03.pcapng',e/'alice.txt',e/'capture_udp.py',e/'udp-command.txt',e/'udp-capture-log.txt',e/'tcp-upload-03-capture-log.txt',e/'udp-frame-details-and-bytes.txt',e/'tcp-frame-details-and-bytes.txt',e/'udp-frames.json',e/'tcp-frames.json',e/'tcp-follow-stream.txt',e/'upload-page-original.html',e/'lab3-audit.txt',e/'udp-key-fields.tsv',e/'tcp-key-fields.tsv',e/'environment.txt']:
 shutil.copy2(p,out/p.name)
s=out/'完整截图';s.mkdir(exist_ok=True)
for p in (e/'screenshots').glob('*.png'):
 if p.name=='browser-before.png':continue
 shutil.copy2(p,s/p.name)
shutil.copy2(e/'screenshots/crop-manifest.json',s/'crop-manifest.json')
shutil.copytree(e/'cropped',out/'报告裁剪图',dirs_exist_ok=True)
r=subprocess.check_output(['/opt/homebrew/bin/tshark','-n','-r',str(e/'tcp-upload-03.pcapng'),'-Y','tcp.stream == 1','-T','fields','-e','frame.number','-e','frame.time_epoch'],text=True)
with (out/'TCP筛选帧号映射.csv').open('w') as f:
 f.write('final_frame,source_frame,epoch_seconds\n')
 for n,line in enumerate(r.splitlines(),1):
  old,ts=line.split('\t');f.write(f'{n},{old},{ts}\n')
manifest={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file()}
(out/'SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
