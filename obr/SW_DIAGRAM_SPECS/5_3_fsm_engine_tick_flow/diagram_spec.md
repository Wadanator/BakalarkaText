# Obrázok 5.3 — FSM engine: poradie spracovania v jednom ticku

## Cieľ

Zobraziť presné poradie spracovania v `process_scene()` tak, aby bola jasná priorita globalEvents nad lokálnymi prechodmi a celá pipeline zmeny stavu vrátane cleanup starých časovačov.

---

## Mapovanie blokov na kód

### Fáza 1 — Začiatok ticku

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Kontrola konca audia | `raspberry_pi/utils/audio_handler.py` → `check_if_ended()` | Overí či aktuálne prehrávaná stopa skončila; ak áno, vloží udalosť do fronty `audio_end_events` v `transition_manager` |
| Kontrola konca videa | `raspberry_pi/utils/video_handler.py` → `check_if_ended()` | Overí dostupnosť externého video procesu cez IPC; ak video skončilo, vloží udalosť do `video_end_events` |
| Scéna skončila? | `raspberry_pi/utils/state_machine.py` → `is_finished()` | Ak `current_state == "END"` vráti `True` → `process_scene()` vráti `False` → scénová slučka sa ukončí |
| Načítanie aktuálneho stavu | `state_machine.py` → `get_current_state_data()` | Vráti slovník stavu z JSON: `onEnter`, `onExit`, `transitions`, `timeline` |

### Fáza 2 — Globálne udalosti (vyhodnocujú sa PRVÉ)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Vyhodnotenie globalEvents | `state_machine.py` → `get_global_events()` + `transition_manager.check_transitions()` so `scene_elapsed_time` | Globálne prechody z koreňa JSON scény; vyhodnocujú sa voči celkovému uplynulému času scény, nie času v stave |
| Globálny prechod nájdený? | návratová hodnota `check_transitions()` | Prvý splnený prechod v poradí zápisu v JSON vyhráva |
| Zmena stavu + koniec ticku | `_change_state()` → `return True` | Tick okamžite končí; lokálne prechody aktuálneho stavu sa nevyhodnotia — globálne majú vždy prednosť |

### Fáza 3 — Lokálne prechody

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Timeline akcie bežia samostatne | `state_executor.py` → `_schedule_timeline()` | Timeline timery sú naplánované pri vstupe do stavu cez `threading.Timer`; tick ich len kontroluje, nespúšťa znova |
| Vyhodnotenie lokálnych prechodov | `transition_manager.py` → `check_transitions()` so `state_elapsed_time` | Vyhodnocuje typy: `timeout`, `audioEnd`, `videoEnd`, `mqttMessage`, `always` — v poradí zápisu v JSON |
| Lokálny prechod nájdený? | návratová hodnota `check_transitions()` | Prvý splnený prechod vyhráva |
| Zmena stavu | `_change_state()` | Vykoná prechod do cieľového stavu |
| Scéna pokračuje | `return True` | Tick skončil normálne bez zmeny stavu; ďalší tick príde po `scene_processing_sleep` |

### Fáza 4 — Detail zmeny stavu (`_change_state()`)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Výstupné akcie starého stavu | `state_executor.py` → `execute_onExit()` | Vykoná MQTT/audio/video príkazy zo sekcie `onExit` odchádzajúceho stavu |
| Prechod do nového stavu | `state_machine.py` → `goto_state()` | Aktualizuje `current_state` a `state_start_time` v internom kontexte |
| Vyčistenie čakajúcich udalostí | `transition_manager.py` → `clear_events()` | Vymaže fronty `mqtt_events`, `audio_end_events`, `video_end_events` — udalosti starého stavu nesmú ovplyvniť nový |
| Zrušenie starých časovačov | `state_executor.py` → `reset_timeline_tracking()` | Inkrementuje `_state_generation` counter; existujúce `threading.Timer` inštancie skontrolujú generáciu pred vykonaním — ak nesedí, akciu preskočia |
| Vstupné akcie + nové časovače | `state_executor.py` → `execute_onEnter()` + `_schedule_timeline()` | Vykoná akcie sekcie `onEnter` nového stavu; naplánuje nové `threading.Timer` pre timeline akcie |

---

## Kľúčové detaily pre obhajobu

| Otázka | Odpoveď |
|---|---|
| Prečo globalEvents pred lokálnymi? | Slúžia ako globálne podmienky (napr. celkový timeout scény) — musia mať vyššiu prioritu ako stavová logika |
| Ako sa zabraňuje race condition pri časovačoch? | `_state_generation` counter — timer pri spustení overí, či generácia súhlasí; ak nie (stav sa zmenil), akciu preskočí |
| Čo ak nie je splnený žiadny prechod? | `process_scene()` vráti `True` — scéna čaká na ďalší tick |
| Ako funguje `always` prechod? | `_check_always()` vráti vždy `True` — okamžitý prechod bez podmienky; typicky posledný v zozname ako fallback |

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
