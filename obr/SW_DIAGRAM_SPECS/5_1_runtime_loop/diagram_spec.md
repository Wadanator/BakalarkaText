# Obrázok 5.1 — Runtime slučka softvérových vrstiev

## Cieľ

Zobraziť uzavretý prevádzkový tok od vstupného triggeru cez backend, MQTT broker a ESP32 uzly späť k dashboardu. Diagram je rozdelený do 5 zón zľava doprava a ukazuje, ako príkaz, feedback a push do UI tvoria uzavretú slučku.

---

## Mapovanie blokov na kód

### Zóna 1 — Vstupy a triggery

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Fyzické tlačidlo | `ArduinoIDE/esp32_mqtt_button/hardware.cpp` → `wasButtonPressed()` | Detekuje stlačenie s cooldownom a debouncingom; po stlačení zavolá `publishSceneTrigger()` ktorý odošle MQTT správu `roomX/scene` s payloadom `START` |
| Operátor (web) | `Web/routes/` → `POST /api/run_scene`, `POST /api/stop_scene` | Operátor spustí alebo zastaví scénu cez webový dashboard; route zavolá `MuseumController.start_scene_by_name()` alebo `stop_scene()` |
| Topic trigger | `raspberry_pi/utils/mqtt/topic_rules.py` → `scene_topic()`, `named_scene_topic()` | `roomX/scene` s payloadom `START` = default scéna; `roomX/start_scene` s payloadom = meno JSON súboru scény |

### Zóna 2 — Backend (Raspberry Pi)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Orchestrácia | `raspberry_pi/main.py` → `MuseumController` | Centrálny kontrolér — prijíma triggery, zamyká `scene_lock`, spúšťa daemon vlákno scény, riadi cleanup a watchdog state file |
| SceneParser | `raspberry_pi/utils/scene_parser.py` → `load_scene()`, `start_scene()`, `process_scene()` | Načítava JSON súbor scény, spúšťa stavový automat, v každom tiku volá `process_scene()` ktorý vracia `True` (pokračuj) alebo `False` (koniec) |
| FSM jadro | `raspberry_pi/utils/state_machine.py` + `transition_manager.py` | `state_machine` uchováva `current_state` a `context` (časovače, fronty udalostí); `transition_manager.check_transitions()` vyhodnocuje prechody v poradí zápisu |
| StateExecutor | `raspberry_pi/utils/state_executor.py` → `execute_onEnter()`, `execute_onExit()`, `_schedule_timeline()` | Vykonáva akcie typov `mqtt`, `audio`, `video`; timeline akcie plánuje cez `threading.Timer` |
| MQTT client + Feedback tracker | `raspberry_pi/utils/mqtt/mqtt_client.py` + `mqtt_feedback_tracker.py` | `publish()` odošle príkaz a okamžite zavolá `track_published_message()` ktorý spustí timeout timer; pri prijatí `OK` feedback timer zruší a aktualizuje confirmed stav |
| ActuatorStateStore | `raspberry_pi/utils/mqtt/mqtt_actuator_state_store.py` | Pre každý topic uchováva dvojicu `desired` (po publish) a `confirmed` (po feedback OK); `force_all_off()` pri STOP nastaví obe hodnoty na `OFF` |
| Web backend | `Web/app.py` + `Web/dashboard.py` | Flask + Flask-SocketIO server bežiaci v daemon vlákne; emituje push udalosti `status_update`, `scene_progress`, `new_log`, `device_runtime_state_update` všetkým pripojeným klientom |
| Scene state file | `/tmp/museum_scene_state` (zapisuje `main.py` → `_set_scene_running()`) | Textový súbor s hodnotou `running` alebo `idle`; watchdog ho číta pred rozhodnutím o reštarte — file starší ako 2 hodiny sa ignoruje |

### Zóna 3 — MQTT Broker

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| MQTT broker | externá služba (Mosquitto / EMQX) | Smerovač správ; neobsahuje logiku aplikácie; backend aj ESP32 uzly sú jeho klienti |

### Zóna 4 — ESP32 uzly

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Spoločné jadro uzlov | `wifi_manager.h`, `mqtt_manager.h`, `connection_monitor.h`, `wdt_manager.h` | Každý uzol zdieľa: Wi-Fi connect/reconnect, MQTT connect/reconnect s LWT (`offline` retained), odber `roomX/STOP`, watchdog timer reset, feedback publish na `topic/feedback` |
| Button uzol | `esp32_mqtt_button.ino` + `hardware.cpp` | `wasButtonPressed()` s cooldownom; po stlačení `publishSceneTrigger()` → MQTT `roomX/scene START`; LED potvrdenie `ledButtonConfirm()` |
| Motor uzol | `esp32_mqtt_controller_MOTORS.ino` + `hardware.cpp` | Prijíma príkazy smer + rýchlosť; `updateMotorSmoothly()` realizuje plynulú PWM zmenu; zabezpečuje bezpečnú zmenu smeru |
| Relay uzol | `esp32_mqtt_controller_RELAY.ino` + `effects_manager.h` | Mapuje MQTT topic → GPIO výstup; `effects_manager` pre časované sekvencie; lokálne vykonáva efektové slučky bez závislosti na backende |

### Zóna 5 — Dashboard (UI)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Dashboard UI | `frontend/src/` — React SPA (Vite) | Po prihlásení nadväzuje Socket.IO spojenie; server pushuje udalosti bez pollingu; operátor vidí stav scény, runtime stav zariadení, logy a štatistiky v reálnom čase |

---

## Kľúčové šípky — čo reprezentujú

| Šípka | Čo sa prenáša | Smer |
|---|---|---|
| Trigger → Orchestrácia | Požiadavka na spustenie scény | Button / MQTT / Web → `main.py` |
| Orchestrácia → SceneParser | Načítaj a spusti scénu | `_initiate_scene_start()` → `load_scene()` |
| FSM → StateExecutor | Vykonaj akcie stavu | `_change_state()` → `execute_onEnter()` |
| StateExecutor → MQTT Client | Príkaz pre zariadenie | `_execute_mqtt()` → `publish()` |
| ESP32 → Feedback tracker | Potvrdenie vykonania | `topic/feedback OK` → `handle_feedback_message()` |
| ActuatorStore → Web backend | Zmena stavu zariadenia | `_notify()` → `broadcast_device_runtime_state()` |
| Orchestrácia → Web backend | Stav systému a scény | `broadcast_status()`, `broadcast_stats()`, `scene_progress` |
| STOP vetva | Núdzové vypnutie | `force_all_off()` + `broadcast_stop()` → `roomX/STOP` |

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
| `ArduinoIDE/esp32_mqtt_button/esp32_mqtt_button.ino` | Button trigger logika |
| `ArduinoIDE/esp32_mqtt_controller_MOTORS/` | Motor PWM riadenie |
| `ArduinoIDE/esp32_mqtt_controller_RELAY/` | Relay mapovanie + efekty |
