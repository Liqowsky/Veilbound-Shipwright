#!/usr/bin/env python3
"""VEILBOUND first touchscreen-native file menu integration for the Android port.

The native game remains authoritative about occupied saves, naming, and opening.
The Android overlay only requests the exact native file-select menu index.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
native = root / "soh/src/overlays/gamestates/ovl_file_choose/z_file_choose.c"
java = root / "Android/app/src/main/java/com/dishii/soh/MainActivity.java"
s = native.read_text(encoding="utf-8-sig")
j = java.read_text()
if "Veilbound_UpdateFileSelectTouch" in s or "veilboundFileSelectPanel" in j:
    raise SystemExit("File select touch patch already applied; refusing duplicate")

anchor='#include "file_choose.h"'
if anchor not in s: raise SystemExit("Missing file_choose.h include")
bridge=r'''
#if defined(__ANDROID__)
#include <jni.h>
#include <SDL.h>
// SDL_main.h rewrites the identifier 'main'; GameState has a real 'main' field.
#ifdef main
#undef main
#endif

static int sVeilboundFileMenuUi = -1;

static jint Veilbound_CallFileSelectJava(const char* methodName, const char* signature, jint value) {
    JNIEnv* env = (JNIEnv*)SDL_AndroidGetJNIEnv();
    if (env == NULL) return -1;
    jobject activity = SDL_AndroidGetActivity();
    if (activity == NULL) return -1;
    jclass cls = (*env)->GetObjectClass(env, activity);
    jint result = -1;
    if (cls != NULL) {
        jmethodID method = (*env)->GetMethodID(env, cls, methodName, signature);
        if (method != NULL) {
            if (signature[0] == '(' && signature[1] == 'Z') {
                (*env)->CallVoidMethod(env, activity, method, value ? JNI_TRUE : JNI_FALSE);
            } else {
                result = (*env)->CallIntMethod(env, activity, method);
            }
        }
        if ((*env)->ExceptionCheck(env)) (*env)->ExceptionClear(env);
        (*env)->DeleteLocalRef(env, cls);
    }
    (*env)->DeleteLocalRef(env, activity);
    return result;
}
static void Veilbound_SetFileSelectTouchUi(int enabled) {
    if (sVeilboundFileMenuUi == enabled) return;
    sVeilboundFileMenuUi = enabled;
    Veilbound_CallFileSelectJava("setVeilboundFileSelectUiActive", "(Z)V", enabled);
}
static void Veilbound_UpdateFileSelectTouch(FileChooseContext* this, Input* input) {
    int isMainMenu = (this->menuMode == FS_MENU_MODE_CONFIG && this->configMode == CM_MAIN_MENU);
    Veilbound_SetFileSelectTouchUi(1); // touch-only throughout file select
    Veilbound_CallFileSelectJava("setVeilboundFileSelectSubmenu", "(Z)V", !isMainMenu);
    if (isMainMenu) {
        int selection = Veilbound_CallFileSelectJava("consumeVeilboundFileSelection", "()I", 0);
        if (selection >= FS_BTN_MAIN_FILE_1 && selection <= FS_BTN_MAIN_OPTIONS) {
            this->buttonIndex = selection;
            // This is identical to confirming the selected row with gamepad A.
            input->press.button |= BTN_A;
        }
    }
}
#else
static void Veilbound_SetFileSelectTouchUi(int enabled) { (void)enabled; }
static void Veilbound_UpdateFileSelectTouch(FileChooseContext* this, Input* input) {
    (void)this; (void)input;
}
#endif
'''
s=s.replace(anchor,anchor+"\n"+bridge,1)
needle='    GameInteractor_ExecuteOnFileChooseMain(thisx);'
if needle not in s:raise SystemExit("Can't find FileChoose_Main() update")
s=s.replace(needle,'    Veilbound_UpdateFileSelectTouch(this, input);\n'+needle,1)
needle='void FileChoose_Destroy(GameState* thisx) {\n}'
if needle not in s:raise SystemExit("Can't find file select destroy")
s=s.replace(needle,'void FileChoose_Destroy(GameState* thisx) {\n    Veilbound_SetFileSelectTouchUi(0);\n}',1)
native.write_text(s)

needle='    private volatile boolean veilboundTitleActive = false;'
if needle not in j:raise SystemExit("Run the existing VEILBOUND Android touch patch before this one")
j=j.replace(needle,needle+'''
    private volatile boolean veilboundFileSelectActive = false;
    private volatile boolean veilboundFileSelectSubmenu = false;
    private int veilboundRequestedFileSlot = -1;
    private LinearLayout veilboundFileSelectPanel;
    private LinearLayout veilboundNavPanel;

    public synchronized int consumeVeilboundFileSelection() {
        int requested = veilboundRequestedFileSlot;
        veilboundRequestedFileSlot = -1;
        return requested;
    }

    private synchronized void requestVeilboundFileSelection(int slot) {
        veilboundRequestedFileSlot = slot;
    }

    public void setVeilboundFileSelectUiActive(boolean active) {
        runOnUiThread(() -> {
            veilboundFileSelectActive = active;
            applyTouchControlsVisibility();
        });
    }

    public void setVeilboundFileSelectSubmenu(boolean submenu) {
        runOnUiThread(() -> {
            if (veilboundFileSelectSubmenu != submenu) {
                veilboundFileSelectSubmenu = submenu;
                applyTouchControlsVisibility();
            }
        });
    }

    private void veilboundBuildFileSelectPanel() {
        if (veilboundFileSelectPanel != null) return;
        FrameLayout container = (FrameLayout)findViewById(android.R.id.content);
        LinearLayout menu = new LinearLayout(this);
        menu.setOrientation(LinearLayout.VERTICAL);
        menu.setGravity(Gravity.CENTER_HORIZONTAL);
        menu.setPadding(dpToPixels(16), dpToPixels(10), dpToPixels(16), dpToPixels(10));
        android.graphics.drawable.GradientDrawable background =
                new android.graphics.drawable.GradientDrawable(
                    android.graphics.drawable.GradientDrawable.Orientation.TL_BR,
                    new int[]{0xE80B2423, 0xEE102E29});
        background.setCornerRadius(dpToPixels(14));
        background.setStroke(dpToPixels(2), 0xFFBE9657);
        menu.setBackground(background);
        TextView title = new TextView(this);
        title.setText("VEILBOUND  ·  SAVES");
        title.setGravity(Gravity.CENTER);
        title.setTextColor(0xFFF4D9A0);
        title.setTextSize(20);
        title.setTypeface(android.graphics.Typeface.create("serif", android.graphics.Typeface.BOLD));
        title.setLetterSpacing(0.1f);
        title.setPadding(0,0,0,dpToPixels(5));
        menu.addView(title);
        String[] labels = {"SAVE 1", "SAVE 2", "SAVE 3", "OPTIONS"};
        int[] slots = {0,1,2,5};
        int screenH = getResources().getDisplayMetrics().heightPixels;
        int rowHeight = Math.max(dpToPixels(38), Math.min(dpToPixels(55), screenH/9));
        for (int i=0;i<labels.length;i++) {
            final int slot=slots[i];
            Button button=new Button(this);
            button.setText(labels[i]);
            button.setTextSize(20);
            button.setTypeface(android.graphics.Typeface.create("serif", android.graphics.Typeface.BOLD));
            button.setLetterSpacing(0.1f);
            button.setAllCaps(false);
            button.setTextColor(0xFFFFDB93);
            android.graphics.drawable.GradientDrawable bg =
                new android.graphics.drawable.GradientDrawable();
            bg.setColor(0xFF103F38);
            bg.setCornerRadius(dpToPixels(8));
            bg.setStroke(dpToPixels(2), 0xFFC49A59);
            button.setBackground(bg);
            button.setOnClickListener(v -> requestVeilboundFileSelection(slot));
            LinearLayout.LayoutParams row = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, rowHeight);
            row.setMargins(0, dpToPixels(3), 0, dpToPixels(3));
            menu.addView(button, row);
        }
        FrameLayout.LayoutParams pos = new FrameLayout.LayoutParams(
                Math.min(dpToPixels(390), (int)(getResources().getDisplayMetrics().widthPixels*.72f)),
                FrameLayout.LayoutParams.WRAP_CONTENT,
                Gravity.CENTER);
        container.addView(menu, pos);
        menu.setVisibility(View.GONE);
        veilboundFileSelectPanel=menu;
        // Touch-friendly native navigation for naming, copy, erase and options.
        LinearLayout nav = new LinearLayout(this);
        nav.setOrientation(LinearLayout.HORIZONTAL);
        String[] captions = {"UP", "DOWN", "LEFT", "RIGHT", "OK", "BACK"};
        int[] keyCodes = {ControllerButtons.BUTTON_DUP, ControllerButtons.BUTTON_DDOWN,
            ControllerButtons.BUTTON_DLEFT, ControllerButtons.BUTTON_DRIGHT,
            ControllerButtons.BUTTON_A, ControllerButtons.BUTTON_B};
        for (int k=0;k<captions.length;k++) {
            final int key=keyCodes[k];
            Button keyButton=new Button(this);
            keyButton.setText(captions[k]);
            keyButton.setTextColor(0xFFF5D59D);
            keyButton.setTextSize(11);
            keyButton.setAllCaps(false);
            android.graphics.drawable.GradientDrawable brass=new android.graphics.drawable.GradientDrawable();
            brass.setColor(0xFF103F38);
            brass.setStroke(dpToPixels(1),0xFFC49A59);
            brass.setCornerRadius(dpToPixels(8));
            keyButton.setBackground(brass);
            keyButton.setOnTouchListener((v,event) -> {
                int action=event.getActionMasked();
                if(action==MotionEvent.ACTION_DOWN) setButton(key,true);
                if(action==MotionEvent.ACTION_UP || action==MotionEvent.ACTION_CANCEL) setButton(key,false);
                return true;
            });
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dpToPixels(48),1);
            lp.setMargins(dpToPixels(2),0,dpToPixels(2),0);
            nav.addView(keyButton,lp);
        }
        FrameLayout.LayoutParams navPos = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM);
        navPos.bottomMargin=dpToPixels(8);
        container.addView(nav,navPos);
        nav.setVisibility(View.GONE);
        veilboundNavPanel=nav;
    }
''',1)
needle='        boolean touchControlsDisabled = preferences.getBoolean(PREF_TOUCH_CONTROLS_DISABLED, false);'
if needle not in j: raise SystemExit("Missing Android touch visibility anchor")
j=j.replace(needle,'''        if (veilboundFileSelectActive) {
            veilboundBuildFileSelectPanel();
            overlayView.setVisibility(View.GONE);
            veilboundFileSelectPanel.setVisibility(veilboundFileSelectSubmenu ? View.GONE : View.VISIBLE);
            if (veilboundNavPanel != null) veilboundNavPanel.setVisibility(veilboundFileSelectSubmenu ? View.VISIBLE : View.GONE);
            return;
        }
        if (veilboundFileSelectPanel != null) veilboundFileSelectPanel.setVisibility(View.GONE);
        if (veilboundNavPanel != null) veilboundNavPanel.setVisibility(View.GONE);
        boolean touchControlsDisabled = preferences.getBoolean(PREF_TOUCH_CONTROLS_DISABLED, false);''',1)
java.write_text(j)
print("Applied native Save 1/2/3/Options taps and Veilbound-themed large Android file menu")
