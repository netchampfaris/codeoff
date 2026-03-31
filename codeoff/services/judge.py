# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
Judge module: executes Python submissions in isolated subprocesses.
"""

import json
import os
import resource
import subprocess
import sys
import tempfile
import time

import frappe


def judge_submission(submission_id):
	"""Background job entry point. Runs the submission against all hidden test cases."""
	submission = frappe.get_doc("Codeoff Submission", submission_id)
	problem = frappe.get_doc("Codeoff Problem", submission.problem)

	submission.status = "Running"
	submission.save(ignore_permissions=True)
	frappe.db.commit()

	test_cases = [tc for tc in problem.test_cases if tc.is_active]
	results = run_tests(
		source_code=submission.source_code,
		function_name=problem.function_name,
		test_cases=test_cases,
		time_limit=problem.time_limit_seconds,
		memory_limit_mb=problem.memory_limit_mb,
	)

	submission.reload()
	submission.status = "Completed"
	submission.passed_tests = results["passed_tests"]
	submission.total_tests = results["total_tests"]
	submission.score = results["passed_tests"]
	submission.runtime_ms = results["runtime_ms"]
	submission.verdict = results["verdict"]
	submission.judge_response = frappe.as_json(results)
	submission.save(ignore_permissions=True)
	frappe.db.commit()

	# Process the verdict (winner determination, bracket advancement)
	from codeoff.services.match_engine import process_verdict

	process_verdict(submission_id)


def run_sample_tests(source_code, problem_name):
	"""Run code against only sample test cases. Returns results directly (ephemeral)."""
	problem = frappe.get_doc("Codeoff Problem", problem_name)
	sample_cases = [tc for tc in problem.test_cases if tc.visibility == "Sample" and tc.is_active]

	return run_tests(
		source_code=source_code,
		function_name=problem.function_name,
		test_cases=sample_cases,
		time_limit=problem.time_limit_seconds,
		memory_limit_mb=problem.memory_limit_mb,
	)


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

	# compile() with a friendly filename so all tracebacks reference "<your code>"
	# and line numbers are 1-based within the user's own code.
	runner = f"""
import json
import sys
import io
import traceback as _tb

_src = {source_code!r}
try:
    exec(compile(_src, "<your code>", "exec"), globals())
except SyntaxError as _e:
    print(json.dumps({{"passed": 0, "total": {len(test_cases)}, "details": [], "error": "SyntaxError on line " + str(_e.lineno) + ": " + str(_e.msg)}}))
    sys.exit(0)

def _run_tests():
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
                actual = {function_name}(*args)
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
