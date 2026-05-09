# Obrázok 5.6 — Funkčný pohľad webového dashboardu

## Cieľ

Ukázať architektúru webového rozhrania — zdroje udalostí na serveri, push tok cez WebSocket, REST požiadavky od klienta a funkčné oblasti UI — ako jeden celok bez potreby pollingu.

---

## Mapovanie blokov na kód

### Infraštruktúra — Webový server

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| HTTP + WebSocket server | `Web/app.py` → `create_app()` + `socketio.run()` | Flask aplikácia s Flask-SocketIO; pri štarte systému sa spustí v daemon vlákne cez `threading.Thread` |
| Nezablokuje hlavnú slučku | `Web/app.py` → `start_web_dashboard()` | Port je načítaný z `config.ini`; daemon vlákno nezablokuje hlavnú slučku backendu |
| Opätovné spustenie pri páde | `Web/app.py` → `run_dashboard()` | Ak `socketio.run(...)` skončí výnimkou, vlákno po 10 sekundách skúsi server spustiť znova |

### Infraštruktúra — Autentifikácia

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Základná autentifikácia na REST požiadavkách | `Web/dashboard.py` → `requires_auth` dekorátor | Každý REST endpoint overuje HTTP Basic Auth hlavičku pred spracovaním |
| WebSocket — overenie prihlasovacích údajov | `Web/dashboard.py` → `@socketio.on('connect')` → `_check_auth()` | Pri každom Socket.IO `connect` evente sa overí token pred nadviazaním spojenia |
| Po pripojení server pošle aktuálny stav | `Web/dashboard.py` → connect handler | Okamžite po overení server emituje `log_history`, aktuálne `stats` a `status` |

### Zdroje udalostí na serveri (ľavý stĺpec)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Hlavný kontrolér systému | `raspberry_pi/main.py` → `broadcast_status()`, `broadcast_stats()` | Volá sa pri každej zmene stavu scény alebo pri periodickom health checku |
| Engine scény | `raspberry_pi/utils/scene_parser.py` + `state_machine.py` → `on_state_change` callback | Každá zmena stavu FSM zavolá callback, ktorý emituje `scene_progress` event s hodnotou `activeState` |
| Evidencia stavu zariadení | `raspberry_pi/utils/mqtt/mqtt_actuator_state_store.py` → `_notify()` → `_update_callback` | Pri každej zmene `desired` alebo `confirmed` stavu zariadenia zavolá callback v `main.py` |
| Logový zachytávač | `Web/log_handler.py` → `WebLogHandler.emit()` → `add_log_entry()` | Python logging handler zachytí každý log záznam a okamžite ho odošle cez Socket.IO |

### Push udalosti — server → klient

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Stav systému | `Web/dashboard.py` → `broadcast_status()` → `socketio.emit('status_update', ...)` | Obsahuje: `scene_running`, `mqtt_connected`, `uptime`; odosielané pri každej zmene stavu |
| Štatistiky | `Web/dashboard.py` → `broadcast_stats()` → `socketio.emit('stats_update', ...)` | Obsahuje: počet spustených scén, uptime, počet pripojených zariadení |
| Aktuálny stav scény | `Web/dashboard.py` → `socketio.emit('scene_progress', ...)` | Obsahuje: `activeState`; emitované pri každej zmene stavu FSM |
| Stav výstupu | `Web/dashboard.py` → `broadcast_device_runtime_state()` → `socketio.emit('device_runtime_state_update', ...)` | Obsahuje požadovaný a potvrdený stav pre jeden MQTT topic; emitované okamžite pri zmene |
| Nový riadok logu | `Web/log_handler.py` → `socketio.emit('new_log', ...)` | Obsahuje: `level`, `module`, `message`, `timestamp` |
| História logov | `Web/dashboard.py` → connect handler a `request_logs` handler | Server posiela 50 záznamov pri pripojení a 250 záznamov pri explicitnej požiadavke `request_logs` |

### Požiadavky od klienta — klient → server

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Požiadavka na stav | `@socketio.on('request_status')` | Klient pošle pri otvorení dashboardu, opätovnom pripojení a návrate do aktívneho okna; server odpovie `status_update` |
| Požiadavka na štatistiky | `@socketio.on('request_stats')` | Klient pošle pri otvorení dashboardu a opätovnom pripojení; server odpovie `stats_update` |
| Požiadavka na logy | `@socketio.on('request_logs')` | Klient pošle pri otvorení obrazovky logov a pri opätovnom pripojení; server odpovie `log_history` |
| Spustenie scény (REST) | `POST /api/run_scene` → `MuseumController.start_scene_by_name()` | Telo požiadavky obsahuje názov súboru scény |
| Zastavenie scény (REST) | `POST /api/stop_scene` → `MuseumController.stop_scene()` | Externé zastavenie aktívnej scény |
| Manuálny MQTT príkaz (REST) | `POST /api/mqtt/send` → `mqtt_client.publish(topic, message)` | Priamy MQTT príkaz z dashboardu — topic + správa |

### UI panely — pravý stĺpec

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Stav systému | `frontend/src/components/HeroCard` | Zobrazuje `scene_running` z `status_update`; stavy: pripravený · beží · chyba |
| Spustiť / Zastaviť scénu | `frontend/src/components/DashboardControls` | Bezpečnostná poistka 5 s; volá `POST /api/run_scene` alebo `stop_scene` |
| MQTT spojenie | `frontend/src/components/StatsGrid` | Indikátor `mqtt_connected` z `status_update` |
| Počet zariadení | `frontend/src/components/StatsGrid` | Hodnota `connected_devices` z `stats_update` |
| Knižnica scén | `frontend/src/views/ScenesView` | Zoznam JSON súborov; akcie: spustiť · upraviť · vytvoriť |
| Editor scén + vizualizácia | `frontend/src/components/SceneEditorModal` | Monaco editor pre JSON + ReactFlow grafický pohľad na stavy a prechody |
| Aktívny stav scény | `src/components/Views/LiveView.jsx` | Zvýraznený aktuálny stav FSM na základe `scene_progress` udalostí |
| Stav zariadení v reálnom čase | `src/components/Views/LiveView.jsx` | Potvrdený stav zariadení z `device_runtime_state_update` a z úvodného načítania `/api/device_states` |
| Živé logy | `frontend/src/views/LogsView` | Filtrovanie podľa úrovne závažnosti (DEBUG/INFO/WARNING/ERROR) |
| Štatistiky scén | `frontend/src/views/StatsView` | Počty spustení, najčastejšie scény, uptime |
| Systémové akcie | `frontend/src/views/SystemView` | Reštart služby · reboot · vypnutie Raspberry Pi |

### Manuálne ovládanie zariadení (spodný panel)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Motory | `frontend/src/views/CommandsView` → `POST /api/mqtt/send` | Tlačidlá Vzad · Stop · Vpred; MQTT príkaz na `roomX/motor1` alebo `motor2` |
| Relé a svetlá | `frontend/src/views/CommandsView` → `POST /api/mqtt/send` | ON/OFF pre každý nakonfigurovaný topic zariadenia |
| Hromadný STOP | `src/components/Views/CommandsView.jsx` → `POST /api/mqtt/send` topic `roomX/STOP` | Odošle spoločný STOP príkaz pre danú miestnosť |
| Správa médií | `frontend/src/views/MediaManager` | Nahranie · prehranie · zmazanie audio a video súborov |
| Priamy MQTT príkaz | `frontend/src/views/CommandsView` → `POST /api/mqtt/send` | Manuálne zadaný topic + správa |
| Konfigurácia zariadení | `frontend/src/components/DevicesConfigModal` | Živá úprava `devices.json` — mapovanie názvov zariadení na MQTT topiky |

### Stav zariadení (priebežne)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Požadovaný stav | `mqtt_actuator_state_store.py` → `desired_state` | Nastavený ihneď po odoslaní príkazu cez `update_desired()`; UI vidí zámer ešte pred potvrdením |
| Potvrdený stav | `mqtt_actuator_state_store.py` → `confirmed_state` | Nastavený po prijatí `OK` feedbacku od ESP32 cez `update_confirmed()` |
| Neznámy / zastaraný | počiatočný stav, offline uzol alebo timeout dostupnosti | `UNKNOWN` kým zariadenie prvýkrát neodpovie, alebo po komunikačnom výpadku |
| Pri zastavení scény všetko OFF | `mqtt_actuator_state_store.py` → `force_all_off()` | Nastaví `desired` aj `confirmed` na `OFF` pre všetky tracked endpointy bez čakania na potvrdenie |

---

## Kľúčové súbory

| Súbor | Úloha |
|---|---|
| `Web/app.py` | Inicializácia Flask + SocketIO, registrácia blueprintov |
| `Web/dashboard.py` | Všetky Socket.IO handlery a emit funkcie |
| `Web/log_handler.py` | Python logging → Socket.IO bridge |
| `raspberry_pi/main.py` | `broadcast_status()`, `broadcast_stats()`, `_on_actuator_state_change()` |
| `raspberry_pi/utils/mqtt/mqtt_actuator_state_store.py` | desired/confirmed stav, notify callback |
| `frontend/src/` | React SPA — všetky UI komponenty a views |
