# Obrázok 5.2 — Životný cyklus backendovej služby

## Cieľ

Ukázať riadený životný cyklus backend služby od inicializácie po cleanup, vrátane štartu scény v daemon vlákne, stop vetiev a synchronizácie scene state file pre watchdog.

---

## Mapovanie blokov na kód

### Fáza 1 — Zavedenie systému

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Zavedenie systému | `raspberry_pi/main.py` → `main()` | Vstupný bod procesu; `setup_bootstrap_logging()` spustí základné logovanie ešte pred načítaním konfigurácie; načíta `config.ini` (bootstrap) |
| Inicializácia služieb | `main.py` → `_initialize_runtime()` → `MuseumController.__init__()` | `ConfigManager` načíta `config.ini`; `ServiceContainer.init_all_services()` inicializuje audio, video, MQTT, system_monitor a button; `_wire_dependencies()` prepojí callbacky medzi komponentmi |
| Webové rozhranie | `main.py` → `start_web_dashboard()` | Posledný krok `__init__()` — Flask + SocketIO sa spustí v daemon vlákne na porte z konfigurácie; daemon vlákno nezablokuje hlavný proces |

### Fáza 2 — Hlavná slučka (Main thread)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Pripojenie k MQTT brokeru | `main.py` → `establish_initial_connection()` | Prvý krok v `run()`; retry logika (`mqtt_retry_attempts`) pred vstupom do slučky |
| Záložný offline režim | — | Ak spojenie zlyhá, vypíše raz `log.warning("OFFLINE MODE")` a systém pokračuje bez MQTT; obnovenie prebieha na pozadí |
| Hlavná monitorovacia slučka | `main.py` → `run()` → `while not self.shutdown_requested` | Periodicky volá `perform_periodic_health_check()`, `check_button_polling()` a `cleanup_stale_devices()`; MQTT reconnect sa spracúva priebežne |
| Požadované vypnutie? | `shutdown_requested` flag | Nastavený cez `signal.SIGINT` / `signal.SIGTERM` handlerom v `_signal_handler()`; `áno` = ukončenie, `nie` = pokračuj v slučke |
| Riadený cleanup | `main.py` → `cleanup()` | `ServiceContainer.cleanup()`, `scene_parser.cleanup()`, `web_dashboard.save_stats()` — chránené flagom `_cleaned_up` proti dvojitému volaniu |

### Fáza 3 — Štart scény

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Požiadavka na štart scény | `main.py` → `_initiate_scene_start()` | Spoločný vstupný bod pre hardvérové tlačidlo, web alebo MQTT trigger |
| Nastavenie príznaku 'beží' | `main.py` → `_set_scene_running(True, expect_current=False)` so `scene_lock` | Atomicky nastaví `self.scene_running = True` a zapíše `'running'` do `/tmp/museum_scene_state`; thread-safe uzamknutie zabraňuje prekrývaniu; zároveň zapisuje stav do Súboru stavu scény |
| Zmenil sa príznak? (self.is_scene_running) | návratová hodnota `_set_scene_running()` | `áno (už beží)` → ignorovanie požiadavky; `nie (nová)` → pokračuj |
| Ignorovanie požiadavky | `_set_scene_running()` → `return False` | Požiadavka sa ticho ignoruje — žiadna výnimka, len návratová hodnota `False`; scéna už aktuálne beží |
| Odoslanie stavu klientom | `web_dashboard.broadcast_status()` | Okamžitá WebSocket notifikácia všetkých klientov o zmene stavu — volá sa len po úspešnom zamknutí |
| Spustenie Daemon vlákna | `threading.Thread(target=_run_scene_logic, daemon=True).start()` | Scéna beží súbežne s hlavnou slučkou; hlavná slučka nie je blokovaná; neblokujúci beh scény na pozadí |

### Fáza 4 — Beh scény (Daemon vlákno)

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Načítanie JSON scény | `scene_parser.py` → `load_scene(scene_path)` | JSON parsing, schémová validácia cez `jsonschema`, logická validácia `goto` targetov; nastavenie `on_state_change` callbacku pre WebSocket `scene_progress` |
| Chyba načítania | `_set_scene_running(False)` + `broadcast_status()` | Ak súbor neexistuje alebo je neplatný — vlákno sa ukončí, stav sa resetuje, operátor dostane notifikáciu; neplatná štruktúra JSON |
| Príprava a Preload | `scene_parser.py` → `enable_feedback_tracking()` → `start_scene()` | `start_scene()` prehľadá JSON a preloaduje SFX súbory (prefix `sfx_`) do RAM; potom spustí state machine a vykoná `execute_onEnter()` pre počiatočný stav |
| Slučka stavového automatu | `while not shutdown_requested: process_scene() + sleep` | Opakovaný FSM tick; `scene_processing_sleep` medzi iteráciami; slučka sa ukončí pri `scene_running = False` alebo `process_scene()` → `False` (stav `END`); FSM engine, vyhodnocovanie prechodov |
| Ukončenie scény | `finally` v `_run_scene_logic()` | V každom prípade: `disable_feedback_tracking()` · `stop_video()` · `_set_scene_running(False)` (zápis `'idle'`) · ak `transitioned`: `force_all_off()` + `broadcast_stop()` + `broadcast_status()`; bezpečný OFF výstupov, zastavenie médií |

### Fáza 5 — Externý stop

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Externá požiadavka na zastavenie | `main.py` → `stop_scene()` | Volané z web API route `POST /api/stop_scene` cez `WebDashboard`; globálny STOP príkaz (cez web) |
| Bežala scéna? | `_set_scene_running(False, expect_current=True)` | Ak `self.scene_running` je už `False`, `expect_current=True` vráti `False` → `transitioned = False`; `áno` = vynútený cleanup, `nie` = len notifikácia |
| Vynútený cleanup scény | `scene_parser.stop_scene()` · `stop_audio()` · `stop_video()` · `force_all_off(source='external_stop')` · `broadcast_stop()` · `broadcast_status()` | Kompletné zastavenie výstupov a notifikácia klientov; volá sa len ak `transitioned = True`; `force_all_off`, okamžité stopnutie médií |
| Len notifikácia | `web_dashboard.broadcast_status()` + `return True` | Len WebSocket notifikácia — žiadny `broadcast_stop`, stop audio/video ani `force_all_off`; aktualizácia stavu klientov |

### Fáza 6 — Watchdog

| Blok v diagrame | Súbor / funkcia | Čo robí v reálnom kóde |
|---|---|---|
| Súbor stavu scény | `/tmp/museum_scene_state` ← `_set_scene_running()` | Zapisuje `'running'` pri každom štarte (z `Nastavenie príznaku 'beží'`) a `'idle'` pri každom ukončení (z `Ukončenie scény`) |
| Watchdog proces | `MuseumWatchdog._is_scene_running()` | Číta state file pred rozhodnutím o reštarte; file starší ako 2 hodiny sa považuje za stale a ignoruje; externá kontrola zdravia |

---

## Kľúčové súbory

| Súbor | Úloha |
|---|---|
| `raspberry_pi/main.py` | Celý životný cyklus — init, run loop, scene thread, stop, cleanup |
| `raspberry_pi/utils/scene_parser.py` | Load scény, FSM tick, preloading, finally cleanup |
| `raspberry_pi/utils/mqtt/mqtt_actuator_state_store.py` | `force_all_off()` pri každom ukončení |
| `Web/dashboard.py` | `broadcast_status()` — notifikácia UI pri každej zmene stavu |
| `/tmp/museum_scene_state` | Medziprocesová komunikácia pre watchdog |
