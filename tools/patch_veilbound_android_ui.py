#!/usr/bin/env python3
"""Apply VEILBOUND title screen touch UI to checked-out Shipwright Android port."""
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text()
if 'setVeilboundTitleUiActive' in s:
    raise SystemExit("Already patched")
anchor="    private boolean touchControlsMenuVisible = false;"
if anchor not in s:
    raise SystemExit("Android port title-control anchor changed")
s=s.replace(anchor,anchor+"""
    private volatile boolean veilboundTitleActive = false;

    // Called by the native title actor: blank virtual gamepad on title screen,
    // and touch anywhere to issue ONE proper START press to the game.
    public void setVeilboundTitleUiActive(boolean active) {
        runOnUiThread(() -> {
            veilboundTitleActive = active;
            applyTouchControlsVisibility();
        });
    }
""")
anchor="        boolean touchControlsDisabled = preferences.getBoolean(PREF_TOUCH_CONTROLS_DISABLED, false);"
if anchor not in s:
    raise SystemExit("Android visibility anchor changed")
s=s.replace(anchor,"""        if (veilboundTitleActive) {
            overlayView.setVisibility(View.VISIBLE);
            if (buttonGroup != null) buttonGroup.setVisibility(View.GONE);
            if (buttonToggle != null) buttonToggle.setVisibility(View.GONE);
            overlayView.setOnTouchListener((view, event) -> {
                int action = event.getActionMasked();
                if (action == MotionEvent.ACTION_DOWN) {
                    setButton(ControllerButtons.BUTTON_START, true);
                } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                    setButton(ControllerButtons.BUTTON_START, false);
                }
                return true;
            });
            return;
        }
        boolean touchControlsDisabled = preferences.getBoolean(PREF_TOUCH_CONTROLS_DISABLED, false);""")
p.write_text(s)
print("Patched native-driven title touch controls:",p)
