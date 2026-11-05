from pathlib import Path
import shutil,zipfile
w=Path(__file__).parent;src=w/'source';out=Path('/Users/apple/Workspace/NC_cl/01_提交成果/实验3');out.mkdir(exist_ok=True);d=out/'Overleaf源工程';d.mkdir(exist_ok=True)
for p in src.rglob('*'):
 if p.is_file() and (p.suffix in ['.tex','.sty'] or p.name in ['README.txt','latexmkrc'] or (p.parent.name=='assets' and p.suffix=='.pdf' and p.stem!='data-list')):
  target=d/p.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
z=out/'06_实验3_许盛凯_2024141460445_Overleaf.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in sorted(d.rglob('*')):
  if p.is_file():f.write(p,p.relative_to(d))
print(z)
