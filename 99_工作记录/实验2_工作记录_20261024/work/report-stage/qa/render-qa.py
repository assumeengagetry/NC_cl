from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
doc=fitz.open(root/'main.pdf')
for i,page in enumerate(doc):
 page.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(root/f'qa/page-{i+1:02d}.png')
for group in range((len(doc)+3)//4):
 sheet=Image.new('RGB',(1200,1700),'#cccccc')
 for k in range(4):
  n=group*4+k
  if n>=len(doc):break
  im=Image.open(root/f'qa/page-{n+1:02d}.png');im.thumbnail((580,820));sheet.paste(im,((k%2)*600+10,(k//2)*850+20));ImageDraw.Draw(sheet).text(((k%2)*600+10,(k//2)*850+5),f'Page {n+1}',fill='black')
 sheet.save(root/f'qa/contact-{group+1}.png')
print('Pages',len(doc))
print([(i+1,tuple(round(v,2) for v in p.rect)) for i,p in enumerate(doc)])
