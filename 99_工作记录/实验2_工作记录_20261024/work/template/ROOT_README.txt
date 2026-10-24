模板分析已完成：template-analysis.md。
注意原DOC纸张为184.15×260.0028mm，不是A4；正文框146.7556mm；左标签列22.0663mm；主文字宋体10.5pt；标题15/22pt；无页眉页脚。
LaTeX框架：template-layout.tex（未填数据、不作为最终成果）。
参考PDF：readable-reference/实验报告模板.pdf。
全部7页参考图：readable-reference/template-page-1.png 至 template-page-7.png。因本机无SimSun/SimHei/FZ大标宋，已用独立FONTCONFIG_FILE加载Songti SC/Heiti SC替代，并明确记录。DOC解析不修改原件。
指导书6页已逐页完整看过：guide-pages/guide-1.png 至 guide-pages/guide-6.png；10题和全部要求见template-analysis.md。
可复用实验一封面logo/scu，不能复用A4正文、页眉、课时或数据。
已安装稳定工具Tectonic 0.17.0（/opt/homebrew/bin/tectonic）用于XeTeX兼容编译，正在首次下载TeX bundle。未创建最终PDF。
另：bundled pdftoppm缺Adobe-GB1映射，渲染实验一PDF会误显示中文丢字；已在work/template/pythonlib安装PyMuPDF，可用 PYTHONPATH=<该目录> bundled-python 进行可靠渲染。完整封面参考图lab1-cover-complete.png，已检查，与实验一main.tex吻合。后续最终PDF建议用PyMuPDF逐页渲染避免Poppler字体映射假故障。
LaTeX框架已实际编译通过并逐页看图。template-cover-smoke.tex/pdf为内部5页格式测试：第1页A4复现实验一封面，第2—5页184.15×260.0028mm模板正文。已验证纸张切换，封面定位正确。主框架template-layout.tex默认不启用封面；将注释的\TemplateCover启用即可。供内容集成后继续排版使用。
表格宏：\TemplateRow[上边线宽][下边线宽]{左标签}{正文}{行高}；默认内横线0.75pt，续页用1.5pt上下边框。正文实际可用宽120.8793mm，每行左右内距1.905mm，正文10.5pt、基线15.6pt。自然高度超过所给行高会主动PackageError，防止遮挡。\reportpage自动完整续表页，\evidencefigure自动顺序编号。
