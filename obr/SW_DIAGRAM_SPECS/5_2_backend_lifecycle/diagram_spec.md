# Obrázok 5.2 - Životný cyklus backendovej služby

## Cieľ
Ukázať riadený životný cyklus služby od inicializácie po cleanup,
vrátane štartu scény v daemon vlákne, stop vetiev a synchronizácie
scene state file pre watchdog.

## Mapovanie blokov na kód

### 1 — Štart
| Blok | Funkcia | Popis |
|------|---------|-------|
| Backend štart | `main()` | Vstupný bod, `setup_bootstrap_logging()` — bootstrap logging pred načítaním konfigurácie |
| Konfigurácia, služby, callbacky | `_initialize_runtime()` → `MuseumController.__init__()` | `ConfigManager`, `ServiceContainer.init_all_services()` (audio · video · MQTT · system_monitor · button), `MQTTActuatorStateStore`, `DeviceOutageTracker`, `_wire_dependencies()` |
| Web dashboard | `start_web_dashboard()` | Posledný krok `__init__()` — Flask + SocketIO spustené v daemon vlákne na porte z konfigurácie |

### 2 — Main loop
| Blok | Funkcia | Popis |
|------|---------|-------|
| Počiatočné MQTT spojenie | `establish_initial_connection()` | Prvý krok v `run()`, retry logika (`mqtt_retry_attempts`) pred vstupom do slučky |
| Offline režim | — | Warning sa vypíše raz (`log.warning("OFFLINE MODE")`), systém pokračuje bez MQTT |
| Hlavná slučka | `run()` → `while not self.shutdown_requested` | `perform_periodic_health_check()` · button polling (`check_button_polling()`) · `cleanup_stale_devices()` |
| Ukončenie? | `shutdown_requested` flag | Nastavený cez `signal.SIGINT` / `signal.SIGTERM` handlerom v `_signal_handler()` |
| Cleanup systému | `cleanup()` | `ServiceContainer.cleanup()`, `scene_parser.cleanup()`, `web_dashboard.save_stats()` — chránené flagom `_cleaned_up` |

### 3 — Štart scény
| Blok | Funkcia | Popis |
|------|---------|-------|
| Štart scény | `_initiate_scene_start()` | Spoločný vstupný bod pre button callback (`on_button_press`), MQTT správu `start_scene` a web API `run_scene` |
| running + /tmp/museum_scene_state | `_set_scene_running(True, expect_current=False)` so `scene_lock` | Atomicky nastaví `self.scene_running = True` a zapíše `'running'` do `_SCENE_STATE_FILE`; ak `expect_current=False` nesedí (scéna beží), vráti `False` |
| return False | `_set_scene_running()` → `return False` | Ak scéna už beží, `_initiate_scene_start` vráti `False`, požiadavka je ignorovaná bez výnimky |
| broadcast_status() | `web_dashboard.broadcast_status()` | Okamžitá WebSocket notifikácia klientov o zmene stavu — volá sa len po úspešnom zamknutí |
| Daemon vlákno scény | `threading.Thread(target=_run_scene_logic, daemon=True).start()` | Main loop nie je blokovaný; scéna beží súbežne |

### 4 — Beh scény (daemon vlákno)
| Blok | Funkcia | Popis |
|------|---------|-------|
| Load scény + callback | `scene_parser.load_scene(scene_path)` | JSON parsing, schema validácia (`jsonschema`), logická validácia (`goto` targety); nastavenie `state_machine.on_state_change` callbacku pre WebSocket `scene_progress` eventy |
| Chyba loadu | `_set_scene_running(False)` + `broadcast_status()` | Ak súbor neexistuje, `scene_parser` nie je dostupný, alebo `load_scene()` vráti `False` — vlákno sa ukončí, stav sa resetuje |
| run_scene() štart | `enable_feedback_tracking()` → `start_scene()` | `start_scene()` rekurzívne prehľadá JSON, preloaduje SFX súbory (prefix `sfx_`) do RAM (`preload_files_for_scene`), spustí state machine (`SM.start()`), vykoná `execute_onEnter()` pre počiatočný stav |
| Scénová slučka | `while not shutdown_requested: process_scene() + sleep` | Opakovaný FSM tick; `scene_processing_sleep` medzi iteráciami; smyčka sa ukončí pri `scene_running = False` alebo `process_scene()` → `False` |
| finally blok | `finally` v `_run_scene_logic()` | Postupne: `disable_feedback_tracking()` · `stop_video()` · `_set_scene_running(False)` (zápis `'idle'`) · ak `transitioned`: `force_all_off(source='scene_end')` + `broadcast_stop()` (MQTT `room/STOP`) · `broadcast_status()` (WebSocket) |

> **Poznámka:** `broadcast_stop()` je volaný dvakrát pri prirodzenom konci scény — raz z `run_scene()` a raz z `finally` bloku (ak `transitioned=True`). Ide o redundanciu v kóde, nie o chybu.

### 5 — Externý stop
| Blok | Funkcia | Popis |
|------|---------|-------|
| stop_scene() | `stop_scene()` | Volané z web API route `POST /api/stop_scene` cez `WebDashboard` |
| transitioned? | `_set_scene_running(False, expect_current=True)` | Ak `self.scene_running` je už `False`, `expect_current=True` spôsobí `return False` → `transitioned = False` |
| Scéna nebeží | `web_dashboard.broadcast_status()` + `return True` | Len WebSocket notifikácia — **žiadny** `broadcast_stop`, `stop_audio`, `stop_video` ani `force_all_off` |
| Zastavenie všetkých výstupov | `scene_parser.stop_scene()` · `stop_audio()` · `stop_video()` · `force_all_off(source='external_stop')` · `broadcast_stop()` · `broadcast_status()` | Kompletné zastavenie výstupov a notifikácia; volá sa len ak `transitioned = True` |

### 6 — Watchdog
| Blok | Funkcia | Popis |
|------|---------|-------|
| /tmp/museum_scene_state | `_SCENE_STATE_FILE.write_text(state_value)` | Zapisuje `'running'` pri každom štarte scény a `'idle'` pri každom ukončení (prirodzenom aj externom) |
| watchdog číta stav | `MuseumWatchdog._is_scene_running()` | Číta state file pred rozhodnutím o reštarte; file starší ako 2 hodiny sa považuje za stale a ignoruje (→ `False`) |

## Zmeny oproti pôvodnej verzii

| Problém | Pôvodný stav | Opravený stav |
|---------|-------------|---------------|
| Chýbajúci `broadcast_status()` po úspešnom zamknutí | Neexistoval BCASTSTART blok | Pridaný BCASTSTART medzi SETSRUN a THREAD |
| Chýbajúca chybová vetva z LOAD | Žiadna error cesta | Pridaný LOADERR — `_set_scene_running(False)` + `broadcast_status()` |
| Chýbajúci audio preloading | LOAD → RUN bez medzikroku | Pridaný PRELOAD: `enable_feedback` + `start_scene()` s preloadingom |
| `force_all_off()` chýbal v ENDSTOP | Len `broadcast stop` | Pridaný: `stop_video` · `_set_scene_running(False)` · `force_all_off()` · `broadcast_stop()` · `broadcast_status()` |
| „nie" vetva externého stopu | Obe vetvy → BROADSTOP (obsahoval `broadcast_stop`) | „nie" vetva → iba `broadcast_status()`, bez MQTT broadcast a bez stop akcií |
| `force_all_off()` chýbal v externom stope | Len `Scéna/audio/video off` | Pridaný `force_all_off(source='external_stop')` do STOPALL |