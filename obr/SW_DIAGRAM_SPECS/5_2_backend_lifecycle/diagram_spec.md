# Obrázok 5.2 - Životný cyklus backendovej služby

## Cieľ
Ukázať riadený životný cyklus služby od inicializácie po cleanup,
vrátane štartu scény v daemon vlákne, stop vetiev a synchronizácie
scene state file pre watchdog.

## Mapovanie blokov na kód

### 1 — Štart
| Blok | Funkcia | Popis |
|------|---------|-------|
| Backend štart | `main()` | Vstupný bod, bootstrap logging |
| Konfigurácia, služby, callbacky | `ConfigManager`, `ServiceContainer.init_all_services()`, `_wire_dependencies()` | Načítanie konfigurácie a inicializácia všetkých služieb |
| Web dashboard | `start_web_dashboard()` | Spustenie Flask+SocketIO v daemon vlákne |

### 2 — Main loop
| Blok | Funkcia | Popis |
|------|---------|-------|
| Počiatočné MQTT spojenie | `establish_initial_connection()` | Pokus o pripojenie s retry logikou pred vstupom do slučky |
| Offline režim | — | Warning sa vypíše raz, systém pokračuje bez MQTT |
| Hlavná slučka | `run()` → `while not self.shutdown_requested` | Periodic health check, button polling, device cleanup |
| Ukončenie? | `shutdown_requested` | Flag nastavený cez SIGINT/SIGTERM |
| Cleanup systému | `ServiceContainer.cleanup()` | Zastavenie služieb, uloženie štatistík |

### 3 — Štart scény
| Blok | Funkcia | Popis |
|------|---------|-------|
| Štart scény | `_initiate_scene_start()` | Vstupný bod z button / MQTT / web API |
| running + /tmp/museum_scene_state | `_set_scene_running()` so `scene_lock` | Atomický zápis flagu a state file |
| Už beží | `_set_scene_running()` → `return False` | Duplicitná požiadavka sa ignoruje |
| Daemon vlákno scény | `threading.Thread(daemon=True)` → `_run_scene_logic()` | Main loop nie je blokovaný |

### 4 — Beh scény
| Blok | Funkcia | Popis |
|------|---------|-------|
| Load scény + callback | `scene_parser.load_scene()` | Načítanie JSON, nastavenie on_state_change callbacku |
| Feedback tracking + scene loop | `enable_feedback_tracking()` → `run_scene()` → `process_scene()` | Sledovanie odpovedí zariadení počas behu |
| Stop výstupov + force_all_off + broadcast stop | `finally` blok: `force_all_off()`, `broadcast_stop()` | Bezpečné vypnutie výstupov a notifikácia klientov |

### 5 — Externý stop
| Blok | Funkcia | Popis |
|------|---------|-------|
| stop_scene() | `stop_scene()` | Volané z web API |
| Scéna beží? | `_set_scene_running(expect_current=True)` | Ak nie, iba broadcast |
| Scéna/audio/video off + force_all_off | `scene_parser.stop_scene()`, `stop_audio()`, `stop_video()`, `force_all_off()` | Zastavenie všetkých výstupov |
| Broadcast stop + status | `broadcast_stop()`, `broadcast_status()` | Notifikácia WebSocket klientov |

### 6 — Watchdog
| Blok | Funkcia | Popis |
|------|---------|-------|
| /tmp/museum_scene_state | `_SCENE_STATE_FILE.write_text()` | Zapisuje sa pri každom štarte aj stopu scény |
| watchdog číta stav | `_is_scene_running()` | Watchdog čaká na idle pred reštartom |