#!/usr/bin/env python3
"""Pack the EXISTING approved Veilbound logo into its original Shipwright O2R slot.

Usage:
 python tools/build_veilbound_hd_o2r.py --logo original_logo.png --base existing.o2r --out VEILBOUND_LOGO_HD.o2r --size 1024

No AI redesign and no logo replacement: the source pixels are only fitted to a larger transparent canvas.
The native EnMag draw path must use the same --size; mismatched sizes are unsafe.
"""
import argparse
import struct
import zipfile
from PIL import Image

p=argparse.ArgumentParser()
p.add_argument("--logo",required=True)
p.add_argument("--base",required=True)
p.add_argument("--out",required=True)
p.add_argument("--size",type=int,choices=(512,1024,2048),default=512)
a=p.parse_args()
im=Image.open(a.logo).convert("RGBA")
if min(im.size)<256:
    raise SystemExit("Source logo is too small for an HD upgrade")
bounds=im.getbbox()
if bounds is None: raise SystemExit("Logo has no visible pixels")
art=im.crop(bounds)
size=a.size
# Keep the original logo proportions and full composition, including the subtitle.
resample=getattr(getattr(Image,"Resampling",Image),"LANCZOS")
art.thumbnail((size-16,size-16),resample)
canvas=Image.new("RGBA",(size,size),(0,0,0,0))
canvas.alpha_composite(art,((size-art.width)//2,(size-art.height)//2))
key="objects/object_mag/gTitleZeldaShieldLogoTex"
with zipfile.ZipFile(a.base) as z:
    blobs={item.filename:z.read(item.filename) for item in z.infolist()}
if key not in blobs: raise SystemExit("Base O2R lacks title logo resource")
original=blobs[key]
if len(original)<80: raise SystemExit("O2R texture header too short")
w,h,length=struct.unpack_from("<III",original,68)
if length!=w*h*4 or len(original)!=80+length:
    raise SystemExit(f"Unexpected O2R RGBA32 resource: {w}x{h}, data={length}")
new=bytearray(original[:80])
struct.pack_into("<III",new,68,size,size,size*size*4)
blobs[key]=bytes(new)+canvas.tobytes()
with zipfile.ZipFile(a.out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,data in blobs.items(): z.writestr(name,data)
with zipfile.ZipFile(a.out) as z:
    result=z.read(key)
    assert len(result)==80+size*size*4
    assert struct.unpack_from("<III",result,68)==(size,size,size*size*4)
print(f"Validated original-logo replacement O2R: {a.out} ({size}x{size})")
