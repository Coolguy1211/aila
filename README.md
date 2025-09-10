# Aila 3.0

Aila 3.0 is an AI-powered programming language that can translate simple Aila commands into safe Python code and execute it via:
- Cloud: Google's Gemini
- Local: Ollama (no network)

## Installation

Navigate to the project folder and install locally:

```bash
python3 -m pip install -e .
```

## Configuration

Set your Gemini API key in your environment (for cloud mode):

```bash
# macOS/Linux
export GEMINI_API_KEY="YOUR_KEY_HERE"

# Windows PowerShell
setx GEMINI_API_KEY "YOUR_KEY_HERE"
```

## Usage

Create an Aila program file (e.g., `example.aila`):

```
say Hello World
repeat 3 Hi there!
wait 1
say Done!
```

Run your program with Gemini (requires `GEMINI_API_KEY`):

```bash
aila example.aila

Run locally with Ollama (no API key required):

```bash
# Install and run Ollama first, and pull a model (e.g., llama3.1)
# macOS: brew install ollama && ollama serve &
ollama pull llama3.1

# Optionally select a model via env var
export OLLAMA_MODEL="llama3.1"

# Compile and run locally
aila --local example.aila
```
```

## Language Features (subset)

- `say X`: Prints X to the console
- `repeat N X`: Repeats printing X N times
- `wait N`: Waits for N seconds
- `window TITLE`: Creates a GUI window with `TITLE`
- `label TEXT`: Adds a label to the window
- `input [TEXT]`: Adds an input field with optional default `TEXT`
- `button TEXT`: Adds a button with `TEXT`
- `show TEXT`: Shows a message box with `TEXT`
- `start`: Starts the GUI event loop
- `close`: Closes the GUI window

## Requirements

- Python 3.9 or higher
- Google Gemini API key (cloud mode)
- Ollama installed and a supported local model pulled (local mode)
- A graphical display environment (`$DISPLAY` set) for GUI applications

## Roadmap: 200 Features for Aila 3.x

Below is a concise outline of 200 planned features, grouped by category. Counts per category sum to 200.

- CLI and Tooling (15)
  - --local Ollama model selection, caching, verbosity, dry-run, AST dump, code-out path, timeout, retries, colored logs, perf timers, version check, doctor, init template, validate, fmt stub
- Compiler/Prompting (20)
  - Strict guardrails expansion, richer examples, deterministic prompts, safety checks, lint on output, structured JSON outputs, retry with diff, hallucination checks, function registry, test snippets, import whitelist, time/memory caps, resource budget, DSL-to-AST pipeline, incremental compile, streaming logs, temperature per-section, prompt fingerprinting, model capability hints, self-check pass
- Local Engine/Ollama (10)
  - Model auto-pull, fallback chain, model aliasing, metadata hints, prompt length guard, local cache dir, offline docs, multi-shot examples, batch compile, sandbox runner tweaks
- Language Core Syntax (30)
  - Variables, numeric ops, strings with interpolation, if/elseif/else/endif, while/end, for-in range, functions define/call/return, comments, include files, constants, error handling try/catch, comparison ops, logical ops, boolean literals, arrays, maps, len, slice, join/split, to-number/string, random, date/time, format, print variants, input read, exit codes, assert, import stdlib
- Standard Library (20)
  - math, strings, lists, dicts, json, time, os-safe, path-safe, uuid, hashing, regex (safe), http (mock/local), csv, ini, env, templating, table render, progress, logger, metrics
- GUI Widgets (18)
  - checkbox, radio, dropdown, slider, progress bar, image, canvas, grid layout, tabs, menu bar, status bar, toolbar, dialog open/save, color picker, date picker, number spinner, tooltip, hotkeys
- GUI Behavior (10)
  - bind events, state store, theme switch, dark mode, responsive layout presets, modal management, validation helpers, focus control, widget ids/lookup, clear/reset
- Filesystem Safety (6)
  - in-memory fs option, virtual sandbox paths, quota limits, file-type allowlist, safe temp files, cleanup hooks
- Networking Safety (6)
  - disable-by-default, localhost-only option, rate limits, request schema validation, response size caps, timeout defaults
- Error Handling and DX (12)
  - friendly tracebacks, code frames, suggestion engine, link to docs, quick fixes, unknown-command hints, deprecation warnings, strict mode, runtime guards, exit statuses, diag report, reproducible seeds
- Testing (10)
  - golden tests for compiler outputs, fixtures for prompts, unit tests for interpreter, snapshot GUI tests, CLI e2e tests, smoke tests, fuzz tests on parser, mutation tests on guardrails, test matrix for models, CI integration
- Performance (8)
  - caching compiled code, incremental runs, debounce on edits, lazy widget instantiation, parallel compile batches, bytecode reuse (safe), fast-paths for common commands, profiling hooks
- Packaging (6)
  - single-file bundle, zipapp option, plugin system layout, version pinning guidance, extras for gui/http, templates
- Documentation (9)
  - language reference, cookbook, migration 2.x->3.x, safety model, local mode guide, troubleshooting, FAQ, examples gallery, contribution guide
- Examples (10)
  - calculators, forms, games, dashboards, file tools, charts, timers, wizards, notepad, widgets showcase
- Internationalization (4)
  - UTF-8 everywhere, message catalogs, locale-aware formatting, RTL layout presets
- Accessibility (5)
  - ARIA-like hints, keyboard navigation, high-contrast theme, screen reader labels, focus outlines
- Telemetry (opt-in) (5)
  - anonymized usage, error reports, toggle in CLI, redact policies, local logs only
- Security (6)
  - command allow/deny lists, sandboxed exec, taint tracking (basic), input validation helpers, template escaping, dependency integrity
- Governance and Releases (10)
  - RFC process, semantic versioning, deprecation policy, LTS branches, release notes automation, changelog, compatibility tests, support matrix, maintainers guide, issue templates

Total: 200 features.
