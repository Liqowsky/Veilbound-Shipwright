#!/usr/bin/env python3
"""Reapply immersive fullscreen after SDL changes Activity window ownership."""
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text()
if "veilboundApplyImmersiveFullscreen" in s:
    raise SystemExit("already applied")
anchor="public class MainActivity extends SDLActivity{"
if anchor not in s: raise SystemExit("MainActivity class anchor not found")
method='''
    private void veilboundApplyImmersiveFullscreen() {
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_FORCE_NOT_FULLSCREEN);
        if (Build.VERSION.SDK_INT >= 28) {
            WindowManager.LayoutParams lp = getWindow().getAttributes();
            lp.layoutInDisplayCutoutMode = Build.VERSION.SDK_INT >= 30
                    ? WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                    : WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            getWindow().setAttributes(lp);
        }
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                View.SYSTEM_UI_FLAG_FULLSCREEN |
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) veilboundApplyImmersiveFullscreen();
    }

    @Override
    protected void onResume() {
        super.onResume();
        veilboundApplyImmersiveFullscreen();
    }
'''
s=s.replace(anchor,anchor+"\n"+method)
p.write_text(s)
print("VEILBOUND SDL immersive lifecycle hooks applied")
