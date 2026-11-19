#!/usr/bin/env python3
"""Crop a real screenshot without resampling, wrap it losslessly in PDF, and record provenance.
Usage: python prepare_figure.py SOURCE OUTPUT_STEM [--crop LEFT TOP RIGHT BOTTOM] [--caption TEXT]
OUTPUT_STEM gets .png, .pdf, .json; no changes to source. Rectangles use original-image pixels.
"""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image, ImageChops
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path)
    ap.add_argument('output_stem',type=Path)
    ap.add_argument('--crop',nargs=4,type=int,metavar=('LEFT','TOP','RIGHT','BOTTOM'))
    ap.add_argument('--caption',default='')
    a=ap.parse_args()
    source=a.source.resolve()
    stem=a.output_stem.resolve()
    stem.parent.mkdir(parents=True,exist_ok=True)
    for suffix in ('.png','.pdf','.json'):
        if stem.with_suffix(suffix)==source:
            raise ValueError('Output would overwrite source')
    raw=Image.open(source)
    raw.load()
    crop=a.crop or [0,0,raw.width,raw.height]
    l,t,r,b=crop
    if not (0<=l<r<=raw.width and 0<=t<b<=raw.height):
        raise ValueError(f'Invalid crop {crop} for {raw.size}')
    im=raw.crop(crop)
    # Use an explicit white matte only if the source is transparent.
    if 'A' in im.getbands():
        rgba=im.convert('RGBA')
        matte=Image.new('RGBA',im.size,(255,255,255,255))
        matte.alpha_composite(rgba)
        im=matte.convert('RGB')
        alpha_operation='Composited transparent pixels onto white.'
    else:
        im=im.convert('RGB')
        alpha_operation='None'
    png=stem.with_suffix('.png')
    pdf=stem.with_suffix('.pdf')
    im.save(png,format='PNG',optimize=True)
    c=Canvas(str(pdf),pagesize=(im.width,im.height),pageCompression=1)
    c.setTitle(a.caption or stem.name)
    c.setAuthor('Screenshot crop; source recorded in sidecar JSON')
    c.drawImage(ImageReader(im),0,0,width=im.width,height=im.height,mask='auto')
    c.showPage()
    c.save()
    reader=PdfReader(pdf)
    images=list(reader.pages[0].images)
    if len(images)!=1:
        raise RuntimeError('PDF must contain exactly one raster image')
    recovered=images[0].image.convert('RGB')
    if recovered.size!=im.size or ImageChops.difference(recovered,im).getbbox() is not None:
        raise RuntimeError('PDF image round-trip was not lossless')
    meta={'source':str(source),'source_sha256':sha(source),'source_size_pixels':list(raw.size),
      'crop_box_ltrb_pixels':crop,'output_size_pixels':list(im.size),'resampling':'None',
      'editing':'Single continuous rectangle crop only','alpha_operation':alpha_operation,
      'caption':a.caption,'png':png.name,'pdf':pdf.name,
      'png_sha256':sha(png),'pdf_sha256':sha(pdf),'lossless_pdf_roundtrip_verified':True}
    stem.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(meta,ensure_ascii=False))

if __name__=='__main__':main()
