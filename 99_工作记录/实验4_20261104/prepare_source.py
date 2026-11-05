from pathlib import Path
import shutil
w=Path(__file__).resolve().parent;s=w/'source';s.mkdir(exist_ok=True);(s/'assets').mkdir(exist_ok=True);(s/'sections').mkdir(exist_ok=True)
old=Path('01_提交成果/实验3/Overleaf源工程')
for n in ['main.tex','report-template.sty','report-layout.tex','latexmkrc']:
 text=(old/n).read_text().replace('实验3：UDP协议分析与TCP连接管理','实验4：ICMP协议分析').replace('2026年10月31日','2026年11月4日')
 if n=='main.tex': text=text.replace('udp.tex','ping.tex').replace('tcp.tex','trace.tex')
 if n=='report-layout.tex':
  text=text.replace('\\newcommand{\\udpfile}{\\textnormal{2024141460445\\_许盛凯\\_实验3\\_UDP.pcapng}}','').replace('\\newcommand{\\tcpfile}{\\textnormal{2024141460445\\_许盛凯\\_实验3\\_TCP.pcapng}}','')
  text+='\n\\newcommand{\\capfile}[1]{\\code{#1.pcapng}}\n'
 (s/n).write_text(text)
shutil.copy2('实验4_ICMP协议分析_实验指导书.pdf','02_课程资料/实验指导书/实验4_ICMP协议分析_实验指导书.pdf')
