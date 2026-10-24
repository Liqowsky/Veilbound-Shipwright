# Veilbound — isolated Shipwright experiment

This is **not** a finished game and does not bundle Nintendo assets.

## Scope

- Original Veilbound main menu: silver ancient medallion, ethereal green smoke, epic whole-kingdom vista (not the desert region). Buttons: NEW GAME, CONTINUE, SETTINGS, CREDITS. No lineage wording on the main menu.
- OoT-like third-person camera and controls.
- First original location: desert warrior settlement, child protagonist, elder farmer, eight crop larvae in 3 tiers, wooden stick. No additional invented characters, quests or lore.
- Goal: assess asset replacement, engine dependencies, and Android build feasibility.

## Source locations established

- `soh/soh/SohGui/`: Ship UI/menus, overlays and settings
- `soh/soh/z_scene_otr.cpp`: scene loading / resource integration
- `soh/soh/z_play_otr.cpp`: play-state integration
- `soh/src/`: extracted game engine and overlays
- `soh/assets/`: resource references / asset pipeline

## Important limitations

Shipwright is built as an enhanced port of Ocarina of Time, not a general-purpose standalone editor. Its data, scene and animation pipeline are deeply linked to the original game. Do not distribute Nintendo assets or ROM files. Review license of any reused code/dependencies before standalone distribution. The fork currently remains public.

## Next technical checkpoint

1. Identify game-title rendering and hook boundaries.
2. Verify whether the engine can enter a new original room without an OoT resource archive.
3. Determine Android support and build requirements, then compare with the already working Godot Android pipeline.
4. Only then integrate original menu art, original models and gameplay.

Main Veilbound Godot repo is separate; this branch is an alternative technology feasibility test.
