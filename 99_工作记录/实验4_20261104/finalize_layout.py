from pathlib import Path
w=Path(__file__).parent;s=w/'source'
for n in ['ping.tex','trace.tex']:
 p=s/'sections'/n;t=p.read_text().replace('对应摘录应答','对应回显应答')
 t=t.replace('本页为本次真实抓包的TShark逐帧字段、字节或原始命令日志的排版摘录，未修改字段值；完整输出随附件保存。本页并非GUI截图。','以下为本次抓包的TShark字段、原始字节或命令日志摘录；完整文本与对应pcapng随附件保存。')
 t=t.replace('五、ICMP路径探测','七、ICMP路径探测')
 if n=='ping.tex':
  t=t.replace('\\reportpage{\\dataheading}', '\\reportpage{\\datacontinued}')
  t=t.replace('\\reportpage{\\datacontinued}', '\\reportpage{\\dataheading}',1)
 p.write_text(t)
(s/'latexmkrc').write_text("$pdf_mode = 5;\n$ENV{'SOURCE_DATE_EPOCH'} = 1793789069;\n$ENV{'FORCE_SOURCE_DATE'} = 1;\n$xelatex = 'xelatex -interaction=nonstopmode -file-line-error %O %S';\n")
