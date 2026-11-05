"""Package the saved PDF/source/evidence and independently rebuild the ZIP."""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pypdf import PdfReader
from package_final import WORK, SOURCE, OUTPUT, NAME, prepare_delivery, sha256


def main():
    screenshots = prepare_delivery()
    destination = OUTPUT / 'Overleaf源工程'
    pdf = OUTPUT / (NAME + '.pdf')
    shutil.copy2(SOURCE / 'main.pdf', pdf)
    shutil.copy2(pdf, destination / 'preview.pdf')
    source_zip = OUTPUT / (NAME + '_Overleaf.zip')
    with zipfile.ZipFile(source_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(destination.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(destination))
    env = os.environ.copy()
    env.update(SOURCE_DATE_EPOCH='1793789069', FORCE_SOURCE_DATE='1')
    compiler = '/Users/apple/Workspace/NC_cl/99_工作记录/实验2_工作记录_20261024/图片兼容修复/tools/TinyTeX/bin/universal-darwin/xelatex'
    # A fresh directory prevents old build files masking missing dependencies.
    with tempfile.TemporaryDirectory(prefix='zip-independent-', dir=WORK) as build_path:
        check = Path(build_path)
        with zipfile.ZipFile(source_zip) as archive:
            archive.extractall(check)
        for number in [1, 2]:
            with (WORK / f'zip-build{number}.log').open('w') as log:
                subprocess.run([compiler, '-interaction=nonstopmode', '-halt-on-error',
                                '-file-line-error', 'main.tex'], cwd=check, env=env,
                               stdout=log, stderr=subprocess.STDOUT, check=True)
        assert (check / 'main.pdf').read_bytes() == pdf.read_bytes(), 'Rebuilt PDF differs'
    reader = PdfReader(pdf)
    text = subprocess.check_output(['/opt/homebrew/bin/pdftotext', str(pdf), '-'], text=True)
    sections = ''.join(path.read_text() for path in (SOURCE / 'sections').glob('*.tex'))
    questions = [int(n) for n in re.findall(r'\\qa\{(\d+)\.', sections)]
    assert sorted(questions) == list(range(1, 18)), questions
    assert screenshots['figures'] > 0
    compact = re.sub(r'\s+', '', text)
    assert '2026.11.04' in compact and '第10周' in compact
    assert '??' not in text
    validation = json.loads((OUTPUT / 'attachments/capture-validation.json').read_text())
    assert validation['passed'] is True, 'Original capture validation has not passed'
    # Review must refer to this exact PDF, rather than being hard-coded True.
    review_path = WORK / 'evidence' / 'visual-review.json'
    review = json.loads(review_path.read_text()) if review_path.is_file() else {}
    reviewed = (review.get('passed') is True and review.get('pdf_sha256') == sha256(pdf)
                and review.get('page_count') == len(reader.pages))
    complete = screenshots['gui_screenshots_complete'] and reviewed
    status = '已完成' if complete else ('待逐页版式复核' if screenshots['gui_screenshots_complete'] else '待补GUI截图版')
    validation.update(report_pages=len(reader.pages), questions=sorted(questions),
                      figures=screenshots['figures'],
                      independent_overleaf_zip_rebuild_byte_equal=True,
                      all_pages_visually_reviewed=reviewed,
                      gui_screenshots_complete=screenshots['gui_screenshots_complete'],
                      screenshot_pixel_matches=sum(record['passed'] for record in screenshots['screenshots']),
                      report_status=status, pdf_sha256=sha256(pdf))
    (OUTPUT / '验收结果.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
    instructions = OUTPUT / '提交说明.txt'
    with instructions.open('a') as file:
        file.write(f'最终验收状态：{status}；报告{len(reader.pages)}页、{screenshots["figures"]}图。\n')
    with zipfile.ZipFile(OUTPUT / (NAME + '.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((OUTPUT / 'attachments').rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(OUTPUT))
        archive.write(OUTPUT / '验收结果.json', '验收结果.json')
        archive.write(instructions, '提交说明.txt')
    lines = [sha256(path) + '  ' + str(path.relative_to(OUTPUT))
             for path in sorted(OUTPUT.rglob('*'))
             if path.is_file() and path.name != 'SHA256SUMS.txt']
    (OUTPUT / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n')
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
