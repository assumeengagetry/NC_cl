# B部分准备完毕（尚未测量）

已完整逐页阅读指导书6页；已审核旧B部分证据，旧数据来自Linux、日期2026-10-20且清缓存失败，不能作为本轮Mac实测。

本机为macOS 26.7.1 (25G241)，Wireshark/TShark 4.6.7；dumpcap有权限访问BPF。物理接口en0地址10.20.41.180；系统DNS走Tailscale接口utun4到100.100.100.100。显式解析器223.5.5.5已通过两域名A查询可达性测试。

未修改网络配置。拟保留系统解析路径，ping抓utun4 DNS与en0 ICMP；四种nslookup统一223.5.5.5经en0。每阶段先采集后命令，输出仅保留实验域名DNS及实测目标ICMP，未筛选临时捕获仅留/tmp。无须更改Wi-Fi DNS或停用VPN。

脚本：run_real_dns.py，静态语法检查通过。需要一次macOS管理员授权执行该脚本。脚本内部在每个域名首次ping前执行 dscacheutil -flushcache 和 killall -HUP mDNSResponder，保留退出状态；两次重复间不再清理。若任一步失败立即停，不写成功。

建议主代理统一弹出一次管理员认证：使用AppleScript do shell script调用 /opt/homebrew/bin/python3 /Users/apple/Workspace/NC_cl/实验2_DNS_20261024/evidence/real-dns/run_real_dns.py with administrator privileges。root只用于清缓存与启动采集，八个测量命令通过sudo -u apple运行；结束后恢复产物属主。

ping采用本机man语法：ping -n -c 3 -W 1500 -t 8 域名；-W单位毫秒，-t是总超时秒。命令总计约40秒。nslookup严格按要求参数，末尾绝对域名点。

请不要同时对两个公网域名发出其他查询，避免混入同名后台查询。
