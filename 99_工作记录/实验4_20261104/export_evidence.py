from pathlib import Path
import subprocess,json
w=Path(__file__).resolve().parent; e=w/'evidence'
fields=['frame.number','frame.time_epoch','frame.time_relative','ip.src','ip.dst','ip.id','ip.ttl','ip.len','ip.hdr_len','ip.flags.mf','ip.frag_offset','ip.reassembled.length','icmp.type','icmp.code','icmp.checksum','icmp.ident','icmp.seq','icmp.resptime','data.data']
for p in sorted(e.glob('*.pcapng')):
 base=['/opt/homebrew/bin/tshark','-r',str(p),'-o','ip.check_checksum:TRUE']
 (e/(p.stem+'-details.txt')).write_bytes(subprocess.check_output(base+['-V','-x']))
 (e/(p.stem+'-fields.tsv')).write_bytes(subprocess.check_output(base+['-T','fields','-E','header=y']+sum((['-e',f] for f in fields),[])))
 (e/(p.stem+'-frames.json')).write_bytes(subprocess.check_output(base+['-T','json','--no-duplicate-keys']))
 print(p.name,subprocess.check_output(base+['-T','fields','-e','frame.number']).decode().splitlines().__len__())
