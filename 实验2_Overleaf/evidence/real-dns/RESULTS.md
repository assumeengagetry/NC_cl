# 实验2 B部分：真实DNS实验结果（分析题3—10）

**实验日期：2026-10-20；正式命令执行时间：08:48:15—08:48:43 UTC。**

本目录为真实 Linux 操作系统上执行任务3、4所得证据，不是 Packet Tracer 仿真数据。已完成两域名首次/重复 ping、同一公共解析器上的四次 nslookup、8份实验专用 pcapng、逐阶段原始终端输出、TShark字段与报文详情、结构化结果与13张真实GUI截图。**未完成的指导书条件是“成功清除并展示本机DNS缓存”：本机没有可用且获授权的对应机制，不能把本轮首次测量称为已验证的冷缓存实验。**

## 1. 环境、接口与方法

- 操作系统：Arch Linux，内核 `7.2.9-arch1-1`。
- TShark/Wireshark：`4.7.4`；BIND nslookup：`9.20.29`；ping：iputils `20250605`。
- 物理外网接口：`wlo1`；IPv4 `10.20.41.171`，经 `10.20.41.1` 路由。
- 系统解析器：`/etc/resolv.conf` 中配置 `100.100.100.100` 与 `fd7a:115c:a1e0::53`。正式任务3实际使用 IPv4 `100.100.100.100`，客户端 `100.102.60.66`，DNS出现在真实虚拟隧道接口 `tailscale0`；ping的ICMP出现在物理接口 `wlo1`。**不能把任务3的DNS端点误写成物理接口IPv4，也不能把系统代理地址写成远端权威服务器。**
- 任务4显式选定公共解析器 `223.5.5.5`，四次查询均经 `wlo1`，客户端为 `10.20.41.171`。
- 任务3实际命令为 `ping -4 -n -c 3 -W 2 域名`。`-4`限制最终ICMP为IPv4，`-n`避免反向解析引入额外域名；**本机实际仍产生了 A、AAAA 两类DNS查询**，不能因使用 `-4` 就删去或忽略抓到的AAAA证据。
- 在两个域名的本轮首次ping前，实际尝试了 `resolvectl flush-caches`，均退出1，提示无法连接本机 resolved 服务。重复ping之间没有再清缓存。相关失败原文分别在 `01-...-flush-attempt.txt` 与 `03-...-flush-attempt.txt`。
- `systemd-resolved`、`dnsmasq`、`nscd` 均inactive；`resolvectl status`、`show-cache`、`statistics` 均失败；`ipconfig`、`nscd`、`dnsmasq` 可执行程序未安装。`tailscaled` active，但其 `tailscale dns --help` 只列出status/query，没有清理/转储DNS缓存子命令。未使用会影响现有服务/VPN的替代办法，未修改系统配置。
- 两个实验域名不在 `/etc/hosts` 中。完整、经过隐私最小化选择的环境检查见 `00-environment-cache-check.txt`。

### 1.1 抓包与隐私最小化

`dumpcap` 在继承 `wireshark` 组的子shell中运行，不使用sudo。任务3在 `tailscale0` 上仅采集与配置解析器之间的53端口流量，并在 `wlo1` 上采集本机ICMP；任务4仅采集与 `223.5.5.5` 的53端口流量。每阶段均在实际命令前启动采集，命令结束后停止。

随后使用真实DNS字段导出：

```text
dns && (dns.qry.name == "www.baidu.com" || dns.qry.name == "www.scu.edu.cn")
```

任务3额外保留 `icmp && ip.addr == 实际ping目标地址`。每阶段的完整命令、捕获过滤器与导出显示过滤器在对应 `*-capture.txt` 中。**未修改、合成、重放任何网络报文**；导出仅删除无关报文并重新编号。全部答案与截图均引用本目录最终交付pcapng的帧号。

未经筛选的临时捕获可能包含无关DNS，仅留在 `/tmp/opencode/nc-cl-exp2/B/`，不进入报告工程。`verification.json` 记录了临时与交付文件的SHA-256和包数，并用pcapng的EPB逐包核对：交付文件中每一帧的**报文字节、原始长度和纳秒时间戳**都能在对应原始捕获中找到，未改写报文。

## 2. 证据文件总表

下表中的“文件01”等简称只在本文使用；文件名中的编号是阶段编号，不是最终报告图号。

| 简称 | 最终pcapng文件 | 总帧数 | DNS帧 | ICMP帧 |
|---|---|---:|---|---|
| 文件01 | `01-task3-baidu-first.pcapng` | 10 | 1—4 | 5—10，3请求+3响应 |
| 文件02 | `02-task3-baidu-repeat.pcapng` | 10 | 1—4 | 5—10，3请求+3响应 |
| 文件03 | `03-task3-scu-first.pcapng` | 7 | 1—4 | 5—7，只有3请求 |
| 文件04 | `04-task3-scu-repeat.pcapng` | 7 | 1—4 | 5—7，只有3请求 |
| 文件05 | `05-task4-baidu-a.pcapng` | 2 | 1查询、2响应 | 无 |
| 文件06 | `06-task4-baidu-cname.pcapng` | 2 | 1查询、2响应 | 无 |
| 文件07 | `07-task4-scu-a.pcapng` | 2 | 1查询、2响应 | 无 |
| 文件08 | `08-task4-scu-cname.pcapng` | 2 | 1查询、2响应 | 无 |

所有8阶段合计42帧，其中24帧DNS构成12组完整事务。机器可读矩阵为 `data-matrix.csv`，分Answers/Authority/Additional的详细记录为 `results.json`；各阶段另有 `*-fields.tsv`、`*-dns-details.txt`、`*-packet-json.json`。

## 分析题3：源/目的IP、传输层与端口

所有本次捕获的DNS事务均为 **IPv4 + UDP**，服务端端口53。下表列查询方向；每个响应的IP和端口完全反向。

| 文件 | 域名 | QTYPE | 查询源IP:端口 | 查询目的IP:端口 | 查询帧→响应帧 |
|---|---|---|---|---|---|
| 01 | www.baidu.com | A | 100.102.60.66:40546 | 100.100.100.100:53 | 1→3 |
| 01 | www.baidu.com | AAAA | 100.102.60.66:40546 | 100.100.100.100:53 | 2→4 |
| 02 | www.baidu.com | A | 100.102.60.66:58834 | 100.100.100.100:53 | 1→3 |
| 02 | www.baidu.com | AAAA | 100.102.60.66:58834 | 100.100.100.100:53 | 2→4 |
| 03 | www.scu.edu.cn | A | 100.102.60.66:57380 | 100.100.100.100:53 | 1→3 |
| 03 | www.scu.edu.cn | AAAA | 100.102.60.66:57380 | 100.100.100.100:53 | 2→4 |
| 04 | www.scu.edu.cn | A | 100.102.60.66:49997 | 100.100.100.100:53 | 1→3 |
| 04 | www.scu.edu.cn | AAAA | 100.102.60.66:49997 | 100.100.100.100:53 | 2→4 |
| 05 | www.baidu.com | A | 10.20.41.171:43043 | 223.5.5.5:53 | 1→2 |
| 06 | www.baidu.com | CNAME | 10.20.41.171:50414 | 223.5.5.5:53 | 1→2 |
| 07 | www.scu.edu.cn | A | 10.20.41.171:59091 | 223.5.5.5:53 | 1→2 |
| 08 | www.scu.edu.cn | CNAME | 10.20.41.171:37510 | 223.5.5.5:53 | 1→2 |

例如文件01帧1为 `100.102.60.66:40546 → 100.100.100.100:53`；帧3为 `100.100.100.100:53 → 100.102.60.66:40546`。本次没有观察到TCP，不能据此推断DNS永远只用UDP。

## 分析题4：事务ID、QR与配对依据

| 文件 | QTYPE | 查询ID = 响应ID | 查询帧/QR | 响应帧/QR |
|---|---|---|---|---|
| 01 | A | `0x8af4` | 1 / 0 | 3 / 1 |
| 01 | AAAA | `0x55f6` | 2 / 0 | 4 / 1 |
| 02 | A | `0x98fc` | 1 / 0 | 3 / 1 |
| 02 | AAAA | `0x93fd` | 2 / 0 | 4 / 1 |
| 03 | A | `0x5a37` | 1 / 0 | 3 / 1 |
| 03 | AAAA | `0x5c34` | 2 / 0 | 4 / 1 |
| 04 | A | `0xa351` | 1 / 0 | 3 / 1 |
| 04 | AAAA | `0x22ac` | 2 / 0 | 4 / 1 |
| 05 | A | `0x4fd0` | 1 / 0 | 2 / 1 |
| 06 | CNAME | `0x54f1` | 1 / 0 | 2 / 1 |
| 07 | A | `0xfe71` | 1 / 0 | 2 / 1 |
| 08 | CNAME | `0x7265` | 1 / 0 | 2 / 1 |

`QR=0`表示查询，`QR=1`表示响应。配对不仅比较ID，还同时核对**反向的源/目的IP和UDP端口、相同QNAME/QTYPE、时间先后**。已用TShark两遍解析的 `dns.response_in` 与 `dns.response_to` 交叉验证所有12组事务；不能只靠一个16位ID做全局唯一配对。字段名首先以本机 `tshark -G fields` 核实，见 `01-tshark-field-definitions.tsv`。

## 分析题5：资源记录、权威性与最终ping地址

### 5.1 与解析目标直接相关的Answer/负回答

下表TTL单位均为秒，逐值来自最终pcapng。SOA位于Authority区，不是Answer区。

| 文件/响应帧 | QTYPE | Answer区结果 | TTL | Authority区重点 |
|---|---|---|---|---|
| 01/3 | A | `www.baidu.com CNAME www.a.shifen.com`；规范名的A为 `110.242.70.57`、`110.242.69.21` | CNAME 868；两个A均83 | 4条 `shifen.com NS`，TTL均43150 |
| 01/4 | AAAA | 同一CNAME；规范名的AAAA为 `2408:871a:2100:1b23:0:ff:b07a:7ebc`、`2408:871a:2100:186c:0:ff:b07e:3fbc` | CNAME 868；两个AAAA均426 | 无 |
| 02/3 | A | 同一CNAME、同两个A且顺序不变 | CNAME 864；两个A均79 | 无 |
| 02/4 | AAAA | 同一CNAME、同两个AAAA | CNAME 864；两个AAAA均422 | 无 |
| 03/3 | A | `www.scu.edu.cn A 202.115.47.167`，未见CNAME | A 239 | 6条 `edu.cn NS`，TTL均118043 |
| 03/4 | AAAA | 0 Answer，RCODE=0 | 无Answer TTL | `scu.edu.cn SOA`，TTL216；MNAME=`dart.scu.edu.cn`，MINIMUM=600 |
| 04/3 | A | 同一直接A | A 233 | 无 |
| 04/4 | AAAA | 0 Answer，RCODE=0 | 无Answer TTL | 同一SOA，TTL210，MINIMUM=600 |

文件01帧3还有7条Additional区A/AAAA；文件03帧3还有8条Additional区A。这些是所列NS的地址，不是被ping网站的最终地址；详情在JSON和 `*-dns-details.txt` 中逐条保留，不能把 `tshark -e dns.a` 聚合输出中的所有地址都当成目标地址。

### 5.2 是否权威

**所有12个DNS响应均为 `Flags=0x8180`、`QR=1, AA=0, RD=1, RA=1, TC=0, RCODE=0`。** 因 `AA=0`，本机看到的都是非权威回答。即使Authority区包含NS/SOA，也不代表该响应具有 `AA=1`；nslookup输出的“Authoritative answers can be found from”也不能代替AA位判断。

### 5.3 最终ping地址及ICMP结果

| 域名/阶段 | ping实际使用地址 | 发送/收到 | 丢包 | pcapng证据 |
|---|---|---|---|---|
| 百度本轮首次 | `110.242.70.57` | 3/3 | 0% | 文件01帧5—10 |
| 百度重复 | `110.242.70.57` | 3/3 | 0% | 文件02帧5—10 |
| 川大本轮首次 | `202.115.47.167` | 3/0 | 100% | 文件03帧5—7，仅Echo Request |
| 川大重复 | `202.115.47.167` | 3/0 | 100% | 文件04帧5—7，仅Echo Request |

百度终端显示 `PING www.a.shifen.com (110.242.70.57)`，与CNAME及捕获的ICMP目的地址一致。川大的DNS A响应成功，且ping已经向该IP发出ICMP，因此不能把ICMP无响应误判为DNS解析失败；仅凭本次证据不能确定是目标禁ping、链路过滤还是其他原因。

## 分析题6：是否别名与规范名

- **`www.baidu.com` 在本次观察中是别名**：文件01/02帧3、4均有所有者为 `www.baidu.com` 的CNAME，直接指向规范名 `www.a.shifen.com`；没有观察到更长CNAME链。
- **`www.scu.edu.cn` 在本次观察中不是CNAME别名**：文件03/04帧3直接给出其自身A记录，没有CNAME。单凭“没看到”证据较弱，任务4同名CNAME专门查询得到NOERROR/NODATA，从另一个解析器视角进一步支持该判断。
- 结论限定于 **2026-10-20、所用解析器与当前DNS视图**，不应写成所有地点、所有时间永远如此。

## 分析题7：客户端查询属于递归还是迭代

所有查询的DNS头实际为 `0x0100`，`QR=0, RD=1`，即客户端**请求递归解析**；所有响应 `RA=1` 表明当前服务器提供递归服务。客户端把同一完整问题交给其解析器，而没有在抓包中逐级查询根、顶级域和权威服务器，所以本次客户端—解析器交互按递归查询方式解释，而不是客户端自己执行迭代查询。

需区分：`RD=1` 是请求意愿，`RA=1` 是服务能力；它们**不证明该次服务端真的访问了根服务器或完成了全程递归**，服务器也可能命中缓存、转发给上游。此次没有捕获代理的全程上游解析链路，不能把未观察到的迭代步骤写成实测事实。

## 分析题8：首次/重复变化及缓存判断

**实际现象不是“重复ping没有DNS包”**：文件01—04每阶段都各有A查询、AAAA查询及各自响应。重复时事务ID和客户端UDP源端口均变更，表明本机再次发出新DNS事务；因此未观察到Windows式本地缓存直接消除客户端DNS查询的现象。

| 比较项 | 首次测量 | 不再次清缓存的重复测量 | 结论 |
|---|---|---|---|
| 百度A链 | 文件01/3：CNAME TTL868，A TTL83 | 文件02/3：CNAME TTL864，A TTL79 | 地址相同，TTL递减4秒 |
| 百度AAAA链 | 文件01/4：CNAME TTL868，AAAA TTL426 | 文件02/4：CNAME TTL864，AAAA TTL422 | 同样递减4秒 |
| 川大A | 文件03/3：TTL239 | 文件04/3：TTL233 | 同一地址，TTL递减6秒 |
| 川大AAAA负回答SOA | 文件03/4：SOA TTL216，MINIMUM600 | 文件04/4：SOA TTL210，MINIMUM600 | 剩余负缓存TTL递减6秒，MINIMUM本身不变 |
| 百度A响应区段 | 文件01/3：Answer3、Authority4、Additional7 | 文件02/3：Answer3、Authority0、Additional0 | 重复响应更精简，但AA仍为0 |
| 川大A响应区段 | 文件03/3：Answer1、Authority6、Additional8 | 文件04/3：Answer1、Authority0、Additional0 | 重复响应更精简，但AA仍为0 |

相同RR数据、TTL随时间减少且响应变精简，**与解析链路中缓存复用相符，支持存在缓存影响的解释**，但仅靠客户端侧抓包不能定位缓存究竟在Tailscale代理、上游递归解析器还是更远处，不能声称已证明某一特定本地缓存命中。响应耗时也不是可靠单独指标：百度A从约7.85ms到2.72ms，但川大A从约10.85ms到81.00ms，重复并非总更快。

本平台不能提供 `ipconfig /flushdns` 与 `/displaydns` 的成功截图；真实失败原文已保存。**首次仅指本轮首次测量，既有代理/上游缓存和先前查询影响未被排除，禁止写“已清空”“冷缓存”“本机没有任何缓存”或补造缺失查询。**

## 分析题9：A查询与CNAME查询的结果差异

四条实际命令均指定同一可达解析器与绝对域名（末尾点）：

```sh
nslookup -type=A www.baidu.com. 223.5.5.5
nslookup -type=CNAME www.baidu.com. 223.5.5.5
nslookup -type=A www.scu.edu.cn. 223.5.5.5
nslookup -type=CNAME www.scu.edu.cn. 223.5.5.5
```

| 文件/帧 | 问题类型 | ANCOUNT/NSCOUNT/ARCOUNT | 实际响应内容与TTL |
|---|---|---|---|
| 05/2 | 百度 A(1) | 3/0/0 | `www.baidu.com CNAME www.a.shifen.com` TTL277；后者A `110.242.69.21` 与 `110.242.70.57`，各TTL82 |
| 06/2 | 百度 CNAME(5) | 1/0/0 | 仅CNAME指向 `www.a.shifen.com`，TTL277，**没有最终A** |
| 07/2 | 川大 A(1) | 1/0/0 | `www.scu.edu.cn A 202.115.47.167`，TTL38 |
| 08/2 | 川大 CNAME(5) | 0/1/0 | Answer为空；Authority为 `scu.edu.cn SOA`，TTL600，MNAME=`dart.scu.edu.cn`，MINIMUM600 |

A查询请求IPv4地址；若该名称是别名，本次百度响应在Answer中同时带回CNAME链和规范名的A记录。CNAME查询只请求“该名字是否有CNAME及其目标”，本次百度只返回CNAME，不自动保证返回最终A。川大有直接A但没有CNAME，所以两种查询返回不同的Answer内容。

任务3与任务4使用的解析器不同，同一RR的剩余TTL不同并不矛盾，也不应将任务4的TTL直接替换任务3实测值；A地址顺序不同不等于地址集合不同。

## 分析题10：两个CNAME专门查询是否支持先前判断

- 文件06帧1/2：事务 `0x54f1`，`QTYPE=CNAME(5)`，RCODE=0、Answer=1，确切CNAME为 **`www.baidu.com → www.a.shifen.com`**，支持任务3的百度别名判断。
- 文件08帧1/2：事务 `0x7265`，`QTYPE=CNAME(5)`，`Flags=0x8180`，**RCODE=0(NOERROR)、Answer=0、Authority=1(SOA)**。这属于本次“没有所请求CNAME类型记录”的 **NOERROR/NODATA**，不是 `RCODE=3(NXDOMAIN)`。文件07的A回答同时证明同名A存在，因此不能将 `*** Can't find ...: No answer` 误读为名字不存在。该结果支持任务3“川大域名为直接A、未见CNAME”的判断。
- SOA处于Authority区以及nslookup的提示语都不改变该响应的 `AA=0`；不能写成“查询到权威CNAME”或“川大CNAME指向SOA的MNAME”。SOA中的 `dart.scu.edu.cn` 是区域主名称服务器，不是 `www.scu.edu.cn` 的别名目标。

## 3. 截图索引与真实性说明

全部截图直接用ImageMagick `import` 从独立 **Xvfb :89** 中截取，未导入日常桌面、登录态或Cookies，没有绘制/仿造Wireshark界面，也没有在截图上覆盖字段。

| 截图文件 | 内容 | 最终文件/帧号 |
|---|---|---|
| `screenshot-01-wireshark-baidu-first-A.png` | 真正Wireshark，百度首次A响应：ID、AA/RD/RA、CNAME与A的TTL | 文件01/3；列表同时显示1—4 |
| `screenshot-02-wireshark-baidu-repeat-A.png` | 真正Wireshark，百度重复A响应及TTL864/79 | 文件02/3 |
| `screenshot-03-wireshark-scu-first-A.png` | 真正Wireshark，川大首次直接A、TTL239 | 文件03/3 |
| `screenshot-04-wireshark-scu-repeat-A.png` | 真正Wireshark，川大重复A、TTL233 | 文件04/3 |
| `screenshot-05-wireshark-nslookup-baidu-A.png` | 真正Wireshark，A查询同时返回CNAME及两个A | 文件05/2 |
| `screenshot-06-wireshark-nslookup-baidu-CNAME.png` | 真正Wireshark，CNAME专门查询仅1条CNAME | 文件06/2 |
| `screenshot-07-wireshark-nslookup-scu-A.png` | 真正Wireshark，川大A专门查询 | 文件07/2 |
| `screenshot-08-wireshark-nslookup-scu-CNAME.png` | 真正Wireshark，NOERROR、0 Answer、SOA及TTL600、AA=0 | 文件08/2 |
| `screenshot-09-terminal-ping-baidu-replay.png` | 真正Konsole，读取百度两阶段原始日志 | 文件01/02的 `*-terminal.txt` |
| `screenshot-10-terminal-ping-scu-replay.png` | 真正Konsole，读取川大两阶段原始日志 | 文件03/04的 `*-terminal.txt` |
| `screenshot-11-terminal-nslookup-baidu-replay.png` | 真正Konsole，读取百度A/CNAME原始日志 | 文件05/06的 `*-terminal.txt` |
| `screenshot-12-terminal-nslookup-scu-replay.png` | 真正Konsole，读取川大A/CNAME原始日志 | 文件07/08的 `*-terminal.txt` |
| `screenshot-13-terminal-cache-flush-failure-replay.png` | 真正Konsole，读取两次清缓存失败原文 | 两个 `*-flush-attempt.txt` |

**终端截图是保存日志的只读展示，不是同时实时执行的第二轮实验。** 画面顶部明确标记 `READ-ONLY REPLAY OF REAL CAPTURE-TIME LOGS`，命令的实际输出原文由 `cat` 直接读取，未替换数值、未模拟输出；实际网络命令的UTC起止时间在原始日志中。将它们用于报告时请将图注写为“真实命令原始输出（日志回显）”，不要误称为新的实时测量。

## 4. 核验、限制与交接

- `verification.json`：8份pcapng全部逐字节/时间戳匹配原始捕获；12组事务全部按ID、问题、反向端点配对，并与TShark响应关联字段一致。
- `data-matrix.csv` 与 `results.json`：覆盖分析题3—10的可机读实测值，RR分区避免混淆Additional地址与目标地址。
- `*-dns-details.txt`：对最终交付pcapng执行 `tshark -2 -n -r 文件 -Y dns -V` 的原生详细输出，可独立查看全部RR与flags。
- `01-tshark-field-definitions.tsv`：本机TShark字段定义证据；查询包的AA/RA在TShark树中可能不展示，机器结果中对应位由实际头部 `dns.flags` 解码，并与响应中展示的AA/RA字段核对，未将字段空白误认为缺包。
- `SHA256SUMS`：最终全部证据文件的哈希（不含自身）。
- 关键限制：清缓存/本地缓存展示未能完成；首次不是已验证冷缓存；任务3是系统代理接口DNS、不是公网解析器直连；未捕获完整上游递归/迭代链路；川大ICMP未通但DNS成功；结论不外推至其他时间/解析器。
- 没有变更 `/etc/resolv.conf`、停用VPN、重启/停止现有服务、安装全局依赖，未在公网查询任何PT专用身份域名，未修改A部分、报告主文件或实验1文件。
- 捕获命令均已自然退出；GUI截图完成后关闭本代理创建的Konsole、Wireshark和Xvfb :89，不影响其他显示或主代理的:88。
