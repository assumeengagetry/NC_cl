# Packet Tracer 准备调查（2026-10-24）

在 /Applications、~/Applications、~/Downloads、当前工作目录以及 Spotlight 检索中，未找到 Cisco Packet Tracer 应用、安装器或 .pkt 工程。未安装任何第三方镜像版本，也未构造或转换 .pkt。

Cisco 官方下载入口：
https://www.netacad.com/resources/lab-downloads

Cisco 官方安装说明：
https://www.netacad.com/skillsforall/files/Cisco_Packet_Tracer_Download_and_Installation_Instructions.pdf

此入口是 JavaScript 应用。终端可读取公开网页，但其中不包含直接的 macOS 安装包 URL。需要通过官方页面选择 macOS 下载；若 Cisco 要求登录，则需要用户完成 NetAcad/SkillsForAll 账号登录。当前版本和 macOS/处理器要求应以实际官方下载列表与安装后 About 为准；没有把第三方网站列出的版本当作本机事实。

原生脚本接口（官方资料）：
https://tutorials.ptnetacad.net/help/default/scriptModules.htm
https://tutorials.ptnetacad.net/help/default/IpcAPI/index.html

Script Modules 位于 Extensions → Scripting；可嵌入 pkt/pka 或作为 PT 模块运行。嵌入模块可能在打开工程时请求权限，所以最终工程应保存真实网络配置后移除临时模块依赖。

官方 API 支持：
- Device.getPort("FastEthernet0") 与 HostPort.setIpSubnetMask(ip, mask)
- HostPort.setDnsServerIp(ip)
- Device.getProcess("DnsServer")
- DnsServerProcess.setEnable(true)
- DnsServerProcess.addARecordToNameServerDb(domainName, address)
- DnsServerProcess.addCNAMEToNameServerDb(domainName, hostName)
- Device.setName 与 moveToLocation

以上是 API 文档能力，尚未安装/运行 Packet Tracer，因此不代表已验证当前版本中的脚本执行。对应文档已保存为 HTML 及纯文本备查。

进一步可用的官方 API（已保存文档）：
- IPC.network() → Network.getDevice(name) / getDeviceAt(index)
- IPC.appWindow().getActiveFile().getWorkspace()；Workspace 对象可取得 LogicalWorkspace（需当前版本运行时核实）
- LogicalWorkspace.addDevice(type, model, x, y)：PC 类型 8、Server 类型 9、Switch 类型 1
- LogicalWorkspace.createLink(device1Name, port1Name, device2Name, port2Name, 8100)：8100 为铜质直通线
- LogicalWorkspace.addNote(x, y, layer, text)
- AppWindow.fileSaveAs(filename)

文档入口：
https://tutorials.ptnetacad.net/help/default/IpcAPI/class_logical_workspace.html
https://tutorials.ptnetacad.net/help/default/IpcAPI/class_host_port.html
https://tutorials.ptnetacad.net/help/default/IpcAPI/class_dns_server_process.html
