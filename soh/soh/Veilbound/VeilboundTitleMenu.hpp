#pragma once
// VEILBOUND / Shipwright feasibility experiment.
// Original title-menu UI component. It has no dependency on Nintendo art assets.
// This is intentionally not hooked to the engine's title state yet.
#include <imgui.h>
#include <cmath>

namespace Veilbound {
enum class TitleAction { None, NewGame, Continue, Settings, Credits };

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
inline TitleAction DrawTitleMenu(bool hasSave) {
    const ImGuiViewport* vp = ImGui::GetMainViewport();
    const float scale = (vp->Size.x / 1280.0f < vp->Size.y / 720.0f)
                            ? vp->Size.x / 1280.0f : vp->Size.y / 720.0f;
    const float s = scale < .55f ? .55f : scale;
    ImGui::SetNextWindowPos(vp->Pos);
    ImGui::SetNextWindowSize(vp->Size);
    ImGui::SetNextWindowBgAlpha(0.97f);
    ImGuiWindowFlags flags = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove |
        ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoNavFocus |
        ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBringToFrontOnFocus;
    TitleAction action = TitleAction::None;
    if (ImGui::Begin("##VeilboundTitle", nullptr, flags)) {
        ImVec2 area = ImGui::GetContentRegionAvail();
        float mid = ImGui::GetWindowPos().x + area.x * .5f;
        float top = ImGui::GetWindowPos().y + area.y * .15f;
        DrawSilverMedallion(ImVec2(mid, top + 82*s), static_cast<float>(ImGui::GetTime()), 58*s);
        ImGui::SetCursorPosY(area.y * .42f);
        ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 8*s);
        ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(14*s, 8*s));
        ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(.10f, .14f, .14f, .96f));
        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(.12f, .30f, .24f, .98f));
        ImGui::PushStyleColor(ImGuiCol_ButtonActive, ImVec4(.13f, .42f, .30f, 1.f));
        auto centerText = [&](const char* text) {
            float w = ImGui::CalcTextSize(text).x;
            ImGui::SetCursorPosX((area.x - w) * .5f);
            ImGui::TextUnformatted(text);
        };
        centerText("V E I L B O U N D");
        ImGui::Dummy(ImVec2(0, 16*s));
        auto menuButton = [&](const char* title) {
            const float w = 290*s;
            ImGui::SetCursorPosX((area.x - w) * .5f);
            bool clicked = ImGui::Button(title, ImVec2(w, 42*s));
            ImGui::Dummy(ImVec2(0, 3*s));
            return clicked;
        };
        if (menuButton("NEW GAME")) action = TitleAction::NewGame;
        ImGui::BeginDisabled(!hasSave);
        if (menuButton("CONTINUE")) action = TitleAction::Continue;
        ImGui::EndDisabled();
        if (menuButton("SETTINGS")) action = TitleAction::Settings;
        if (menuButton("CREDITS")) action = TitleAction::Credits;
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
