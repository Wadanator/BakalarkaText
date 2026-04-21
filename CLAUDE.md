# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This repo serves two purposes simultaneously:

1. **LaTeX bachelor thesis** (`diplomka.tex`) — the primary thing being authored here. Written in Slovak, compiled with `pdflatex` or equivalent.
2. **The actual system source code** the thesis describes — a modular IoT museum exhibition control system.

The thesis references the source code as its subject matter. Both exist side-by-side in the same repo.

## Building the Thesis

The thesis entry point is `diplomka.tex`. Compile with:

```
pdflatex diplomka.tex
pdflatex diplomka.tex   # run twice for cross-references
```

Chapters are in `chapters/`, settings in `settings/`, images in `obr/`.

## Thesis Chapter Map

| File | Content |
|------|---------|
| `chapters/Uvod.tex` | Introduction |
| `chapters/Resers.tex` | Literature review (foreign results only) |
| `chapters/Architektura.tex` | System architecture design |
| `chapters/Implementacia_hw.tex` | Hardware implementation |
| `chapters/Implementacia_sw.tex` | Software implementation |
| `chapters/Experimenty.tex` | Experiments and results |
| `chapters/Zaver.tex` | Conclusion |

## Source of Truth for Technical Content

When writing or editing thesis text about the system, **all technical facts must come from `Instructions_READ_FIRST/`**. Never invent MQTT topics, JSON scene attributes, Python class names, or architectural details that aren't documented there. If information is missing, ask the user to provide the relevant source code.

Key reference docs:
- `Instructions_READ_FIRST/01_project_context.md` — system overview and tech stack
- `Instructions_READ_FIRST/02_system_architecture.md` — runtime architecture
- `Instructions_READ_FIRST/04_mqtt_protocol.md` — MQTT topics and payloads
- `Instructions_READ_FIRST/06_scene_state_machine.md` — JSON scene structure and FSM
- `Instructions_READ_FIRST/09_dashboard_api.md` — WebSocket and Flask API

## Academic Writing Rules (enforced)

The full standards are in `Instructions_READ_FIRST/General_text_instruction.md`. Key constraints:

- **Language**: Slovak, impersonal academic style, passive voice (`zvratné pasívum`)
- **No code identifiers in prose**: write "Spustenie systému", not "`main()`"
- **Citations**: inside the sentence before the period — `...vlastnosti [3].` not `...vlastnosti. [3]`
- **Rešerše chapter**: foreign results only — no own results, no trivial definitions
- **Implementácia chapters**: own results only — no foreign results

## Diagram Standards

Diagrams for the SW chapter live in `obr/SW_DIAGRAM_SPECS/`. Each subdirectory (5_1 through 5_7) contains:
- `diagram_spec.md` — specification for what the diagram should show
- `diagram_*_final.xml` — draw.io source
- `diagram_*_final.png` / `.svg` — exported outputs referenced by LaTeX

Standards are defined in `obr/SW_DIAGRAM_SPECS/SW_DIAGRAMS_STANDARD.md`:
- Block names must be descriptive Slovak phrases, never code identifiers
- Every diagram needs a mini-legend
- Export to PNG + SVG (min width 4000px, scale ≥ 2)

The master checklist for all 7 SW diagrams is `obr/SW_DIAGRAM_SPECS/00_OVERVIEW_CHECKLIST.md`.

## System Architecture (what the thesis describes)

Three sub-projects communicate over MQTT:

**`raspberry_pi/`** — Python 3.10+ backend (`MuseumController`)
- Entry: `main.py`
- Core: `utils/state_machine.py` (FSM engine), `utils/scene_parser.py`, `utils/state_executor.py`
- MQTT layer: `utils/mqtt/` — client, feedback tracker, actuator state store, device registry
- Web backend: `Web/` — Flask + Flask-SocketIO, routes in `Web/routes/`
- Config: `config/config.ini` (MQTT params, GPIO inputs, media paths, room ID)
- Scene definitions: `scenes/room*/` — JSON files defining FSM states, timelines, transitions

**`ArduinoIDE/`** — C++ firmware for ESP32 nodes (Arduino framework)
- `esp32_mqtt_button/` — button input node
- `esp32_mqtt_controller_MOTORS/` — DC motor controller
- `esp32_mqtt_controller_RELAY/` — relay (230 V / 12 V switching) controller

**`src/`** — React + Vite web dashboard
- Connects via Socket.IO to the Flask backend
- Shows room state, device status, logs, and scene controls