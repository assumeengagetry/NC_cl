B 截图计划更新：Wireshark界面曾发生本机Qt辅助功能崩溃，原始抓包完好、重开正常。已保留真实Wireshark完整流量列表 B04-repeat-packets.png（1—22帧可见），原生终端尚待macOS Apple Events授权弹窗允许。
为避免反复失败的界面操作，关键帧截图使用Terminal回显已经保存的TShark原始帧解析日志（必要时筛选字段展示，不改数值），必须在所有对应图注写“原始报文解析日志节选回显，非实时测量”，不能标作Wireshark GUI展开详情。原始frame-XX.txt仍完整保留，字段表及抓包作为主要可核验证据。
B01—03为实际原始命令日志回显，也必须明确标注。Wireshark总体截图用于证明查看最终文件与重复测试无DNS现象。B05/B06/B07...B10图仍按原路径。
A01-final-topology.png已经更新，最后重开后全部注释真实完整可见，不再使用旧截图。A19/A20是重开DNS记录/IP验收，A18是PC验收。A真实恢复数值与最后验证均已追加到a-report-facts.md。
