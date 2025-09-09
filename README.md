# Aila 2.0

Aila 2.0 is an AI-powered programming language that uses Google's Gemini to translate simple Aila commands into safe Python code and execute it.

## Installation

Navigate to the project folder and install locally:

```bash
python3 -m pip install -e .
```

## Configuration

Set your Gemini API key in your environment:

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

Run your program (requires `GEMINI_API_KEY`):

```bash
aila example.aila
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
- Google Gemini API key
