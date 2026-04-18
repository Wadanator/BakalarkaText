# Obrázok 5.6 - Funkčný pohľad webového dashboardu

## Cieľ

Ukázať operátorský pohľad na systém a real-time tok dát
zo servera do UI bez potreby pollingu.

## Povinné funkčné oblasti UI

1. Scény (run/stop, active state)
2. Zariadenia (online/offline, runtime state)
3. Logy (história + live)
4. Štatistiky
5. Systémový stav (uptime, mqtt connected)

## Povinné eventy zo servera

1. status_update
2. stats_update
3. new_log
4. log_history
5. scene_progress
6. device_runtime_state_update

## Povinné interakcie od klienta

1. request_status
2. request_stats
3. request_logs
4. operátorské run/stop akcie

## Povinné callouty

1. SocketIO connect vyžaduje autentifikáciu
2. Po connecte klient dostane initial snapshot
3. Web backend beží v samostatnom daemon threade

## Vizualizačný štýl

1. Typ diagramu: functional architecture
2. Vľavo server event source, vpravo UI panely
3. Obojsmerné šípky:
   - server -> UI event push
   - UI -> server request/command

## Súlad s kódom

1. `Web/app.py` SocketIO init + thread run
2. `Web/dashboard.py` connect auth + emit handlers
3. `main.py` scene_progress, broadcast_status, stats update
