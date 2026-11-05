#!/usr/bin/env python3
"""Independently parse the saved pcapng bytes, validate, then export audit facts.

Only reads captures. TShark is used for corroborating decoded fields/details,
while checksum, pairing and fragmentation assertions use this native parser.
"""
from pathlib import Path
import csv, hashlib, json, re, socket, struct, subprocess
from decimal import Decimal

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'analysis'
OUT.mkdir(exist_ok=True)
EXPECTED = {'01-ping-default':10,'02-ping-2500':20,'03-ping-ttl02':5,
            '04-ping-ttl01':5,'05-ping-ttl03':10,'05-ping-ttl04':10,
            '06-traceroute-icmp':19}
TSHARK = '/opt/homebrew/bin/tshark'

def checksum(buf):
    if len(buf) % 2:
        buf += b'\0'
    n = sum(struct.unpack('!'+'H'*(len(buf)//2),buf))
    while n >> 16:
        n = (n & 65535) + (n >> 16)
    return (~n) & 65535

def pcapng_packets(path):
    raw = path.read_bytes()
    pos, endian, ifaces = 0, '<', []
    records = []
    while pos < len(raw):
        assert len(raw)-pos >= 12, 'truncated pcapng block'
        if raw[pos:pos+4] == b'\x0a\x0d\x0d\x0a':
            endian = '<' if raw[pos+8:pos+12] == b'\x4d\x3c\x2b\x1a' else '>'
            ifaces = []
        kind, length = struct.unpack_from(endian+'II',raw,pos)
        assert length >= 12 and length % 4 == 0
        assert struct.unpack_from(endian+'I',raw,pos+length-4)[0] == length
        body = raw[pos+8:pos+length-4]
        if kind == 1:
            linktype, _, snaplen = struct.unpack_from(endian+'HHI',body)
            res = Decimal('0.000001')
            q = 8
            while q+4 <= len(body):
                code,n = struct.unpack_from(endian+'HH',body,q)
                val = body[q+4:q+4+n]
                if code == 0:
                    break
                if code == 9:
                    v=val[0]
                    res = Decimal(2 if v&128 else 10) ** (-int(v&127))
                q += 4+((n+3)//4)*4
            ifaces.append((linktype,res,snaplen))
        elif kind == 6:
            iface,hi,lo,caplen,wirelen=struct.unpack_from(endian+'IIIII',body)
            lt,res,_=ifaces[iface]
            assert lt==1, f'expected Ethernet, got {lt}'
            assert caplen==wirelen, 'truncated packet'
            packet=body[20:20+caplen]
            assert len(packet)==caplen
            records.append({'frame':len(records)+1,'time':Decimal((hi<<32)+lo)*res,
                            'wire_length':wirelen,'packet':packet})
        pos += length
    assert pos==len(raw)
    return records

def ipv4(buf, quoted=False):
    assert len(buf)>=20 and buf[0]>>4==4
    hlen=(buf[0]&15)*4
    total=struct.unpack_from('!H',buf,2)[0]
    assert hlen>=20 and hlen<=len(buf)
    assert checksum(buf[:hlen])==0, 'invalid IPv4 checksum'
    if not quoted:
        assert total<=len(buf)
    ident, flags_offset=struct.unpack_from('!HH',buf,4)
    return {'ip_header_length':hlen, 'ip_total_length':total,
            'ip_id':f'0x{ident:04x}', 'ip_flags':flags_offset>>13,
            'mf':bool(flags_offset&8192), 'df':bool(flags_offset&16384),
            'offset_units':flags_offset&8191,'offset_bytes':(flags_offset&8191)*8,
            'ttl':buf[8],'protocol':buf[9],
            'ip_checksum':f'0x{struct.unpack_from("!H",buf,10)[0]:04x}',
            'src':socket.inet_ntoa(buf[12:16]),'dst':socket.inet_ntoa(buf[16:20]),
            'dscp_ecn':f'0x{buf[1]:02x}',
            '_payload':buf[hlen:total], '_ipbytes':buf[:total]}

def icmp(buf, quoted=False):
    assert len(buf)>=8
    if not quoted:
        assert checksum(buf)==0,'invalid ICMP checksum'
    d={'type':buf[0],'code':buf[1],
       'icmp_checksum':f'0x{struct.unpack_from("!H",buf,2)[0]:04x}',
       'icmp_length':len(buf), 'icmp_header_hex':buf[:8].hex(' ')}
    if d['type'] in (0,8):
        d.update(identifier=struct.unpack_from('!H',buf,4)[0],
                 identifier_hex=f'0x{struct.unpack_from("!H",buf,4)[0]:04x}',
                 sequence=struct.unpack_from('!H',buf,6)[0],
                 icmp_data_length=len(buf)-8, icmp_data_hex=buf[8:].hex())
        if len(buf)>=16 and buf[8:12]!=b'\0'*4:
            sec,usec=struct.unpack_from('!II',buf,8)
            if usec<1000000:
                d['data_timestamp_epoch']=str(Decimal(sec)+Decimal(usec)/1000000)
    elif d['type'] == 11:
        d['unused_hex']=buf[4:8].hex()
        inner=ipv4(buf[8:],quoted=True)
        inner.update(icmp(inner['_payload'],quoted=True))
        d['quote_bytes']=len(buf)-8
        d['quote']=inner
    return d

def clean(x):
    if isinstance(x,dict): return {k:clean(v) for k,v in x.items() if not k.startswith('_')}
    if isinstance(x,list): return [clean(v) for v in x]
    if isinstance(x,Decimal): return str(x)
    return x

facts={'parser':'Native pcapng/Ethernet/IPv4/ICMP parser; no capture mutation',
       'captures':{}, 'validation':{}, 'notes':[]}
ip_checks=icmp_checks=quoted_ip_checks=0
for stem,n_expected in EXPECTED.items():
    path=ROOT/(stem+'.pcapng')
    records=pcapng_packets(path)
    assert len(records)==n_expected,(stem,len(records))
    for r in records:
        packet=r.pop('packet')
        assert packet[12:14]==b'\x08\x00'
        r.update(ipv4(packet[14:]))
        r['ethernet_header_length']=14
        r['ip_payload_length']=len(r['_payload'])
        assert r['protocol']==1
        ip_checks+=1
    # Reassemble at the IP payload layer, keyed by endpoints/protocol/IPv4 ID.
    groups={}
    for r in records:
        if r['mf'] or r['offset_units']:
            k=(r['src'],r['dst'],r['protocol'],r['ip_id'])
            groups.setdefault(k,[]).append(r)
        else:
            r.update(icmp(r['_payload']))
            icmp_checks+=1
            if r['type']==11: quoted_ip_checks+=1
    messages=[r for r in records if not (r['mf'] or r['offset_units'])]
    reassembled=[]
    for k,parts in groups.items():
        parts.sort(key=lambda r:r['offset_units'])
        expected_offset=0; payload=b''
        for i,r in enumerate(parts):
            assert r['offset_bytes']==expected_offset,'fragment gap/overlap'
            assert r['mf']==(i<len(parts)-1),'MF inconsistent with last fragment'
            if r['mf']: assert len(r['_payload'])%8==0
            payload+=r['_payload'];expected_offset+=len(r['_payload'])
        m=dict(parts[0]);m.update(icmp(payload));icmp_checks+=1
        m['fragment_frames']=[r['frame'] for r in parts]
        m['completed_frame']=parts[-1]['frame']
        m['first_time']=parts[0]['time'];m['time']=parts[-1]['time']
        m['reassembled_ip_payload_length']=len(payload)
        m['reassembled_original_ipv4_length']=m['ip_header_length']+len(payload)
        m['_reassembled_payload']=payload
        reassembled.append(m);messages.append(m)
    messages.sort(key=lambda r:r['time'])
    reqs=[m for m in messages if m['type']==8]
    replies=[m for m in messages if m['type']==0]
    errs=[m for m in messages if m['type']==11]
    pairs=[];error_pairs=[]
    for r in replies:
        match=[q for q in reqs if q['src']==r['dst'] and q['dst']==r['src']
               and q['identifier']==r['identifier'] and q['sequence']==r['sequence']
               and q['icmp_data_hex']==r['icmp_data_hex'] and q['time']<r['time']]
        assert len(match)==1,'ambiguous/unpaired echo reply'
        q=match[0]
        pairs.append({'request_frames':q.get('fragment_frames',[q['frame']]),
                      'reply_frames':r.get('fragment_frames',[r['frame']]),
                      'identifier':r['identifier'],'sequence':r['sequence'],
                      'capture_rtt_ms':str((r['time']-q['time'])*1000),
                      'first_fragment_rtt_ms':str((r.get('first_time',r['time'])-q.get('first_time',q['time']))*1000),
                      'icmp_data_length':r['icmp_data_length'],'data_equal':True})
    for r in errs:
        inn=r['quote']
        match=[q for q in reqs if q['src']==inn['src'] and q['dst']==inn['dst']
               and q['ip_id']==inn['ip_id'] and q['identifier']==inn['identifier']
               and q['sequence']==inn['sequence'] and q['icmp_checksum']==inn['icmp_checksum']
               and q['time']<r['time']]
        assert len(match)==1,'unpaired Time Exceeded quote'
        q=match[0]
        error_pairs.append({'request_frame':q['frame'],'error_frame':r['frame'],
                            'router':r['src'],'sequence':q['sequence'],
                            'original_ttl':q['ttl'],'quoted_ttl':inn['ttl'],
                            'quote_bytes':r['quote_bytes'],
                            'quoted_data_length':inn['icmp_data_length'],
                            'capture_rtt_ms':str((r['time']-q['time'])*1000)})
    command=(ROOT/(stem+'-command.txt')).read_text()
    ping_times=re.findall(r'icmp_seq=(\d+).*?time=([\d.]+) ms',command)
    if ping_times:
        assert len(ping_times)==len(pairs)
        for pair,(seq,ms) in zip(sorted(pairs,key=lambda x:x['sequence']),ping_times):
            assert pair['sequence']==int(seq)
            pair['ping_rtt_ms']=ms
            pair['ping_minus_capture_ms']=str(Decimal(ms)-Decimal(pair['capture_rtt_ms']))
    facts['captures'][stem]={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                            'frames':len(records),'echo_requests':len(reqs),'echo_replies':len(replies),
                            'time_exceeded':len(errs),'fragmented_datagrams':len(groups),
                            'frame_records':clean(records),'reassembled_messages':clean(reassembled),
                            'echo_pairs':pairs,'time_exceeded_pairs':error_pairs}
    # Each detailed export opens the complete pcap so reassembly state is retained.
    detail=OUT/stem;detail.mkdir(exist_ok=True)
    base=[TSHARK,'-o','ip.check_checksum:TRUE','-r',str(path)]
    all_details=subprocess.check_output(base+['-V','-x'],text=True)
    (detail/'all-frames-details-and-bytes.txt').write_text(all_details)
    chunks=re.split(r'(?m)(?=^Frame \d+:)',all_details)
    for chunk in chunks:
        hit=re.match(r'Frame (\d+):',chunk)
        if hit:(detail/f'frame-{int(hit.group(1)):02d}.txt').write_text(chunk)
    fields=['frame.number','frame.time_epoch','frame.len','ip.src','ip.dst','ip.hdr_len',
            'ip.len','ip.id','ip.flags','ip.flags.df','ip.flags.mf','ip.frag_offset',
            'ip.ttl','ip.proto','ip.checksum','ip.checksum.status','ip.reassembled_in',
            'ip.reassembled.length','icmp.type','icmp.code','icmp.checksum',
            'icmp.checksum.status','icmp.ident','icmp.seq','icmp.data','data.len',
            'data.data','icmp.resp_in','icmp.resp_to','icmp.resptime']
    args=base+['-T','fields','-E','header=y','-E','occurrence=a','-E','aggregator=,']
    for f in fields:args+=['-e',f]
    (detail/'tshark-fields.tsv').write_text(subprocess.check_output(args,text=True))
    # Native TSV makes outer-vs-quoted fields explicit; raw TShark repeats nested fields.
    cols=['frame','time','wire_length','src','dst','ip_header_length','ip_total_length',
          'ip_id','ttl','protocol','ip_checksum','mf','offset_units','offset_bytes',
          'ip_payload_length','type','code','identifier','sequence','icmp_checksum',
          'icmp_length','icmp_data_length']
    with (detail/'native-outer-fields.tsv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=cols,delimiter='\t',extrasaction='ignore');w.writeheader()
        w.writerows(clean(records))
    # Corroborate native pairing RTTS against TShark's reassembly-aware ICMP fields.
    tshark_rtts=subprocess.check_output(base+['-Y','icmp.type==0','-T','fields','-e','icmp.resptime'],text=True).splitlines()
    assert [Decimal(x) for x in tshark_rtts if x]==[Decimal(p['capture_rtt_ms']) for p in pairs]

default=facts['captures']['01-ping-default']
assert default['echo_requests']==default['echo_replies']==5
assert all(r.get('icmp_data_length')==56 and r.get('icmp_length')==64 and r['ip_total_length']==84 and r['wire_length']==98 for r in default['frame_records'])
assert default['frame_records'][0]['identifier_hex']=='0x00f4'
large=facts['captures']['02-ping-2500']
assert large['fragmented_datagrams']==10 and len(large['reassembled_messages'])==10
for m in large['reassembled_messages']:
    assert m['reassembled_ip_payload_length']==2508 and m['icmp_data_length']==2500
    parts=[r for r in large['frame_records'] if r['frame'] in m['fragment_frames']]
    assert [r['ip_total_length'] for r in parts]==[1500,1048]
    assert [r['ip_payload_length'] for r in parts]==[1480,1028]
    assert [r['offset_units'] for r in parts]==[0,185]
    assert [r['offset_bytes'] for r in parts]==[0,1480]
assert facts['captures']['03-ping-ttl02']['time_exceeded']==0
assert facts['captures']['04-ping-ttl01']['time_exceeded']==0
ttl3=facts['captures']['05-ping-ttl03']
assert ttl3['echo_requests']==ttl3['time_exceeded']==5 and ttl3['echo_replies']==0
assert all(p['router']=='202.115.39.102' and p['quoted_ttl']==1 and p['quote_bytes']==28 for p in ttl3['time_exceeded_pairs'])
trace=facts['captures']['06-traceroute-icmp']
assert (trace['echo_requests'],trace['echo_replies'],trace['time_exceeded'])==(12,3,4)
assert trace['time_exceeded_pairs'][0]=={'request_frame':3,'error_frame':4,'router':'10.134.191.254','sequence':3,'original_ttl':1,'quoted_ttl':1,'quote_bytes':48,'quoted_data_length':20,'capture_rtt_ms':'5.950000'}
assert all(r['icmp_data_length']==20 and r['icmp_length']==28 and r['ip_total_length']==48 for r in trace['frame_records'] if r.get('type')==8)
facts['validation']={'passed':True,'total_frames':sum(c['frames'] for c in facts['captures'].values()),
                     'ipv4_checksums_validated':ip_checks,'icmp_checksums_validated':icmp_checks,
                     'quoted_ipv4_checksums_validated':quoted_ip_checks,
                     'fragmented_messages_reassembled':10,
                     'echo_data_byte_equal_pairs':sum(len(c['echo_pairs']) for c in facts['captures'].values()),
                     'time_exceeded_quotes_matched':sum(len(c['time_exceeded_pairs']) for c in facts['captures'].values()),
                     'tshark_rtts_equal_native':True}
facts['notes']=[
 'Ordinary macOS ping uses 56 ICMP data bytes: its first 8 bytes are timestamp, and Wireshark renders the remaining 48 as Data. ICMP header is a separate 8 bytes.',
 'ICMP BE Identifier is used for matching. IPv4 Identification identifies the datagram/fragments and is a different field.',
 'IPv4 fragment-offset field units are 8 bytes: raw value185 equals byte displacement1480. Noninitial fragment has no repeated ICMP header.',
 'Large-ping reassembled ICMP message is2508 bytes =8+2500; original unfragmented IPv4 length2528. On-wire fragments are1500+1048 IPv4 bytes because each carries its own20-byte IP header.',
 'TShark reassembly-aware ICMP RTT uses request/reply completion frames, e.g.frames2 and4 for first large ping. First-fragment timestamps yield a different interval.',
 'Capture RTT and ping RTT measure different stack boundaries; retain both measurements without claiming bit-identical values.',
 'Time Exceeded error includes outerIPv4/outerICMP then quoted originalIPv4 and at least its first8 payload bytes. Nested TTL1 is observed rather than assumed0.',
 'TTL1 andTTL2 ping captures contain requests only; absence of errors can reflect router ICMP response policy/rate limiting. Traceroute did obtain one first-hop error for its third probe.',
 'Traceroute -I uses ICMP Echo probes here: 12 probes with TTL1..4 and3 per TTL; UDP port-unreachable termination is inapplicable to this recorded run.',
 'Traceroute IP48 bytes =IP20+ICMP8+data20; data are20 zero bytes. Identifier0xf58d stays constant; ICMP seq1..12 and IPv4 ID0xf58e..0xf599 increase.'
]
(ROOT/'facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
lines=['# Experiment4 capture facts','',json.dumps(facts['validation'],ensure_ascii=False),'']
for stem,c in facts['captures'].items():
    lines += [f'## {stem}',f"Frames={c['frames']}; Echo requests={c['echo_requests']}; Echo replies={c['echo_replies']}; Time Exceeded={c['time_exceeded']}; fragmented datagrams={c['fragmented_datagrams']}",'']
    if c['echo_pairs']:
        lines+=['|Request frames|Reply frames|ID|Seq|Data bytes|capture RTT ms|ping RTT ms|','|---|---|---|---|---|---|---|']
        for p in c['echo_pairs']:
            lines.append(f"|{p['request_frames']}|{p['reply_frames']}|{p['identifier']}|{p['sequence']}|{p['icmp_data_length']}|{p['capture_rtt_ms']}|{p.get('ping_rtt_ms','')}|")
        lines.append('')
    if c['time_exceeded_pairs']:
        lines+=['|Probe|Error|Router|Seq|Sent TTL|Quoted TTL|Quoted bytes|capture RTT ms|','|---|---|---|---|---|---|---|---|']
        for p in c['time_exceeded_pairs']:
            lines.append(f"|{p['request_frame']}|{p['error_frame']}|{p['router']}|{p['sequence']}|{p['original_ttl']}|{p['quoted_ttl']}|{p['quote_bytes']}|{p['capture_rtt_ms']}|")
        lines.append('')
lines+=['## Interpretation notes','']+['- '+n for n in facts['notes']]
(ROOT/'facts.md').write_text('\n'.join(lines)+'\n')
(ROOT/'capture-validation.json').write_text(json.dumps(facts['validation'],ensure_ascii=False,indent=2)+'\n')
print(json.dumps(facts['validation'],ensure_ascii=False))
