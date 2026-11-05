from pathlib import Path
import subprocess,time,signal,json,datetime,os
W=Path(__file__).resolve().parent; E=W/'evidence'; E.mkdir(exist_ok=True)
def out(cmd):
 p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);return p.stdout
(E/'environment.txt').write_text('Measured at '+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()+'\n'+''.join('\n$ '+' '.join(c)+'\n'+out(c) for c in [['sw_vers'],['ifconfig','en0'],['route','-n','get','202.115.32.43'],['dscacheutil','-q','host','-a','name','cs.scu.edu.cn'],['/opt/homebrew/bin/tshark','--version']]))
runs=[]
def run(name,cmd,timeout=200):
 print('Starting '+name+': '+' '.join(cmd),flush=True)
 f=(E/(name+'-capture.txt')).open('w')
 cap=subprocess.Popen(['/opt/homebrew/bin/dumpcap','-i','en0','-f','ip proto 1 and (host 10.135.133.108)','-w',str(E/(name+'.pcapng'))],stdout=f,stderr=subprocess.STDOUT)
 try:
  time.sleep(.6)
  if cap.poll() is not None:raise RuntimeError('dumpcap failed')
  start=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
  p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
  end=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
  (E/(name+'-command.txt')).write_text('Capture interface: en0\nStart (+08:00): '+start+'\n$ '+' '.join(cmd)+'\n'+p.stdout+'\nExit code: '+str(p.returncode)+'\nEnd (+08:00): '+end+'\n')
  runs.append({'name':name,'command':cmd,'start':start,'end':end,'exit':p.returncode})
  print(p.stdout,flush=True)
  return p.stdout
 finally:
  time.sleep(.4);cap.send_signal(signal.SIGINT);cap.wait(timeout=10);f.close()
  (E/'run-manifest.json').write_text(json.dumps(runs,ensure_ascii=False,indent=2))
target='202.115.32.43'
run('01-ping-default',['/sbin/ping','-n','-c','5','-W','1000',target])
run('02-ping-2500',['/sbin/ping','-n','-c','5','-W','1000','-s','2500',target])
run('03-ping-ttl02',['/sbin/ping','-n','-c','5','-W','1000','-m','2',target])
run('04-ping-ttl01',['/sbin/ping','-n','-c','5','-W','1000','-m','1',target])
for ttl in range(3,31):
 s=run(f'05-ping-ttl{ttl:02d}',['/sbin/ping','-n','-c','5','-W','1000','-m',str(ttl),target])
 if 'bytes from '+target in s:break
run('06-traceroute-icmp',['/usr/sbin/traceroute','-I','-n','-m','30','-q','3','-w','1',target],timeout=160)
print('Capture complete',flush=True)
