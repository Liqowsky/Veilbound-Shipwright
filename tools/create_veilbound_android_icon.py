#!/usr/bin/env python3
"""Create VEILBOUND Android launcher icons from vector-like Pillow drawing."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys
root=Path(sys.argv[1])
def icon(n):
    im=Image.new("RGBA",(n,n),(9,25,26,255))
    d=ImageDraw.Draw(im)
    u=lambda a:round(a*n/512)
    d.rounded_rectangle((u(17),u(17),u(495),u(495)),radius=u(112),fill=(9,29,29),outline=(172,125,52),width=max(1,u(18)))
    d.ellipse((u(80),u(85),u(432),u(430)),fill=(9,62,51),outline=(23,176,118),width=max(1,u(9)))
    f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf",u(370))
    t="V"; bb=d.textbbox((0,0),t,font=f)
    x=(n-(bb[2]-bb[0]))//2-bb[0]
    y=(n-(bb[3]-bb[1]))//2-bb[1]-u(23)
    d.text((x+u(7),y+u(7)),t,font=f,fill=(5,12,12),stroke_width=u(8),stroke_fill=(4,6,6))
    d.text((x,y),t,font=f,fill=(232,190,105),stroke_width=u(6),stroke_fill=(122,80,38))
    d.polygon([(u(256),u(376)),(u(284),u(418)),(u(256),u(464)),(u(228),u(418))],fill=(31,208,132),outline=(224,183,94))
    return im
for suffix,side in [("mdpi",48),("hdpi",72),("xhdpi",96),("xxhdpi",144),("xxxhdpi",192)]:
    p=root/"res"/("mipmap-"+suffix)/"ic_launcher.png"
    p.parent.mkdir(parents=True,exist_ok=True)
    icon(side).save(p)
icon(512).save(root/"veilbound_launcher_master_512.png")
print("Generated VEILBOUND V launcher icons")
