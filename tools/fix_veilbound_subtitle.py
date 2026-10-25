#!/usr/bin/env python3
"""Fix the baked duplicate/low-contrast subtitle in an existing Veilbound 512x512 O2R.
Keeps the original 512x512 resource header and all other mod resources unchanged.
Run with: python tools/fix_veilbound_subtitle.py --input current.o2r --output fixed.o2r
Requires Pillow and DejaVuSerifCondensed-Bold font.
"""
import argparse
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

parser=argparse.ArgumentParser()
parser.add_argument("--input",required=True)
parser.add_argument("--output",required=True)
a=parser.parse_args()
key="objects/object_mag/gTitleZeldaShieldLogoTex"
with zipfile.ZipFile(a.input) as source:
    blobs={name:source.read(name) for name in source.namelist()}
data=blobs[key]
if len(data)!=80+512*512*4:
    raise SystemExit("Requires existing 512x512 RGBA32 logo texture; refusing mismatched format")
im=Image.frombytes("RGBA",(512,512),data[80:])
overlay=Image.new("RGBA",(512,512),(0,0,0,0))
draw=ImageDraw.Draw(overlay)
draw.rounded_rectangle((23,279,407,320),radius=9,fill=(10,21,22,244),outline=(194,145,68,235),width=2)
draw.line((31,284,399,284),fill=(46,127,92,220),width=1)
draw.line((31,315,399,315),fill=(112,79,39,170),width=1)
font_candidates=["/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
font_file=next((p for p in font_candidates if Path(p).exists()),None)
if not font_file:
    raise SystemExit("Install fonts-dejavu-core")
font=ImageFont.truetype(font_file,24)
label="ECHOES OF THE FIRST RIFT"
bounds=draw.textbbox((0,0),label,font=font,stroke_width=1)
x=(430-(bounds[2]-bounds[0]))//2+1
draw.text((x+1,286),label,font=font,fill=(19,10,5,255),stroke_width=2,stroke_fill=(0,0,0,255))
draw.text((x,285),label,font=font,fill=(242,206,121,255),stroke_width=1,stroke_fill=(94,62,28,255))
im=Image.alpha_composite(im,overlay)
blobs[key]=data[:80]+im.tobytes()
with zipfile.ZipFile(a.output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as target:
    for name,blob in blobs.items():
        target.writestr(name,blob)
print("Produced 512x512 logo mod with separated, legible subtitle:",a.output)
