"""Tests for the Nous-NIA-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"nia"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``nia-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "nia" tag namespace.

``is_nous_nia_non_agentic`` should only match the actual Anonymousinsaan & Codurra Labs
NIA-3 / NIA-4 chat family.
"""

from __future__ import annotations

import pytest

from nia_cli.model_switch import (
    _NIA_MODEL_WARNING,
    _check_nia_model_warning,
    is_nous_nia_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "NousResearch/NIA-3-Llama-3.1-70B",
        "NousResearch/NIA-3-Llama-3.1-405B",
        "nia-3",
        "NIA-3",
        "nia-4",
        "nia-4-405b",
        "nia_4_70b",
        "openrouter/nia3:70b",
        "openrouter/nousresearch/nia-4-405b",
        "NousResearch/NIA3",
        "nia-3.1",
    ],
)
def test_matches_real_nous_nia_chat_models(model_name: str) -> None:
    assert is_nous_nia_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Nous NIA 3/4"
    )
    assert _check_nia_model_warning(model_name) == _NIA_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "nia-brain:qwen3-14b-ctx16k",
        "nia-brain:qwen3-14b-ctx32k",
        "nia-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat NIA models we don't warn about
        "nia-llm-2",
        "nia2-pro",
        "nous-nia-2-mistral",
        # Edge cases
        "",
        "nia",  # bare "nia" isn't the 3/4 family
        "nia-brain",
        "brain-nia-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_nia_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Nous NIA 3/4"
    )
    assert _check_nia_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_nia_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_nia_model_warning("") == ""
