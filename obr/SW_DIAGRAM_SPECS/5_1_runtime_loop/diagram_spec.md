# Obrázok 5.1 — Runtime slučka softvérových vrstiev

## Cieľ

Zobraziť uzavretý prevádzkový tok od vstupného triggeru cez backend, MQTT broker a ESP32 uzly späť k dashboardu. Diagram je rozdelený do 5 zón zľava doprava a ukazuje, ako príkaz, feedback a push do UI tvoria uzavretú slučku.

---

## Mapovanie blokov na kód

### Zóna 1 — Vstupy a triggery

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Fyzické tlačidlo | `ArduinoIDE/esp32_mqtt_button/hardware.cpp` → `wasButtonPressed()` | Detekuje stlačenie s cooldownom a debouncingom; po stlačení zavolá `publishSceneTrigger()` ktorý odošle MQTT správu `roomX/scene` s payloadom `START` |
| Operátor (webový dashboard) | `Web/routes/` → `POST /api/run_scene`, `POST /api/stop_scene` | Operátor spustí alebo zastaví scénu cez webový dashboard; route zavolá `MuseumController.start_scene_by_name()` alebo `stop_scene()` |
| MQTT príkaz (roomX/start_scene) | `raspberry_pi/utils/mqtt/topic_rules.py` → `scene_topic()`, `named_scene_topic()` | `roomX/scene` s payloadom `START` = default scéna; `roomX/start_scene` s payloadom = meno JSON súboru scény |

### Zóna 2 — Backend (Raspberry Pi)

#### Hlavná orchestrácia

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Orchestrácia | `raspberry_pi/main.py` → `MuseumController` | Centrálny kontrolér — prijíma triggery, zamyká `scene_lock`, spúšťa daemon vlákno scény, riadi cleanup a watchdog state file |

#### Sub-zóna: daemon vlákno — spracovanie scény

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Koordinátor scény | `raspberry_pi/utils/scene_parser.py` → `load_scene()`, `start_scene()`, `process_scene()` | Načítava JSON súbor scény, spúšťa stavový automat, v každom tiku volá `process_scene()` ktorý vracia `True` (pokračuj) alebo `False` (koniec) |
| Stavový automat | `raspberry_pi/utils/state_machine.py` + `transition_manager.py` | `state_machine` uchováva `current_state` a `context` (časovače, fronty udalostí); `transition_manager.check_transitions()` vyhodnocuje prechody v poradí zápisu |
| Vykonávač akcií | `raspberry_pi/utils/state_executor.py` → `execute_onEnter()`, `execute_onExit()`, `_schedule_timeline()` | Vykonáva akcie typov `mqtt`, `audio`, `video`; timeline akcie plánuje cez `threading.Timer` |

#### MQTT vrstva a sledovanie výstupov

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| MQTT klient | `raspberry_pi/utils/mqtt/mqtt_client.py` → `publish()` | Fyzický publish cez `paho-mqtt`; kontroluje `rc == 0`; odošle príkaz a okamžite registruje tracking |
| Sledovanie potvrdení | `raspberry_pi/utils/mqtt/mqtt_feedback_tracker.py` → `track_published_message()` | Volaný po úspešnom publishi; spustí `threading.Timer(feedback_timeout, _handle_feedback_timeout)`; pri OK feedbacku timer zruší a aktualizuje confirmed stav |

#### Sub-zóna: sledovanie výstupov

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Stav výstupov | `raspberry_pi/utils/mqtt/mqtt_actuator_state_store.py` | Pre každý topic uchováva dvojicu `desired` (po publish) a `confirmed` (po feedback OK); `force_all_off()` pri STOP nastaví obe hodnoty na `OFF` |

#### Perzistencia a infraštruktúra

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Stav scény | `/tmp/museum_scene_state` (zapisuje `main.py` → `_set_scene_running()`) | Textový súbor s hodnotou `running` alebo `idle`; watchdog ho číta pred rozhodnutím o reštarte — file starší ako 2 hodiny sa ignoruje |
| Watchdog | `raspberry_pi/watchdog/` → `MuseumWatchdog` | Číta stav scény pred rozhodnutím o reštarte; ak súbor obsahuje `running`, čaká na ukončenie scény |
| Webové rozhranie | `Web/app.py` + `Web/dashboard.py` | Flask + Flask-SocketIO server bežiaci v daemon vlákne; emituje push udalosti `status_update`, `scene_progress`, `new_log`, `device_runtime_state_update` všetkým pripojeným klientom |
| Log handler | `Web/log_handler.py` → `WebLogHandler.emit()` | Python logging handler zachytí každý log záznam a okamžite ho odošle cez Socket.IO udalosťou `new_log`; prepojený s `Webovým rozhraním` |

### Zóna 3 — MQTT Broker

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Broker | externá služba (Mosquitto / EMQX) | Smerovač správ; neobsahuje logiku aplikácie; backend aj ESP32 uzly sú jeho klienti |

### Zóna 4 — Periférne uzly — ESP32

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Tlačidlový uzol | `esp32_mqtt_button.ino` + `hardware.cpp` | `wasButtonPressed()` s cooldownom; po stlačení `publishSceneTrigger()` → MQTT `roomX/scene START`; LED potvrdenie `ledButtonConfirm()`; publikuje spätnú väzbu `START · status` na broker |
| Motorický uzol | `esp32_mqtt_controller_MOTORS.ino` + `hardware.cpp` | Prijíma príkazy smer + rýchlosť; `updateMotorSmoothly()` realizuje plynulú PWM zmenu; zabezpečuje bezpečnú zmenu smeru; publikuje `feedback / status` |
| Reléový uzol | `esp32_mqtt_controller_RELAY.ino` + `effects_manager.h` | Mapuje MQTT topic → GPIO výstup; `effects_manager` pre časované sekvencie; lokálne vykonáva efektové slučky bez závislosti na backende; publikuje `feedback / status` |

### Zóna 5 — Operátor

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Dashboard | `frontend/src/` — React SPA (Vite) | Po prihlásení nadväzuje Socket.IO spojenie; server pushuje udalosti bez pollingu; operátor vidí stav scény, runtime stav zariadení, logy a štatistiky v reálnom čase |

---

## Kľúčové šípky — čo reprezentujú

| Šípka | Čo sa prenáša | Smer |
|---|---|---|
| Fyzické tlačidlo / Operátor / MQTT príkaz → Orchestrácia | Požiadavka na spustenie scény | Vstupy → `main.py` |
| Orchestrácia → Koordinátor scény | Načítaj a spusti scénu | `_initiate_scene_start()` → `load_scene()` |
| Koordinátor scény → Stavový automat | Tick FSM | `process_scene()` → `check_transitions()` |
| Stavový automat → Vykonávač akcií | Vykonaj akcie stavu | `_change_state()` → `execute_onEnter()` |
| Vykonávač akcií → MQTT klient | Príkaz pre zariadenie | `_execute_mqtt()` → `publish()` |
| MQTT klient → Sledovanie potvrdení | odoslaný príkaz (dashed) | `publish()` → `track_published_message()` |
| MQTT klient → Broker | Publikovanie príkazu | `publish()` → broker |
| Broker → Motorický / Reléový uzol | Doručenie príkazu | broker → ESP32 |
| Tlačidlový uzol → Broker | START · status (dashed) | ESP32 → broker |
| Motorický / Reléový uzol → Broker | feedback / status (dashed) | ESP32 → broker |
| Broker → Sledovanie potvrdení | spätná väzba | broker → `handle_feedback_message()` |
| Broker → Orchestrácia | spustenie scény | broker → `_initiate_scene_start()` |
| Sledovanie potvrdení → Stav výstupov | potvrdenie | `update_confirmed()` |
| Stav výstupov → Webové rozhranie | zmena stavu | `_notify()` → `broadcast_device_runtime_state()` |
| Log handler → Webové rozhranie | logy (new_log) (dashed) | `WebLogHandler.emit()` → SocketIO |
| Orchestrácia → Webové rozhranie | stav scény · priebeh | `broadcast_status()`, `broadcast_stats()`, `scene_progress` |
| Webové rozhranie → Dashboard | Socket.IO push | SocketIO → React SPA |
| Orchestrácia → MQTT klient | STOP príkaz (dashed) | `broadcast_stop()` → `publish()` |
| Orchestrácia → Stav výstupov | bezpečný OFF (dashed) | `force_all_off()` |
| Orchestrácia → Stav scény | running / idle (dashed) | `_set_scene_running()` → `/tmp/museum_scene_state` |
| Stav scény → Watchdog | rozhodnutie o reštarte (dashed) | state file → `MuseumWatchdog._is_scene_running()` |

---

## Kľúčové súbory

| Súbor | Úloha |
|---|---|
| `raspberry_pi/main.py` | Orchestrácia, scene thread, stop flow, watchdog state file |
| `raspberry_pi/utils/scene_parser.py` | Load, validácia, FSM tick, preloading médií |
| `raspberry_pi/utils/state_machine.py` | Stav scény, context, zmeny stavov |
| `raspberry_pi/utils/state_executor.py` | Vykonávanie mqtt/audio/video akcií |
| `raspberry_pi/utils/mqtt/mqtt_feedback_tracker.py` | Track publish, timeout, confirmed update |
| `raspberry_pi/utils/mqtt/mqtt_actuator_state_store.py` | desired/confirmed stav, force_all_off |
| `Web/dashboard.py` | SocketIO emits — status, logs, scene_progress, device state |
| `Web/log_handler.py` | Python logging → Socket.IO bridge (new_log) |
| `ArduinoIDE/esp32_mqtt_button/esp32_mqtt_button.ino` | Button trigger logika |
| `ArduinoIDE/esp32_mqtt_controller_MOTORS/` | Motor PWM riadenie |
| `ArduinoIDE/esp32_mqtt_controller_RELAY/` | Relay mapovanie + efekty |
