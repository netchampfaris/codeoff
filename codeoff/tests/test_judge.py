from frappe.tests import IntegrationTestCase

from codeoff.services.sandbox import run_tests
from codeoff.tests.utils import make_test_cases


class TestCodeoffJudge(IntegrationTestCase):
	"""Tests for the judge module's code execution logic."""

	def test_correct_solution_accepted(self):
		"""Correct solution should get Accepted verdict."""
		test_cases = make_test_cases(
			[
				{"input": "[1, 2]", "expected": "3"},
				{"input": "[10, 20]", "expected": "30"},
			]
		)

		result = run_tests(
			source_code="def add(a, b):\n\treturn a + b",
			function_name="add",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Accepted")
		self.assertEqual(result["passed_tests"], 2)
		self.assertEqual(result["total_tests"], 2)

	def test_wrong_answer(self):
		"""Incorrect solution should get Wrong Answer."""
		test_cases = make_test_cases(
			[
				{"input": "[1, 2]", "expected": "3"},
				{"input": "[10, 20]", "expected": "30"},
			]
		)

		result = run_tests(
			source_code="def add(a, b):\n\treturn 0",
			function_name="add",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Wrong Answer")
		self.assertEqual(result["passed_tests"], 0)

	def test_partial_correct(self):
		"""Solution that passes some but not all tests."""
		test_cases = make_test_cases(
			[
				{"input": "[1, 2]", "expected": "3"},
				{"input": "[0, 0]", "expected": "0"},
				{"input": "[-1, 1]", "expected": "0"},
			]
		)

		result = run_tests(
			source_code="def add(a, b):\n\tif a < 0 or b < 0:\n\t\treturn 999\n\treturn a + b",
			function_name="add",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Wrong Answer")
		self.assertEqual(result["passed_tests"], 2)
		self.assertEqual(result["total_tests"], 3)

	def test_runtime_error(self):
		"""Code that raises an exception — runner catches it per-test, so Wrong Answer."""
		test_cases = make_test_cases([{"input": "[1, 2]", "expected": "3"}])

		result = run_tests(
			source_code="def add(a, b):\n\traise ValueError('boom')",
			function_name="add",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Wrong Answer")
		self.assertEqual(result["passed_tests"], 0)

	def test_syntax_error_in_code(self):
		"""Code with syntax errors should get Runtime Error."""
		test_cases = make_test_cases([{"input": "[1, 2]", "expected": "3"}])

		result = run_tests(
			source_code="def add(a, b)\n\treturn a + b",  # missing colon
			function_name="add",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Runtime Error")

	def test_time_limit_exceeded(self):
		"""Infinite loop should produce Time Limit Exceeded."""
		test_cases = make_test_cases([{"input": "[1, 2]", "expected": "3"}])

		result = run_tests(
			source_code="def add(a, b):\n\twhile True: pass",
			function_name="add",
			test_cases=test_cases,
			time_limit=1.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Time Limit Exceeded")

	def test_stdout_captured(self):
		"""Print statements in user code should be captured and returned."""
		test_cases = make_test_cases([{"input": "[1, 2]", "expected": "3"}])

		result = run_tests(
			source_code="def add(a, b):\n\tprint('debug', a, b)\n\treturn a + b",
			function_name="add",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Accepted")
		self.assertIn("debug", result.get("stdout", ""))

	def test_traceback_included_on_error(self):
		"""Per-test errors should include a traceback in details."""
		test_cases = make_test_cases([{"input": "[1, 2]", "expected": "3"}])

		result = run_tests(
			source_code="def add(a, b):\n\traise ValueError('oops')",
			function_name="add",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Wrong Answer")
		details = result.get("details", [])
		self.assertTrue(len(details) > 0)
		self.assertIn("traceback", details[0])
		self.assertIn("ValueError", details[0]["traceback"])

	def test_timeout(self):
		"""Infinite loop should get Time Limit Exceeded."""
		test_cases = make_test_cases([{"input": "[1, 2]", "expected": "3"}])

		result = run_tests(
			source_code="def add(a, b):\n\twhile True:\n\t\tpass",
			function_name="add",
			test_cases=test_cases,
			time_limit=1.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Time Limit Exceeded")

	def test_no_test_cases(self):
		"""Empty test case list should return Internal Error."""
		result = run_tests(
			source_code="def add(a, b):\n\treturn a + b",
			function_name="add",
			test_cases=[],
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Internal Error")

	def test_list_return_value(self):
		"""Judge should correctly compare list return values."""
		test_cases = make_test_cases([{"input": "[[2, 7, 11, 15], 9]", "expected": "[0, 1]"}])

		result = run_tests(
			source_code="def two_sum(nums, target):\n\tfor i in range(len(nums)):\n\t\tfor j in range(i+1, len(nums)):\n\t\t\tif nums[i] + nums[j] == target:\n\t\t\t\treturn [i, j]",
			function_name="two_sum",
			test_cases=test_cases,
			time_limit=5.0,
			memory_limit_mb=256,
		)

		self.assertEqual(result["verdict"], "Accepted")
		self.assertEqual(result["passed_tests"], 1)
