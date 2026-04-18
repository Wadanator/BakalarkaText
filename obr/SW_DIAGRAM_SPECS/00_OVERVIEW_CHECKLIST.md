# SW Diagram Specs - Master Checklist

Tento súbor je centrálny zoznam požiadaviek pre obrázky SW kapitoly.
Je pripravený na následné generovanie Mermaid verzií.

## Prehľad obrázkov

1. 5.1 Runtime slučka SW vrstiev
   - Priečinok: `5_1_runtime_loop`
   - Súbor: `diagram_spec.md`
   - Fokus: end-to-end tok trigger -> FSM -> MQTT -> feedback -> dashboard

2. 5.2 Životný cyklus backendovej služby
   - Priečinok: `5_2_backend_lifecycle`
   - Súbor: `diagram_spec.md`
   - Fokus: init, run loop, scene thread, stop, cleanup, scene state file

3. 5.3 Logické spracovanie FSM
   - Priečinok: `5_3_fsm_engine_tick_flow`
   - Súbor: `diagram_spec.md`
   - Fokus: poradie v ticku, globalEvents priorita, state transition pipeline

4. 5.4 Štruktúra konfiguračnej scény JSON
   - Priečinok: `5_4_json_scene_structure`
   - Súbor: `diagram_spec.md`
   - Fokus: root, states, onEnter/onExit/timeline/transitions/globalEvents

5. 5.5 Sekvenčný tok MQTT počas akcie
   - Priečinok: `5_5_mqtt_sequence_runtime`
   - Súbor: `diagram_spec.md`
   - Fokus: desired/confirmed, feedback timeout vetva, STOP vetva

6. 5.6 Funkčný pohľad dashboardu
   - Priečinok: `5_6_dashboard_functional_view`
   - Súbor: `diagram_spec.md`
   - Fokus: eventy, status, logs, stats, scene progress, operátorské akcie

7. 5.7 Spoločná a špecifická logika uzlov ESP32
   - Priečinok: `5_7_esp32_common_vs_specific`
   - Súbor: `diagram_spec.md`
   - Fokus: spoločné jadro + vetvy button/motor/relay

## Pravidlá pre všetky diagramy

1. Každý diagram musí mať jasný hlavný tok (číslované kroky).
2. Spätné väzby sa kreslia ako samostatné vetvy, nie iba textom v blokoch.
3. Rozlišovať interný tok backendu vs. externý MQTT tok.
4. Pri SW diagrame nikdy nemiešať fyzické zapojenie pinov (to patrí do HW).
5. Použiť krátke názvy v boxoch, dlhšie vysvetlenie dať do popisu pod obrázkom.
6. Každý diagram musí mať mini legendu (typy čiar a význam farieb).

## Overenie pred exportom

1. Sedí diagram s runtime v `raspberry_pi/main.py`.
2. Sedí poradie FSM v `raspberry_pi/utils/scene_parser.py`.
3. Sedí desired/confirmed logika so `mqtt_feedback_tracker.py` a `mqtt_actuator_state_store.py`.
4. Sedí dashboard event flow s `raspberry_pi/Web/dashboard.py`.
5. Exportovať do SVG + PDF fallback.
