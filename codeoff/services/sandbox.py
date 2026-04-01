# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
Sandbox module: validates and restricts user-submitted Python code,
and executes it in isolated subprocesses.

Provides three layers of defense:
1. AST validation (pre-execution) — rejects code with dangerous patterns before running.
2. Runtime restrictions (in-subprocess) — restricted builtins, import allowlist, no file/network access.
3. OS-level limits — memory, process count, and timeout constraints.
"""

import ast
import json
import os
import resource
import subprocess
import sys
import tempfile
import time

# Modules that are safe for competitive programming
ALLOWED_MODULES = frozenset(
	{
		"math",
		"cmath",
		"collections",
		"itertools",
		"functools",
		"heapq",
		"bisect",
		"re",
		"string",
		"operator",
		"copy",
		"decimal",
		"fractions",
		"random",
		"statistics",
		"typing",
		"dataclasses",
		"enum",
		"array",
		"deque",
		"sortedcontainers",
		"json",
	}
)

# Attributes that should never be accessed
BLOCKED_ATTRIBUTES = frozenset(
	{
		"__subclasses__",
		"__bases__",
		"__mro__",
		"__class__",
		"__globals__",
		"__code__",
		"__builtins__",
		"__import__",
		"__loader__",
		"__spec__",
	}
)

# Modules that must never be imported
BLOCKED_MODULES = frozenset(
	{
		"os",
		"sys",
		"subprocess",
		"socket",
		"shutil",
		"signal",
		"ctypes",
		"importlib",
		"pathlib",
		"io",
		"_io",
		"builtins",
		"code",
		"codeop",
		"compileall",
		"gc",
		"inspect",
		"pickle",
		"shelve",
		"marshal",
		"multiprocessing",
		"threading",
		"_thread",
		"concurrent",
		"asyncio",
		"http",
		"urllib",
		"requests",
		"ftplib",
		"smtplib",
		"xmlrpc",
		"webbrowser",
		"tempfile",
		"glob",
		"fnmatch",
		"resource",
		"pty",
		"fcntl",
		"termios",
		"mmap",
		"sqlite3",
		"dbm",
		"csv",  # no file I/O needed
		"zipfile",
		"tarfile",
		"gzip",
		"bz2",
		"lzma",
		"zipimport",
		"pkgutil",
		"runpy",
		"tracemalloc",
	}
)


class SandboxValidationError(Exception):
	"""Raised when user code fails sandbox validation."""

	pass


def validate_source_code(source_code: str) -> None:
	"""
	Validate user source code via AST analysis.
	Raises SandboxValidationError if dangerous patterns are detected.
	"""
	try:
		tree = ast.parse(source_code)
	except SyntaxError:
		# Let the actual execution handle syntax errors with proper line numbers
		return

	for node in ast.walk(tree):
		_check_imports(node)
		_check_attribute_access(node)
		_check_dangerous_names(node)
		_check_dangerous_calls(node)


def _check_imports(node: ast.AST) -> None:
	"""Block imports of dangerous modules."""
	if isinstance(node, ast.Import):
		for alias in node.names:
			module_root = alias.name.split(".")[0]
			if module_root in BLOCKED_MODULES:
				raise SandboxValidationError(f"Import of '{alias.name}' is not allowed")
			if module_root not in ALLOWED_MODULES:
				raise SandboxValidationError(
					f"Import of '{alias.name}' is not allowed. "
					f"Allowed modules: {', '.join(sorted(ALLOWED_MODULES))}"
				)

	elif isinstance(node, ast.ImportFrom):
		if node.module:
			module_root = node.module.split(".")[0]
			if module_root in BLOCKED_MODULES:
				raise SandboxValidationError(f"Import from '{node.module}' is not allowed")
			if module_root not in ALLOWED_MODULES:
				raise SandboxValidationError(
					f"Import from '{node.module}' is not allowed. "
					f"Allowed modules: {', '.join(sorted(ALLOWED_MODULES))}"
				)


def _check_attribute_access(node: ast.AST) -> None:
	"""Block access to dangerous dunder attributes."""
	if isinstance(node, ast.Attribute):
		if node.attr in BLOCKED_ATTRIBUTES:
			raise SandboxValidationError(f"Access to '{node.attr}' is not allowed")


def _check_dangerous_names(node: ast.AST) -> None:
	"""Block access to dangerous names like __builtins__."""
	if isinstance(node, ast.Name) and node.id in ("__builtins__", "__loader__", "__spec__"):
		raise SandboxValidationError(f"Access to '{node.id}' is not allowed")


def _check_dangerous_calls(node: ast.AST) -> None:
	"""Block calls to dangerous built-in functions."""
	if isinstance(node, ast.Call):
		func = node.func
		# Direct call: eval(...), exec(...), __import__(...)
		if isinstance(func, ast.Name) and func.id in (
			"eval",
			"exec",
			"compile",
			"__import__",
			"breakpoint",
			"open",
			"input",
			"exit",
			"quit",
		):
			raise SandboxValidationError(f"Call to '{func.id}()' is not allowed")

		# getattr/setattr/delattr with string literal targeting blocked attrs
		if isinstance(func, ast.Name) and func.id in ("getattr", "setattr", "delattr"):
			if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
				if node.args[1].value in BLOCKED_ATTRIBUTES:
					raise SandboxValidationError(
						f"Using {func.id}() to access '{node.args[1].value}' is not allowed"
					)


# ── Runtime restriction code (injected into the subprocess runner) ──────────

IMPORT_HOOK_CODE = """
import importlib
import importlib.abc

_ALLOWED_MODULES = {allowed_modules!r}

class _SafeImportFinder(importlib.abc.MetaPathFinder):
    \"\"\"Only allow importing from the allowlist.\"\"\"
    def find_module(self, fullname, path=None):
        root = fullname.split(".")[0]
        # Allow stdlib internals needed by the runner itself
        if root.startswith("_") or root in ("encodings", "codecs", "zipimport"):
            return None
        if root not in _ALLOWED_MODULES:
            return self  # returning self means we handle it — by raising

    def load_module(self, fullname):
        raise ImportError(f"Import of '{{fullname}}' is not allowed in the sandbox")

import sys as _sys
_sys.meta_path.insert(0, _SafeImportFinder())
"""

RESTRICTED_BUILTINS_CODE = '''
import builtins as _builtins

_ALLOWED_IMPORT_MODULES = $ALLOWED_MODULES$

def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split('.')[0]
    if root not in _ALLOWED_IMPORT_MODULES:
        raise ImportError(f"Import of '{name}' is not allowed in the sandbox")
    return _builtins.__import__(name, globals, locals, fromlist, level)

_SAFE_BUILTINS = {
    '__name__': '__main__',
    '__build_class__': _builtins.__build_class__,
    '__import__': _safe_import,
    # Types and constructors
    'True': True, 'False': False, 'None': None,
    'int': int, 'float': float, 'complex': complex,
    'str': str, 'bytes': bytes, 'bytearray': bytearray,
    'bool': bool, 'list': list, 'tuple': tuple, 'dict': dict, 'set': set, 'frozenset': frozenset,
    'type': type, 'object': object, 'property': property, 'classmethod': classmethod, 'staticmethod': staticmethod,
    'super': super, 'memoryview': memoryview, 'slice': slice,
    # Iterators and generators
    'range': range, 'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter, 'reversed': reversed,
    'iter': iter, 'next': next,
    # Math and comparison
    'abs': abs, 'divmod': divmod, 'pow': pow, 'round': round, 'min': min, 'max': max, 'sum': sum,
    # String and repr
    'repr': repr, 'ascii': ascii, 'chr': chr, 'ord': ord, 'format': format, 'bin': bin, 'oct': oct, 'hex': hex,
    # Collections
    'len': len, 'sorted': sorted, 'hash': hash, 'id': id, 'callable': callable,
    'isinstance': isinstance, 'issubclass': issubclass,
    'any': any, 'all': all,
    # Printing (captured by runner)
    'print': print,
    # Exceptions
    'Exception': Exception, 'BaseException': BaseException,
    'ArithmeticError': ArithmeticError, 'AssertionError': AssertionError,
    'AttributeError': AttributeError, 'EOFError': EOFError,
    'FloatingPointError': FloatingPointError, 'GeneratorExit': GeneratorExit,
    'ImportError': ImportError, 'IndexError': IndexError,
    'KeyError': KeyError, 'KeyboardInterrupt': KeyboardInterrupt,
    'LookupError': LookupError, 'MemoryError': MemoryError,
    'NameError': NameError, 'NotImplementedError': NotImplementedError,
    'OSError': OSError, 'OverflowError': OverflowError,
    'RecursionError': RecursionError, 'ReferenceError': ReferenceError,
    'RuntimeError': RuntimeError, 'StopIteration': StopIteration,
    'StopAsyncIteration': StopAsyncIteration,
    'SyntaxError': SyntaxError, 'SystemError': SystemError,
    'TypeError': TypeError, 'UnboundLocalError': UnboundLocalError,
    'UnicodeDecodeError': UnicodeDecodeError, 'UnicodeEncodeError': UnicodeEncodeError,
    'UnicodeError': UnicodeError, 'UnicodeTranslateError': UnicodeTranslateError,
    'ValueError': ValueError, 'ZeroDivisionError': ZeroDivisionError,
}
'''


def get_import_hook_code() -> str:
	"""Return Python code that installs the import allowlist in the subprocess."""
	return IMPORT_HOOK_CODE.format(allowed_modules=set(ALLOWED_MODULES))


def get_restricted_builtins_code() -> str:
	"""Return Python code that defines _SAFE_BUILTINS dict in the subprocess."""
	return RESTRICTED_BUILTINS_CODE.replace("$ALLOWED_MODULES$", repr(set(ALLOWED_MODULES)))


# ── Public API: run user code in sandboxed subprocess ───────────────────────


def run_tests(source_code, function_name, test_cases, time_limit=2.0, memory_limit_mb=256):
	"""Execute source code against test cases in an isolated subprocess."""
	if not test_cases:
		return {
			"verdict": "Internal Error",
			"passed_tests": 0,
			"total_tests": 0,
			"runtime_ms": 0,
			"details": [],
			"error": "No test cases found",
		}

	# Pre-execution sandbox validation (AST analysis)
	try:
		validate_source_code(source_code)
	except SandboxValidationError as e:
		return {
			"verdict": "Sandbox Violation",
			"passed_tests": 0,
			"total_tests": len(test_cases),
			"runtime_ms": 0,
			"details": [],
			"error": str(e),
		}

	# Build the runner script
	runner_script = _build_runner_script(source_code, function_name, test_cases)

	start_time = time.time()
	try:
		result = _execute_in_subprocess(runner_script, time_limit, memory_limit_mb)
	except subprocess.TimeoutExpired:
		elapsed_ms = int((time.time() - start_time) * 1000)
		return {
			"verdict": "Time Limit Exceeded",
			"passed_tests": 0,
			"total_tests": len(test_cases),
			"runtime_ms": elapsed_ms,
			"details": [],
			"error": "Execution timed out",
		}
	except Exception as e:
		elapsed_ms = int((time.time() - start_time) * 1000)
		return {
			"verdict": "Internal Error",
			"passed_tests": 0,
			"total_tests": len(test_cases),
			"runtime_ms": elapsed_ms,
			"details": [],
			"error": str(e),
		}

	elapsed_ms = int((time.time() - start_time) * 1000)

	if result.returncode != 0:
		stderr = result.stderr or ""
		if "MemoryError" in stderr:
			verdict = "Memory Limit Exceeded"
		else:
			verdict = "Runtime Error"

		return {
			"verdict": verdict,
			"passed_tests": 0,
			"total_tests": len(test_cases),
			"runtime_ms": elapsed_ms,
			"details": [],
			"error": stderr[:2000],
		}

	# Parse results from stdout
	try:
		output = json.loads(result.stdout)
	except Exception:
		return {
			"verdict": "Internal Error",
			"passed_tests": 0,
			"total_tests": len(test_cases),
			"runtime_ms": elapsed_ms,
			"details": [],
			"error": f"Could not parse judge output: {(result.stdout or '')[:500]}",
		}

	# Sanitize per-test tracebacks in case the temp path leaked via stderr
	for detail in output.get("details", []):
		if "traceback" in detail:
			detail["traceback"] = _sanitize_error(detail["traceback"])
		if "error" in detail:
			detail["error"] = _sanitize_error(detail["error"])

	passed = output.get("passed", 0)
	total = output.get("total", len(test_cases))
	top_error = output.get("error")

	if top_error:
		verdict = "Runtime Error"
	elif passed == total:
		verdict = "Accepted"
	else:
		verdict = "Wrong Answer"

	return {
		"verdict": verdict,
		"passed_tests": passed,
		"total_tests": total,
		"runtime_ms": elapsed_ms,
		"details": output.get("details", []),
		"stdout": output.get("stdout", ""),
		**(({"error": top_error}) if top_error else {}),
	}


# ── Private helpers ─────────────────────────────────────────────────────────


def _build_runner_script(source_code, function_name, test_cases):
	"""Build a self-contained Python script that runs the user code against test cases."""
	tests_json = json.dumps(
		[
			{
				"input": json.loads(tc.input_data) if isinstance(tc.input_data, str) else tc.input_data,
				"expected": json.loads(tc.expected_output)
				if isinstance(tc.expected_output, str)
				else tc.expected_output,
			}
			for tc in test_cases
		]
	)

	import_hook = get_import_hook_code()
	restricted_builtins = get_restricted_builtins_code()

	# compile() with a friendly filename so all tracebacks reference "<your code>"
	# and line numbers are 1-based within the user's own code.
	runner = f"""
import json
import sys
import io
import traceback as _tb

# -- Sandbox: install import allowlist --
{import_hook}

# -- Sandbox: define restricted builtins --
{restricted_builtins}

_src = {source_code!r}

# Execute user code in a namespace with restricted builtins
_user_globals = {{'__builtins__': _SAFE_BUILTINS}}
try:
    exec(compile(_src, "<your code>", "exec"), _user_globals)
except SyntaxError as _e:
    print(json.dumps({{"passed": 0, "total": {len(test_cases)}, "details": [], "error": "SyntaxError on line " + str(_e.lineno) + ": " + str(_e.msg)}}))
    sys.exit(0)

def _run_tests():
    _func = _user_globals['{function_name}']
    tests = json.loads('''{tests_json}''')
    results = []
    passed = 0
    total = len(tests)
    all_stdout = ""

    for i, test in enumerate(tests):
        try:
            args = test["input"]
            if not isinstance(args, list):
                args = [args]
            _capture = io.StringIO()
            sys.stdout = _capture
            try:
                actual = _func(*args)
            finally:
                sys.stdout = sys.__stdout__
                all_stdout += _capture.getvalue()
            expected = test["expected"]
            is_pass = actual == expected
            if is_pass:
                passed += 1
            results.append({{"test": i, "passed": is_pass, "expected": expected, "actual": actual}})
        except Exception as e:
            sys.stdout = sys.__stdout__
            tb = _tb.format_exc()
            results.append({{"test": i, "passed": False, "error": str(e), "traceback": tb}})

    output = {{"passed": passed, "total": total, "details": results, "stdout": all_stdout}}
    print(json.dumps(output))

_run_tests()
"""
	return runner


def _execute_in_subprocess(script, time_limit, memory_limit_mb):
	"""Run a Python script in an isolated subprocess with resource limits."""
	with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
		f.write(script)
		script_path = f.name

	try:
		memory_bytes = memory_limit_mb * 1024 * 1024

		def set_limits():
			# Set memory limit (may fail on some platforms)
			try:
				resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
			except Exception:
				pass
			# Prevent fork bombs — allow only 1 process (the current one)
			try:
				resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
			except Exception:
				pass

		result = subprocess.run(
			[sys.executable, script_path],
			capture_output=True,
			text=True,
			timeout=time_limit + 1,  # small buffer over test time limit
			preexec_fn=set_limits,
			env=_get_safe_env(),
		)
		result.stderr = _sanitize_error(result.stderr or "", script_path)
		return result
	finally:
		os.unlink(script_path)


def _sanitize_error(text: str, script_path: str = "") -> str:
	"""Strip temp file paths from error output before surfacing to users."""
	import re

	if script_path:
		text = text.replace(script_path, "<your code>")
	# Catch any remaining tmp*.py paths (e.g. from nested tracebacks)
	text = re.sub(r'"?/[^"\s]*tmp\w+\.py"?', '"<your code>"', text)
	return text


def _get_safe_env():
	"""Return a minimal environment for subprocess execution."""
	return {
		"PATH": "/usr/bin:/usr/local/bin",
		"HOME": "/tmp",
		"LANG": "en_US.UTF-8",
	}
