# Copyright (c) 2026, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

"""TealTiger governance middleware Extension for AG2 Beta.

Provides deterministic governance for AG2 Beta agents via the composable
middleware system. Intercepts tool calls and agent turns to enforce policies,
track cost, detect PII, and produce structured audit evidence (TEEC receipts).

No LLM in the governance path. All evaluation is deterministic with <5ms
overhead.

Maintainer: nagasatish007
Docs: https://github.com/agentguard-ai/tealtiger/tree/main/packages/ag2-tealtiger
Examples: https://github.com/ag2ai/build-with-ag2/extensions/tealtiger-governance
"""

from autogen.beta.exceptions import missing_additional_dependency

try:
    from .middleware import TealTigerMiddleware
    from .types import (
        DecisionAction,
        DecisionSource,
        GovernanceDecision,
        GovernanceMode,
        GovernancePolicy,
        TEECReceipt,
    )
except ImportError as e:
    TealTigerMiddleware = missing_additional_dependency("TealTigerMiddleware", "tealtiger>=1.3.0", e)  # type: ignore[misc]
    DecisionAction = missing_additional_dependency("DecisionAction", "tealtiger>=1.3.0", e)  # type: ignore[misc]
    DecisionSource = missing_additional_dependency("DecisionSource", "tealtiger>=1.3.0", e)  # type: ignore[misc]
    GovernanceDecision = missing_additional_dependency("GovernanceDecision", "tealtiger>=1.3.0", e)  # type: ignore[misc]
    GovernanceMode = missing_additional_dependency("GovernanceMode", "tealtiger>=1.3.0", e)  # type: ignore[misc]
    GovernancePolicy = missing_additional_dependency("GovernancePolicy", "tealtiger>=1.3.0", e)  # type: ignore[misc]
    TEECReceipt = missing_additional_dependency("TEECReceipt", "tealtiger>=1.3.0", e)  # type: ignore[misc]

__all__ = (
    "DecisionAction",
    "DecisionSource",
    "GovernanceDecision",
    "GovernanceMode",
    "GovernancePolicy",
    "TEECReceipt",
    "TealTigerMiddleware",
)
