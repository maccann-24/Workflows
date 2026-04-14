"""Unit tests for orchestrator.py — Morning Briefing Orchestrator runtime.

All Claude API and CLI calls are mocked. No real API calls are made.
Tests cover cost estimation, latency tracking, dual-mode dispatch (SDK vs CLI),
retry logic, and the OrchestratorResult dataclass contract.
"""

import os
import sys
import time
import types
from dataclasses import fields
from unittest.mock import MagicMock, patch

import pytest

from orchestrator import OrchestratorResult, run_orchestrator, _estimate_cost


# ---------------------------------------------------------------------------
# Helper: create a mock anthropic module for sys.modules patching
# ---------------------------------------------------------------------------

def _make_mock_anthropic(mock_client):
    """Build a mock 'anthropic' module that returns the given mock client."""
    mock_mod = types.ModuleType("anthropic")
    mock_mod.Anthropic = MagicMock(return_value=mock_client)
    return mock_mod


def _make_mock_client(response_text="MORNING BRIEFING — test", side_effect=None):
    """Build a mock Anthropic client with messages.create configured."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]

    mock_client = MagicMock()
    if side_effect:
        mock_client.messages.create.side_effect = side_effect
    else:
        mock_client.messages.create.return_value = mock_message
    return mock_client


# ---------------------------------------------------------------------------
# Cost estimation (character-based)
# ---------------------------------------------------------------------------


def test_cost_estimation():
    """Verify _estimate_cost follows Sonnet pricing with char-based token approximation.

    Sonnet pricing: $3/1M input tokens, $15/1M output tokens.
    Token approximation: len(text) / 4.

    For input_text of 4000 chars (≈1000 tokens) and output_text of 2000 chars (≈500 tokens):
        cost = (1000 / 1_000_000) * 3 + (500 / 1_000_000) * 15
             = 0.003 + 0.0075
             = 0.0105
    """
    input_text = "x" * 4000   # ≈ 1000 tokens at 4 chars/token
    output_text = "y" * 2000  # ≈ 500 tokens at 4 chars/token

    cost = _estimate_cost(input_text, output_text)

    assert isinstance(cost, float)
    assert abs(cost - 0.0105) < 1e-6


# ---------------------------------------------------------------------------
# Latency tracking
# ---------------------------------------------------------------------------


def test_latency_tracking():
    """Verify latency_ms is recorded and roughly correct."""
    mock_client = _make_mock_client("MORNING BRIEFING — latency test")

    def slow_create(**kwargs):
        time.sleep(0.05)  # 50 ms
        return mock_client.messages.create.return_value

    mock_client.messages.create.side_effect = slow_create
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="MORNING BRIEFING — latency test")]
    )
    mock_mod = _make_mock_anthropic(mock_client)

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"}):
        with patch.dict(sys.modules, {"anthropic": mock_mod}):
            result = run_orchestrator("Receipt: Test, Apr 1, $5, coffee")

    assert isinstance(result.latency_ms, float)
    assert result.latency_ms >= 40.0, f"Expected >= 40ms, got {result.latency_ms}ms"
    assert result.latency_ms < 5000.0


# ---------------------------------------------------------------------------
# OrchestratorResult dataclass contract
# ---------------------------------------------------------------------------


def test_result_dataclass():
    """OrchestratorResult must have the expected fields with correct types."""
    expected_fields = {
        "output": str,
        "latency_ms": float,
        "estimated_cost_usd": float,
        "model": str,
        "timestamp": str,
    }

    actual_fields = {f.name: f.type for f in fields(OrchestratorResult)}

    for field_name, field_type in expected_fields.items():
        assert field_name in actual_fields, (
            f"OrchestratorResult is missing field '{field_name}'"
        )


# ---------------------------------------------------------------------------
# Dispatch mode: CLI when no API key
# ---------------------------------------------------------------------------


def test_cli_mode_used_when_no_api_key():
    """With no ANTHROPIC_API_KEY, the orchestrator should use subprocess."""
    mock_completed = MagicMock()
    mock_completed.stdout = "MORNING BRIEFING — CLI fallback"
    mock_completed.returncode = 0

    env_without_key = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}

    with patch.dict(os.environ, env_without_key, clear=True):
        with patch("orchestrator.subprocess.run", return_value=mock_completed) as mock_run:
            result = run_orchestrator("Receipt: Test, Apr 1, $5, coffee")

    mock_run.assert_called_once()
    assert isinstance(result, OrchestratorResult)
    assert "MORNING BRIEFING" in result.output


# ---------------------------------------------------------------------------
# Dispatch mode: SDK when API key is set
# ---------------------------------------------------------------------------


def test_sdk_mode_used_when_api_key_set():
    """With ANTHROPIC_API_KEY set, the orchestrator should use the anthropic SDK."""
    response_text = "MORNING BRIEFING — SDK mode"
    mock_client = _make_mock_client(response_text)
    mock_mod = _make_mock_anthropic(mock_client)

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"}):
        with patch.dict(sys.modules, {"anthropic": mock_mod}):
            result = run_orchestrator("Receipt: Test, Apr 1, $5, coffee")

    mock_mod.Anthropic.assert_called_once()
    mock_client.messages.create.assert_called_once()
    assert result.output == response_text


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------


def test_retry_on_failure():
    """First call fails, second succeeds — retry should work."""
    success_msg = MagicMock()
    success_msg.content = [MagicMock(text="MORNING BRIEFING — retry success")]

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [
        Exception("Transient error"),
        success_msg,
    ]
    mock_mod = _make_mock_anthropic(mock_client)

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"}):
        with patch.dict(sys.modules, {"anthropic": mock_mod}):
            result = run_orchestrator("Receipt: Test, Apr 1, $5, coffee")

    assert mock_client.messages.create.call_count == 2
    assert result.output == "MORNING BRIEFING — retry success"


# ---------------------------------------------------------------------------
# Persistent failure raises RuntimeError
# ---------------------------------------------------------------------------


def test_error_on_persistent_failure():
    """Two consecutive failures should raise RuntimeError."""
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [
        Exception("First failure"),
        Exception("Second failure"),
    ]
    mock_mod = _make_mock_anthropic(mock_client)

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"}):
        with patch.dict(sys.modules, {"anthropic": mock_mod}):
            with pytest.raises(RuntimeError):
                run_orchestrator("Receipt: Test, Apr 1, $5, coffee")

    assert mock_client.messages.create.call_count == 2
