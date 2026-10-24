/*
 * File: z_title.c
 * Overlay: ovl_title
 * Description: Displays the Nintendo Logo
 */

#include "global.h"
#include "alloca.h"
#include "textures/nintendo_rogo_static/nintendo_rogo_static.h"
#include "assets/objects/gameplay_keep/gameplay_keep.h"
#include <soh/Enhancements/bootcommands.h>
#include <soh/GameVersions.h>
#include <soh/SaveManager.h>
#include "soh/ResourceManagerHelpers.h"
#include "soh/Enhancements/game-interactor/GameInteractor_Hooks.h"
#include <string.h>

#include "time.h"

// Note: In other rom versions this function also updates unk_1D4, coverAlpha, addAlpha, visibleDuration to calculate
// the fade-in/fade-out + the duration of the n64 logo animation
void Title_Calc(TitleContext* this) {
    if ((this->coverAlpha == 0) && (this->visibleDuration != 0)) {
        this->visibleDuration--;
        this->unk_1D4--;
        if (this->unk_1D4 == 0) {
            this->unk_1D4 = 400;
        }
    } else {
        this->coverAlpha += this->addAlpha;
        if (this->coverAlpha <= 0) {
            this->coverAlpha = 0;
            this->addAlpha = 3;
        } else if (this->coverAlpha >= 0xFF) {
            this->coverAlpha = 0xFF;
            this->exit = 1;
        }
    }
    this->uls = this->ult & 0x7F;
    this->ult++;
}

void Title_SetupView(TitleContext* this, f32 x, f32 y, f32 z) {
    View* view = &this->view;
    Vec3f eye;
    Vec3f lookAt;
    Vec3f up;

    eye.x = x;
    eye.y = y;
    eye.z = z;
    up.x = up.z = 0.0f;
    lookAt.x = lookAt.y = lookAt.z = 0.0f;
    up.y = 1.0f;

    func_800AA460(view, 30.0f, 10.0f, 12800.0f);
    func_800AA358(view, &eye, &lookAt, &up);
    func_800AAA50(view, 0xF);
}

// Native OoT game-state experiment: never use ImGui to render the title.
// This replaces Nintendo logo rendering with an original silver/emerald emblem.
// The next phase must replace the separate file-select state as well.
void Title_Draw(TitleContext* this) {
    GraphicsContext* gfxCtx = this->state.gfxCtx;
    s32 beatPhase = this->ult % 160;
    s32 pulse = ((beatPhase >= 16 && beatPhase < 24) || (beatPhase >= 42 && beatPhase < 50)) ? 8 : 0;
    s32 radius = 20 + pulse;
    s32 x = 160;
    s32 y = 112;
    s32 i;
    OPEN_DISPS(gfxCtx);
    Gfx_SetupDL_39Opa(gfxCtx);
    gDPPipeSync(POLY_OPA_DISP++);
    gDPSetCycleType(POLY_OPA_DISP++, G_CYC_FILL);
    // Original deep-green backdrop, rendered by the original engine pipeline.
    gDPSetFillColor(POLY_OPA_DISP++, (GPACK_RGBA5551(7, 19, 23, 1) << 16) |
                                           GPACK_RGBA5551(7, 19, 23, 1));
    gDPFillRectangle(POLY_OPA_DISP++, 0, 0, 319, 239);
    // Layered forged-silver medallion, two heartbeats, luminous emerald core.
    gDPSetFillColor(POLY_OPA_DISP++, (GPACK_RGBA5551(184, 196, 191, 1) << 16) |
                                           GPACK_RGBA5551(184, 196, 191, 1));
    for (i = -radius; i <= radius; i += 3) {
        s32 halfWidth = (radius * radius - i * i) / (radius * 2);
        gDPFillRectangle(POLY_OPA_DISP++, x-halfWidth, y+i, x+halfWidth, y+i+1);
    }
    gDPSetFillColor(POLY_OPA_DISP++, (GPACK_RGBA5551(10, 41, 35, 1) << 16) |
                                           GPACK_RGBA5551(10, 41, 35, 1));
    for (i = -radius+5; i <= radius-5; i += 3) {
        s32 halfWidth = ((radius-5)*(radius-5) - i*i)/((radius-5)*2);
        gDPFillRectangle(POLY_OPA_DISP++, x-halfWidth, y+i, x+halfWidth, y+i+1);
    }
    gDPSetFillColor(POLY_OPA_DISP++, (GPACK_RGBA5551(34, 205, 125, 1) << 16) |
                                           GPACK_RGBA5551(34, 205, 125, 1));
    gDPFillRectangle(POLY_OPA_DISP++, x-6-pulse/4, y-6-pulse/4, x+6+pulse/4, y+6+pulse/4);
    gDPPipeSync(POLY_OPA_DISP++);
    // Respect the existing game's fade/transition logic.
    Environment_FillScreen(gfxCtx, 0, 0, 0, (s16)this->coverAlpha, FILL_SCREEN_XLU);
    CLOSE_DISPS(gfxCtx);
}

void Title_Main(GameState* thisx) {
    TitleContext* this = (TitleContext*)thisx;

    OPEN_DISPS(this->state.gfxCtx);

    gSPSegment(POLY_OPA_DISP++, 0, NULL);
    gSPSegment(POLY_OPA_DISP++, 1, this->staticSegment);
    Gfx_SetupFrame(this->state.gfxCtx, 0, 0, 0);
    Title_Calc(this);
    Title_Draw(this);

    if (this->exit) {
        gSaveContext.seqId = (u8)NA_BGM_DISABLED;
        gSaveContext.natureAmbienceId = 0xFF;
        gSaveContext.gameMode = GAMEMODE_TITLE_SCREEN;
        this->state.running = false;
        SET_NEXT_GAMESTATE(&this->state, Opening_Init, OpeningContext);
    }

    CLOSE_DISPS(this->state.gfxCtx);
}

void Title_Destroy(GameState* thisx) {
    TitleContext* this = (TitleContext*)thisx;

    Sram_InitSram(&this->state);
}

void Title_Init(GameState* thisx) {
    TitleContext* this = (TitleContext*)thisx;

    this->staticSegment = NULL;
    osSyncPrintf("z_title.c\n");

    R_UPDATE_RATE = 1;
    Matrix_Init(&this->state);
    View_Init(&this->view, this->state.gfxCtx);
    this->state.main = Title_Main;
    this->state.destroy = Title_Destroy;
    this->exit = false;
    gSaveContext.fileNum = 0xFF;
    this->ult = 0;
    this->unk_1D4 = 0x14;
    this->coverAlpha = 255;
    this->addAlpha = -3;
    this->visibleDuration = 0x3C;

    GameInteractor_ExecuteOnZTitleInit(this);
}
