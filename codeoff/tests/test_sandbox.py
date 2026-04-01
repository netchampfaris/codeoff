from frappe.tests import IntegrationTestCase

from codeoff.services.judge import run_tests
from codeoff.services.sandbox import SandboxValidationError, validate_source_code
from codeoff.tests.utils import make_test_cases


class TestSandboxValidation(IntegrationTestCase):
	"""Tests for AST-level sandbox validation."""

	def test_blocks_os_import(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("import os")

	def test_blocks_subprocess_import(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("import subprocess")

	def test_blocks_socket_import(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("import socket")

	def test_blocks_from_os_import(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("from os import path")

	def test_blocks_shutil_import(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("import shutil")

	def test_blocks_ctypes_import(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("import ctypes")

	def test_allows_math_import(self):
		validate_source_code("import math")

	def test_allows_collections_import(self):
		validate_source_code("from collections import defaultdict")

	def test_allows_itertools_import(self):
		validate_source_code("import itertools")

	def test_allows_heapq_import(self):
		validate_source_code("import heapq")

	def test_blocks_dunder_subclasses(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("x = ().__class__.__subclasses__()")

	def test_blocks_dunder_globals(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("x = f.__globals__")

	def test_blocks_dunder_builtins(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("x = __builtins__")

	def test_blocks_eval_call(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("eval('1+1')")

	def test_blocks_exec_call(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("exec('pass')")

	def test_blocks_open_call(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("open('/etc/passwd')")

	def test_blocks_compile_call(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("compile('pass', '', 'exec')")

	def test_blocks_dunder_import_call(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("__import__('os')")

	def test_blocks_input_call(self):
		with self.assertRaises(SandboxValidationError):
			validate_source_code("input('enter: ')")

	def test_allows_normal_code(self):
		validate_source_code(
			"def two_sum(nums, target):\n"
			"    lookup = {}\n"
			"    for i, n in enumerate(nums):\n"
			"        if target - n in lookup:\n"
			"            return [lookup[target - n], i]\n"
			"        lookup[n] = i\n"
		)

	def test_allows_code_with_safe_imports(self):
		validate_source_code(
			"from collections import Counter\n"
			"import math\n"
			"def solve(nums):\n"
			"    c = Counter(nums)\n"
			"    return math.sqrt(sum(c.values()))\n"
		)


class TestSandboxRuntime(IntegrationTestCase):
	"""Tests that sandbox restrictions are enforced at runtime."""

	def _run(self, code, function_name="solve"):
		test_cases = make_test_cases([{"input": "[1]", "expected": "1"}])
		return run_tests(
			source_code=code,
			function_name=function_name,
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

	def test_os_import_blocked_at_ast(self):
		result = self._run("import os\ndef solve(x): return x")
		self.assertEqual(result["verdict"], "Sandbox Violation")
		self.assertIn("not allowed", result["error"])

	def test_subprocess_blocked_at_ast(self):
		result = self._run("import subprocess\ndef solve(x): return x")
		self.assertEqual(result["verdict"], "Sandbox Violation")

	def test_open_blocked_at_ast(self):
		result = self._run("def solve(x):\n\topen('/etc/passwd')\n\treturn x")
		self.assertEqual(result["verdict"], "Sandbox Violation")

	def test_eval_blocked_at_ast(self):
		result = self._run("def solve(x):\n\treturn eval('x')")
		self.assertEqual(result["verdict"], "Sandbox Violation")

	def test_normal_code_still_works(self):
		result = self._run("def solve(x): return x")
		self.assertEqual(result["verdict"], "Accepted")

	def test_code_with_math_import_works(self):
		test_cases = make_test_cases([{"input": "[4]", "expected": "2.0"}])
		result = run_tests(
			source_code="import math\ndef solve(x): return math.sqrt(x)",
			function_name="solve",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)
		self.assertEqual(result["verdict"], "Accepted")

	def test_code_with_collections_works(self):
		test_cases = make_test_cases([{"input": "[[1, 2, 1]]", "expected": "2"}])
		result = run_tests(
			source_code="from collections import Counter\ndef solve(nums): return Counter(nums).most_common(1)[0][1]",
			function_name="solve",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)
		self.assertEqual(result["verdict"], "Accepted")

	def test_restricted_builtins_blocks_open_at_runtime(self):
		"""Even if AST check were bypassed, open() is not in restricted builtins."""
		# This is caught at AST level, so verdict is Sandbox Violation
		result = self._run("def solve(x):\n\tf = open('/etc/passwd')\n\treturn x")
		self.assertIn(result["verdict"], ("Sandbox Violation", "Runtime Error"))

	def test_dunder_import_blocked_at_ast(self):
		result = self._run("def solve(x):\n\t__import__('os')\n\treturn x")
		self.assertEqual(result["verdict"], "Sandbox Violation")
