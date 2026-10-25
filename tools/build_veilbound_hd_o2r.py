#!/usr/bin/env python3
"""Experimental 512x512 logo mod from a real high-resolution transparent PNG.
Requires Pillow. Preserves stock mod resources and updates width/height/data size
of the existing SoH RGBA32 O2R texture resource. Not Retro-generated; Android
compatibility must be tested. Requires companion 512x512 title-actor build.
Usage:
python tools/build_veilbound_hd_o2r.py --logo your_veilbound_logo_hd.png \\
  --base VEILBOUND_v8_ENGRAVED_BUTTON_ANDROID.o2r \\
  --out VEILBOUND_TRUE_HD_512_ANDROID_EXPERIMENT.o2r
"""
import argparse,struct,zipfile
from PIL import Image
p=argparse.ArgumentParser()
p.add_argument("--logo",required=True)
p.add_argument("--base",required=True)
p.add_argument("--out",required=True)
a=p.parse_args()
im=Image.open(a.logo).convert("RGBA")
if max(im.size)<1024:raise SystemExit("Refusing low-resolution logo input")
art=im.crop(im.getbbox())
art.thumbnail((506,340),Image.Resampling.LANCZOS)
canvas=Image.new("RGBA",(512,512),(0,0,0,0))
canvas.alpha_composite(art,((512-art.width)//2,(512-art.height)//2-22))
with zipfile.ZipFile(a.base) as z:
    blobs={item.filename:z.read(item.filename) for item in z.infolist()}
key="objects/object_mag/gTitleZeldaShieldLogoTex"
original=blobs[key]
if len(original)<80 or struct.unpack_from("<III",original,68)!=(160,160,102400):
    raise SystemExit("Unexpected stock RGBA32 texture header; refusing unsafe conversion")
new=bytearray(original[:80])
struct.pack_into("<III",new,68,512,512,512*512*4)
blobs[key]=bytes(new)+canvas.tobytes()
with zipfile.ZipFile(a.out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,data in blobs.items():z.writestr(name,data)
print("Generated experimental 512x512 O2R:",a.out)
