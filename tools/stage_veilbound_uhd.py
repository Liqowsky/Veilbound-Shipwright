#!/usr/bin/env python3
"""Prepare high-resolution title texture replacement SOURCE for Retro.
This does not pretend that adding PNGs to an O2R zip installs UHD assets.
Usage: python tools/stage_veilbound_uhd.py --source-dir ... --destination ...
Optionally --manifest input_manifest.json exported from Retro, then preserve it.
"""
import argparse, shutil
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser()
p.add_argument("--source-dir",required=True)
p.add_argument("--destination",required=True)
p.add_argument("--manifest")
a=p.parse_args()
src=Path(a.source_dir);dest=Path(a.destination)
target=dest/"objects"/"object_mag"
target.mkdir(parents=True,exist_ok=True)
logo=Image.open(src/"veilbound_logo_hd.png").convert("RGBA")
if logo.width<1024:raise ValueError("Logo source is not UHD")
# Full-size separate layers are kept; the baked-logo O2R texture is the ONLY
# asset handled by the legacy actor until a HD asset draw path is confirmed.
logo.save(target/"gTitleZeldaShieldLogoTex.png")
for file in ("veilbound_press_start_hd.png","veilbound_studio_hd.png","veilbound_subtitle_hd.png"):
    im=Image.open(src/file).convert("RGBA")
    im.save(dest/file)
if a.manifest:
    shutil.copyfile(a.manifest,dest/"manifest.json")
(dest/"README.txt").write_text(
    "VEILBOUND UHD sources ready for Retro. Retro must generate the actual O2R using"
    " a manifest extracted from the matching game version. The additional button"
    " and studio PNGs are source art ONLY; they are NOT installed as working game"
    " textures until assigned to an engine texture resource. Do not package this"
    " directory with zip and rename it .o2r.\n")
print("Staged UHD sources:",dest)
