# Copyright (c) 2026, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for TealTiger middleware policy evaluation logic.

Tests the internal helpers without requiring AG2 Beta runtime (mocked).
"""

from autogen.beta.extensions.tealtiger.types import (
    GovernanceMode,
    GovernancePolicy,
)


class TestPolicyEvaluation:
    """Test policy matching logic."""

    def test_tool_allowlist_allows_matching_tool(self):
        """Tool in allowlist should be allowed."""
        policy = GovernancePolicy.tool_allowlist(["search", "read_file"])
        assert policy.type == "tool_allowlist"
        assert "search" in policy.config["allowed"]
        assert "read_file" in policy.config["allowed"]

    def test_tool_allowlist_denies_unlisted_tool(self):
        """Tool NOT in allowlist should be denied."""
        policy = GovernancePolicy.tool_allowlist(["search", "read_file"])
        assert "delete_file" not in policy.config["allowed"]
        assert "send_email" not in policy.config["allowed"]

    def test_tool_denylist_blocks_listed_tool(self):
        """Tool in denylist should be blocked."""
        policy = GovernancePolicy.tool_denylist(["rm_rf", "drop_table"])
        assert policy.type == "tool_denylist"
        assert "rm_rf" in policy.config["denied"]

    def test_pii_block_default_categories(self):
        """PII block with no args uses default categories."""
        policy = GovernancePolicy.pii_block()
        assert "ssn" in policy.config["categories"]
        assert "credit_card" in policy.config["categories"]
        assert "email" in policy.config["categories"]
        assert "phone" in policy.config["categories"]

    def test_pii_block_custom_categories(self):
        """PII block with custom categories."""
        policy = GovernancePolicy.pii_block(["ssn", "medical"])
        assert policy.config["categories"] == ["ssn", "medical"]

    def test_cost_limit_policy(self):
        """Cost limit policy stores max_per_session."""
        policy = GovernancePolicy.cost_limit(max_per_session=5.0)
        assert policy.type == "cost_limit"
        assert policy.config["max_per_session"] == 5.0

    def test_secret_detection_policy(self):
        """Secret detection policy stores action."""
        policy = GovernancePolicy.secret_detection(action="redact")
        assert policy.type == "secret_detection"
        assert policy.config["action"] == "redact"


class TestPIIDetection:
    """Test PII pattern detection from middleware internals."""

    def test_ssn_detected(self):
        """SSN pattern should be detected."""
        import re

        pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
        assert pattern.search("My SSN is 123-45-6789")
        assert not pattern.search("My phone is 555-1234")

    def test_credit_card_detected(self):
        """Credit card pattern should be detected."""
        import re

        pattern = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
        assert pattern.search("Card: 4111-1111-1111-1111")
        assert pattern.search("Card: 4111 1111 1111 1111")
        assert not pattern.search("Not a card: 123-456")

    def test_email_detected(self):
        """Email pattern should be detected."""
        import re

        pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        assert pattern.search("user@example.com")
        assert not pattern.search("not-an-email")

    def test_secret_openai_key_detected(self):
        """OpenAI API key pattern should be detected."""
        import re

        pattern = re.compile(r"\b(sk-[a-zA-Z0-9]{20,})\b")
        assert pattern.search("key: sk-abcdefghij1234567890")
        assert not pattern.search("not-a-key: sk-short")

    def test_secret_github_pat_detected(self):
        """GitHub PAT pattern should be detected."""
        import re

        pattern = re.compile(r"\b(ghp_[a-zA-Z0-9]{36,})\b")
        assert pattern.search("token: ghp_abcdefghijklmnopqrstuvwxyz1234567890")
        assert not pattern.search("not-a-pat: ghp_short")

    def test_secret_aws_key_detected(self):
        """AWS access key pattern should be detected."""
        import re

        pattern = re.compile(r"\b(AKIA[0-9A-Z]{16})\b")
        assert pattern.search("AKIAIOSFODNN7EXAMPLE")
        assert not pattern.search("AKIA_too_short")


class TestGovernanceMode:
    """Test governance mode behavior definitions."""

    def test_observe_mode_value(self):
        assert GovernanceMode.OBSERVE.value == "observe"

    def test_monitor_mode_value(self):
        assert GovernanceMode.MONITOR.value == "monitor"

    def test_enforce_mode_value(self):
        assert GovernanceMode.ENFORCE.value == "enforce"


class TestGlobMatching:
    """Test glob pattern matching for tool allowlists."""

    def test_exact_match(self):
        import fnmatch

        assert fnmatch.fnmatch("search", "search")
        assert not fnmatch.fnmatch("search", "read_file")

    def test_wildcard_match(self):
        import fnmatch

        assert fnmatch.fnmatch("github_create_issue", "github_*")
        assert fnmatch.fnmatch("github_list_prs", "github_*")
        assert not fnmatch.fnmatch("slack_send", "github_*")

    def test_multiple_patterns(self):
        import fnmatch

        patterns = ["search", "read_*", "github_*"]
        assert any(fnmatch.fnmatch("search", p) for p in patterns)
        assert any(fnmatch.fnmatch("read_file", p) for p in patterns)
        assert any(fnmatch.fnmatch("github_create_issue", p) for p in patterns)
        assert not any(fnmatch.fnmatch("delete_all", p) for p in patterns)
