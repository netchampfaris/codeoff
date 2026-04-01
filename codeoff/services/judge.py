# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
Judge module: orchestrates submission judging via background jobs.
"""

import frappe

from codeoff.services.sandbox import run_tests


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
