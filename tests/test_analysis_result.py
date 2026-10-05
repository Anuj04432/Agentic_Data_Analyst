"""
Unit tests for components/analysis_result.py.
Verifies color palettes, badge metadata generation, warning parsing,
and Streamlit UI rendering functions.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from components.analysis_result import (
    get_health_grade_color,
    get_distribution_badge_info,
    get_correlation_badge_info,
    render_health_grade_badge,
    render_health_score_card,
    render_actionable_warnings,
    render_distribution_badge,
    render_correlation_badge,
)


class TestHealthGradeColor(unittest.TestCase):
    """Test suite for get_health_grade_color."""

    def test_standard_grades(self):
        """Test standard grade letters A through F."""
        a = get_health_grade_color("A")
        self.assertEqual(a["color"], "#10b981")
        self.assertEqual(a["label"], "Excellent")

        b = get_health_grade_color("B")
        self.assertEqual(b["color"], "#3b82f6")
        self.assertEqual(b["label"], "Good")

        c = get_health_grade_color("C")
        self.assertEqual(c["color"], "#f59e0b")
        self.assertEqual(c["label"], "Fair")

        d = get_health_grade_color("D")
        self.assertEqual(d["color"], "#f97316")
        self.assertEqual(d["label"], "Poor")

        f = get_health_grade_color("F")
        self.assertEqual(f["color"], "#ef4444")
        self.assertEqual(f["label"], "Critical")

    def test_case_and_whitespace_insensitivity(self):
        """Test lowercase and surrounding whitespace."""
        res = get_health_grade_color("  a  ")
        self.assertEqual(res["label"], "Excellent")

    def test_unknown_grade_fallback(self):
        """Test unrecognized grade returns gray fallback."""
        res = get_health_grade_color("Z")
        self.assertEqual(res["color"], "#6b7280")
        self.assertEqual(res["label"], "Unknown")


class TestDistributionBadgeInfo(unittest.TestCase):
    """Test suite for get_distribution_badge_info."""

    def test_symmetrical(self):
        """Test symmetrical / normal distributions."""
        info = get_distribution_badge_info("Fairly Symmetrical")
        self.assertEqual(info["label"], "Symmetrical")
        self.assertEqual(info["icon"], "⚖️")

    def test_skewed_right(self):
        """Test moderate and highly right-skewed distributions."""
        mod = get_distribution_badge_info("Moderately Skewed (Right)")
        self.assertEqual(mod["label"], "Right-Skewed")
        self.assertEqual(mod["icon"], "📈")

        high = get_distribution_badge_info("Highly Skewed (Right)")
        self.assertEqual(high["label"], "Highly Right-Skewed")
        self.assertEqual(high["color"], "#ef4444")

    def test_skewed_left(self):
        """Test moderate and highly left-skewed distributions."""
        mod = get_distribution_badge_info("Moderately Skewed (Left)")
        self.assertEqual(mod["label"], "Left-Skewed")
        self.assertEqual(mod["icon"], "📉")

        high = get_distribution_badge_info("Highly Skewed (Left)")
        self.assertEqual(high["label"], "Highly Left-Skewed")
        self.assertEqual(high["color"], "#ef4444")

    def test_unknown_distribution(self):
        """Test fallback for unknown shape."""
        info = get_distribution_badge_info("Bimodal custom")
        self.assertEqual(info["label"], "Bimodal custom")
        self.assertEqual(info["icon"], "📊")


class TestCorrelationBadgeInfo(unittest.TestCase):
    """Test suite for get_correlation_badge_info."""

    def test_strong_positive(self):
        info = get_correlation_badge_info(0.85)
        self.assertIn("Strong Positive", info["label"])
        self.assertEqual(info["icon"], "🟢")

    def test_moderate_positive(self):
        info = get_correlation_badge_info(0.45)
        self.assertIn("Moderate Positive", info["label"])
        self.assertEqual(info["icon"], "🔵")

    def test_weak_or_negligible(self):
        info = get_correlation_badge_info(0.12)
        self.assertIn("Weak / Negligible", info["label"])
        self.assertEqual(info["icon"], "⚪")

    def test_moderate_negative(self):
        info = get_correlation_badge_info(-0.55)
        self.assertIn("Moderate Negative", info["label"])
        self.assertEqual(info["icon"], "🟠")

    def test_strong_negative(self):
        info = get_correlation_badge_info(-0.92)
        self.assertIn("Strong Negative", info["label"])
        self.assertEqual(info["icon"], "🔴")

    def test_invalid_type_fallback(self):
        info = get_correlation_badge_info("invalid")  # type: ignore
        self.assertIn("Weak / Negligible", info["label"])


class TestRenderUIComponents(unittest.TestCase):
    """Test suite for Streamlit UI rendering functions."""

    @patch("streamlit.markdown")
    def test_render_health_grade_badge(self, mock_markdown):
        """Test render_health_grade_badge outputs valid HTML."""
        html_out = render_health_grade_badge("A", score=95.0, size="large")
        self.assertIn("Grade A (95.0/100)", html_out)
        self.assertIn("Excellent", html_out)
        mock_markdown.assert_called_once()

    @patch("streamlit.info")
    def test_render_health_score_card_empty(self, mock_info):
        """Test empty health data triggers info notice."""
        render_health_score_card(None)
        mock_info.assert_called_once()

    @patch("streamlit.columns")
    @patch("streamlit.progress")
    @patch("streamlit.markdown")
    @patch("streamlit.container")
    def test_render_health_score_card_valid(self, mock_container, mock_markdown, mock_progress, mock_columns):
        """Test full score card rendering with deductions."""
        def fake_columns(spec):
            n = len(spec) if isinstance(spec, (list, tuple)) else int(spec)
            return [MagicMock() for _ in range(n)]

        mock_columns.side_effect = fake_columns
        health_data = {
            "health_score": 82.5,
            "grade": "B",
            "summary": "Good dataset with minor issues",
            "deductions": {
                "missing": 5.0,
                "duplicates": 2.5,
                "outliers": 10.0,
                "constant_cols": 0.0,
            },
        }
        render_health_score_card(health_data, border=False)
        mock_progress.assert_called_once_with(0.825)

    @patch("streamlit.success")
    def test_render_actionable_warnings_clean(self, mock_success):
        """Test no warnings displays clean dataset success message."""
        render_actionable_warnings([])
        mock_success.assert_called_once()

    @patch("streamlit.expander")
    @patch("streamlit.markdown")
    def test_render_actionable_warnings_with_issues(self, mock_markdown, mock_expander):
        """Test multiple warnings render inside expander."""
        mock_exp = MagicMock()
        mock_expander.return_value.__enter__.return_value = mock_exp

        warnings = [
            "High missing data (35.0%) in column: 'age'",
            "Found 12 duplicate rows (5.2% of dataset)",
            "High multicollinearity detected between 'col1' and 'col2'",
        ]
        render_actionable_warnings(warnings)
        mock_expander.assert_called_once()
        self.assertEqual(mock_markdown.call_count, 3)

    @patch("streamlit.markdown")
    def test_render_distribution_badge(self, mock_markdown):
        """Test distribution badge renders HTML."""
        badge = render_distribution_badge("Fairly Symmetrical")
        self.assertIn("Symmetrical", badge)
        mock_markdown.assert_called_once()

    @patch("streamlit.markdown")
    def test_render_correlation_badge(self, mock_markdown):
        """Test correlation badge renders HTML."""
        badge = render_correlation_badge(0.88)
        self.assertIn("Strong Positive", badge)
        mock_markdown.assert_called_once()


if __name__ == "__main__":
    unittest.main()
