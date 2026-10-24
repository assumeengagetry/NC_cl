#!/usr/bin/env python3
"""Run as root after one macOS administrator authorization; no DNS settings changed."""
import datetime, hashlib, json, os, pathlib, re, shlex, signal, subprocess, time
ROOT = pathlib.Path(__file__).resolve().parent
WORK = pathlib.Path('/tmp/nccl-real-dns-20261024')
WORK.mkdir(exist_ok=True)
WS = pathlib.Path('/Applications/Wireshark.app/Contents/MacOS')
USER = 'apple'
PHY = 'en0'
TUN = 'utun4'
SYSTEM_DNS = '100.100.100.100'
RESOLVER = '223.5.5.5'
LOCAL = '10.20.41.180'

def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='milliseconds')

def run(cmd, dest=None, timeout=30, user=False):
    actual = ['/usr/bin/sudo','-u',USER] + cmd if user and os.geteuid()==0 else cmd
    begin = now()
    p = subprocess.run(actual,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    end = now()
    txt = f'Timezone: Asia/Shanghai\nStart: {begin}\n$ {shlex.join(cmd)}\n{p.stdout}\n[exit={p.returncode}]\nEnd: {end}\n'
    if dest: pathlib.Path(dest).write_text(txt)
    return p, txt

def flush(stage):
    lines=[]
    for cmd in [['/usr/bin/dscacheutil','-flushcache'],['/usr/bin/killall','-HUP','mDNSResponder']]:
        p,txt=run(cmd)
        lines.append(txt)
        if p.returncode: raise RuntimeError('Cache flush failed: '+txt)
    time.sleep(1)
    p,txt=run(['/usr/bin/dscacheutil','-cachedump'])
    lines.append(txt)
    (ROOT/(stage+'-cache-flush.txt')).write_text('\n'.join(lines))

manifest=[]

def capture_phase(stage, cmd, is_ping=False, clear=False):
    raw=WORK/(stage+'-raw.pcapng')
    caplog=ROOT/(stage+'-capture.txt')
    # Broad capture stays in /tmp; final display filter retains only the experiment names and ping ICMP.
    phy_filter=f'(host {RESOLVER} and port 53) or (icmp and host {LOCAL})'
    tun_filter=f'host {SYSTEM_DNS} and port 53'
    dc=[str(WS/'dumpcap'),'-q','-i',PHY,'-f',phy_filter,'-i',TUN,'-f',tun_filter,'-w',str(raw)]
    capstart=now()
    with caplog.open('w') as log:
        log.write(f'Capture start: {capstart}\n$ {shlex.join(dc)}\n');log.flush()
        proc=subprocess.Popen(dc,stdout=log,stderr=log)
        time.sleep(1)
        if proc.poll() is not None: raise RuntimeError('dumpcap could not start')
        try:
            if clear: flush(stage)
            p,txt=run(cmd,ROOT/(stage+'-terminal.txt'),timeout=20,user=True)
            time.sleep(0.7)
        finally:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=10)
        capend=now()
        log.write(f'Capture end: {capend}\n')
    display='dns && (dns.qry.name == "www.baidu.com" || dns.qry.name == "www.scu.edu.cn")'
    pingip=None
    if is_ping:
        m=re.search(r'^PING .*?\((\d+\.\d+\.\d+\.\d+)\)',txt,re.M)
        if m:
            pingip=m.group(1)
            display=f'({display}) || (icmp && ip.addr == {pingip})'
    dst=ROOT/(stage+'.pcapng')
    export=[str(WS/'tshark'),'-n','-r',str(raw),'-Y',display,'-w',str(dst)]
    r=subprocess.run(export,capture_output=True,text=True)
    with caplog.open('a') as log: log.write('\nExport display filter: '+display+'\n$ '+shlex.join(export)+'\n'+r.stdout+r.stderr+f'\n[exit={r.returncode}]\n')
    if r.returncode: raise RuntimeError('Export failed')
    manifest.append({'phase':stage,'command':cmd,'capture_start':capstart,'capture_end':capend,'ping_ip':pingip,'command_exit':p.returncode,'raw_file':str(raw),'final_phase_file':dst.name,'export_filter':display,'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'phase_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'cache_flush':clear})
    (ROOT/'phases.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
    if os.geteuid()!=0: raise SystemExit('Needs administrator authorization to flush macOS DNS cache.')
    if (ROOT/'phases.json').exists(): raise SystemExit('Already has run results; do not overwrite')
    logs=[]
    for cmd in [['/usr/bin/sw_vers'],[str(WS/'tshark'),'--version'],['/sbin/route','-n','get',RESOLVER],['/sbin/route','-n','get',SYSTEM_DNS],['/usr/sbin/networksetup','-getdnsservers','Wi-Fi'],['/usr/sbin/networksetup','-getsearchdomains','Wi-Fi'],['/usr/bin/id']]:
        p,txt=run(cmd);logs.append(txt)
    (ROOT/'00-environment.txt').write_text('\n'.join(logs))
    ping=['/sbin/ping','-n','-c','3','-W','1500','-t','8']
    capture_phase('01-ping-baidu-first',ping+['www.baidu.com'],True,True)
    capture_phase('02-ping-baidu-repeat',ping+['www.baidu.com'],True)
    capture_phase('03-ping-scu-first',ping+['www.scu.edu.cn'],True,True)
    capture_phase('04-ping-scu-repeat',ping+['www.scu.edu.cn'],True)
    for num,domain,typ in [(5,'baidu','A'),(6,'baidu','CNAME'),(7,'scu','A'),(8,'scu','CNAME')]:
        fqdn='www.baidu.com.' if domain=='baidu' else 'www.scu.edu.cn.'
        capture_phase(f'{num:02d}-nslookup-{domain}-{typ.lower()}',['/usr/bin/nslookup','-type='+typ,fqdn,RESOLVER])
    final=ROOT.parent.parent/'2024141460445_许盛凯_实验2_DNS.pcapng'
    subprocess.run([str(WS/'mergecap'),'-w',str(final)]+[str(ROOT/(x['phase']+'.pcapng')) for x in manifest],check=True)
    (ROOT/'run-complete.txt').write_text(f'Completed: {now()}\nNo DNS, routing, network service, or VPN settings were modified.\nRoot used only to clear system DNS cache; measurements executed as apple.\nFinal capture: {final.name}\n')
    # Restore ownership for editable user deliverables, with no persistent privilege/config changes.
    import pwd
    ident=pwd.getpwnam(USER)
    for p in list(ROOT.rglob('*'))+[ROOT,final]:
        os.chown(p,ident.pw_uid,ident.pw_gid)
