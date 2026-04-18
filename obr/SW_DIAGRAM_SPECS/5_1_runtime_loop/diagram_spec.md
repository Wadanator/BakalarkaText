# Obrázok 5.1 - Runtime slučka softvérových vrstiev

## 1) Cieľ diagramu

Zobraziť uzavretý prevádzkový tok od vstupného triggeru po vykonanie akcie,
potvrdenie feedbackom, aktualizáciu runtime stavu a následné rozhodovanie.
Diagram nesmie byť len topológia ani len MQTT sekvenčný tok.

## 2) Povinné zóny plátna

Rozloženie zľava doprava na 5 zón:

1. Vstupy a trigger
2. Raspberry Pi backend
3. MQTT broker
4. ESP32 vykonávacia vrstva
5. Dashboard a operátor

## 3) Povinné bloky

### Zóna 1 - Vstupy

1. Fyzické tlačidlo
2. Operátor (Run/Stop)
3. Topic trigger (roomX/scene, roomX/start_scene)

### Zóna 2 - Backend

1. Orchestrácia (MuseumController)
2. SceneParser
3. FSM jadro (StateMachine + TransitionManager)
4. StateExecutor (audio/video/mqtt akcie)
5. MQTT client + feedback tracker
6. Actuator state store (desired/confirmed)
7. Web backend (Flask + SocketIO)
8. Scene state file (/tmp/museum_scene_state)

### Zóna 3 - Broker

1. MQTT broker

### Zóna 4 - ESP32

1. Button uzol
2. Motor uzol
3. Relay uzol
4. Spoločné jadro uzlov (Wi-Fi, MQTT, status/LWT, STOP odber)

### Zóna 5 - UI

1. Dashboard UI
2. Operátor vidí status + logy + scene progress + runtime states

## 4) Povinné šípky (číslované)

1. Trigger -> Orchestrácia (start scene)
2. Orchestrácia -> SceneParser (load/start)
3. SceneParser -> FSM (process tick)
4. FSM -> StateExecutor (vykonanie akcií)
5. StateExecutor -> MQTT client (publish command)
6. MQTT client -> Broker -> ESP32 (doručenie príkazu)
7. ESP32 -> Broker -> Feedback tracker (feedback / status)
8. Feedback tracker -> Actuator store (confirmed update)
9. Publish command -> Actuator store (desired update)
10. Actuator store -> Web backend -> Dashboard (device_runtime_state_update)
11. Orchestrácia -> Web backend -> Dashboard (status_update, scene_progress, stats_update)
11b. Web vrstva (log handler) -> Dashboard (new_log)
12. Stop vetva: Orchestrácia -> roomX/STOP -> ESP32 + force_all_off
13. Watchdog vetva: Scene state file <-> watchdog rozhodovanie

## 5) Povinné callouty

1. GlobalEvents sa vyhodnocujú pred lokálnymi transitions.
2. Desired sa mení pri publish, confirmed pri feedback OK.
3. Feedback timeout sa loguje ako komunikačný problém.
4. STOP nastaví bezpečný OFF stav cez force_all_off.
5. Dashboard je pushovaný eventami, nie pollingom.

## 6) Štýl čiar a farieb

1. Plná modrá: riadiace príkazy
2. Prerušovaná zelená: feedback a status
3. Bodkočiarkovaná sivá: interné backend volania
4. Červená: safety vetva (STOP, force_all_off)
5. Oranžová: SocketIO push udalosti

## 7) Čo nesmie byť v diagrame

1. Fyzické zapojenie a piny
2. Podrobné JSON polia
3. Dlhé odstavce v boxoch
4. Triedne diagramy na úrovni metód

## 8) Súlad s kódom (kontrolné body)

1. `main.py`: scene thread, stop flow, force_all_off, broadcast_stop, status broadcast
2. `scene_parser.py`: tick poradie audio/video end -> globalEvents -> local transitions
3. `mqtt_feedback_tracker.py`: track publish, timeout branch, confirmed update
4. `mqtt_actuator_state_store.py`: desired/confirmed + force_all_off
5. `Web/dashboard.py`: status_update, stats_update, new_log, device_runtime_state_update

## 9) Mermaid preklad - odporúčaný typ

Použiť `flowchart LR` s vnorenými subgraph sekciami.
Pre interné backend väzby použiť prerušované linky (`-.->`).
Pre návratové vetvy použiť samostatné popisky, nie prekrížené hrany.

## 10) Akceptačné kritériá

1. Čitateľ vie za 5 sekúnd vysvetliť uzavretú slučku.
2. Je viditeľný rozdiel medzi príkazom, feedbackom a dashboard pushom.
3. Je viditeľná bezpečnostná vetva STOP.
4. Diagram nepôsobí ako duplikát architektúrneho obrázka 3.x.
