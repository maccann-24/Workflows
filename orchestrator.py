"""
Morning Briefing Orchestrator

Dual-mode Claude wrapper that routes a mixed morning queue through the
Morning Briefing Orchestrator prompt and returns a structured briefing.

Modes:
  1. Anthropic SDK  — used when ANTHROPIC_API_KEY is set in the environment
  2. Claude CLI      — fallback for Pro Max plan users (no API key needed)

Usage:
  python orchestrator.py              # runs with the synthetic demo input
  python orchestrator.py --sdk        # force SDK mode (requires API key)
  python orchestrator.py --cli        # force CLI mode
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from prompts import (
    FEW_SHOT_EXAMPLE_INPUT,
    FEW_SHOT_EXAMPLE_OUTPUT,
    SYNTHETIC_INPUT,
    SYSTEM_PROMPT,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL: str = "claude-sonnet-4-6"

# Sonnet pricing (per 1M tokens)
INPUT_COST_PER_MILLION: float = 3.0
OUTPUT_COST_PER_MILLION: float = 15.0

# Rough chars-per-token ratio for cost estimation
CHARS_PER_TOKEN: int = 4

MAX_RETRIES: int = 2  # total attempts = 1 initial + 1 retry


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class OrchestratorResult:
    """Holds the orchestrator response plus telemetry."""

    output: str
    latency_ms: float
    estimated_cost_usd: float
    model: str
    timestamp: str


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------

def _build_user_prompt(morning_queue: str) -> str:
    """Assemble the full user-facing prompt with few-shot example and queue.

    The system prompt is passed separately when using the SDK. For the CLI
    path, the system prompt is prepended here so everything travels as a
    single string.
    """
    return (
        "Here is a few-shot example of the expected input and output format:\n\n"
        "--- EXAMPLE INPUT ---\n"
        f"{FEW_SHOT_EXAMPLE_INPUT.strip()}\n\n"
        "--- EXAMPLE OUTPUT ---\n"
        f"{FEW_SHOT_EXAMPLE_OUTPUT.strip()}\n\n"
        "--- END EXAMPLE ---\n\n"
        "Now process the following morning queue:\n\n"
        f"{morning_queue.strip()}"
    )


def _build_cli_prompt(morning_queue: str) -> str:
    """Build a single prompt string for the CLI that includes system context."""
    user_prompt = _build_user_prompt(morning_queue)
    return (
        f"{SYSTEM_PROMPT.strip()}\n\n"
        f"{user_prompt}"
    )


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

def _estimate_cost(input_text: str, output_text: str) -> float:
    """Estimate USD cost based on character-level token approximation.

    This is a rough estimate. Actual token counts depend on the tokenizer.
    """
    input_tokens = len(input_text) / CHARS_PER_TOKEN
    output_tokens = len(output_text) / CHARS_PER_TOKEN
    cost = (
        (input_tokens / 1_000_000) * INPUT_COST_PER_MILLION
        + (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
    )
    return round(cost, 6)


# ---------------------------------------------------------------------------
# SDK mode
# ---------------------------------------------------------------------------

def _run_sdk(morning_queue: str) -> OrchestratorResult:
    """Call Claude via the Anthropic Python SDK."""
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError(
            "Anthropic SDK not installed. Install with: pip install anthropic"
        ) from exc

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    user_prompt = _build_user_prompt(morning_queue)

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            start = time.monotonic()
            message = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT.strip(),
                messages=[{"role": "user", "content": user_prompt}],
            )
            elapsed_ms = (time.monotonic() - start) * 1000

            output = message.content[0].text
            cost = _estimate_cost(
                SYSTEM_PROMPT + user_prompt,
                output,
            )

            return OrchestratorResult(
                output=output,
                latency_ms=round(elapsed_ms, 1),
                estimated_cost_usd=cost,
                model=MODEL,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                print(f"[SDK] Attempt {attempt + 1} failed: {exc}. Retrying...", file=sys.stderr)

    raise RuntimeError(f"SDK mode failed after {MAX_RETRIES} attempts: {last_error}")


# ---------------------------------------------------------------------------
# CLI mode
# ---------------------------------------------------------------------------

def _run_cli(morning_queue: str) -> OrchestratorResult:
    """Call Claude via the `claude` CLI subprocess."""
    full_prompt = _build_cli_prompt(morning_queue)

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            start = time.monotonic()
            result = subprocess.run(
                ["claude", "-p", full_prompt],
                capture_output=True,
                text=True,
                timeout=120,
            )
            elapsed_ms = (time.monotonic() - start) * 1000

            if result.returncode != 0:
                stderr_msg = result.stderr.strip() if result.stderr else "unknown error"
                raise RuntimeError(f"claude CLI exited with code {result.returncode}: {stderr_msg}")

            output = result.stdout.strip()
            if not output:
                raise RuntimeError("claude CLI returned empty output")

            cost = _estimate_cost(full_prompt, output)

            return OrchestratorResult(
                output=output,
                latency_ms=round(elapsed_ms, 1),
                estimated_cost_usd=cost,
                model=f"{MODEL} (via CLI)",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except subprocess.TimeoutExpired as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                print(f"[CLI] Attempt {attempt + 1} timed out. Retrying...", file=sys.stderr)
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                print(f"[CLI] Attempt {attempt + 1} failed: {exc}. Retrying...", file=sys.stderr)

    raise RuntimeError(f"CLI mode failed after {MAX_RETRIES} attempts: {last_error}")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_orchestrator(
    morning_queue: str,
    *,
    force_mode: str | None = None,
) -> OrchestratorResult:
    """Run the Morning Briefing Orchestrator against a morning queue input.

    Primary mode: Anthropic SDK (if ANTHROPIC_API_KEY is set)
    Fallback mode: claude CLI (Pro Max plan, no API key needed)

    Args:
        morning_queue: The raw morning queue text to process.
        force_mode: Optional override — "sdk" or "cli" to skip auto-detection.

    Returns:
        OrchestratorResult with output, latency, cost estimate, and metadata.

    Raises:
        RuntimeError: If both modes fail or the forced mode fails.
    """
    if not morning_queue or not morning_queue.strip():
        raise ValueError("morning_queue must be a non-empty string")

    # Determine which mode to use
    use_sdk: bool
    if force_mode == "sdk":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("--sdk flag requires ANTHROPIC_API_KEY to be set")
        use_sdk = True
    elif force_mode == "cli":
        use_sdk = False
    else:
        # Auto-detect: prefer SDK when API key is available
        use_sdk = bool(os.environ.get("ANTHROPIC_API_KEY"))

    if use_sdk:
        print("[orchestrator] Using Anthropic SDK mode", file=sys.stderr)
        return _run_sdk(morning_queue)
    else:
        print("[orchestrator] Using Claude CLI mode", file=sys.stderr)
        return _run_cli(morning_queue)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the orchestrator with the synthetic demo input and print results."""
    # Parse optional flags
    force_mode: str | None = None
    if "--sdk" in sys.argv:
        force_mode = "sdk"
    elif "--cli" in sys.argv:
        force_mode = "cli"

    print("=" * 72)
    print("Morning Briefing Orchestrator")
    print("=" * 72)
    print()

    try:
        result = run_orchestrator(SYNTHETIC_INPUT, force_mode=force_mode)
    except (RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # Print the briefing output
    print(result.output)
    print()

    # Print telemetry
    print("-" * 72)
    print(f"Model:          {result.model}")
    print(f"Latency:        {result.latency_ms:,.1f} ms")
    print(f"Est. cost:      ${result.estimated_cost_usd:.6f}")
    print(f"Timestamp:      {result.timestamp}")
    print("-" * 72)


if __name__ == "__main__":
    main()
