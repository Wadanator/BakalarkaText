# Obrázok 5.5 - Sekvenčný tok MQTT správ počas vykonania akcie

## Cieľ

Zobraziť kompletný runtime sekvenčný tok pre jednu akciu:
publish príkazu, desired update, feedback branch, confirmed update,
timeout branch a STOP branch.

## Aktéri (lifelines)

1. StateExecutor
2. MQTT Client
3. MQTT Broker
4. ESP32 Node
5. MQTTFeedbackTracker
6. MQTTActuatorStateStore
7. WebDashboard

## Povinné kroky - happy path

1. StateExecutor -> MQTT Client: publish(topic, message)
2. MQTT Client -> Tracker: track_published_message
3. Tracker -> StateStore: update_desired
4. MQTT Client -> Broker: publish command
5. Broker -> ESP32: deliver command
6. ESP32 -> Broker: feedback OK na topic/feedback
7. Broker -> Tracker: handle_feedback_message
8. Tracker -> StateStore: update_confirmed
9. StateStore -> WebDashboard: device_runtime_state_update

## Povinné alternatívne vetvy

### Vetva A - timeout

1. Feedback neprišiel do timeoutu
2. Tracker loguje FEEDBACK TIMEOUT
3. Pending entry sa odstráni

### Vetva B - scene stop

1. Controller vyvolá force_all_off
2. Controller publishne roomX/STOP
3. StateStore nastaví tracked endpointy na OFF
4. Dashboard dostane update

## Povinné callouty

1. audio/video topics sa v trackeri preskakujú
2. expected_feedback_topic sa odvodzuje z topic rules
3. pending sa drží po original_topic

## Vizualizačný štýl

1. Typ diagramu: sequence diagram
2. ALT bloky pre timeout a stop
3. Farby:
   - command path modrá
   - feedback zelená
   - timeout červená
   - state update oranžová

## Súlad s kódom

1. `mqtt_client.py` publish -> tracker hook
2. `mqtt_feedback_tracker.py` track + handle + timeout
3. `mqtt_actuator_state_store.py` desired/confirmed/force_all_off
4. `main.py` stop_scene + broadcast_stop
