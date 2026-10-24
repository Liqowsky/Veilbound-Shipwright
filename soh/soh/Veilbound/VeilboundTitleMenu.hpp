#pragma once
// VEILBOUND / Shipwright feasibility experiment.
// Original title-menu UI component. It has no dependency on Nintendo art assets.
// This is intentionally not hooked to the engine's title state yet.
#include <imgui.h>
#include <cmath>

namespace Veilbound {
enum class TitleAction { None, NewGame, Continue, Settings, Credits };

inline void DrawKingdomBackdrop(const ImVec2& origin, const ImVec2& size, float t) {
    ImDrawList* d = ImGui::GetWindowDrawList();
    const float x = origin.x, y = origin.y, w = size.x, h = size.y;
    // Layered world panorama rather than a single desert biome: dark forests,
    // distant citadels, snowy mountains, ruined spires and drifting mist.
    d->AddRectFilledMultiColor(origin, ImVec2(x+w,y+h),
        IM_COL32(10,21,34,255), IM_COL32(27,37,52,255),
        IM_COL32(9,18,22,255), IM_COL32(8,22,19,255));
    auto mountain = [&](float center, float top, float width, ImU32 color) {
        d->AddTriangleFilled(ImVec2(x+center*w,y+top*h),
            ImVec2(x+(center-width)*w,y+.75f*h),
            ImVec2(x+(center+width)*w,y+.75f*h), color);
    };
    mountain(.13f,.26f,.27f,IM_COL32(43,63,71,255));
    mountain(.30f,.40f,.18f,IM_COL32(37,55,69,255));
    mountain(.68f,.28f,.26f,IM_COL32(41,53,72,255));
    mountain(.89f,.18f,.24f,IM_COL32(49,60,78,255));
    mountain(.92f,.33f,.17f,IM_COL32(35,47,62,255));
    // Distant castle silhouette and ancient needle-like towers.
    d->AddRectFilled(ImVec2(x+.075f*w,y+.38f*h),ImVec2(x+.24f*w,y+.63f*h),IM_COL32(20,34,40,255));
    for(int i=0;i<6;++i) {
        float xx=x+(.07f+i*.035f)*w;
        float yy=y+(.29f+(i%3)*.045f)*h;
        d->AddRectFilled(ImVec2(xx,yy),ImVec2(xx+.022f*w,y+.63f*h),IM_COL32(24,38,47,255));
        d->AddTriangleFilled(ImVec2(xx-.004f*w,yy),ImVec2(xx+.011f*w,yy-.065f*h),
            ImVec2(xx+.026f*w,yy),IM_COL32(36,55,64,255));
    }
    d->AddRectFilled(ImVec2(x+.81f*w,y+.33f*h),ImVec2(x+.85f*w,y+.68f*h),IM_COL32(18,31,42,255));
    d->AddTriangleFilled(ImVec2(x+.80f*w,y+.34f*h),ImVec2(x+.83f*w,y+.12f*h),
        ImVec2(x+.86f*w,y+.34f*h),IM_COL32(22,42,52,255));
    // Low, swaying silhouettes of forest and ancient walls.
    d->AddRectFilled(ImVec2(x,y+.78f*h),ImVec2(x+w,y+h),IM_COL32(7,17,20,255));
    for(int i=0;i<65;++i) {
        float xx=x+(i+.5f)*w/65.f;
        float yy=y+(.70f+.045f*std::sin(i*1.83f))*h;
        float ht=(.09f+.06f*(.5f+.5f*std::sin(i*2.9f)))*h;
        d->AddTriangleFilled(ImVec2(xx,yy-ht),ImVec2(xx-.014f*w,yy+.015f*h),
            ImVec2(xx+.014f*w,yy+.015f*h),IM_COL32(9,28,27,245));
    }
    // Slow mist ribbons and wandering emerald embers.
    for(int j=0;j<13;++j) {
        float pos=std::fmod(j*.13f+t*.0045f,1.3f)-.15f;
        float yy=y+(.60f+.022f*j)*h;
        d->AddLine(ImVec2(x+pos*w,yy),ImVec2(x+(pos+.30f)*w,yy+5.f),
            IM_COL32(155,185,176,11+j%5*3),6.f+j%3*5.f);
    }
    for(int i=0;i<27;++i) {
        float pos=std::fmod(i*.173f+t*.004f,1.f);
        float yy=.15f+std::fmod(i*.417f+t*.005f, .67f);
        d->AddCircleFilled(ImVec2(x+pos*w,y+yy*h),1.2f+i%3*.5f,
            IM_COL32(58,225,151,38+i%3*15),8);
    }
    // Edge shade leaves the middle legible and frames the full world.
    d->AddRectFilledMultiColor(ImVec2(x,y),ImVec2(x+w*.28f,y+h),
        IM_COL32(0,0,0,145),IM_COL32(0,0,0,0),IM_COL32(0,0,0,0),IM_COL32(0,0,0,165));
    d->AddRectFilledMultiColor(ImVec2(x+w*.72f,y),ImVec2(x+w,y+h),
        IM_COL32(0,0,0,0),IM_COL32(0,0,0,125),IM_COL32(0,0,0,160),IM_COL32(0,0,0,0));
}

inline void DrawSilverMedallion(const ImVec2& center, float t, float r) {
    auto* dl = ImGui::GetWindowDrawList();
    const ImU32 silver = IM_COL32(193, 209, 208, 255);
    const ImU32 shade = IM_COL32(55, 75, 73, 255);
    for (int i = 0; i < 4; ++i) {
        const float rr = r - 5.0f * i;
        dl->AddCircle(center, rr, i % 2 == 0 ? silver : shade, 64, i == 0 ? 5.0f : 2.0f);
    }
    for (int i = 0; i < 8; ++i) {
        float a = static_cast<float>(i) * 6.2831853f / 8.0f + t * .07f;
        ImVec2 a0{center.x + std::cos(a) * r * .79f, center.y + std::sin(a) * r * .79f};
        ImVec2 a1{center.x + std::cos(a) * r * 1.14f, center.y + std::sin(a) * r * 1.14f};
        dl->AddLine(a0, a1, silver, 4.0f);
    }
    const float pulse = .5f + .5f * std::sin(t * 1.7f);
    dl->AddCircleFilled(center, r*1.55f, IM_COL32(19,108,73,19),64);
    dl->AddCircleFilled(center, r*1.28f, IM_COL32(26,126,80,24),64);
    for (int i = 6; i >= 0; --i) {
        float rad = r * (.34f + static_cast<float>(i) * .09f);
        int alpha = static_cast<int>((28.0f + pulse * 17.0f) * (1.0f - i / 9.0f));
        dl->AddCircleFilled(center, rad, IM_COL32(30, 222, 135, alpha), 48);
    }
    dl->AddCircleFilled(center, r * .28f, IM_COL32(40, 208, 128, 235), 48);
    // Three drifting wreaths of green spectral smoke.
    for (int layer = 0; layer < 3; ++layer) {
        for (int i = 0; i < 18; ++i) {
            float phase = t * (.14f + layer * .055f) + i * .35f + layer;
            float rad = r * (1.18f + layer * .09f + .08f * std::sin(t + i));
            ImVec2 p{center.x + std::cos(phase) * rad, center.y + std::sin(phase) * rad * .66f};
            dl->AddCircleFilled(p, 2.5f + .9f * layer, IM_COL32(49, 199, 111, 25 + layer * 9), 12);
        }
    }
}

// Call once per frame inside an existing ImGui frame. Navigation actions are
// returned to the host so no OoT save state is modified until adapters exist.
inline float IntroEase(float v) {
    v = v < 0.f ? 0.f : (v > 1.f ? 1.f : v);
    return v*v*(3.f-2.f*v);
}

inline TitleAction DrawTitleMenu(bool hasSave) {
    const ImGuiViewport* vp = ImGui::GetMainViewport();
    const float scale = (vp->Size.x / 1280.0f < vp->Size.y / 720.0f)
                            ? vp->Size.x / 1280.0f : vp->Size.y / 720.0f;
    const float s = scale < .55f ? .55f : scale;
    ImGui::SetNextWindowPos(vp->Pos);
    ImGui::SetNextWindowSize(vp->Size);
    ImGui::SetNextWindowBgAlpha(1.0f);
    ImGuiWindowFlags flags = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove |
        ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoNavFocus |
        ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBringToFrontOnFocus;
    TitleAction action = TitleAction::None;
    if (ImGui::Begin("##VeilboundTitle", nullptr, flags)) {
        ImVec2 area = ImGui::GetContentRegionAvail();
        const float introTime = static_cast<float>(ImGui::GetTime());
        DrawKingdomBackdrop(ImGui::GetWindowPos(), vp->Size, introTime);
        const float fly = IntroEase(introTime / 1.30f);
        const float medallionScale = .35f + .65f*fly;
        const float medallionOffset = (1.f-fly)*(-vp->Size.y*.53f);
        const float beat1 = std::exp(-std::pow((introTime-1.58f)/.11f,2.f));
        const float beat2 = std::exp(-std::pow((introTime-2.05f)/.11f,2.f));
        const float beat = .13f*beat1+.17f*beat2;
        const float smoke = IntroEase((introTime-2.05f)/1.65f);
        const ImVec2 winPos = ImGui::GetWindowPos();
        const ImVec2 center(winPos.x + vp->Size.x*.5f, winPos.y + vp->Size.y*.15f + 82.f*s + medallionOffset);
        if (introTime > 2.1f && introTime < 4.5f) {
            auto* draw = ImGui::GetWindowDrawList();
            for(int i=0;i<20;++i){
                float a = introTime*1.2f+i*.314159f;
                float radius = (50.f+smoke*330.f+i*2.f)*s;
                ImVec2 point(center.x+std::cos(a)*radius,center.y+std::sin(a)*radius*.38f+smoke*75.f*s);
                draw->AddCircleFilled(point,(8.f+smoke*14.f)*s,
                    IM_COL32(40,175,110,static_cast<int>(50.f*(1.f-smoke*.65f))),18);
            }
        }
        float mid = ImGui::GetWindowPos().x + area.x * .5f;
        float top = ImGui::GetWindowPos().y + area.y * .15f;
        DrawSilverMedallion(center, introTime, 58*s*(medallionScale+beat));
        ImGui::SetCursorPosY(area.y * .42f);
        ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 8*s);
        ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(14*s, 8*s));
        ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(.055f, .09f, .10f, .85f));
        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(.09f, .30f, .24f, .95f));
        ImGui::PushStyleColor(ImGuiCol_ButtonActive, ImVec4(.13f, .42f, .30f, 1.f));
        auto centerText = [&](const char* text) {
            float w = ImGui::CalcTextSize(text).x;
            ImGui::SetCursorPosX((area.x - w) * .5f);
            ImGui::TextUnformatted(text);
        };
        const bool introRevealed = introTime >= 3.2f;
        ImGui::SetWindowFontScale(2.0f*s);
        if (introRevealed) centerText("V E I L B O U N D");
        ImGui::SetWindowFontScale(1.0f);
        ImGui::Dummy(ImVec2(0, 16*s));
        auto menuButton = [&](const char* title) {
            const float w = 290*s;
            ImGui::SetCursorPosX((area.x - w) * .5f);
            bool clicked = ImGui::Button(title, ImVec2(w, 42*s));
            ImGui::Dummy(ImVec2(0, 3*s));
            return clicked;
        };
        if (introTime >= 4.1f && menuButton("NEW GAME")) action = TitleAction::NewGame;
        ImGui::BeginDisabled(!hasSave);
        if (introTime >= 4.1f && menuButton("CONTINUE")) action = TitleAction::Continue;
        ImGui::EndDisabled();
        if (introTime >= 4.1f && menuButton("SETTINGS")) action = TitleAction::Settings;
        if (introTime >= 4.1f && menuButton("CREDITS")) action = TitleAction::Credits;
        ImGui::PopStyleColor(3);
        ImGui::PopStyleVar(2);
    }
    ImGui::End();
    return action;
}
} // namespace Veilbound

#include <ship/window/gui/GuiWindow.h>
namespace Veilbound {
// Bridge into Shipwright's actual GuiWindow rendering lifecycle.
class TitleWindow final : public Ship::GuiWindow {
  public:
    using GuiWindow::GuiWindow;
    void InitElement() override {}
    void UpdateElement() override {}
    void DrawElement() override {}
    void Draw() override {
        const TitleAction action = DrawTitleMenu(false);
        if (action == TitleAction::NewGame || action == TitleAction::Continue) {
            Hide(); // Prototype: yield back to existing Shipwright title/flow.
        } else if (action == TitleAction::Settings) {
            showSettings = !showSettings;
        } else if (action == TitleAction::Credits) {
            showCredits = !showCredits;
        }
        if (showSettings) {
            ImGui::Begin("VEILBOUND SETTINGS", &showSettings);
            ImGui::TextUnformatted("Experimental UI. Game options not connected yet.");
            ImGui::End();
        }
        if (showCredits) {
            ImGui::Begin("VEILBOUND CREDITS", &showCredits);
            ImGui::TextUnformatted("Veilbound - original independent RPG experiment");
            ImGui::End();
        }
    }
  private:
    bool showSettings = false;
    bool showCredits = false;
};
} // namespace Veilbound
