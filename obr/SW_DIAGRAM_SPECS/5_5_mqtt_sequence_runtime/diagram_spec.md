# Obrázok 5.5 - Sekvenčný tok MQTT správ počas vykonania akcie

## Cieľ
Zobraziť kompletný runtime sekvenčný tok pre jednu akciu scény:
odoslanie príkazu, desired update, feedback vetva, confirmed update,
timeout vetva a STOP vetva. Dôraz na poradie volaní presne podľa kódu
a na rozlíšenie desired vs. confirmed stavu v ActuatorStateStore.

---

## Mapovanie blokov na kód

### 1 — Odoslanie príkazu
| Blok | Funkcia / súbor | Popis |
|------|----------------|-------|
| StateExecutor vykoná akciu | `state_executor.py` → `_execute_mqtt()` | Zavolá `mqtt_client.publish(topic, message)` |
| MQTT Client publikuje na broker | `mqtt_client.py` → `publish()` | `self.client.publish(topic, message)` — fyzický publish je **prvý** krok; rc == 0 podmienka |
| FeedbackTracker zaznamená | `mqtt_feedback_tracker.py` → `track_published_message()` | Volaný **po** úspešnom publishi; zavolá `update_desired` a spustí `threading.Timer(feedback_timeout, _handle_feedback_timeout)` |
| ActuatorStateStore update_desired | `mqtt_actuator_state_store.py` → `update_desired()` | Nastaví `desired_state` endpointu; UI vidí plánovaný stav ešte pred potvrdením |

> **Poznámka:** audio/video témy (`/audio`, `/video`) sa v `track_published_message()` preskakujú — pre ne sa timer nespúšťa. `expected_feedback_topic` sa odvodzuje cez `MQTTTopicRules.expected_feedback_topic()`. Pending záznamy sú uložené pod kľúčom `original_topic`.

### 2 — Doručenie príkazu
| Blok | Funkcia / súbor | Popis |
|------|----------------|-------|
| MQTT Broker doručí príkaz | — (externý systém) | Broker presmeruje správu na prihláseného subscribera — ESP32 Node |
| ESP32 Node vykoná akciu | — (firmware zariadenia) | Fyzická akcia (relé, motor, svetlo...) |

### 3 — Spätná väzba (happy path)
| Blok | Funkcia / súbor | Popis |
|------|----------------|-------|
| ESP32 publikuje feedback | — (firmware) | Publikuje `topic/feedback` s payloadom `OK` |
| Broker doručí feedback | — (externý systém) | Správa dorazí na `mqtt_client._on_message()` |
| MQTTMessageHandler presmeruje | `mqtt_message_handler.py` → `handle_message()` → `_is_command_feedback_message()` | Rozpozná feedback tému a zavolá `feedback_tracker.handle_feedback_message()` |
| FeedbackTracker spracuje | `mqtt_feedback_tracker.py` → `handle_feedback_message()` | Zruší timeout timer (`timer.cancel()`), overí `payload.upper() == 'OK'`; mimo `lock` zavolá `state_store.update_confirmed()` |
| ActuatorStateStore update_confirmed | `mqtt_actuator_state_store.py` → `update_confirmed()` | Nastaví `confirmed_state`; zavolá `_notify(snapshot)` → `_update_callback` |
| WebDashboard dostane update | `main.py` → `_on_actuator_state_change()` → `web_dashboard.broadcast_device_runtime_state()` | SocketIO emit `device_runtime_state_update` všetkým pripojeným klientom |

### 4 — Alternatíva A: Feedback timeout
| Blok | Funkcia / súbor | Popis |
|------|----------------|-------|
| Timeout timer vypršal | `mqtt_feedback_tracker.py` → `_handle_feedback_timeout()` | `threading.Timer` vyprší bez prijatia feedbacku |
| FeedbackTracker loguje TIMEOUT | `_handle_feedback_timeout()` → `logger.error("FEEDBACK TIMEOUT: ...")` | Pending entry sa odstráni z `pending_feedbacks` |
| Stav ostáva nepotvrdený | `mqtt_actuator_state_store.py` | `update_confirmed()` sa **nevolá** — `desired_state` ostáva nastavený, `confirmed_state` ostáva `UNKNOWN` |

### 5 — Alternatíva B: Zastavenie scény
| Blok | Funkcia / súbor | Popis |
|------|----------------|-------|
| Spúšťač zastavenia | `main.py` → `stop_scene()` alebo `_run_scene_logic()` finally blok | Vyvolané z web API (`POST /api/stop_scene`), tlačidla alebo prirodzeného konca scény |
| force_all_off | `mqtt_actuator_state_store.py` → `force_all_off(source=...)` | **Prvý krok** — všetky tracked endpointy nastavia `desired` aj `confirmed` na `OFF`; `_notify` sa zavolá pre každý endpoint |
| WebDashboard zobrazí OFF | `main.py` → `_on_actuator_state_change()` → `broadcast_device_runtime_state()` | UI vidí OFF okamžite — ešte pred fyzickým STOP príkazom |
| MuseumController publish STOP | `main.py` → `broadcast_stop()` → `mqtt_client.publish(f"{room_id}/STOP", "STOP")` | **Druhý krok** — až po `force_all_off()`; STOP téma sa v trackeri preskakuje (žiadny feedback timer) |
| Broker doručí STOP | — (externý systém) | — |
| ESP32 vypne výstupy | — (firmware) | Fyzické vypnutie všetkých výstupov zariadenia |

---

## Vizualizačný štýl

| Prvok | Štýl |
|-------|------|
| Typ diagramu | `sequenceDiagram` (Mermaid) s `autonumber` |
| Odoslanie príkazu | Modrá (`#E6F1FB` / `#185FA5`) |
| Doručenie a vykonanie | Sivá (`#F1EFE8` / `#5F5E5A`) |
| Spätná väzba — happy path | Zelená (`#E1F5EE` / `#0F6E56`) |
| Timeout vetva | Červená (`#FAECE7` / `#993C1D`) |
| STOP vetva | Červená (`#FAECE7` / `#993C1D`) |
| Alternatívne vetvy | `alt` bloky s popisným nadpisom |
| Poznámky ku kódu | `Note` bloky nad príslušným účastníkom |

---

## Súlad s kódom

| Sekcia | Súbor | Kľúčová metóda |
|--------|-------|----------------|
| Publish + track | `mqtt_client.py` | `publish()` → `feedback_tracker.track_published_message()` |
| Desired update | `mqtt_feedback_tracker.py` | `track_published_message()` → `state_store.update_desired()` |
| Feedback routing | `mqtt_message_handler.py` | `handle_message()` → `handle_feedback_message()` |
| Confirmed update + notify | `mqtt_feedback_tracker.py` | `handle_feedback_message()` → `state_store.update_confirmed()` |
| Dashboard push | `mqtt_actuator_state_store.py` + `main.py` | `_notify()` → `_on_actuator_state_change()` → `broadcast_device_runtime_state()` |
| Timeout | `mqtt_feedback_tracker.py` | `_handle_feedback_timeout()` |
| STOP | `main.py` | `force_all_off()` → `broadcast_stop()` |