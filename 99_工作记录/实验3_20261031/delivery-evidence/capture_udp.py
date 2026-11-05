from pathlib import Path
import subprocess,json,datetime,hashlib,time
r=Path(__file__).parent
p=r/'2024141460445_许盛凯_实验3_UDP.pcapng'
assert not p.exists()
start=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
cap=subprocess.Popen(['/opt/homebrew/bin/dumpcap','-i','en0','-f','udp port 53 and host 223.5.5.5','-w',str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
time.sleep(.5)
args=['/usr/bin/nslookup','-type=A','www.baidu.com.','223.5.5.5']
s=subprocess.run(args,capture_output=True,text=True,timeout=15)
(r/'udp-command.txt').write_text(f'Start: {start}\n$ '+ ' '.join(args)+f'\n{s.stdout}{s.stderr}\nExit: {s.returncode}\nEnd: '+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()+'\n')
time.sleep(.4)
cap.send_signal(2)
out,err=cap.communicate(timeout=5)
(r/'udp-capture-log.txt').write_text(out+err)
assert cap.returncode==0,err
assert s.returncode==0,s.stderr
for args,outname in [(['-T','json'],'udp-frames.json'),(['-V','-x'],'udp-frame-details-and-bytes.txt')]:
    q=subprocess.run(['/opt/homebrew/bin/tshark','-n','-r',str(p),'-o','udp.check_checksum:TRUE']+args,capture_output=True,check=True)
    (r/outname).write_bytes(q.stdout)
print(json.dumps({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nslookup_output':s.stdout},ensure_ascii=False))
