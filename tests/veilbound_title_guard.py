#!/usr/bin/env python3
"""Veilbound title-screen source guard.

This is a source inspection smoke test, NOT an Android runtime/image test.
It deliberately uses only the Python standard library.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ACTOR = ROOT / "soh/src/overlays/actors/ovl_En_Mag/z_en_mag.c"

def check() -> list[str]:
    failures = []
    if not ACTOR.is_file():
        return [f"Missing native title actor: {ACTOR}"]
    source = ACTOR.read_text(encoding="utf-8")
    begin = source.find("void EnMag_DrawInner(Actor* thisx, PlayState* play, Gfx** gfxP) {")
    if begin < 0:
        return ["EnMag_DrawInner native implementation not found"]
    end = source.find("\nvoid EnMag_Draw(", begin)
    if end < 0:
        return ["EnMag_Draw boundary missing"]
    draw = source[begin:end]
    update_begin = source.find("void EnMag_Update(Actor* thisx, PlayState* play) {")
    update_end = source.find("\nvoid EnMag_DrawTextureI8(", update_begin)
    update = source[update_begin:update_end] if update_begin >= 0 and update_end >= 0 else ""

    # Check the intended integration point and forbid UI-layer substitutes.
    if "VEILBOUND" not in draw:
        failures.append("Native EnMag_DrawInner lacks VEILBOUND title marker")
    if not re.search(r"gDP(?:FillRectangle|SetFillColor|SetPrimColor)|gSPTextureRectangle", draw):
        failures.append("Native title draw has no graphics display-list instructions")
    # Ignore comments: descriptive phrases like "NOT an ImGui overlay" are harmless.
    without_comments = re.sub(r"/\\*.*?\\*/", "", draw, flags=re.DOTALL)
    without_comments = re.sub(r"//[^\\n]*", "", without_comments)
    if re.search(r"\\b(?:ImGui|igBegin|igEnd|igText)\\s*\\(", without_comments):
        failures.append("Native title actor invokes an ImGui UI function")
    if "GAMEMODE_FILE_SELECT" not in update or "TRANS_TRIGGER_START" not in update:
        failures.append("Native input-to-file-select transition is missing")
    if "CHECK_BTN_ALL" not in update:
        failures.append("Native title button handling is missing")
    if "moonHalfWidth" in draw:
        failures.append("Unapproved moon experiment reappeared in title actor")

    return failures

if __name__ == "__main__":
    errors = check()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
    print("PASS: Native title-source guards (not proof of compiled APK or displayed pixels)")
