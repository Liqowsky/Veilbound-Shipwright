#!/usr/bin/env python3
"""Build-time integration of the user-approved Veilbound title PNG and looped OGG."""
from pathlib import Path
from zipfile import ZipFile
import sys
from PIL import Image

root = Path(sys.argv[1])
archive = Path(sys.argv[2])
out = root / "soh/src/overlays/actors/ovl_En_Mag/veilbound_rift_generated.h"
music_out = root / "Android/app/src/main/assets/veilbound/emerald_whispers_loop.ogg"
with ZipFile(archive) as z:
    names = set(z.namelist())
    image_name = "veilbound_title/veilbound_rift_native_320x180.png"
    music_name = "veilbound_title/emerald_whispers_loop.ogg"
    for name in (image_name, music_name):
        if name not in names:
            raise SystemExit("Missing Veilbound asset in ZIP: " + name)
    music_out.parent.mkdir(parents=True, exist_ok=True)
    music_out.write_bytes(z.read(music_name))
    sky_out = music_out.parent / "veilbound_rift_640x360.png"
    sky_out.write_bytes(z.read("veilbound_title/veilbound_rift_640x360.png"))
    if music_out.stat().st_size < 100000:
        raise SystemExit("Emerald Whispers audio asset unexpectedly small")
    import io
    pic = Image.open(io.BytesIO(z.read("veilbound_title/veilbound_rift_640x360.png"))).convert("RGBA")
    pic = pic.resize((640,360),Image.Resampling.LANCZOS if hasattr(Image,"Resampling") else Image.LANCZOS)
    lines = ["/* Auto-generated from approved Veilbound rift PNG. */",
             "#ifndef VEILBOUND_RIFT_GENERATED_H",
             "#define VEILBOUND_RIFT_GENERATED_H"]
    for row in range(12):
        for col in range(10):
            data=pic.crop((col*64,row*30,(col+1)*64,(row+1)*30)).tobytes()
            name=f"sVeilboundRiftTile_{row}_{col}"
            lines.append(f"static const unsigned char {name}[{len(data)}] = {{")
            for i in range(0,len(data),32):
                lines.append(",".join(str(v) for v in data[i:i+32])+",")
            lines.append("};")
    lines.append("static const unsigned char* const sVeilboundRiftTiles[120] = {")
    for row in range(12):
        lines.append(",".join(f"sVeilboundRiftTile_{row}_{col}" for col in range(10))+",")
    lines += ["};","#endif"]
    out.write_text("\n".join(lines)+"\n")
print("Integrated Veilbound title:",music_out.stat().st_size,"OGG bytes; 120 tiled RGBA32 textures.")
