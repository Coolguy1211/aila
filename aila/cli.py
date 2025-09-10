import os
import sys
import time
import pprint
import tempfile
import subprocess
from google import genai
from argparse import ArgumentParser
import ollama
import hashlib
from tenacity import Retrying, stop_after_attempt, wait_fixed
from .parser import Parser

__version__ = "3.0.0"
MODEL = "gemini-2.5-flash"
CACHE_DIR = ".aila_cache"

class Colors:
    """A simple class for printing colored text to the terminal."""
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.HEADER = '\033[95m' if enabled else ''
        self.OKBLUE = '\033[94m' if enabled else ''
        self.OKCYAN = '\033[96m' if enabled else ''
        self.OKGREEN = '\033[92m' if enabled else ''
        self.WARNING = '\033[93m' if enabled else ''
        self.FAIL = '\033[91m' if enabled else ''
        self.ENDC = '\033[0m' if enabled else ''
        self.BOLD = '\033[1m' if enabled else ''

    def _print(self, color, text):
        print(f"{color}{text}{self.ENDC}")

    def header(self, text): self._print(self.HEADER, text)
    def blue(self, text): self._print(self.OKBLUE, text)
    def cyan(self, text): self._print(self.OKCYAN, text)
    def green(self, text): self._print(self.OKGREEN, text)
    def warn(self, text): self._print(self.WARNING, text)
    def fail(self, text): self._print(self.FAIL, text)
    def bold(self, text): self._print(self.BOLD, text)
    def plain(self, text): print(text)

PROMPT_TEMPLATE = """
You are Aila 3.0's compiler. Your sole purpose is to translate the user's Aila code into safe, sandboxed Python 3 code. You must only generate code for the commands present in the user's input.

**GUI INSTRUCTIONS:**
- To use GUI features, you MUST first import and instantiate the AilaGUI class like this:
  `from aila.gui import AilaGUI`
  `gui = AilaGUI()`
- All subsequent GUI commands MUST be called as methods on this `gui` object (e.g., `gui.create_window(...)`).

**CRITICAL SAFETY INSTRUCTIONS:**
- If you use functions from the `time` module, you MUST include `import time` at the beginning of the script.
- YOU MUST NOT import any modules other than `aila.gui` and `time`.
- YOU MUST NOT use any built-in functions that interact with the filesystem (e.g., `open`, `read`, `write`), network (e.g., `socket`, `urllib`), or subprocesses (e.g., `os.system`, `subprocess.run`).
- YOU MUST NOT use `eval()` or `exec()`.
- All generated code MUST be wrapped in a `try...except Exception as e:` block that prints the error.
- The output MUST be only the raw Python code, with no surrounding text, comments, or markdown fences like ```python.

**LANGUAGE SPECIFICATIONS & EXAMPLES:**

- `say TEXT`: Prints text to the console.
  - Aila: `say Hello World`
  - Python: `print("Hello World")`

- `repeat N TEXT`: Repeats printing text N times.
  - Aila: `repeat 3 "Hi!"`
  - Python: `for _ in range(3): print("Hi!")`

- `wait SECONDS`: Pauses execution.
  - Aila: `wait 1.5`
  - Python: `time.sleep(1.5)`

- `window TITLE`: Creates a GUI window.
  - Aila: `window "My App"`
  - Python: `gui.create_window("My App")`

- `label TEXT`: Adds a text label to the window.
  - Aila: `label "Enter your name:"`
  - Python: `gui.label("Enter your name:")`

- `input [DEFAULT_TEXT]`: Adds a text input box.
  - Aila: `input "Default value"`
  - Python: `name_entry = gui.input("Default value")`

- `button TEXT`: Adds a button. The `on_click` function should contain the logic.
  - Aila:
    input "0"
    button "Increment"
  - Python:
    entry = gui.input("0")
    def on_increment():
        current_value = int(entry.get())
        entry.delete(0, "end")
        entry.insert(0, str(current_value + 1))
    gui.button("Increment", on_click=on_increment)

- `show TEXT`: Shows a message box with `TEXT`.
  - Aila: `show "Hello"`
  - Python: `gui.show("Hello")`

- `start`: Starts the GUI event loop. This must be the last command for a GUI app.
  - Aila: `start`
  - Python: `gui.start()`

**USER'S AILA CODE (INPUT):**
```
{aila_code}
```

**YOUR PYTHON 3 CODE (OUTPUT):**
"""

def lint_code(code: str, colors: Colors) -> bool:
    """Checks if the generated code is valid Python syntax."""
    try:
        compile(code, "<string>", "exec")
        return True
    except SyntaxError as e:
        colors.fail("\n[Lint Error] Generated code is not valid Python:")
        colors.plain(str(e))
        return False

def check_safety(code: str, colors: Colors) -> bool:
    """Scans generated code for forbidden keywords."""
    forbidden_keywords = [
        "import os", "import sys", "subprocess", "socket", "urllib",
        "open(", "eval(", "exec(", "ctypes", "shutil"
    ]
    violations = [kw for kw in forbidden_keywords if kw in code]
    if violations:
        colors.fail("\n[Safety Violation] Generated code contains forbidden keywords:")
        for v in violations:
            colors.plain(f"  - Found '{v}'")
        return False
    return True

def get_client(timeout: int):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment!")
        sys.exit(1)
    return genai.Client(api_key=api_key, http_options={"timeout": timeout})

def compile_aila(aila_code: str, client) -> str:
    """Send Aila code to Gemini to generate Python code with strict guardrails."""
    model = client.get_generative_model(MODEL)
    prompt = PROMPT_TEMPLATE.format(aila_code=aila_code)
    response = model.generate_content(
        prompt,
        stream=True
    )

    full_response = ""
    for chunk in response:
        full_response += chunk.text

    code = full_response.strip()
    code = code.replace('```python', '').replace('```', '')
    return code.strip()

def compile_aila_ollama(aila_code: str, model: str, timeout: int) -> str:
    """Use a local Ollama model to translate Aila to Python with the same guardrails."""
    prompt = PROMPT_TEMPLATE.format(aila_code=aila_code)
    options = {"timeout": timeout}
    result = ollama.generate(model=model, prompt=prompt, options=options)
    code = (result.get("response") or "").strip()
    code = code.replace('```python', '').replace('```', '')
    return code.strip()


def get_cache_key(data: str) -> str:
    """Computes the SHA256 hash of a string to use as a cache key."""
    return hashlib.sha256(data.encode()).hexdigest()

def save_to_cache(cache_dir: str, key: str, content: str):
    """Saves content to a file in the cache directory."""
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_path = os.path.join(cache_dir, key)
    with open(cache_path, "w") as f:
        f.write(content)

def load_from_cache(cache_dir: str, key: str) -> str | None:
    """Loads content from a file in the cache directory if it exists."""
    cache_path = os.path.join(cache_dir, key)
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return f.read()
    return None


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


def handle_run(args, colors):
    """Handles the 'run' command."""
    start_time = time.time()
    filename = args.filename
    if not os.path.exists(filename):
        colors.fail(f"File not found: {filename}")
        sys.exit(1)

    with open(filename, "r") as f:
        aila_code = f.read()

    colors.bold("=== Aila Code ===")
    colors.plain(aila_code)

    if args.dump_ast:
        colors.header("\n--- Abstract Syntax Tree ---")
        parser = Parser(aila_code)
        ast = parser.parse()
        pprint.pprint(ast)
        sys.exit(0)

    py_code = None
    cache_key = get_cache_key(aila_code)
    compilation_time = 0

    if not args.no_cache:
        py_code = load_from_cache(args.cache_dir, cache_key)
        if py_code:
            colors.warn("\n[Cache] Loaded from cache.")

    if py_code is None:
        compile_start_time = time.time()

        retryer = Retrying(
            stop=stop_after_attempt(args.retries),
            wait=wait_fixed(args.retry_delay),
            reraise=True
        )

        try:
            if args.local:
                model_name = args.model
                colors.blue(f"\n[Local] Compiling via Ollama (model: {model_name}, timeout: {args.timeout}s)...")
                py_code = retryer(compile_aila_ollama, aila_code, model_name, args.timeout)
            else:
                client = get_client(timeout=args.timeout)
                colors.blue(f"\n[Aila -> Python] Compiling via Gemini (timeout: {args.timeout}s)...")
                py_code = retryer(compile_aila, aila_code, client)
        except Exception as e:
            colors.fail(f"\nAPI call failed after {args.retries} retries: {e}")
            colors.warn("\nThis could be due to a few reasons:")
            colors.warn("  - Your internet connection is unstable.")
            colors.warn("  - The Gemini API service is temporarily down.")
            colors.warn("  - The compilation is taking longer than expected.")
            colors.warn("\nYou can try increasing the timeout and retries with the --timeout and --retries flags.")
            py_code = None # Ensure py_code is None on failure

        compilation_time = time.time() - compile_start_time

        if py_code:
            # Post-compilation checks
            if not lint_code(py_code, colors) or not check_safety(py_code, colors):
                colors.fail("\nCompilation failed due to linting or safety violations.")
                # Invalidate the cache if the generated code was bad
                if not args.no_cache:
                    cache_path = os.path.join(args.cache_dir, cache_key)
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
                sys.exit(1)

            if not args.no_cache:
                colors.warn("\n[Cache] Saving to cache.")
                save_to_cache(args.cache_dir, cache_key, py_code)

    if not py_code:
        colors.fail("\nError: Compilation failed, no Python code generated.")
        sys.exit(1)

    colors.bold("\n=== Python Code ===")
    colors.cyan(py_code)

    if args.code_out:
        try:
            with open(args.code_out, "w") as f:
                f.write(py_code)
            colors.green(f"\n[Code Out] Saved generated Python to {args.code_out}")
        except IOError as e:
            colors.fail(f"\nError writing to {args.code_out}: {e}")
            sys.exit(1)

    if args.dry_run:
        colors.warn("\n--dry-run specified. Skipping execution.")
        sys.exit(0)

    colors.bold("\n[Python] Executing...")
    exec_start_time = time.time()
    output = run_python(py_code)
    exec_time = time.time() - exec_start_time

    colors.plain(output)

    if args.verbose > 0:
        colors.header("\n--- Performance ---")
        if compilation_time > 0:
            colors.plain(f"Compilation: {compilation_time:.2f}s")
        colors.plain(f"Execution:     {exec_time:.2f}s")
        colors.plain(f"Total:         {time.time() - start_time:.2f}s")

def handle_init(args, colors):
    """Handles the 'init' command."""
    filename = args.filename
    template = """\
# Welcome to Aila!
# This is a simple starter program.

say "Hello, World!"

# Try adding a GUI!
# window "My First App"
# label "Welcome to Aila"
# button "Click Me"
# start
"""
    if os.path.exists(filename):
        colors.fail(f"Error: File '{filename}' already exists. Aborting.")
        sys.exit(1)

    try:
        with open(filename, "w") as f:
            f.write(template)
        colors.green(f"Successfully created '{filename}'.")
        colors.plain("You can now run it with: aila run " + filename)
    except IOError as e:
        colors.fail(f"Error creating file: {e}")
        sys.exit(1)


def handle_doctor(args, colors):
    colors.bold("--- Aila Environment Doctor ---")

    # Check for Gemini API Key
    colors.bold("\n[1] Gemini (Cloud) Check:")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        colors.green("  - GEMINI_API_KEY is set.")
    else:
        colors.warn("  - GEMINI_API_KEY is not set. Cloud mode will not work.")

    # Check for Ollama Connection
    colors.bold("\n[2] Ollama (Local) Check:")
    try:
        # We can use the ollama.ps() command as a lightweight way to check the connection
        response = ollama.ps()
        colors.green("  - Ollama connection successful.")
        if args.verbose > 0:
            models = response.get('models', [])
            if models:
                colors.plain("    Available models:")
                for model in models:
                    colors.plain(f"      - {model['name']}")
            else:
                colors.warn("    Ollama is running, but no models found.")

    except Exception as e:
        colors.fail("  - Ollama connection failed.")
        colors.warn("    Please ensure Ollama is installed, running, and accessible.")
        if args.verbose > 0:
            colors.plain(f"    Error: {e}")

    colors.bold("\nDoctor's report complete.")

def handle_validate(args, colors):
    """Handles the 'validate' command."""
    colors.bold(f"--- Validating {args.filename} ---")
    filename = args.filename
    if not os.path.exists(filename):
        colors.fail(f"File not found: {filename}")
        sys.exit(1)

    with open(filename, "r") as f:
        aila_code = f.read()

    parser = Parser(aila_code)
    ast = parser.parse()
    errors = []

    # Define command specifications: {command: (min_args, max_args)}
    # Use float('inf') for no upper limit.
    COMMAND_SPECS = {
        "say": (1, float('inf')),
        "repeat": (2, float('inf')),
        "wait": (1, 1),
        "window": (1, float('inf')),
        "label": (1, float('inf')),
        "input": (0, float('inf')),
        "button": (1, float('inf')),
        "show": (1, float('inf')),
        "start": (0, 0),
        "close": (0, 0),
    }

    for command in ast:
        if command.name not in COMMAND_SPECS:
            errors.append(f"L{command.line_number}: Unknown command '{command.name}'")
            continue

        min_args, max_args = COMMAND_SPECS[command.name]
        num_args = len(command.args)

        if not (min_args <= num_args <= max_args):
            if min_args == max_args:
                expected = f"{min_args} arguments"
            elif max_args == float('inf'):
                expected = f"at least {min_args} arguments"
            else:
                expected = f"between {min_args} and {max_args} arguments"
            errors.append(f"L{command.line_number}: Command '{command.name}' expects {expected}, but got {num_args}")

    if errors:
        colors.fail("\nValidation failed with the following errors:")
        for error in errors:
            colors.plain(f"  - {error}")
        sys.exit(1)
    else:
        colors.green("\nValidation successful: No issues found.")

def handle_fmt(args, colors):
    """Handles the 'fmt' command."""
    filename = args.filename
    colors.bold(f"--- Formatting {filename} ---")
    if not os.path.exists(filename):
        colors.fail(f"File not found: {filename}")
        sys.exit(1)

    with open(filename, "r") as f:
        original_content = f.read()

    parser = Parser(original_content)
    ast = parser.parse()

    formatted_lines = []
    for command in ast:
        formatted_lines.append(f"{command.name} {' '.join(command.args)}")

    # Add a trailing newline
    formatted_content = "\n".join(formatted_lines) + "\n"

    if args.check:
        if original_content == formatted_content:
            colors.green(f"'{filename}' is already formatted.")
            sys.exit(0)
        else:
            colors.fail(f"'{filename}' is not formatted.")
            # To be more helpful, we could show a diff here in a future version
            sys.exit(1)
    else:
        if original_content == formatted_content:
            colors.green(f"'{filename}' is already formatted. No changes made.")
        else:
            try:
                with open(filename, "w") as f:
                    f.write(formatted_content)
                colors.green(f"Successfully formatted '{filename}'.")
            except IOError as e:
                colors.fail(f"Error writing formatted file: {e}")
                sys.exit(1)

def main():
    parser = ArgumentParser(prog="aila", description="Aila 3.0 Toolchain")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity level")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Compile and run an Aila program")
    run_parser.add_argument("filename", help="Path to .aila program")
    run_parser.add_argument("--local", action="store_true", help="Compile with local Ollama model instead of Gemini")
    run_parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3.1"), help="The local model to use (requires --local)")
    run_parser.add_argument("--no-cache", action="store_true", help="Disable caching of compiled code")
    run_parser.add_argument("--cache-dir", default=CACHE_DIR, help=f"Directory to store cached code (default: {CACHE_DIR})")
    run_parser.add_argument("--dry-run", action="store_true", help="Compile the code but do not execute it")
    run_parser.add_argument("--code-out", help="Save the generated Python code to a file")
    run_parser.add_argument("--dump-ast", action="store_true", help="Parse the Aila code and print the Abstract Syntax Tree")
    run_parser.add_argument("--timeout", type=int, default=60, help="Timeout for API calls in seconds")
    run_parser.add_argument("--retries", type=int, default=2, help="Number of retries for API calls on failure")
    run_parser.add_argument("--retry-delay", type=int, default=5, help="Delay between retries in seconds")
    run_parser.set_defaults(func=handle_run)

    # Init command
    init_parser = subparsers.add_parser("init", help="Create a new Aila project")
    init_parser.add_argument("filename", nargs="?", default="main.aila", help="Name of the file to create (default: main.aila)")
    init_parser.set_defaults(func=handle_init)

    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Check your environment for issues")
    doctor_parser.set_defaults(func=handle_doctor)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate an Aila program")
    validate_parser.add_argument("filename", help="Path to .aila program to validate")
    validate_parser.set_defaults(func=handle_validate)

    # Fmt command
    fmt_parser = subparsers.add_parser("fmt", help="Format an Aila program")
    fmt_parser.add_argument("filename", help="Path to .aila program to format")
    fmt_parser.add_argument("--check", action="store_true", help="Check if the file is formatted without modifying it")
    fmt_parser.set_defaults(func=handle_fmt)

    args = parser.parse_args()
    colors = Colors(enabled=not args.no_color)

    # If no command is given, default to showing help
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(0)

    args.func(args, colors)

if __name__ == "__main__":
    main()
