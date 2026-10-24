#!/usr/bin/env python3
"""Extract only actual captured DNS values and verify packet preservation."""
from pathlib import Path
import collections, csv, hashlib, ipaddress, json, struct, subprocess

HERE=Path(__file__).resolve().parent
PCAP=HERE.parent.parent/'2024141460445_许盛凯_实验2_DNS.pcapng'
WS=Path('/Applications/Wireshark.app/Contents/MacOS')

def tshark(path, args):
    return subprocess.check_output([str(WS/'tshark'),'-2','-n','-r',str(path)]+args,text=True)

def packets(path):
    data=path.read_bytes(); off=0; endian='<'; interfaces=[]; out=[]
    while off<len(data):
        if data[off:off+4]==b'\x0a\x0d\x0d\x0a':
            endian='<' if data[off+8:off+12]==b'\x4d\x3c\x2b\x1a' else '>'
            interfaces=[]
        typ,size=struct.unpack_from(endian+'II',data,off)
        assert size>=12 and size%4==0
        assert struct.unpack_from(endian+'I',data,off+size-4)[0]==size
        body=data[off+8:off+size-4]
        if typ==1:
            resolution=1_000_000
            pos=8
            while pos+4<=len(body):
                opt,n=struct.unpack_from(endian+'HH',body,pos);pos+=4
                value=body[pos:pos+n];pos+=(n+3)//4*4
                if opt==0:break
                if opt==9:
                    b=value[0];resolution=(2**(b&127) if b&128 else 10**b)
            interfaces.append(resolution)
        elif typ==6:
            iface,hi,lo,caplen,origlen=struct.unpack_from(endian+'IIIII',body)
            # All present captures use decimal resolution no finer than ns.
            ns=((hi<<32)|lo)*1_000_000_000//interfaces[iface]
            out.append((ns,origlen,body[20:20+caplen]))
        off+=size
    assert off==len(data)
    return out

def name(data,pos):
    labels=[];end=None;seen=set()
    while True:
        assert pos not in seen;seen.add(pos)
        n=data[pos];pos+=1
        if n&192==192:
            target=((n&63)<<8)|data[pos]
            if end is None:end=pos+1
            pos=target;continue
        if n==0:return '.'.join(labels),end or pos
        labels.append(data[pos:pos+n].decode('ascii'));pos+=n

def decode_dns(data):
    ident,flags,qd,an,ns,ar=struct.unpack_from('!6H',data)
    pos=12;questions=[]
    for _ in range(qd):
        q,pos=name(data,pos);typ,cls=struct.unpack_from('!HH',data,pos);pos+=4
        questions.append({'name':q,'type':typ,'class':cls})
    result={'id':f'0x{ident:04x}','flags':f'0x{flags:04x}','QR':flags>>15,'AA':(flags>>10)&1,'TC':(flags>>9)&1,'RD':(flags>>8)&1,'RA':(flags>>7)&1,'RCODE':flags&15,'questions':questions}
    for key,count in [('Answer',an),('Authority',ns),('Additional',ar)]:
        rrs=[]
        for _ in range(count):
            owner,pos=name(data,pos);typ,cls,ttl,length=struct.unpack_from('!HHIH',data,pos);pos+=10
            start=pos;raw=data[pos:pos+length];pos+=length
            rr={'owner':owner,'type':typ,'class':cls,'ttl':ttl}
            if typ in (1,28):rr['address']=str(ipaddress.ip_address(raw))
            elif typ in (2,5,12):rr['target']=name(data,start)[0]
            elif typ==6:
                rr['mname'],p=name(data,start);rr['rname'],p=name(data,p)
                rr.update(zip(['serial','refresh','retry','expire','minimum'],struct.unpack_from('!5I',data,p)))
            else:rr['rdata_hex']=raw.hex()
            rrs.append(rr)
        result[key]=rrs
    assert pos==len(data)
    return result

fields=['frame.number','frame.time_epoch','frame.interface_name','ip.src','ip.dst','udp.srcport','udp.dstport','dns.id','dns.flags','dns.qry.name','dns.qry.type','dns.response_in','dns.response_to','udp.payload']
args=['-Y','dns','-T','fields']
for f in fields:args+=['-e',f]
rows=list(csv.reader(tshark(PCAP,args).splitlines(),delimiter='\t'))
records=[]
for row in rows:
    rec=dict(zip(fields,row));dns=decode_dns(bytes.fromhex(rec.pop('udp.payload').replace(':','')))
    rec.update(dns);records.append(rec)
(HERE/'final-dns-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))

pairs=[];pending={}
for rec in records:
    q=rec['questions'][0]
    src=(rec['ip.src'],rec['udp.srcport']);dst=(rec['ip.dst'],rec['udp.dstport'])
    signature=(rec['id'],q['name'],q['type'])
    if rec['QR']==0:pending[(src,dst,signature)]=rec
    else:
        req=pending.pop((dst,src,signature))
        assert float(rec['frame.time_epoch'])>=float(req['frame.time_epoch'])
        assert req['dns.response_in']==rec['frame.number']
        assert rec['dns.response_to']==req['frame.number']
        pairs.append({'query_frame':int(req['frame.number']),'response_frame':int(rec['frame.number']),'id':rec['id'],'qname':q['name'],'qtype':q['type'],'query_src':':'.join(dst),'query_dst':':'.join(src),'time_ms':round((float(rec['frame.time_epoch'])-float(req['frame.time_epoch']))*1000,3),'QR_query':req['QR'],'QR_response':rec['QR']})
assert not pending
(HERE/'final-transaction-pairs.json').write_text(json.dumps(pairs,ensure_ascii=False,indent=2))

phases=json.loads((HERE/'phases.json').read_text());allraw=collections.Counter();allselected=collections.Counter();phase_ranges=[];raw_unreadable=[]
final_packets=packets(PCAP)
for phase in phases:
    raw=Path(phase['raw_file']);filtered=HERE/phase['final_phase_file']
    selected=packets(filtered)
    try:
        raw_packets=collections.Counter(packets(raw))
        assert not (collections.Counter(selected)-raw_packets)
        assert hashlib.sha256(raw.read_bytes()).hexdigest()==phase['raw_sha256']
        allraw.update(raw_packets)
    except PermissionError:
        raw_unreadable.append(str(raw))
    assert hashlib.sha256(filtered.read_bytes()).hexdigest()==phase['phase_sha256']
    allselected.update(selected)
    indices=[i+1 for i,x in enumerate(final_packets) if x in collections.Counter(selected)]
    dns_count=len(tshark(filtered,['-Y','dns','-T','fields','-e','frame.number']).splitlines())
    phase_ranges.append({'phase':phase['phase'],'final_frames':indices,'total':len(selected),'dns_frames':dns_count,'icmp_frames':len(selected)-dns_count,'cache_flush':phase['cache_flush'],'ping_ip':phase['ping_ip']})
assert collections.Counter(final_packets)==allselected
if not raw_unreadable:assert not (collections.Counter(final_packets)-allraw)
assert len(final_packets)==sum(x['total'] for x in phase_ranges)
summary={'capture':PCAP.name,'sha256':hashlib.sha256(PCAP.read_bytes()).hexdigest(),'total_frames':len(final_packets),'dns_frames':len(records),'complete_dns_pairs':len(pairs),'merged_bytes_and_timestamps_equal_phase_files':True,'filtered_bytes_and_timestamps_verified_against_raw':not raw_unreadable,'raw_files_unreadable':raw_unreadable,'phases':phase_ranges,'settings_changed':False}
(HERE/'final-validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
tsvfields=fields[:-1]+['dns.flags.authoritative','dns.flags.recdesired','dns.flags.recavail','dns.flags.rcode','dns.flags.truncated','dns.count.answers','dns.count.auth_rr','dns.count.add_rr','dns.cname','dns.a','dns.resp.ttl']
cmd=['-Y','dns','-T','fields','-E','header=y']
for f in tsvfields:cmd+=['-e',f]
(HERE/'final-dns-fields.tsv').write_text(tshark(PCAP,cmd))
(HERE/'final-packet-dissection.pdml').write_text(tshark(PCAP,['-Y','dns','-T','pdml']))
for frame in [int(r['frame.number']) for r in records]:
    (HERE/f'frame-{frame:02d}.txt').write_text(tshark(PCAP,['-Y',f'frame.number=={frame}','-V','-x']))
print(json.dumps(summary,ensure_ascii=False,indent=2))
