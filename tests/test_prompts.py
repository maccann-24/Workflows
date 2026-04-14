"""Unit tests for prompts.py — Morning Briefing Orchestrator prompt constants.

Tests verify that the exported prompt strings contain the required routing
categories, guardrails, error handling rules, and few-shot example structure
defined in Workflow Build Specs Section 6.
"""

from prompts import (
    FEW_SHOT_EXAMPLE_INPUT,
    FEW_SHOT_EXAMPLE_OUTPUT,
    SYNTHETIC_INPUT,
    SYSTEM_PROMPT,
)


# ---------------------------------------------------------------------------
# SYSTEM_PROMPT
# ---------------------------------------------------------------------------


def test_system_prompt_not_empty():
    """SYSTEM_PROMPT must be a non-empty string."""
    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT.strip()) > 0


def test_system_prompt_contains_routing_rules():
    """SYSTEM_PROMPT must mention all 5 routing categories by name."""
    for category in ("EXPENSES", "HIRES", "PROJECTS", "INBOX", "RESEARCH"):
        assert category in SYSTEM_PROMPT, (
            f"Routing category '{category}' not found in SYSTEM_PROMPT"
        )


def test_system_prompt_contains_guardrails():
    """SYSTEM_PROMPT must describe how to handle missing data."""
    assert "MISSING" in SYSTEM_PROMPT, (
        "SYSTEM_PROMPT does not mention 'MISSING' handling guardrail"
    )


def test_system_prompt_contains_error_handling():
    """SYSTEM_PROMPT must describe the invalid-input response."""
    assert "Invalid input" in SYSTEM_PROMPT or "invalid input" in SYSTEM_PROMPT.lower(), (
        "SYSTEM_PROMPT does not mention invalid input response"
    )


# ---------------------------------------------------------------------------
# FEW_SHOT_EXAMPLE_INPUT
# ---------------------------------------------------------------------------


def test_few_shot_example_input_not_empty():
    """FEW_SHOT_EXAMPLE_INPUT must be a non-empty string."""
    assert isinstance(FEW_SHOT_EXAMPLE_INPUT, str)
    assert len(FEW_SHOT_EXAMPLE_INPUT.strip()) > 0


# ---------------------------------------------------------------------------
# FEW_SHOT_EXAMPLE_OUTPUT
# ---------------------------------------------------------------------------


def test_few_shot_example_output_contains_sections():
    """FEW_SHOT_EXAMPLE_OUTPUT must contain all 5 section headers."""
    for header in ("EXPENSES", "HIRES", "PROJECTS", "INBOX", "RESEARCH"):
        assert header in FEW_SHOT_EXAMPLE_OUTPUT, (
            f"Section header '{header}' not found in FEW_SHOT_EXAMPLE_OUTPUT"
        )


# ---------------------------------------------------------------------------
# SYNTHETIC_INPUT
# ---------------------------------------------------------------------------


def test_synthetic_input_not_empty():
    """SYNTHETIC_INPUT must be a non-empty string."""
    assert isinstance(SYNTHETIC_INPUT, str)
    assert len(SYNTHETIC_INPUT.strip()) > 0


def test_synthetic_input_contains_multiple_items():
    """SYNTHETIC_INPUT must include items from at least 3 different categories.

    The demo input in the build spec contains receipts (EXPENSES), a new hire
    (HIRES), a project update (PROJECTS), emails (INBOX), and a research ask
    (RESEARCH).  We verify that at least 3 distinguishable category signals
    are present so the orchestrator has meaningful routing work to do.
    """
    category_signals = {
        "EXPENSES": ["receipt", "Receipt"],
        "HIRES": ["new hire", "New hire", "Role:"],
        "PROJECTS": ["project", "Project", "Budget", "Schedule"],
        "INBOX": ["Email", "email", "From:"],
        "RESEARCH": ["Research", "research", "company"],
    }

    matched_categories = []
    for category, keywords in category_signals.items():
        if any(kw in SYNTHETIC_INPUT for kw in keywords):
            matched_categories.append(category)

    assert len(matched_categories) >= 3, (
        f"SYNTHETIC_INPUT only matched {len(matched_categories)} categories "
        f"({matched_categories}); expected at least 3"
    )
