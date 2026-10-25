#!/usr/bin/env python3
"""Rebuild the HD 512x512 logo mod with ONE subtitle plaque below the emblem.
Requires original transparent wordmark PNG and an existing 512x512 SoH O2R.
"""
import argparse,zipfile
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser()
p.add_argument("--input",required=True)
p.add_argument("--logo",required=True)
p.add_argument("--output",required=True)
p.add_argument("--preview")
a=p.parse_args()
key="objects/object_mag/gTitleZeldaShieldLogoTex"
with zipfile.ZipFile(a.input) as z: blobs={name:z.read(name) for name in z.namelist()}
if len(blobs[key])!=80+512*512*4:raise SystemExit("Expected RGBA32 512x512 texture; aborting")
source=Image.open(a.logo).convert("RGBA")
bbox=source.getbbox()
if bbox is None:raise SystemExit("Empty logo")
logo=source.crop(bbox);logo.thumbnail((495,270),Image.Resampling.LANCZOS)
canvas=Image.new("RGBA",(512,512),(0,0,0,0))
canvas.alpha_composite(logo,((512-logo.width)//2,65))
d=ImageDraw.Draw(canvas)
d.rounded_rectangle((38,354,474,404),radius=9,fill=(8,23,22,245),outline=(208,156,79,245),width=3)
d.rounded_rectangle((43,359,469,399),radius=6,outline=(38,112,84,200),width=1)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf",25)
text="ECHOES OF THE FIRST RIFT"
bb=d.textbbox((0,0),text,font=font,stroke_width=1)
x=(512-(bb[2]-bb[0]))//2
d.text((x+1,361),text,font=font,fill=(30,16,10,255),stroke_width=2,stroke_fill=(2,3,3,255))
d.text((x,360),text,font=font,fill=(242,207,133,255),stroke_width=1,stroke_fill=(121,78,31,255))
blobs[key]=blobs[key][:80]+canvas.tobytes()
with zipfile.ZipFile(a.output,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,data in blobs.items():z.writestr(name,data)
if a.preview:canvas.save(a.preview)
print("Rebuilt separated subtitle from clean logo:",a.output)
