# B部分实测事实及可用于报告的文字（独立审计版）

本文件只引用 **2026年10月24日这台Mac的本轮测量**。下文帧号全部指最终提交文件 `2024141460445_许盛凯_实验2_DNS.pcapng`，不是各阶段分文件内的帧号。该文件共30帧：12帧DNS组成6组完整事务，18帧ICMP。SHA-256为 `9d6478264dd180322bfeaa24cb43b30d5f15fa019f6ca31bd814b6eaee2c85c9`。已独立对照最终pcapng的TShark解码、JSON和原始日志；数值一致。不能使用旧Linux证据中的地址、TTL、12组事务或清缓存失败结论。

以下图引用使用LaTeX标签占位，由主报告按实际图出现次序生成图号。若合并图片，应保留相应标签或同步替换引用，不能在没有图片时保留空标签。

## 可填入“实验环境”的文字

实际操作系统为macOS 26.7.1（构建25G241），Wireshark及其自带TShark/dumpcap为4.6.7。真实网络抓包同时监听Wi-Fi接口en0和Tailscale虚拟接口utun4。en0上的本机IPv4为10.20.41.180；系统解析器的实际DNS报文经utun4，由100.96.206.115发往100.100.100.100:53。四种nslookup均显式指定同一可达解析器223.5.5.5，经en0发送。本轮没有修改DNS、路由、网络服务或VPN配置。Wi-Fi服务中原有114.114.114.114配置不等于本次ping实际使用的解析器，分析以抓包端点为准。

本轮真实命令执行时间为2026年10月24日16:38:43.817至16:39:13.343（Asia/Shanghai，UTC+8）；首次抓包开始于16:38:41.735，最后抓包于16:39:14.272结束。实验日期填写2026年10月24日。课时不能由上述32秒命令时间或第3—4节推算，仍应按课程证据确定。

## 可填入“实验内容/操作过程”的文字

1. 用Wireshark自带dumpcap在真实接口en0、utun4启动采集。在en0只采集与223.5.5.5的53端口流量及本机ICMP，在utun4只采集与100.100.100.100的53端口流量。每阶段先启动抓包，再执行命令，结束后停止抓包。
2. 在www.baidu.com及www.scu.edu.cn各自首次ping前，以管理员权限分别执行 `dscacheutil -flushcache` 和 `killall -HUP mDNSResponder`，两条命令均退出0。百度前时间为16:38:42，川大前为16:38:52。随后以普通用户身份执行 `ping -n -c 3 -W 1500 -t 8 域名`；在同一域名重复ping前不再清缓存。macOS的-W单位为毫秒，-t单位为秒，未套用Windows或Linux参数。见图\ref{fig:mac-cache}、图\ref{fig:mac-ping-baidu}、图\ref{fig:mac-ping-scu}。
3. 尝试 `dscacheutil -cachedump`，两次实际输出均为 `Unable to get details from the cache node`，虽进程退出0，也不能写成已成功显示缓存。清缓存命令成功与缓存条目转储失败是两件不同的事。本轮可通过首次有DNS、重复无DNS的报文变化分析缓存，但没有可提交的本机缓存条目清单。也没有清空Tailscale代理或公网递归解析器缓存，不能称为完整DNS链路冷缓存实验。
4. 依次执行四条指定的nslookup命令（如下），四条均真实完成并抓到对应查询与响应：

```sh
nslookup -type=A www.baidu.com. 223.5.5.5
nslookup -type=CNAME www.baidu.com. 223.5.5.5
nslookup -type=A www.scu.edu.cn. 223.5.5.5
nslookup -type=CNAME www.scu.edu.cn. 223.5.5.5
```

5. 用显示过滤器 `dns && (dns.qry.name == "www.baidu.com" || dns.qry.name == "www.scu.edu.cn")` 保留实验DNS；ping阶段额外保留 `icmp && ip.addr == 实际ping地址`。八个阶段筛选后按原始时间戳合并为最终pcapng，帧号重新统一为1—30。筛选没有改写报文字节或时间戳，逐包核验为真；未经筛选的临时捕获不进入交付工程。各阶段捕获过滤器、导出过滤器及时间在 `*-capture.txt` 和 `phases.json` 中保留。

## 数据记录：四次ping和帧范围

| 测试 | 命令开始时间（UTC+8） | 最终文件帧范围 | DNS情况 | ping实际地址 | 发送/收到 | 丢包率 |
|---|---|---|---|---|---|---|
| 百度首次 | 16:38:43.817 | 1—8 | 帧1查询、2响应 | 183.2.172.177 | 3/3 | 0.0% |
| 百度重复 | 16:38:48.140 | 9—14 | 没有该域名DNS报文 | 183.2.172.177 | 3/3 | 0.0% |
| 川大首次 | 16:38:53.498 | 15—19 | 帧15查询、16响应 | 202.115.47.167 | 3/0 | 100.0% |
| 川大重复 | 16:39:00.107 | 20—22 | 没有该域名DNS报文 | 202.115.47.167 | 3/0 | 100.0% |

百度两次往返时间min/avg/max分别为38.089/40.282/44.610 ms和38.297/40.546/44.943 ms。川大两次ping进程退出2，统计显示3发0收；帧17—19及20—22均是发往202.115.47.167的Echo Request。本次没有Echo Reply，不能进一步断定是服务器禁止ICMP还是链路过滤。见图\ref{fig:mac-ping-baidu}、图\ref{fig:mac-ping-scu}、图\ref{fig:dns-first-baidu}、图\ref{fig:dns-first-scu}、图\ref{fig:dns-repeat}。

## 分析题3：DNS查询和响应的IP、协议及端口

本轮6组DNS事务均为IPv4上的UDP。查询目的端口均为53，响应源端口为53，响应的IP与端口相对查询完全反向。

| 查询帧→响应帧 | 用途/问题 | 查询源IP:端口 | 查询目的IP:端口 | 接口 |
|---|---|---|---|---|
| 1→2 | 百度首次ping，A(1) | 100.96.206.115:52347 | 100.100.100.100:53 | utun4 |
| 15→16 | 川大首次ping，A(1) | 100.96.206.115:58581 | 100.100.100.100:53 | utun4 |
| 23→24 | 百度nslookup，A(1) | 10.20.41.180:54482 | 223.5.5.5:53 | en0 |
| 25→26 | 百度nslookup，CNAME(5) | 10.20.41.180:54278 | 223.5.5.5:53 | en0 |
| 27→28 | 川大nslookup，A(1) | 10.20.41.180:64055 | 223.5.5.5:53 | en0 |
| 29→30 | 川大nslookup，CNAME(5) | 10.20.41.180:49628 | 223.5.5.5:53 | en0 |

例如帧1为100.96.206.115:52347→100.100.100.100:53，帧2为100.100.100.100:53→100.96.206.115:52347。图\ref{fig:dns-first-baidu}与图\ref{fig:ns-baidu-a}分别展示系统解析路径和显式公网解析路径。DNS端点不要与en0的ICMP端点混写。本次没有观察到DNS TCP，不能外推为DNS只能使用UDP。

## 分析题4：事务ID、QR与请求响应配对

| 查询帧→响应帧 | Transaction ID | QNAME | QTYPE | 响应延时 |
|---|---|---|---|---|
| 1→2 | 0xa06b | www.baidu.com | A(1) | 39.067 ms |
| 15→16 | 0x42ae | www.scu.edu.cn | A(1) | 36.420 ms |
| 23→24 | 0x706e | www.baidu.com | A(1) | 8.574 ms |
| 25→26 | 0xfe02 | www.baidu.com | CNAME(5) | 8.987 ms |
| 27→28 | 0x9c7e | www.scu.edu.cn | A(1) | 14.043 ms |
| 29→30 | 0x010d | www.scu.edu.cn | CNAME(5) | 23.671 ms |

所有查询QR=0、Flags=0x0100；所有响应QR=1、Flags=0x8180。QR用于区分查询和响应。配对时同时核对事务ID、相同QNAME/QTYPE、源/目的IP与UDP端口的反向对应，以及查询先于响应的时间关系；还以TShark的response_in/response_to关联字段交叉核验。不能只把16位ID当作全局唯一标识。见图\ref{fig:dns-first-baidu}、图\ref{fig:dns-first-scu}及图\ref{fig:ns-scu-cname}；所有帧号均属于最终pcapng。

## 分析题5：资源记录、权威性及ping最终使用的地址

本轮所有DNS记录CLASS均为IN(1)。各响应完整分区如下（TTL单位秒）：

| 响应帧 | Answer区资源记录 | Authority区 | Additional区 | AN/NS/AR |
|---|---|---|---|---|
| 2 | www.baidu.com CNAME www.a.shifen.com，TTL1001；www.a.shifen.com A 183.2.172.177，TTL606 | 空 | 空 | 2/0/0 |
| 16 | www.scu.edu.cn A 202.115.47.167，TTL606 | 空 | 空 | 1/0/0 |
| 24 | www.baidu.com CNAME www.a.shifen.com，TTL1094；www.a.shifen.com A 110.242.70.57及110.242.69.21，两个TTL均29 | 空 | 空 | 3/0/0 |
| 26 | www.baidu.com CNAME www.a.shifen.com，TTL1072 | 空 | 空 | 1/0/0 |
| 28 | www.scu.edu.cn A 202.115.47.167，TTL600 | 空 | 空 | 1/0/0 |
| 30 | 空 | scu.edu.cn SOA，TTL600 | 空 | 0/1/0 |

帧30的SOA字段为MNAME=dart.scu.edu.cn，RNAME=root@scu.edu.cn，SERIAL=2024110590，REFRESH=1200，RETRY=1200，EXPIRE=1209600，MINIMUM=600。SOA位于Authority区，其中MNAME是区域主名称服务器，不能当成网站的CNAME目标。见图\ref{fig:ns-scu-cname}。

6个响应均为AA=0、RD=1、RA=1、RCODE=0(NOERROR)、TC=0，因此本机观察到的均为非权威回答，且未截断；Authority区存在SOA也不改变AA=0的事实。百度ping最终地址为系统DNS响应帧2给出的183.2.172.177，对应帧3—14的ICMP；川大ping最终地址为帧16给出的202.115.47.167，对应帧17—22的ICMP。百度nslookup经另一解析器返回110.242.70.57与110.242.69.21，不能把它们改写为本次ping实际目标；不同解析器/视图的结果可以不同，现有证据不足以确定差异的具体上游原因。见图\ref{fig:dns-first-baidu}、图\ref{fig:dns-first-scu}、图\ref{fig:mac-ping-baidu}、图\ref{fig:ns-baidu-a}。

川大已经获得成功的A回答并向其地址发送ICMP，因此ICMP无响应不能写成DNS解析失败。

## 分析题6：两个域名是否为别名及规范名

本次www.baidu.com是CNAME别名：帧2、24、26均明确返回 `www.baidu.com CNAME www.a.shifen.com`，其直接规范名为www.a.shifen.com。帧16和28直接返回www.scu.edu.cn自身的A记录，未见CNAME；帧30的CNAME专门查询又返回NOERROR且Answer=0，支持本次www.scu.edu.cn为直接A、没有该名称CNAME记录的判断。见图\ref{fig:dns-first-baidu}、图\ref{fig:dns-first-scu}、图\ref{fig:ns-baidu-cname}、图\ref{fig:ns-scu-cname}。结论限定于2026年10月24日所用解析器及其DNS视图，不外推为永久性质。

## 分析题7：递归或迭代的判断及证据范围

6个查询头部均有RD=1，表示客户端请求递归解析；6个响应均RA=1，表示当前解析器具备递归服务能力。客户端将完整问题发给所选解析器并接收最终回答，本次客户端—解析器交互按递归查询解释。抓包没有显示客户端逐级查询根、顶级域和权威服务器的迭代过程。见图\ref{fig:dns-first-baidu}、图\ref{fig:ns-baidu-a}。

RD表示请求意愿，RA表示服务器能力；它们不能证明该次解析器确实访问了根服务器。服务器可能从缓存回答或转发至上游。本轮只采集本机接口的相关流量，未观察到远端解析器的完整上游链路，不能声称抓到了完整根/TLD/权威递归过程。

## 分析题8：首次、重复ping的DNS变化与缓存分析

百度首次ping出现一组A查询/响应（帧1、2），随后发送3组ICMP请求与响应（帧3—8）；不清缓存重复时只出现3组ICMP请求与响应（帧9—14），没有该域名DNS报文。川大首次出现一组A查询/响应（帧15、16）和3个ICMP请求（帧17—19）；不清缓存重复时仅出现3个ICMP请求（帧20—22），同样没有该域名DNS报文。两域名重复ping仍使用与首次相同的IP。见图\ref{fig:dns-repeat}、图\ref{fig:mac-ping-baidu}、图\ref{fig:mac-ping-scu}。

在首次前清理本机系统缓存、重复间不再清理的条件下，重复ping在所监测解析路径上未再次发出DNS查询而仍获得同一地址，支持有效DNS缓存被复用的解释。首次响应TTL分别包括百度CNAME1001秒、百度A606秒、川大A606秒；重复发生在数秒后，均处于这些TTL内。但重复阶段没有DNS响应，不能编造“重复响应TTL递减”的数据，也不能仅由本机抓包精确定位缓存在哪一个组件。

两次 `dscacheutil -cachedump` 都无法返回缓存节点详情，故未成功直接展示缓存条目；应把这项限制写入小结。成功清理的是本机系统DNS缓存，不包括Tailscale代理、上游递归服务器的缓存。以上是当前路径和采集窗口内的现象，不能宣称所有接口或所有可能加密DNS路径绝对无查询。

## 分析题9：A与CNAME查询的实际差异

四次nslookup统一使用223.5.5.5。A查询请求IPv4地址记录（QTYPE=1），CNAME查询请求别名指向关系（QTYPE=5）。百度A查询帧23→24在Answer中带回一条CNAME和规范名的两条A记录；百度CNAME查询帧25→26只带回一条CNAME，没有最终A。川大A查询帧27→28带回自身A记录；CNAME查询帧29→30的Answer为空，Authority中带回SOA。实际各分区记录、TTL见题5表。见图\ref{fig:ns-baidu-a}、图\ref{fig:ns-baidu-cname}、图\ref{fig:ns-scu-a}、图\ref{fig:ns-scu-cname}。

这说明A查询响应可以附带解析地址所需的CNAME链，而CNAME查询不必同时返回最终IPv4地址。本轮不同查询的剩余TTL不同，不能拿nslookup两种类型的TTL替代重复ping的缓存测量。

## 分析题10：CNAME专门查询是否支持此前别名判断

百度CNAME查询ID为0xfe02（帧25、26），响应Answer=1，明确给出www.baidu.com→www.a.shifen.com，TTL1072秒，支持此前百度为别名的判断。川大CNAME查询ID为0x010d（帧29、30），响应RCODE=0、Answer=0、Authority=1(SOA)，属于本次所请求CNAME类型没有数据的NOERROR/NODATA；它不是RCODE=3的NXDOMAIN。帧28同名A记录的存在也说明不能把nslookup显示的“No answer”理解为域名不存在。该结果支持此前川大为直接A、没有CNAME的判断。见图\ref{fig:ns-baidu-cname}、图\ref{fig:ns-scu-cname}。

帧30的dart.scu.edu.cn是SOA的MNAME，不是www.scu.edu.cn的规范名；响应AA仍为0，nslookup的“Authoritative answers can be found from”提示语不能替代AA位判断。

## 可用于“结论/小结”的文字

本轮真实抓包完成两个公网域名首次/重复ping及四种nslookup，6组DNS事务按ID、问题、反向端点和时间共同配对。百度存在指向www.a.shifen.com的CNAME，川大本次返回直接A，CNAME专门查询为NOERROR/NODATA。系统DNS与显式公网解析器对百度给出不同IPv4地址，报告分别记录，未混用为ping目标。首次有DNS、重复无DNS且使用相同地址的现象支持缓存复用。川大ICMP未响应，但成功A回答已证明DNS解析完成。

本轮限制为：macOS缓存条目转储未能成功，仅能通过清缓存命令状态与报文变化分析；未清理代理或远端缓存；未观察远端解析器完整上游过程；无法仅凭本次ICMP结果确定川大不回包的原因。网络设置未变动，无需恢复临时DNS配置。

## 建议截图标签与取证内容

| 标签占位 | 图片应来自本轮真实软件结果 | 最终帧引用 |
|---|---|---|
| fig:mac-cache | 两次清缓存成功和cachedump失败的原日志回显，图注明确“日志回显” | 无网络帧，引用01/03的cache-flush.txt |
| fig:mac-ping-baidu | 百度首次/重复实际输出，若读取日志须明确“日志回显” | 1—14 |
| fig:mac-ping-scu | 川大首次/重复实际输出，若读取日志须明确“日志回显” | 15—22 |
| fig:dns-first-baidu | Wireshark打开最终pcapng，帧2，展开DNS标志与两条Answer | 1、2 |
| fig:dns-first-scu | Wireshark帧16，直接A及TTL | 15、16 |
| fig:dns-repeat | 最终文件列表或实际阶段文件列表展示两次重复窗口只有ICMP，应标明重复窗口 | 9—14、20—22 |
| fig:ns-baidu-a | Wireshark帧24，CNAME及两个A和TTL | 23、24 |
| fig:ns-baidu-cname | Wireshark帧26，仅CNAME | 25、26 |
| fig:ns-scu-a | Wireshark帧28，直接A | 27、28 |
| fig:ns-scu-cname | Wireshark帧30，NOERROR、0 Answer和SOA | 29、30 |

所有终端截图若是cat读取保存的命令输出，应称为“真实命令原始输出（日志回显）”；不能称为同一时刻另一次实时测量。未生成或未拍摄的图不能在报告中声明已存在。
