from pathlib import Path
import re
s=Path(__file__).parent/'source/sections'
for n in ['ping.tex','trace.tex']:
 p=s/n;t=p.read_text();blocks=t.split('\\reportpage');out=[blocks[0]]
 for b in blocks[1:]:
  matches=list(re.finditer(r'\\ev\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}',b))
  if matches:
   imgs=[]
   for m in matches:
    title=m[3].replace('回显','摘录')+'（原始输出摘录）'
    imgs.append('\\ev{'+m[1]+'}{'+m[2]+'}{'+title+'}')
   groups=[[x] for x in imgs] if n=='ping.tex' and any('ping-request' in x for x in imgs) else [imgs]
   for group in groups:
    out.append('\\reportpage{\\datacontinued}{\n\\subheading{本节原始输出证据}\n本页为本次真实抓包的TShark逐帧字段、字节或原始命令日志的排版摘录，未修改字段值；完整输出随附件保存。本页并非GUI截图。\n'+'\n'.join(group)+'\n}\n\n')
   b=re.sub(r'\\ev\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\s*','',b)
  out.append('\\reportpage'+b)
 p.write_text(''.join(out))
p=s/'procedure.tex';t=p.read_text();t=t.replace('报告插图来自真实Wireshark界面或终端回显本次已保存日志。日志回显图明确标注，未伪称又一次实时测量。保留原始截图和裁剪坐标，插图采用无损PDF封装，保持之前Overleaf图片兼容方案。','报告插图使用本次真实TShark逐帧输出及已保存命令日志的排版摘录，明确标注为原始输出，并非GUI截图；没有改写报文字段或伪称实时重测。完整文本与pcapng保存在附件，插图采用PDF封装，保持之前Overleaf图片兼容方案。');p.write_text(t)
p=s/'trace.tex';t=p.read_text().replace('完整输出为保存日志的终端回显','完整输出为保存日志的排版摘录');p.write_text(t)
p=s/'ping.tex';t=p.read_text().replace('原始命令结果回显','原始命令结果摘录');p.write_text(t)
p=s/'closing.tex';t=p.read_text().replace('完整截图','原始输出');p.write_text(t)
