# Experiment4 capture facts

{"passed": true, "total_frames": 79, "ipv4_checksums_validated": 79, "icmp_checksums_validated": 69, "quoted_ipv4_checksums_validated": 9, "fragmented_messages_reassembled": 10, "echo_data_byte_equal_pairs": 18, "time_exceeded_quotes_matched": 9, "tshark_rtts_equal_native": true}

## 01-ping-default
Frames=10; Echo requests=5; Echo replies=5; Time Exceeded=0; fragmented datagrams=0

|Request frames|Reply frames|ID|Seq|Data bytes|capture RTT ms|ping RTT ms|
|---|---|---|---|---|---|---|
|[1]|[2]|244|0|56|5.429000|5.759|
|[3]|[4]|244|1|56|5.159000|5.572|
|[5]|[6]|244|2|56|4.702000|5.182|
|[7]|[8]|244|3|56|4.801000|5.036|
|[9]|[10]|244|4|56|4.628000|5.086|

## 02-ping-2500
Frames=20; Echo requests=5; Echo replies=5; Time Exceeded=0; fragmented datagrams=10

|Request frames|Reply frames|ID|Seq|Data bytes|capture RTT ms|ping RTT ms|
|---|---|---|---|---|---|---|
|[1, 2]|[3, 4]|7412|0|2500|5.561000|5.895|
|[5, 6]|[7, 8]|7412|1|2500|5.757000|6.232|
|[9, 10]|[11, 12]|7412|2|2500|5.682000|6.144|
|[13, 14]|[15, 16]|7412|3|2500|5.995000|6.351|
|[17, 18]|[19, 20]|7412|4|2500|5.424000|5.765|

## 03-ping-ttl02
Frames=5; Echo requests=5; Echo replies=0; Time Exceeded=0; fragmented datagrams=0

## 04-ping-ttl01
Frames=5; Echo requests=5; Echo replies=0; Time Exceeded=0; fragmented datagrams=0

## 05-ping-ttl03
Frames=10; Echo requests=5; Echo replies=0; Time Exceeded=5; fragmented datagrams=0

|Probe|Error|Router|Seq|Sent TTL|Quoted TTL|Quoted bytes|capture RTT ms|
|---|---|---|---|---|---|---|---|
|1|2|202.115.39.102|0|3|1|28|15.868000|
|3|4|202.115.39.102|1|3|1|28|7.121000|
|5|6|202.115.39.102|2|3|1|28|8.068000|
|7|8|202.115.39.102|3|3|1|28|7.363000|
|9|10|202.115.39.102|4|3|1|28|7.369000|

## 05-ping-ttl04
Frames=10; Echo requests=5; Echo replies=5; Time Exceeded=0; fragmented datagrams=0

|Request frames|Reply frames|ID|Seq|Data bytes|capture RTT ms|ping RTT ms|
|---|---|---|---|---|---|---|
|[1]|[2]|25845|0|56|3.677000|3.870|
|[3]|[4]|25845|1|56|4.626000|4.955|
|[5]|[6]|25845|2|56|4.367000|4.558|
|[7]|[8]|25845|3|56|5.171000|5.521|
|[9]|[10]|25845|4|56|4.594000|4.980|

## 06-traceroute-icmp
Frames=19; Echo requests=12; Echo replies=3; Time Exceeded=4; fragmented datagrams=0

|Request frames|Reply frames|ID|Seq|Data bytes|capture RTT ms|ping RTT ms|
|---|---|---|---|---|---|---|
|[14]|[15]|62861|10|20|4.086000||
|[16]|[17]|62861|11|20|4.102000||
|[18]|[19]|62861|12|20|2.896000||

|Probe|Error|Router|Seq|Sent TTL|Quoted TTL|Quoted bytes|capture RTT ms|
|---|---|---|---|---|---|---|---|
|3|4|10.134.191.254|3|1|1|48|5.950000|
|8|9|202.115.39.102|7|3|1|28|10.726000|
|10|11|202.115.39.102|8|3|1|28|7.379000|
|12|13|202.115.39.102|9|3|1|28|6.474000|

## Interpretation notes

- Ordinary macOS ping uses 56 ICMP data bytes: its first 8 bytes are timestamp, and Wireshark renders the remaining 48 as Data. ICMP header is a separate 8 bytes.
- ICMP BE Identifier is used for matching. IPv4 Identification identifies the datagram/fragments and is a different field.
- IPv4 fragment-offset field units are 8 bytes: raw value185 equals byte displacement1480. Noninitial fragment has no repeated ICMP header.
- Large-ping reassembled ICMP message is2508 bytes =8+2500; original unfragmented IPv4 length2528. On-wire fragments are1500+1048 IPv4 bytes because each carries its own20-byte IP header.
- TShark reassembly-aware ICMP RTT uses request/reply completion frames, e.g.frames2 and4 for first large ping. First-fragment timestamps yield a different interval.
- Capture RTT and ping RTT measure different stack boundaries; retain both measurements without claiming bit-identical values.
- Time Exceeded error includes outerIPv4/outerICMP then quoted originalIPv4 and at least its first8 payload bytes. Nested TTL1 is observed rather than assumed0.
- TTL1 andTTL2 ping captures contain requests only; absence of errors can reflect router ICMP response policy/rate limiting. Traceroute did obtain one first-hop error for its third probe.
- Traceroute -I uses ICMP Echo probes here: 12 probes with TTL1..4 and3 per TTL; UDP port-unreachable termination is inapplicable to this recorded run.
- Traceroute IP48 bytes =IP20+ICMP8+data20; data are20 zero bytes. Identifier0xf58d stays constant; ICMP seq1..12 and IPv4 ID0xf58e..0xf599 increase.
