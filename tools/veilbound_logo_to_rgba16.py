#!/usr/bin/env python3
"""Convert a transparent Veilbound logo PNG into a static RGBA16 tiled header.

Usage:
    python3 tools/veilbound_logo_to_rgba16.py approved-logo.png --output build/veilbound_logo.inc

The generated header must be included by a native actor and drawn through N64
Gfx commands; generating this file alone does not install the texture into OoT.
Pillow is required: python3 -m pip install Pillow
"""
import argparse
from pathlib import Path
from PIL import Image

def convert(src: Path, out: Path, width: int = 256, height: int = 128) -> None:
    img = Image.open(src).convert("RGBA")
    img.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((width - img.width) // 2, (height - img.height) // 2))
    # RGBA5551: 5 bits R/G/B, 1 bit alpha, big-endian word values.
    def pixel(r, g, b, a):
        if a < 96:
            return 0
        return ((r >> 3) << 11) | ((g >> 3) << 6) | ((b >> 3) << 1) | 1
    lines = [
        "/* Generated from the approved Veilbound logo. Do not edit by hand. */",
        "#ifndef VEILBOUND_LOGO_RGBA16_INC",
        "#define VEILBOUND_LOGO_RGBA16_INC",
        f"#define VEILBOUND_LOGO_WIDTH {width}",
        f"#define VEILBOUND_LOGO_HEIGHT {height}",
        "static const unsigned short sVeilboundLogoRGBA16[] = {",
    ]
    values = [pixel(*p) for p in canvas.getdata()]
    for i in range(0, len(values), 16):
        lines.append("    " + ", ".join(f"0x{v:04X}" for v in values[i:i + 16]) + ",")
    lines.extend(["};", "#endif", ""])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {out}, {width}x{height}, {len(values)} RGBA16 pixels")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("logo", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--width", type=int, default=256)
    ap.add_argument("--height", type=int, default=128)
    args = ap.parse_args()
    if args.width <= 0 or args.height <= 0 or args.width % 32 or args.height % 32:
        ap.error("Output width/height must be positive multiples of 32")
    convert(args.logo, args.output, args.width, args.height)
