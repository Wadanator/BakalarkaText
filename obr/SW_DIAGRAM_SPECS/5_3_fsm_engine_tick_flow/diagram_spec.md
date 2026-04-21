# Obrázok 5.3 — FSM engine: poradie spracovania v jednom ticku

## Cieľ

Zobraziť presné poradie spracovania v `process_scene()` tak, aby bola jasná priorita globalEvents nad lokálnymi prechodmi a celá pipeline zmeny stavu vrátane cleanup starých časovačov.

---

## Mapovanie blokov na kód

### Fáza 1 — Začiatok ticku

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Kontrola prehrávania audia | `raspberry_pi/utils/audio_handler.py` → `check_if_ended()` | Overí či aktuálne prehrávaná stopa skončila; ak áno, vloží záznam o ukončení do fronty udalostí `audio_end_events` v `transition_manager` |
| Kontrola prehrávania videa | `raspberry_pi/utils/video_handler.py` → `check_if_ended()` | Overí dostupnosť externého video procesu cez IPC; ak video skončilo, vloží záznam o ukončení do fronty `video_end_events` |
| Je scéna ukončená? | `raspberry_pi/utils/state_machine.py` → `is_finished()` | Ak `current_state == "END"` vráti `True` → `process_scene()` vráti `False` → scénová slučka sa ukončí (`Áno` = Ukončenie slučky, `Nie` = pokračuj) |
| Načítanie definície stavu | `state_machine.py` → `get_current_state_data()` | Vráti slovník stavu z JSON: `onEnter`, `onExit`, `transitions`, `timeline`; pravidlá a akcie pre aktuálny krok |

### Fáza 2 — Globálne udalosti (vyhodnocujú sa PRVÉ)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Sú definované globálne pravidlá? | `state_machine.py` → `get_global_events()` | Overí, či JSON scéna obsahuje sekciu `globalEvents` s definovanými pravidlami; `Nie` = preskočí na Spracovanie časových udalostí, `Áno` = pokračuj na vyhodnotenie podmienky |
| Bola splnená globálna podmienka? | `transition_manager.check_transitions()` so `scene_elapsed_time` | Globálne prechody sa vyhodnocujú voči celkovému uplynulému času scény, nie času v stave; prvý splnený prechod vyhráva; `Áno` = Proces zmeny stavu, `Nie` = Spracovanie časových udalostí |

### Fáza 3 — Lokálne prechody

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Spracovanie časových udalostí | `state_executor.py` → `_schedule_timeline()` | Timeline timery naplánované pri vstupe do stavu cez `threading.Timer`; tick ich len kontroluje, nespúšťa znova; vykonávané automaticky na pozadí |
| Vyhodnotenie podmienok stavu | `transition_manager.py` → `check_transitions()` so `state_elapsed_time` | Vyhodnocuje typy: `timeout`, `audioEnd`, `videoEnd`, `mqttMessage`, `always` — v poradí zápisu v JSON; senzory, tlačidlá, uplynutý čas |
| Je čas prejsť do nového stavu? | návratová hodnota `check_transitions()` | Prvý splnený prechod vyhráva; `Áno` = Proces zmeny stavu, `Nie` = Ukončenie cyklu |

### Fáza 4 — Detail zmeny stavu (Proces zmeny stavu)

Tento blok v diagrame je zobrazený ako jeden súhrnný blok s číslovaným zoznamom krokov:

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Proces zmeny stavu | `state_machine.py` → `_change_state()` | Vykoná celú sekvenciu zmeny stavu v tomto poradí: |

Kroky Procesu zmeny stavu:
1. **Vykonanie výstupných akcií** — `state_executor.py` → `execute_onExit()` — vykoná MQTT/audio/video príkazy zo sekcie `onExit` odchádzajúceho stavu
2. **Aktivácia nového stavu** — `state_machine.py` → `goto_state()` — aktualizuje `current_state` a `state_start_time` v internom kontexte
3. **Vymazanie starých udalostí** — `transition_manager.py` → `clear_events()` — vymaže fronty `mqtt_events`, `audio_end_events`, `video_end_events` — udalosti starého stavu nesmú ovplyvniť nový
4. **Zrušenie pôvodných časovačov** — `state_executor.py` → `reset_timeline_tracking()` — inkrementuje `_state_generation` counter; existujúce `threading.Timer` inštancie skontrolujú generáciu pred vykonaním — ak nesedí, akciu preskočia
5. **Vykonanie vstupných akcií** — `state_executor.py` → `execute_onEnter()` + `_schedule_timeline()` — vykoná akcie sekcie `onEnter` nového stavu; naplánuje nové `threading.Timer` pre timeline akcie

### Ukončenie cyklu

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Ukončenie cyklu | `return True` z `process_scene()` | Tick skončil normálne (bez zmeny stavu alebo po zmene stavu); scéna pokračuje ďalej; ďalší tick príde po `scene_processing_sleep` |

---

## Kľúčové detaily pre obhajobu

| Otázka | Odpoveď |
|---|---|
| Prečo globalEvents pred lokálnymi? | Slúžia ako globálne podmienky (napr. celkový timeout scény) — musia mať vyššiu prioritu ako stavová logika |
| Ako sa zabraňuje race condition pri časovačoch? | `_state_generation` counter — timer pri spustení overí, či generácia súhlasí; ak nie (stav sa zmenil), akciu preskočí |
| Čo ak nie je splnený žiadny prechod? | `process_scene()` vráti `True` — scéna čaká na ďalší tick |
| Ako funguje `always` prechod? | `_check_always()` vráti vždy `True` — okamžitý prechod bez podmienky; typicky posledný v zozname ako fallback |
| Prečo sú globálne pravidlá a podmienka dve separátne rozhodnutia? | Prvé rozhodnutie overí, či JSON vôbec obsahuje globalEvents sekciu; druhé vyhodnotí, či je niektorá podmienka splnená — obe sú potrebné pre správnu logiku vetvenia |

---

## Kľúčové súbory

| Súbor | Úloha |
|---|---|
| `raspberry_pi/utils/scene_parser.py` | Volá `process_scene()` v slučke |
| `raspberry_pi/utils/state_machine.py` | Udržiava stav, `is_finished()`, `goto_state()` |
| `raspberry_pi/utils/transition_manager.py` | `check_transitions()`, `clear_events()`, fronty udalostí |
| `raspberry_pi/utils/state_executor.py` | `execute_onEnter/Exit()`, `_schedule_timeline()`, `reset_timeline_tracking()` |
| `raspberry_pi/utils/audio_handler.py` | `check_if_ended()` — zdroj `audioEnd` udalostí |
| `raspberry_pi/utils/video_handler.py` | `check_if_ended()` — zdroj `videoEnd` udalostí |
