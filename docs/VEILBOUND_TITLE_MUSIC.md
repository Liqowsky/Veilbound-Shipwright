# VEILBOUND title music integration — Emerald Whispers

Status: WAV/OGG prepared; custom streamed-audio archive still needs building and Android runtime verification.

The user-supplied track is `Emerald Whispers`. The clean loop is available in the VEILBOUND title audio export ZIP supplied in this chat, NOT in this repository. Do not commit copyrighted `oot.o2r` or other Nintendo assets.

## Integration location

The title actor is `soh/src/overlays/actors/ovl_En_Mag/z_en_mag.c`, changed on this branch to show an emerald glow and a PRESS START prompt. Don't add native filesystem WAV/OGG calls into this actor. Its standard title BGM is controlled by the engine's audio sequence system.

## Required streamed audio import

Per Shipwright streamed-audio modding flow:
1. Use a compatible Future exporter to convert `Emerald Whispers.ogg` into a custom streamed-audio `.o2r` archive.
2. Load that `.o2r` from the game's `mods` directory, alongside the native game archive.
3. Map the custom track onto the title-music audio slot using the Audio Editor. Do not guess at a numerical sequence ID.
4. Verify startup, loop transition, PRESS START-to-file-select fade and Android audio output.

Do not report music as integrated until custom streamed-audio loading and a startup capture have been confirmed.

## Music

Original: approximately 3:04 stereo at 48kHz.
Prepared OGG: approximately 2:58 stereo 44.1kHz; arranged for loop.
