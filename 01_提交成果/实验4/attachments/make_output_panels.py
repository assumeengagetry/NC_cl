from pathlib import Path
from reportlab.pdfgen import canvas
import subprocess,re,textwrap
w=Path(__file__).resolve().parent;e=w/'evidence';a=w/'source/assets';a.mkdir(exist_ok=True)
def tsh(name,frame):return subprocess.check_output(['/opt/homebrew/bin/tshark','-r',str(e/(name+'.pcapng')),'-Y',f'frame.number=={frame}','-V','-x'],text=True)
def concise(s,hexlines=0):
 keep=[];h=0
 for line in s.splitlines():
  t=line.strip()
  if t.startswith(('Frame ','Arrival Time:','Epoch Arrival Time:','Internet Protocol Version','Internet Control','Type:','Code:','Checksum:','Identifier (BE):','Sequence Number (BE):','Total Length:','Identification:','Time to Live:','Header Checksum:','Header Length:','Fragment Offset:','Protocol:','ICMP Data:','Data (','[Length:','[Request frame:','[Response time:','[2 IPv4','[Reassembled IPv4','Unused:')) or 'More fragments:' in t or 'Fragment Offset:' in t or 'Header Length:' in t or "Don't fragment:" in t:
   if t.startswith('ICMP Data:'):continue
   keep.append(t)
  if re.match(r'^[0-9a-f]{4}  ',line) and h<hexlines:keep.append(line);h+=1
 return '\n'.join(keep)
def panel(name,title,text,maxw=79):
 lines=[]
 for line in text.splitlines():lines.extend(textwrap.wrap(line,maxw,replace_whitespace=False,drop_whitespace=False,subsequent_indent='  ') or [''])
 width=440;lh=11;height=36+lh*len(lines)
 c=canvas.Canvas(str(a/(name+'.pdf')),pagesize=(width,height));c.setTitle(title);c.setFont('Helvetica-Bold',9);c.drawString(10,height-14,title);c.setFont('Courier',8.8);y=height-29
 for line in lines:c.drawString(10,y,line);y-=lh
 c.save();(e/(name+'-figure-text.txt')).write_text(text)
 print(name,len(lines),round(height/width,2))
panel('ping-request','TShark excerpts | 01-ping-default | frame 1',concise(tsh('01-ping-default',1),7))
panel('ping-reply','TShark excerpts | 01-ping-default | frame 2',concise(tsh('01-ping-default',2),7))
panel('ping-time','Saved command log | 01-ping-default',(e/'01-ping-default-command.txt').read_text().replace('Capture interface: en0\n',''))
panel('large-first','TShark excerpts | 02-ping-2500 | frame 1',concise(tsh('02-ping-2500',1)))
panel('large-reassembly','TShark excerpts | 02-ping-2500 | frame 2',concise(tsh('02-ping-2500',2)))
panel('ttl3','TShark excerpts | 05-ping-ttl03 | frame 2',concise(tsh('05-ping-ttl03',2)))
parts=[]
for n in ['03-ping-ttl02','04-ping-ttl01','05-ping-ttl03','05-ping-ttl04']:
 lines=(e/(n+'-command.txt')).read_text().splitlines()
 parts.append('\n'.join(l for l in lines if l.startswith(('$ ','5 packets','round-trip','64 bytes','36 bytes'))))
panel('ttl-commands','Saved command log excerpts | TTL 2 / 1 / 3 / 4','\n\n'.join(parts))
panel('trace-command','Saved command log | 06-traceroute-icmp',(e/'06-traceroute-icmp-command.txt').read_text())
panel('trace-probe','TShark excerpts | 06-traceroute-icmp | frame 1',concise(tsh('06-traceroute-icmp',1),4))
summary=subprocess.check_output(['/opt/homebrew/bin/tshark','-r',str(e/'06-traceroute-icmp.pcapng'),'-T','fields','-E','header=y','-e','frame.number','-e','frame.time_relative','-e','ip.ttl','-e','icmp.type','-e','icmp.ident','-e','icmp.seq'],text=True)
panel('trace-list','TShark fields | 06-traceroute-icmp','Columns separated by spaces; outer,quoted values separated by comma.\n'+summary.replace('\t','  '))
panel('trace-error','TShark excerpts | 06-traceroute-icmp | frame 4',concise(tsh('06-traceroute-icmp',4),0))
panel('trace-final','TShark excerpts | 06-traceroute-icmp | frame 19',concise(tsh('06-traceroute-icmp',19),4))
