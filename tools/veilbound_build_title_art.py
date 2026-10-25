#!/usr/bin/env python3
"""Generate original 4K master button + optimized native RGBA32 title textures.
Requires Pillow. This script is run BEFORE Android and Linux builds.
No external assets/network access required. Output header is build-generated.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import argparse

def font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def master():
    # Draw at 3840x2160 as a true high-res editable/source raster.
    w,h=3840,2160
    im=Image.new("RGBA",(w,h),(0,0,0,0))
    glow=Image.new("RGBA",(w,h),(0,0,0,0))
    g=ImageDraw.Draw(glow)
    box=(1050,890,2790,1310)
    for j in range(22):
        x=box[0]+j*10;y=box[1]+j*8
        g.rounded_rectangle((x,y,box[2]-j*10,box[3]-j*8),radius=100-j*2,
                            outline=(8,223,126,max(0,38-j)),width=11)
    im=Image.alpha_composite(im,glow.filter(ImageFilter.GaussianBlur(65)))
    d=ImageDraw.Draw(im)
    outer=(1060,900,2780,1300)
    d.rounded_rectangle(outer,radius=116,fill=(41,30,23,255),outline=(195,148,78,255),width=18)
    d.rounded_rectangle((1092,932,2748,1268),radius=91,fill=(13,39,32,255),outline=(99,76,43,255),width=15)
    d.rounded_rectangle((1120,960,2720,1240),radius=77,outline=(32,133,95,205),width=9)
    d.arc((1135,969,2705,1240),180,355,fill=(227,179,95,135),width=8)
    for xx in (1102,2738):
        d.ellipse((xx-55,1055,xx+55,1165),fill=(9,74,55,255),outline=(221,174,93,255),width=12)
        d.polygon([(xx,1070),(xx+29,1110),(xx,1150),(xx-29,1110)],fill=(29,203,139,255))
    title="PRESS START"
    f=font(184)
    bounds=d.textbbox((0,0),title,font=f,stroke_width=2)
    tw=bounds[2]-bounds[0]
    tx=(w-tw)//2
    ty=1025
    d.text((tx+5,ty+9),title,font=f,fill=(0,0,0,230),stroke_width=5,stroke_fill=(0,0,0,180))
    d.text((tx,ty),title,font=f,fill=(236,198,132,255),stroke_width=3,stroke_fill=(135,86,43,255))
    return im

def mist():
    # A genuinely smooth, non-tiled alpha cloud; used with native modulation.
    size=32
    im=Image.new("RGBA",(size,size))
    pix=im.load()
    for y in range(size):
        for x in range(size):
            nx=(x-15.5)/15.5;ny=(y-15.5)/15.5
            r2=(nx*nx*0.9 + ny*ny*1.6)
            noise=0.86+0.12*math.sin(x*.68+y*.21)+0.1*math.cos(y*.61-x*.37)
            alpha=round(max(0,1-r2)**2.5 * 100 * noise)
            pix[x,y]=(19,204,132, max(0,min(255,alpha)))
    return im

def write_header(path, btn, haze):
    def arr(name,im):
        data=list(im.tobytes())
        # 144x36 button is much sharper than N64's 16x16 bitmap font glyphs.
        lines=[]
        for i in range(0,len(data),24):
            lines.append("    "+", ".join(str(v) for v in data[i:i+24])+",")
        return f"static u8 {name}[] __attribute__((aligned(8))) = {{\n"+"\n".join(lines)+"\n};\n"
    header="#ifndef VEILBOUND_TITLE_BUTTON_H\n#define VEILBOUND_TITLE_BUTTON_H\n"
    header+="#define VEILBOUND_BUTTON_WIDTH 144\n#define VEILBOUND_BUTTON_HEIGHT 36\n"
    header+=arr("sVeilboundStartButtonTex",btn)
    header+=arr("sVeilboundMistTex",haze)
    header+="#endif\n"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(header)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--header",required=True)
    ap.add_argument("--master-dir",required=True)
    opts=ap.parse_args()
    dest=Path(opts.master_dir);dest.mkdir(parents=True,exist_ok=True)
    m=master();m.save(dest/"VEILBOUND_press_start_4k_master.png")
    b=m.crop((1020,870,2820,1330)).resize((144,36),Image.Resampling.LANCZOS)
    mist_img=mist()
    mist_img.resize((512,512),Image.Resampling.LANCZOS).save(dest/"VEILBOUND_emerald_mist_512.png")
    b.resize((1152,288),Image.Resampling.NEAREST).save(dest/"VEILBOUND_button_native_preview.png")
    write_header(Path(opts.header),b,mist_img)
    print("Generated source 3840x2160, native RGBA32 button 144x36, and alpha-smoke 32x32:",opts.header)
