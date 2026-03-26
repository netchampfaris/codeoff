"""
Load coding problems into the database.

Workflow for deployed sites (problems/ folder is gitignored):

  1. Locally — generate a self-contained seed file from the markdown files:
       bench --site <local-site> execute codeoff.load_problems.dump
     This writes  codeoff/problems_seed.json  (also gitignored).

  2. Copy the seed file to the server:
       scp codeoff/problems_seed.json user@server:/path/to/bench/apps/codeoff/codeoff/

  3. On the server — insert the problems:
       bench --site <site> execute codeoff.load_problems.run

Re-running run() is safe — existing slugs are skipped.
To replace a problem, delete it from the DB first and re-run.
"""

import json
import re
from pathlib import Path

import frappe

PROBLEMS_DIR = Path(__file__).parent.parent / "problems"


def _parse_frontmatter(text):
	match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
	if not match:
		return {}, text
	front = {}
	for line in match.group(1).splitlines():
		if ":" in line:
			key, _, val = line.partition(":")
			front[key.strip()] = val.strip().strip('"')
	return front, text[match.end() :]


def _extract_section(body, heading):
	"""Return content under a ## heading, up to the next ## heading or end."""
	pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
	m = re.search(pattern, body, re.DOTALL)
	return m.group(1).strip() if m else ""


def _extract_code_block(text):
	m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
	return m.group(1).strip() if m else ""


def _parse_test_table(table_text, visibility):
	cases = []
	for line in table_text.strip().splitlines():
		line = line.strip()
		# skip header, separator, and note lines
		if not line.startswith("|") or "---" in line or "`input_data`" in line or "# |" in line:
			continue
		parts = [p.strip() for p in line.strip("|").split("|")]
		if len(parts) < 3:
			continue
		cases.append(
			{
				"case_name": f"Case {parts[0].strip()}",
				"visibility": visibility,
				"input_data": parts[1].strip("`"),
				"expected_output": parts[2].strip("`"),
				"weight": 1,
				"is_active": 1,
			}
		)
	return cases


def _parse_problem(md_path):
	text = md_path.read_text()
	fm, body = _parse_frontmatter(text)

	# Statement: everything before "## Starter Code", minus the leading # Title line
	cut = re.search(r"\n## Starter Code\b", body)
	statement = body[: cut.start()].strip() if cut else body.strip()
	statement = re.sub(r"^#[^\n]*\n+", "", statement)

	starter_section = _extract_section(body, "Starter Code")
	starter_code = (
		_extract_code_block(starter_section)
		if starter_section
		else f"{fm.get('function_signature', '')}\n    pass"
	)

	test_cases_section = _extract_section(body, "Test Cases")
	test_cases = []
	sample_m = re.search(r"### Sample.*?\n(.*?)(?=\n### |\Z)", test_cases_section, re.DOTALL)
	hidden_m = re.search(r"### Hidden\n(.*?)(?=\n### |\Z)", test_cases_section, re.DOTALL)
	if sample_m:
		test_cases += _parse_test_table(sample_m.group(1), "Sample")
	if hidden_m:
		test_cases += _parse_test_table(hidden_m.group(1), "Hidden")

	return {
		"title": fm.get("title", md_path.stem),
		"slug": fm.get("slug", md_path.stem),
		"difficulty": fm.get("difficulty", "Easy"),
		"function_name": fm.get("function_name", ""),
		"function_signature": fm.get("function_signature", ""),
		"time_limit_seconds": float(fm.get("time_limit_seconds", 2.0)),
		"memory_limit_mb": int(fm.get("memory_limit_mb", 256)),
		"statement": statement,
		"starter_code": starter_code,
		"is_active": 1,
		"test_cases": test_cases,
	}


SEED_FILE = Path(__file__).parent / "problems_seed.json"


@frappe.whitelist()
def import_from_json(json_data: str):
	"""Insert problems from a JSON string. Restricted to System Managers."""
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Only System Managers can import problems.", frappe.PermissionError)

	try:
		problems = json.loads(json_data)
	except Exception:
		frappe.throw("Invalid JSON.")

	if not isinstance(problems, list):
		frappe.throw("Expected a JSON array of problems.")

	created = skipped = 0
	for data in problems:
		slug = data.get("slug")
		if not slug:
			continue
		if frappe.db.exists("Codeoff Problem", {"slug": slug}):
			skipped += 1
			continue
		doc = frappe.get_doc({"doctype": "Codeoff Problem", **data})
		doc.insert(ignore_permissions=True)
		created += 1

	frappe.db.commit()
	return {"created": created, "skipped": skipped}


def dump():
	"""Parse the local problems/ directory and write problems_seed.json."""
	if not PROBLEMS_DIR.exists():
		print(f"Problems directory not found: {PROBLEMS_DIR}")
		return

	md_files = sorted(PROBLEMS_DIR.rglob("*.md"))
	print(f"Parsing {len(md_files)} problem file(s)...")

	problems = [_parse_problem(p) for p in md_files]
	SEED_FILE.write_text(json.dumps(problems, indent=2))
	print(f"Written {len(problems)} problems to {SEED_FILE}")


def run():
	"""Insert problems into the database from problems/ or problems_seed.json."""
	if PROBLEMS_DIR.exists():
		md_files = sorted(PROBLEMS_DIR.rglob("*.md"))
		print(f"Loading from problems/ ({len(md_files)} files)\n")
		problems = [_parse_problem(p) for p in md_files]
	elif SEED_FILE.exists():
		print(f"Loading from {SEED_FILE}\n")
		problems = json.loads(SEED_FILE.read_text())
	else:
		print(
			"No problems source found. Either place the problems/ folder next to this file, "
			"or copy problems_seed.json here (generated with load_problems.dump)."
		)
		return

	created = skipped = 0
	for data in problems:
		slug = data["slug"]
		if frappe.db.exists("Codeoff Problem", {"slug": slug}):
			print(f"  SKIP  {data['title']} (slug '{slug}' already exists)")
			skipped += 1
			continue
		doc = frappe.get_doc({"doctype": "Codeoff Problem", **data})
		doc.insert(ignore_permissions=True)
		print(f"  OK    {data['title']}  ({len(data['test_cases'])} test cases)")
		created += 1

	frappe.db.commit()
	print(f"\nDone — created {created}, skipped {skipped}.")
