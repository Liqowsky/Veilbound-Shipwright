# VEILBOUND — Wybrzeże Świtu / Pustynia Dwóch Epok

**Status:** pierwszy **prototyp geometrii w Blenderze**, a nie grywalny poziom Ship of Harkinian/Android.

## Kanon lokacji
Bohater pochodzi z pustynnego wybrzeża Vaelorii. W dzieciństwie: piasek, piaskowcowa osada, turkusowe morze, latarnia, dom rodzinny na skałach i jaskinia. Po katastrofie bohater wpada do morza i budzi się 25 lat później na tym samym wybrzeżu, lecz na pustyni zasypanej śniegiem, podczas śnieżyc. **Geografia wspólna, dwie epoki**.

## Pliki
- `world_layout.json`: współrzędne kluczowych punktów, powiązania i warianty epok.
- `generate_blender.py`: uruchamiany w Blenderze skrypt budujący prototyp z terenami, wodą, osadą, latarnią, jaskinią i obiektami wersji przyszłej.

## Uruchomienie
W Blenderze 4.x: Scripting → otwórz `generate_blender.py` → Run Script. Zmień widoczność kolekcji `PAST_...` i `FUTURE_...` by zobaczyć epoki. Skrypt tworzy **nową scenę**, więc uruchamiaj go w pustym pliku albo po zapisaniu pracy. Potem zapisz `.blend`.

## Następne techniczne bramki
1. Weryfikacja geometrii i skali w Blenderze.
2. Low-poly siatka terenu: rozdział kolizji od renderowanej geometrii.
3. Eksport `.glb` i weryfikacja pipeline importu scen z narzędziem obsługującym nasz fork Shipwrighta.
4. Import i test kamery, kolizji, pozycji startu, dwóch epok na Androidzie.
5. Dopiero wtedy wysokiej rozdzielczości ręcznie malowane tekstury oraz docelowa geometria/particle.

Nie dotykamy obecnego działającego APK ani wejść START. Prototyp jest niezależny od buildów Androida.
