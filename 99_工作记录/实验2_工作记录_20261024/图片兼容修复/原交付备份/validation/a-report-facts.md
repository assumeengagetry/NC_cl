# A部分真实操作记录（2026-10-24，Packet Tracer 9.0.1）
四台逻辑设备名称均按学号：PC、DNS、HOST、SW；1 PC-PT + 2 Server-PT + Switch-PT。三条Copper Straight-Through：PC Fa0—SW Fa0/1，DNS Fa0—SW Fa1/1，HOST Fa0—SW Fa2/1，均绿。
初始PC 192.168.1.155/24，DNS .199；DNS服务器 .199/24；HOST .200/24；无默认网关（GUI 0.0.0.0）。DNS On，A www.xushengkai.com=.200；CNAME www1.2024141460445.com=www.xushengkai.com。
正常三种ping全部4发4收、0%丢包、TTL128；初始正常测量min/max/avg均0ms（GUI time<1ms）。首次实际直连亦4/4，没有首次ARP丢包。Simulation额外测试A主名出现一次33ms，alias四次4ms，不能混写为初始测试。
实际A响应PDU：IP .199→.155，UDP53→1027，ID0xd1fe，QR1，QNAME www.xushengkai.com，QTYPE1，QD1 AN1 NS0 AR0；Answer A owner www.xushengkai.com，192.168.1.200，CLASS1，TTL86400，length4。截图A07-sim-A-response-RR.png，字段原始读取05-sim-A-response-fields.txt。
实际别名响应PDU：IP .199→.155，UDP53→1028，ID0x6aa9，QR1，QNAME www1.2024141460445.com，QTYPE1，QD1 AN2 NS0 AR0；GUI只展开一个DNS Answer块，owner www.xushengkai.com A .200 TTL86400 CLASS1 length4。不能声称GUI直接显示了第二条CNAME RR的TTL/字段。配置表CNAME与成功解析证明别名映射，PDU ANCOUNT=2但该版本界面只显示上述A块，需如实写此证据范围。截图A09-sim-CNAME-response-RR.png，字段06-sim-CNAME-response-fields.txt。PT显示OPCODE0x1（软件原值），不要改写或当真实公网DNS操作码使用。
故障阶段：只把DNS服务器IP .199→.198，PC保留旧DNS .199，HOST/A均.200。实际IP ping4/4；主名与别名都回显Ping request could not find host ... Please check the name and try again. 没出现缓存暂时成功。DNS超时使用PT原生Fast Forward Time推进后结束。CLI日志07/08/09-fault；截图A10/11/12；故障PC/DNS原生serializeToXml保存为nccl-pt-fault-*.xml。A13-fault-client-DNS是后续对旧DNS配置回看截图（两次都相同实际配置），不伪称故障测试同步瞬间。
修复：PC DNS .198，DNS服务器 .198，HOST .200；GUI配置截图A14，三种测试日志10/11/12-restored和截图A15/16/17（结果待主代理最后确认）。
全部完整截图在attachments/screenshots/full，CLI原始完整累积输出在attachments/packet-tracer；部分早期命令有输入法导致Invalid Command和不支持cls，保留原始日志，报告只引用正式命令测试块，不能声称日志从未有误输入。

最终核验已完成：工程实际重新打开两轮。最后一轮无脚本权限弹窗；文件脚本所有7个临时文件均删除，全部IPC权限为0，并设为Disabled。重新打开PC的IP配置实读0.0.0.0/.198/255.255.255.0/.155，DNS服务器Services On，两条A/CNAME记录正确（A19），DNS接口实读.198/24（A20）。工程独立存在，无外部脚本路径依赖。
恢复实际三种ping均4/4 TTL128。IP首次恢复响应19ms，其余<1ms，统计min0 max19 avg4ms；两个域名均min/max/avg0ms。最终拓扑A01所有身份、角色、地址、域名注记完整。
