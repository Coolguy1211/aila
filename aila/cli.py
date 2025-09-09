import os
import sys
import tempfile
import subprocess
from google import genai
from argparse import ArgumentParser
import ollama

MODEL = "gemini-1.5-flash"

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment!")
        sys.exit(1)
    return genai.Client(api_key=api_key)

def compile_aila(aila_code: str, client) -> str:
    """Send Aila code to Gemini to generate Python code with strict guardrails."""
    prompt = f"""
You are Aila 2.0's compiler. Translate the following Aila program into Python 3 using Tkinter via AilaGUI.

INPUT (Aila):
{aila_code}

LANG SPECS (subset):
- say TEXT -> print(TEXT)
- repeat N TEXT -> repeat print(TEXT) N times
- wait SECONDS -> time.sleep(SECONDS)
- window TITLE -> gui.create_window(TITLE)
- label TEXT -> gui.label(TEXT)
- input [TEXT] -> gui.input(TEXT?)
- button TEXT -> gui.button(TEXT, on_click=no_op)
- show TEXT -> gui.show(TEXT)
- start -> gui.start()
- close -> gui.close()

REQUIREMENTS:
- Output ONLY valid Python code. No markdown.
- Always `from aila.gui import AilaGUI` and `import time` if wait is used.
- Create `gui = AilaGUI()` first and call `create_window` before widgets.
- Wrap the whole program in `try/except` and print errors.
- Do NOT import anything else except standard lib.
- Do NOT use eval/exec/network/filesystem.
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    code = response.text.strip()
    code = code.replace('```python', '').replace('```', '')
    return code.strip()

def get_ollama_model() -> str:
    model = os.getenv("OLLAMA_MODEL", "llama3.1")
    return model

def compile_aila_ollama(aila_code: str) -> str:
    """Use a local Ollama model to translate Aila to Python with the same guardrails."""
    prompt = f"""
You are Aila 3.0's local compiler. Translate the following Aila program into Python 3 using Tkinter via AilaGUI.

INPUT (Aila):
{aila_code}

LANG SPECS (subset):
- say TEXT -> print(TEXT)
- repeat N TEXT -> repeat print(TEXT) N times
- wait SECONDS -> time.sleep(SECONDS)
- window TITLE -> gui.create_window(TITLE)
- label TEXT -> gui.label(TEXT)
- input [TEXT] -> gui.input(TEXT?)
- button TEXT -> gui.button(TEXT, on_click=no_op)
- show TEXT -> gui.show(TEXT)
- start -> gui.start()
- close -> gui.close()

REQUIREMENTS:
- Output ONLY valid Python code. No markdown fences.
- Always `from aila.gui import AilaGUI` and `import time` if wait is used.
- Create `gui = AilaGUI()` first and call `create_window` before widgets.
- Wrap the whole program in `try/except` and print errors.
- Do NOT import anything else except standard lib.
- Do NOT use eval/exec/network/filesystem.
"""
    result = ollama.generate(model=get_ollama_model(), prompt=prompt)
    code = (result.get("response") or "").strip()
    code = code.replace('```python', '').replace('```', '')
    return code.strip()

def run_python(code: str) -> str:
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=20
        )
        os.remove(tmp_path)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running code: {e}"

def main():
    parser = ArgumentParser(prog="aila", description="Aila 3.0 runner")
    parser.add_argument("filename", nargs="?", help="Path to .aila program")
    parser.add_argument("--local", action="store_true", help="Compile with local Ollama model instead of Gemini")
    args = parser.parse_args()

    if not args.filename:
        print("Usage: aila [--local] <filename.aila>")
        sys.exit(0)

    filename = args.filename
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        sys.exit(1)

    with open(filename, "r") as f:
        aila_code = f.read()

    print("=== Aila Code ===\n", aila_code)

    if args.local:
        print("\n[Local] Compiling via Ollama...")
        py_code = compile_aila_ollama(aila_code)
        print("\n=== Python Code ===\n", py_code)
        print("\n[Python] Executing...\n")
        output = run_python(py_code)
        print(output)
        return

    client = get_client()
    print("\n[Aila -> Python] Compiling via Gemini...")
    py_code = compile_aila(aila_code, client)
    print("\n=== Python Code ===\n", py_code)

    print("\n[Python] Executing...\n")
    output = run_python(py_code)
    print(output)
