"""
evals.py — Morning Briefing Orchestrator eval harness

Loads test_inputs.json, calls run_orchestrator() from orchestrator.py,
scores each run across 4 dimensions, and writes a timestamped JSON result file.

Usage:
    python evals.py
"""

import json
import os
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from tabulate import tabulate

# ---------------------------------------------------------------------------
# Import the orchestrator under test
# ---------------------------------------------------------------------------
try:
    from orchestrator import run_orchestrator
except ImportError as e:
    print(f"ERROR: Could not import run_orchestrator from orchestrator.py: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TESTS_FILE = Path(__file__).parent / "test_inputs.json"
RESULTS_DIR = Path(__file__).parent / "evals" / "results"
PASS_THRESHOLD = 0.85
RATE_LIMIT_DELAY_S = 2  # seconds between calls (Pro Max courtesy delay)

# Fixed section order as specified in the system prompt
SECTION_ORDER = ["EXPENSES", "HIRES", "PROJECTS", "INBOX", "RESEARCH"]

# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------


def _parse_queue_summary_counts(output: str) -> dict[str, int]:
    """
    Parse the queue summary line into per-section counts.

    The spec format is:
        Queue: N items routed (X expenses, Y hire[s], Z project[s], W email[s], V research)

    Returns a dict with the same SECTION_ORDER keys where present.
    """
    # Normalise to lower-case for matching
    lower = output.lower()

    # Pull out the parenthesised portion from the queue summary line
    queue_match = re.search(r"queue:\s*\d+\s*items?\s*routed\s*\(([^)]+)\)", lower)
    if not queue_match:
        return {}

    body = queue_match.group(1)  # e.g. "2 expenses, 1 hire, 1 project, 2 emails, 1 research"

    mapping = {
        "EXPENSES": re.search(r"(\d+)\s+expense", body),
        "HIRES": re.search(r"(\d+)\s+hire", body),
        "PROJECTS": re.search(r"(\d+)\s+project", body),
        "INBOX": re.search(r"(\d+)\s+email", body),
        "RESEARCH": re.search(r"(\d+)\s+research", body),
    }

    result = {}
    for section, match in mapping.items():
        if match:
            result[section] = int(match.group(1))
    return result


def _count_input_items(input_text: str) -> int:
    """
    Count numbered items in the input queue (lines that start with a digit followed
    by a period or closing parenthesis, e.g. '1.' or '1)').
    """
    matches = re.findall(r"^\s*\d+[\.\)]\s+\S", input_text, re.MULTILINE)
    return len(matches)


def score_routing_accuracy(output: str, expected_routing: dict) -> float:
    """
    Compare parsed section counts in the output against expected_routing.

    Score = number of sections where count matches / total expected sections.
    If expected_routing is empty (error cases), return 1.0 only if there are
    no sections at all in the output (i.e., the output is an error message).
    """
    if not expected_routing:
        # Error case: output should NOT contain any section headers or routing
        has_sections = bool(
            re.search(r"^(EXPENSES|HIRES|PROJECTS|INBOX|RESEARCH)\s*$", output, re.MULTILINE)
        )
        return 0.0 if has_sections else 1.0

    parsed = _parse_queue_summary_counts(output)
    if not parsed:
        return 0.0

    total = len(expected_routing)
    correct = 0
    for section, expected_count in expected_routing.items():
        actual = parsed.get(section, 0)
        if actual == expected_count:
            correct += 1
    return correct / total if total > 0 else 1.0


def score_format_compliance(output: str, expected_routing: dict) -> float:
    """
    3 checks:
    1. Output starts with "MORNING BRIEFING —" header (no preamble) — unless error case
    2. Sections present in output appear in fixed order (EXPENSES < HIRES < PROJECTS < INBOX < RESEARCH)
    3. Sections NOT in expected_routing are absent from output (no empty sections)
    """
    # Error case: both valid outcomes are an error message, so format check is just
    # that output does NOT start with a MORNING BRIEFING header
    if not expected_routing:
        starts_correctly = not re.search(
            r"MORNING BRIEFING", output, re.IGNORECASE
        )
        return 1.0 if starts_correctly else 0.0

    checks_passed = 0
    total_checks = 3

    # Check 1: starts with MORNING BRIEFING header (first non-empty line)
    first_content_line = next(
        (line.strip() for line in output.splitlines() if line.strip()), ""
    )
    if re.match(r"MORNING BRIEFING\s*[—-]", first_content_line, re.IGNORECASE):
        checks_passed += 1

    # Check 2: sections present in output appear in fixed order
    section_positions = {}
    for section in SECTION_ORDER:
        match = re.search(rf"^{section}\s*$", output, re.MULTILINE)
        if match:
            section_positions[section] = match.start()

    found_sections = [s for s in SECTION_ORDER if s in section_positions]
    positions_in_order = [section_positions[s] for s in found_sections]
    if positions_in_order == sorted(positions_in_order):
        checks_passed += 1

    # Check 3: sections NOT in expected_routing must be absent
    unexpected_sections_present = 0
    for section in SECTION_ORDER:
        if section not in expected_routing:
            # Should not appear as a standalone section header
            if re.search(rf"^{section}\s*$", output, re.MULTILINE):
                unexpected_sections_present += 1
    if unexpected_sections_present == 0:
        checks_passed += 1

    return checks_passed / total_checks


def score_guardrail_accuracy(output: str, expected_guardrails: list, expected_routing: dict) -> float:
    """
    For inputs WITH expected_guardrails: verify that "MISSING" markers appear in output.
    For inputs WITHOUT expected_guardrails: verify that no "MISSING" markers appear in output.

    Error cases (empty expected_routing): check that the full error message is returned.
    """
    if not expected_routing:
        # Error cases — check for invalid-input message
        has_error_msg = bool(
            re.search(r"invalid input", output, re.IGNORECASE)
        )
        return 1.0 if has_error_msg else 0.0

    if expected_guardrails:
        # At least one MISSING marker is expected
        missing_count = len(re.findall(r"MISSING", output, re.IGNORECASE))
        return 1.0 if missing_count >= len(expected_guardrails) else 0.0
    else:
        # No guardrails expected — no MISSING markers should appear
        missing_count = len(re.findall(r"MISSING", output, re.IGNORECASE))
        return 1.0 if missing_count == 0 else 0.0


def score_completeness(output: str, input_text: str, expected_routing: dict) -> float:
    """
    Count numbered items in the input queue and verify the queue summary
    line reports the same total count.
    """
    if not expected_routing:
        # Error cases — completeness is satisfied when output is brief (no partial content)
        # Count that output is short enough to be just an error message
        word_count = len(output.split())
        return 1.0 if word_count <= 25 else 0.0

    input_item_count = _count_input_items(input_text)
    if input_item_count == 0:
        return 1.0  # Nothing to count

    # Parse the queue summary total
    lower = output.lower()
    summary_match = re.search(r"queue:\s*(\d+)\s*items?\s*routed", lower)
    if not summary_match:
        return 0.0

    reported_total = int(summary_match.group(1))
    return 1.0 if reported_total == input_item_count else 0.0


# ---------------------------------------------------------------------------
# Per-test runner
# ---------------------------------------------------------------------------


def run_single_eval(test_case: dict) -> dict:
    """
    Run one test case. Returns a result dict with all scores and metadata.
    """
    test_id = test_case["id"]
    category = test_case["category"]
    input_text = test_case["input"]
    expected_routing = test_case.get("expected_routing", {})
    expected_guardrails = test_case.get("expected_guardrails", [])
    notes = test_case.get("notes", "")

    result = {
        "id": test_id,
        "category": category,
        "notes": notes,
        "scores": {
            "routing_accuracy": 0.0,
            "format_compliance": 0.0,
            "guardrail_accuracy": 0.0,
            "completeness": 0.0,
            "aggregate": 0.0,
        },
        "output_preview": "",
        "estimated_cost_usd": 0.0,
        "latency_s": 0.0,
        "error": None,
    }

    try:
        t_start = time.monotonic()
        orchestrator_result = run_orchestrator(input_text)
        t_end = time.monotonic()

        latency = round(t_end - t_start, 3)
        result["latency_s"] = latency

        output = orchestrator_result.output
        result["estimated_cost_usd"] = orchestrator_result.estimated_cost_usd
        result["output_preview"] = output[:500] + ("..." if len(output) > 500 else "")

        # Score
        routing = score_routing_accuracy(output, expected_routing)
        fmt = score_format_compliance(output, expected_routing)
        guardrail = score_guardrail_accuracy(output, expected_guardrails, expected_routing)
        completeness = score_completeness(output, input_text, expected_routing)
        aggregate = round((routing + fmt + guardrail + completeness) / 4, 4)

        result["scores"] = {
            "routing_accuracy": round(routing, 4),
            "format_compliance": round(fmt, 4),
            "guardrail_accuracy": round(guardrail, 4),
            "completeness": round(completeness, 4),
            "aggregate": aggregate,
        }

    except ValueError:
        # Orchestrator rejects empty/invalid input at the Python level (before
        # calling Claude). For error-category test cases this is correct behavior
        # — the system rejected bad input. Score as a successful error rejection.
        if not expected_routing:
            result["scores"] = {
                "routing_accuracy": 1.0,
                "format_compliance": 1.0,
                "guardrail_accuracy": 1.0,
                "completeness": 1.0,
                "aggregate": 1.0,
            }
            result["output_preview"] = "[ValueError — input rejected by orchestrator guard]"
        else:
            result["error"] = f"ValueError on non-error test case: {traceback.format_exc()}"

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
        # Scores remain 0.0

    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _percentile(sorted_values: list[float], pct: float) -> float:
    """Return the pct-th percentile (0–100) of a pre-sorted list."""
    if not sorted_values:
        return 0.0
    idx = (pct / 100) * (len(sorted_values) - 1)
    lower_idx = int(idx)
    upper_idx = min(lower_idx + 1, len(sorted_values) - 1)
    frac = idx - lower_idx
    return round(
        sorted_values[lower_idx] * (1 - frac) + sorted_values[upper_idx] * frac, 3
    )


def build_summary_table(results: list[dict]) -> tuple[list, list, dict]:
    """
    Returns (headers, rows, summary_stats) for tabulate.
    """
    dims = ["routing_accuracy", "format_compliance", "guardrail_accuracy", "completeness"]

    # Per-dimension means
    dim_means = {}
    for d in dims:
        vals = [r["scores"][d] for r in results]
        dim_means[d] = round(sum(vals) / len(vals), 4) if vals else 0.0

    overall_mean = round(sum(dim_means.values()) / len(dim_means), 4)

    # Cost
    costs = [r["estimated_cost_usd"] for r in results]
    mean_cost = round(sum(costs) / len(costs), 6) if costs else 0.0
    total_cost = round(sum(costs), 6)

    # Latency
    latencies = sorted([r["latency_s"] for r in results])
    mean_latency = round(sum(latencies) / len(latencies), 3) if latencies else 0.0
    p50 = _percentile(latencies, 50)
    p95 = _percentile(latencies, 95)
    p99 = _percentile(latencies, 99)

    errors = [r for r in results if r["error"]]

    summary_stats = {
        "total_tests": len(results),
        "errors": len(errors),
        "dim_means": dim_means,
        "overall_mean": overall_mean,
        "mean_cost_usd": mean_cost,
        "total_cost_usd": total_cost,
        "latency": {
            "mean_s": mean_latency,
            "p50_s": p50,
            "p95_s": p95,
            "p99_s": p99,
        },
    }

    # Build the terminal table
    headers = ["Dimension", "Mean Score", "Pass (≥0.85)"]
    rows = []
    for d in dims:
        score = dim_means[d]
        passed = "PASS" if score >= PASS_THRESHOLD else "FAIL"
        rows.append([d.replace("_", " ").title(), f"{score:.4f}", passed])

    rows.append(["---", "---", "---"])
    overall_pass = "PASS" if overall_mean >= PASS_THRESHOLD else "FAIL"
    rows.append(["OVERALL", f"{overall_mean:.4f}", overall_pass])

    rows.append(["---", "---", "---"])
    rows.append(["Mean cost (USD)", f"${mean_cost:.6f}", ""])
    rows.append(["Total cost (USD)", f"${total_cost:.6f}", ""])
    rows.append(["Latency mean (s)", f"{mean_latency:.3f}", ""])
    rows.append(["Latency p50 (s)", f"{p50:.3f}", ""])
    rows.append(["Latency p95 (s)", f"{p95:.3f}", ""])
    rows.append(["Latency p99 (s)", f"{p99:.3f}", ""])
    rows.append(["Errors", str(len(errors)), ""])
    rows.append(["Total tests", str(len(results)), ""])

    return headers, rows, summary_stats


def write_results_json(results: list[dict], summary_stats: dict) -> Path:
    """Write detailed results to evals/results/eval_run_{timestamp}.json."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"eval_run_{timestamp}.json"

    payload = {
        "run_timestamp": timestamp,
        "summary": summary_stats,
        "results": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return output_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    # Load test inputs
    if not TESTS_FILE.exists():
        print(f"ERROR: {TESTS_FILE} not found.")
        sys.exit(1)

    with open(TESTS_FILE, encoding="utf-8") as f:
        test_cases = json.load(f)

    total = len(test_cases)
    print(f"\nMorning Briefing Orchestrator — Eval Harness")
    print(f"Running {total} test cases with {RATE_LIMIT_DELAY_S}s delay between calls\n")

    results = []
    for i, tc in enumerate(test_cases, start=1):
        test_id = tc.get("id", f"test_{i}")
        print(f"  [{i:02d}/{total}] {test_id} ... ", end="", flush=True)

        result = run_single_eval(tc)
        results.append(result)

        agg = result["scores"]["aggregate"]
        err_flag = " [ERROR]" if result["error"] else ""
        print(f"aggregate={agg:.2f}{err_flag}")

        # Rate-limit delay (skip after last test)
        if i < total:
            time.sleep(RATE_LIMIT_DELAY_S)

    # Build and print summary table
    headers, rows, summary_stats = build_summary_table(results)
    print("\n" + "=" * 60)
    print("EVAL SUMMARY")
    print("=" * 60)
    print(tabulate(rows, headers=headers, tablefmt="simple"))

    # Print failed tests if any
    failed = [r for r in results if r["scores"]["aggregate"] < PASS_THRESHOLD]
    if failed:
        print(f"\nFailed tests ({len(failed)}):")
        for r in failed:
            scores = r["scores"]
            print(
                f"  {r['id']:20s}  routing={scores['routing_accuracy']:.2f}  "
                f"format={scores['format_compliance']:.2f}  "
                f"guardrail={scores['guardrail_accuracy']:.2f}  "
                f"completeness={scores['completeness']:.2f}"
            )
            if r["error"]:
                # Print first line of error only to keep output clean
                first_line = r["error"].splitlines()[0]
                print(f"    Error: {first_line}")

    # Write detailed JSON
    output_path = write_results_json(results, summary_stats)
    print(f"\nDetailed results written to: {output_path}\n")


if __name__ == "__main__":
    main()
