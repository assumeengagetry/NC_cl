"""Prepare the delivery without changing report sections.

Screenshot convention: evidence/screenshots/<asset>.png is wrapped losslessly
in source/assets/<asset>.pdf. Full originals and crop metadata are copied too.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
from PIL import Image
from pypdf import PdfReader

WORK = Path(__file__).resolve().parent
SOURCE = WORK / 'source'
OUTPUT = Path('/Users/apple/Workspace/NC_cl/01_提交成果/实验4')
NAME = '06_实验4_许盛凯_2024141460445'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def figure_references():
    references = []
    for section in re.findall(r'\\input\{(sections/[^}]+)\}', (SOURCE / 'main.tex').read_text()):
        path = SOURCE / (section if section.endswith('.tex') else section + '.tex')
        text = re.sub(r'(?m)(?<!\\)%.*$', '', path.read_text())
        for match in re.finditer(r'\\(?:ev|Evidence)\{([^}]+)\}\{([^}]+)\}', text):
            label, asset = match.groups()
            references.append({'label': label, 'asset': Path(asset).stem})
    labels = [r['label'] for r in references]
    if len(labels) != len(set(labels)):
        raise ValueError('Duplicate figure labels in included sections')
    return references


def screenshot_validation():
    """Check saved screenshots and exact embedded pixels; vectors cannot pass.

    Screen provenance cannot be inferred from pixels. Original full screenshots
    and capture/crop records remain separate evidence, preserved without edits.
    """
    records = []
    for ref in figure_references():
        asset = ref['asset']
        png = WORK / 'evidence' / 'screenshots' / (asset + '.png')
        pdf = SOURCE / 'assets' / (asset + '.pdf')
        record = dict(ref, screenshot=f'screenshots/{asset}.png',
                      pdf_asset=f'assets/{asset}.pdf', passed=False)
        if not png.is_file() or not pdf.is_file():
            record['reason'] = 'Screenshot PNG or corresponding PDF asset missing'
        else:
            try:
                with Image.open(png) as source_image:
                    source_image.load()
                    original = source_image.convert('RGB')
                reader = PdfReader(pdf)
                embedded = list(reader.pages[0].images) if len(reader.pages) == 1 else []
                matches = [image for image in embedded
                           if image.image.convert('RGB').size == original.size
                           and image.image.convert('RGB').tobytes() == original.tobytes()]
                if not matches:
                    record['reason'] = 'PDF does not contain the exact saved screenshot raster'
                else:
                    record.update(passed=True, width=original.width, height=original.height,
                                  png_sha256=sha256(png), pdf_sha256=sha256(pdf))
            except Exception as exc:
                record['reason'] = str(exc)
        records.append(record)
    return {'gui_screenshots_complete': bool(records) and all(r['passed'] for r in records),
            'figures': len(records), 'screenshots': records,
            'method': 'Each referenced figure PDF contains the exact RGB pixels of its saved screenshot PNG.'}


def prepare_delivery():
    OUTPUT.mkdir(exist_ok=True)
    screenshot_check = screenshot_validation()
    if screenshot_check['gui_screenshots_complete']:
        image_note = ('报告插图来自真实Wireshark界面及终端对本次已保存命令日志的回显；'
                      '日志回显不是重新测量。assets/采用截图的无损PDF封装。'
                      '原始PNG、完整截图及可用的裁剪记录保存在证据附件screenshots/中。')
        completion_note = '已补齐报告所引用的真实截图；最终编译、逐页检查和完整验收结果见验收结果.json。'
    else:
        missing = [r['asset'] for r in screenshot_check['screenshots'] if not r['passed']]
        image_note = ('截图验证尚未全部通过；不得把排版输出摘录当成GUI截图。'
                      '尚需复核的插图：' + '、'.join(missing) + '。')
        completion_note = '当前为待补截图版，最终状态以验收结果.json为准。'
    readme = (
        '实验4：ICMP协议分析\n'
        '姓名：许盛凯；学号：2024141460445；第10周；实验日期2026-11-04。\n'
        'Overleaf上传此ZIP，主文件main.tex，编译器XeLaTeX，建议TeX Live 2026。\n'
        '正文和表格均为可编辑LaTeX。' + image_note + '\n'
        '沿用原始DOC的非A4页面、字体字号、表格边框和续表；Fandol替代缺失商业中文字体，'
        '教师评议、成绩、签名和未核实课时留空。\n'
        '报告回答全部17题。' + completion_note + '\n'
    )
    (SOURCE / 'README.txt').write_text(readme)
    destination = OUTPUT / 'Overleaf源工程'
    destination.mkdir(exist_ok=True)
    for path in SOURCE.rglob('*'):
        if path.is_file() and (path.suffix in ['.tex', '.sty']
                               or path.name in ['README.txt', 'latexmkrc']
                               or path.parent.name == 'assets' and path.suffix == '.pdf'):
            target = destination / path.relative_to(SOURCE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    attachments = OUTPUT / 'attachments'
    shutil.copytree(WORK / 'evidence', attachments, dirs_exist_ok=True)
    for name in ['capture_lab4.py', 'export_evidence.py', 'make_output_panels.py']:
        shutil.copy2(WORK / name, attachments / name)
    (attachments / 'screenshot-validation.json').write_text(
        json.dumps(screenshot_check, ensure_ascii=False, indent=2) + '\n')
    (attachments / '复现与证据说明.txt').write_text(
        '1. 七个pcapng均为2026-11-04真实en0采集，合计79帧，未经筛选重排；正文短名与附件同名。\n'
        '2. 目标固定为cs.scu.edu.cn解析到的202.115.32.43；本机10.135.133.108，MTU1500。\n'
        '3. command.txt是执行当时保存的命令输出，capture.txt是dumpcap采集统计；'
        'frames.json、fields.tsv、details.txt由TShark读取相应原始pcapng生成。\n'
        '4. validate_capture.py独立解析Ethernet/IPv4/ICMP、校验和、分片及引用；'
        'capture-validation.json记录结果，facts.json/MD为逐组配对记录，analysis/保存逐帧详情。\n'
        '5. ' + image_note + ' screenshot-validation.json逐图核对PNG与PDF内嵌栅格像素一致。'
        '旧*-figure-text.txt为原始字段摘录，不冒称软件截图。\n'
        '6. capture_lab4.py含本次固定地址，复用前另存并核对接口、IP和目标，勿覆盖原证据。\n'
        '7. 本轮未修改DNS、代理、路由或防火墙，采集已停止。\n'
    )
    (OUTPUT / '提交说明.txt').write_text(
        readme + '\n交付：PDF、Overleaf ZIP、原始抓包与证据ZIP及展开目录。\n')
    return screenshot_check


if __name__ == '__main__':
    print(json.dumps(prepare_delivery(), ensure_ascii=False, indent=2))
