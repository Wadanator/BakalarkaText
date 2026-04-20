# Obrázok 5.5 — Sekvenčný tok MQTT správ počas vykonania akcie

## Cieľ

Zobraziť kompletný runtime sekvenčný tok pre jednu MQTT akciu scény: odoslanie príkazu, desired update, feedback vetva (happy path), timeout vetva a STOP vetva. Dôraz na poradie volaní presne podľa kódu a na rozlíšenie desired vs. confirmed stavu.

---

## Mapovanie blokov na kód

### Fáza 1 — Odoslanie príkazu

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| StateExecutor vykoná akciu | `raspberry_pi/utils/state_executor.py` → `_execute_mqtt()` | Zavolá `mqtt_client.publish(topic, message)` pre každú mqtt akciu z `onEnter`, `onExit` alebo `timeline` |
| MQTT Client publikuje na broker | `raspberry_pi/utils/mqtt/mqtt_client.py` → `publish()` | Fyzický publish cez `paho-mqtt`; kontroluje `rc == 0`; toto je **prvý** krok pred trackovaním |
| FeedbackTracker zaznamená | `raspberry_pi/utils/mqtt/mqtt_feedback_tracker.py` → `track_published_message()` | Volaný **po** úspešnom publishi; zavolá `update_desired` a spustí `threading.Timer(feedback_timeout, _handle_feedback_timeout)` |
| ActuatorStateStore — desired update | `raspberry_pi/utils/mqtt/mqtt_actuator_state_store.py` → `update_desired()` | Nastaví `desired_state` pre daný topic; UI ihneď vidí plánovaný stav ešte pred fyzickým potvrdením |

> **Poznámka:** Audio a video tópiky sa v `track_published_message()` preskakujú — pre ne sa feedback timer nespúšťa.

### Fáza 2 — Doručenie príkazu na ESP32

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| MQTT Broker doručí príkaz | externá služba | Broker presmeruje správu na prihláseného subscribera — príslušný ESP32 uzol |
| ESP32 vykoná akciu | `ArduinoIDE/esp32_mqtt_controller_RELAY.ino` alebo `_MOTORS.ino` | Fyzická akcia — spínanie relé, pohyb motora, zmena svetla |

### Fáza 3 — Spätná väzba (happy path)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| ESP32 publikuje feedback | firmware → `mqtt_manager.h` | Publikuje `OK` na tému `topic/feedback` po úspešnom vykonaní akcie |
| Broker doručí feedback | externá služba | Správa dorazí na `mqtt_client._on_message()` callbacku backendu |
| MQTTMessageHandler presmeruje | `mqtt_message_handler.py` → `handle_message()` → `_is_command_feedback_message()` | Rozpozná feedback tému a zavolá `feedback_tracker.handle_feedback_message()` |
| FeedbackTracker spracuje | `mqtt_feedback_tracker.py` → `handle_feedback_message()` | Zruší timeout timer (`timer.cancel()`), overí `payload.upper() == 'OK'`; zavolá `state_store.update_confirmed()` |
| ActuatorStateStore — confirmed update | `mqtt_actuator_state_store.py` → `update_confirmed()` | Nastaví `confirmed_state`; zavolá `_notify(snapshot)` → `_update_callback` |
| WebDashboard dostane update | `main.py` → `_on_actuator_state_change()` → `web_dashboard.broadcast_device_runtime_state()` | SocketIO emit `device_runtime_state_update` — UI zobrazí potvrdený stav |

### Fáza 4 — Alternatíva A: Feedback timeout

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Timeout timer vypršal | `mqtt_feedback_tracker.py` → `_handle_feedback_timeout()` | `threading.Timer` vyprší bez prijatia feedbacku |
| FeedbackTracker loguje TIMEOUT | `_handle_feedback_timeout()` → `logger.error(...)` | Pending entry sa odstráni z `pending_feedbacks`; scéna pokračuje ďalej |
| Stav ostáva nepotvrdený | `mqtt_actuator_state_store.py` | `update_confirmed()` sa nevolá — `desired_state` ostáva nastavený, `confirmed_state` ostáva `UNKNOWN` |

### Fáza 5 — Alternatíva B: Zastavenie scény (STOP vetva)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Spúšťač zastavenia | `main.py` → `stop_scene()` alebo `_run_scene_logic()` finally blok | Vyvolané z web API, tlačidla alebo prirodzeného konca scény (stav `END`) |
| force\_all\_off | `mqtt_actuator_state_store.py` → `force_all_off(source=...)` | **Prvý krok** — všetky tracked endpointy nastavia `desired` aj `confirmed` na `OFF`; `_notify` sa zavolá pre každý endpoint |
| WebDashboard zobrazí OFF | `main.py` → `_on_actuator_state_change()` → `broadcast_device_runtime_state()` | UI vidí OFF ešte pred fyzickým STOP príkazom |
| Backend publikuje STOP | `main.py` → `broadcast_stop()` → `mqtt_client.publish(f"{room_id}/STOP", "STOP")` | **Druhý krok** — až po `force_all_off()`; STOP tóika sa v trackeri preskakuje |
| ESP32 vypne výstupy | firmware → STOP handler | Fyzické vypnutie všetkých výstupov zariadenia |

---

## Kľúčové detaily pre obhajobu

| Otázka | Odpoveď |
|---|---|
| Prečo `desired` pred `confirmed`? | UI musí okamžite reflektovať zámer operátora; `confirmed` príde až po sieťovom obehu cez broker |
| Čo sa stane pri timeout? | Stav zostane `desired=ON, confirmed=UNKNOWN`; zaloguje sa chyba; scéna pokračuje |
| Prečo `force_all_off` pred publish STOP? | UI musí vidieť OFF skôr ako fyzické zariadenia reagujú — predchádza vizuálnemu oneskoreniu |
| Sú audio/video akcie trackované? | Nie — `track_published_message()` ich preskakuje; žiadny feedback timer pre ne |

---

## Kľúčové súbory

| Súbor | Úloha |
|---|---|
| `raspberry_pi/utils/state_executor.py` | Inicializuje publish cez `_execute_mqtt()` |
| `raspberry_pi/utils/mqtt/mqtt_client.py` | Fyzický publish, volá `track_published_message()` |
| `raspberry_pi/utils/mqtt/mqtt_feedback_tracker.py` | Track publish, timeout timer, confirmed update |
| `raspberry_pi/utils/mqtt/mqtt_actuator_state_store.py` | desired/confirmed stav, `force_all_off()` |
| `raspberry_pi/utils/mqtt/mqtt_message_handler.py` | Routing prichádzajúcich správ vrátane feedback |
| `Web/dashboard.py` | `broadcast_device_runtime_state()` — push do UI |
