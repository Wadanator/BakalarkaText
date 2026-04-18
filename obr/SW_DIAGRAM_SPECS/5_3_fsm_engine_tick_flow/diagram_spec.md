# Obrázok 5.3 - FSM engine: poradie spracovania v jednom ticku

## Cieľ
Zobraziť poradie spracovania v `process_scene()` tak,
aby bola jasná priorita globalEvents a pipeline zmeny stavu.

## Mapovanie blokov na kód

### 1 — Začiatok ticku
| Blok | Funkcia | Popis |
|------|---------|-------|
| Kontrola konca audia | `audio_handler.check_if_ended()` | Ak audio skončilo, registruje udalosť do fronty |
| Kontrola konca videa | `video_handler.check_if_ended()` | Ak video skončilo, registruje udalosť do fronty |
| Scéna skončila? | `state_machine.is_finished()` | Ak `current_state == "END"` → `return False` |
| Načítanie aktuálneho stavu | `state_machine.get_current_state_data()` | Dáta stavu: onEnter, onExit, transitions, timeline |

### 2 — Globálne udalosti
| Blok | Funkcia | Popis |
|------|---------|-------|
| Vyhodnotenie globálnych prechodov | `get_global_events()` + `check_transitions()` so `scene_elapsed_time` | globalEvents z JSON, vyhodnotené voči celkovému času scény |
| Globálny prechod nájdený? | návratová hodnota `check_transitions()` | Prvý splnený prechod v poradí zápisu |
| Zmena stavu a návrat | `_change_state()` → `return True` | Tick končí, lokálne prechody sa nevyhodnocujú |

### 3 — Lokálne prechody
| Blok | Funkcia | Popis |
|------|---------|-------|
| Časované akcie bežia samostatne | `check_and_execute_timeline()` — no-op | Timery sú naplánované pri onEnter cez `threading.Timer` |
| Vyhodnotenie lokálnych prechodov | `check_transitions()` so `state_elapsed_time` | timeout · audioEnd · videoEnd · mqttMessage · always |
| Lokálny prechod nájdený? | návratová hodnota `check_transitions()` | Prvý splnený prechod v poradí zápisu |
| Zmena stavu | `_change_state()` | Vykonanie prechodu |
| Scéna pokračuje | `return True` | Tick skončil normálne |

### 4 — Zmena stavu
| Blok | Funkcia | Popis |
|------|---------|-------|
| Vykonanie výstupných akcií | `execute_onExit()` | MQTT/audio/video príkazy starého stavu |
| Prechod do nového stavu | `state_machine.goto_state()` | Aktualizácia vnútorného kontextu |
| Vyčistenie čakajúcich udalostí | `transition_manager.clear_events()` | MQTT · audioEnd · videoEnd fronty |
| Zrušenie starých časovačov | `reset_timeline_tracking()` | Inkrementácia `_state_generation`, cancel starých timerov |
| Vykonanie vstupných akcií + nové časovače | `execute_onEnter()` + `_schedule_timeline()` | Akcie nového stavu, nové threading.Timer inšta