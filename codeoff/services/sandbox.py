# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
Sandbox module: validates and restricts user-submitted Python code.

Provides two layers of defense:
1. AST validation (pre-execution) — rejects code with dangerous patterns before running.
2. Runtime restrictions (in-subprocess) — restricted builtins, import allowlist, no file/network access.
"""

import ast

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
