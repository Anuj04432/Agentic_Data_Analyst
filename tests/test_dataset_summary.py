"""
Unit tests for components/dataset_summary.py.
Verifies metric extraction, dual-input compatibility (df vs audit),
edge case handling, and Streamlit rendering.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import pandas as pd
from analysis.profiling import generate_dataset_audit
from components.dataset_summary import (
    extract_summary_metrics,
    render_dataset_summary,
)


class TestExtractSummaryMetrics(unittest.TestCase):
    """Test suite for extract_summary_metrics in components/dataset_summary.py."""

    def test_none_and_empty_inputs(self):
        """Test that None or empty inputs return the safe default structure."""
        # Both None
        res_none = extract_summary_metrics(None, None)
        self.assertEqual(res_none["rows"], 0)
        self.assertEqual(res_none["columns"], 0)
        self.assertEqual(res_none["total_cells"], 0)
        self.assertEqual(res_none["missing_cells"], 0)
        self.assertEqual(res_none["missing_pct"], 0.0)
        self.assertEqual(res_none["duplicates"], 0)
        self.assertEqual(res_none["duplicate_pct"], 0.0)
        self.assertEqual(res_none["memory"], "0 B")

        # Empty DataFrame
        res_empty_df = extract_summary_metrics(df=pd.DataFrame())
        self.assertEqual(res_empty_df["rows"], 0)
        self.assertEqual(res_empty_df["memory"], "0 B")

        # Empty audit dictionary
        res_empty_audit = extract_summary_metrics(audit={})
        self.assertEqual(res_empty_audit["rows"], 0)
        self.assertEqual(res_empty_audit["memory"], "0 B")

    def test_clean_dataframe(self):
        """Test metric calculation on a clean DataFrame without missing values or duplicates."""
        df = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "score": [10.5, 20.0, 30.5, 40.0, 50.5],
            "grade": ["A", "B", "A", "C", "B"],
        })
        res = extract_summary_metrics(df=df)

        self.assertEqual(res["rows"], 5)
        self.assertEqual(res["columns"], 3)
        self.assertEqual(res["total_cells"], 15)
        self.assertEqual(res["missing_cells"], 0)
        self.assertEqual(res["missing_pct"], 0.0)
        self.assertEqual(res["duplicates"], 0)
        self.assertEqual(res["duplicate_pct"], 0.0)
        self.assertTrue(res["memory"].endswith("B"))

    def test_dataframe_with_missing_and_duplicates(self):
        """Test calculation with known missing cells and duplicate rows."""
        # 4 rows, 2 columns = 8 total cells. 2 missing cells = 25%. 1 duplicate row = 25%.
        df = pd.DataFrame({
            "col1": [10, 20, 10, None],
            "col2": ["A", "B", "A", None],
        })
        res = extract_summary_metrics(df=df)

        self.assertEqual(res["rows"], 4)
        self.assertEqual(res["columns"], 2)
        self.assertEqual(res["total_cells"], 8)
        self.assertEqual(res["missing_cells"], 2)
        self.assertEqual(res["missing_pct"], 25.0)
        self.assertEqual(res["duplicates"], 1)
        self.assertEqual(res["duplicate_pct"], 25.0)

    def test_audit_input_compatibility(self):
        """Test extracting metrics from an audit dictionary produced by generate_dataset_audit."""
        df = pd.DataFrame({
            "a": [1, 2, 3, 1],
            "b": [10.0, None, 30.0, 10.0],
            "c": ["x", "y", "z", "x"],
        })
        audit = generate_dataset_audit(df)
        res_audit = extract_summary_metrics(audit=audit)
        res_direct = extract_summary_metrics(df=df)

        # Both direct df calculation and audit extraction must match
        self.assertEqual(res_audit["rows"], res_direct["rows"])
        self.assertEqual(res_audit["columns"], res_direct["columns"])
        self.assertEqual(res_audit["total_cells"], res_direct["total_cells"])
        self.assertEqual(res_audit["missing_cells"], res_direct["missing_cells"])
        self.assertEqual(res_audit["missing_pct"], res_direct["missing_pct"])
        self.assertEqual(res_audit["duplicates"], res_direct["duplicates"])
        self.assertEqual(res_audit["duplicate_pct"], res_direct["duplicate_pct"])
        self.assertEqual(res_audit["memory"], res_direct["memory"])

    def test_audit_with_dict_missingness(self):
        """Test compatibility when audit['missingness'] is provided as a dict instead of a DataFrame."""
        custom_audit = {
            "shape": {"rows": 100, "columns": 5},
            "memory": {"bytes": 2048, "formatted": "2.00 KB"},
            "missingness": {
                "total_missing_cells": 10,
                "overall_missing_pct": 2.0,
            },
            "duplicates": {
                "duplicate_count": 5,
                "duplicate_pct": 5.0,
            },
        }
        res = extract_summary_metrics(audit=custom_audit)

        self.assertEqual(res["rows"], 100)
        self.assertEqual(res["columns"], 5)
        self.assertEqual(res["total_cells"], 500)
        self.assertEqual(res["missing_cells"], 10)
        self.assertEqual(res["missing_pct"], 2.0)
        self.assertEqual(res["duplicates"], 5)
        self.assertEqual(res["duplicate_pct"], 5.0)
        self.assertEqual(res["memory"], "2.00 KB")


class TestRenderDatasetSummary(unittest.TestCase):
    """Test suite for render_dataset_summary UI rendering in Streamlit."""

    @patch("components.dataset_summary.st.info")
    def test_empty_dataset_renders_info(self, mock_info):
        """Test that empty or None dataset shows st.info and exits early."""
        metrics = render_dataset_summary(df=None, audit=None)
        mock_info.assert_called_once()
        self.assertEqual(metrics["rows"], 0)

    @patch("components.dataset_summary.st.metric")
    @patch("components.dataset_summary.st.container")
    @patch("components.dataset_summary.st.columns")
    def test_populated_dataframe_renders_cards(self, mock_columns, mock_container, mock_metric):
        """Test that populated dataframe renders all 5 metric cards inside columns."""
        mock_cols = [MagicMock() for _ in range(5)]
        mock_columns.return_value = mock_cols

        mock_context = MagicMock()
        mock_container.return_value.__enter__.return_value = mock_context

        df = pd.DataFrame({
            "col1": [1, 2, 3, 1],
            "col2": ["A", "B", None, "A"],
        })

        metrics = render_dataset_summary(df=df, border=True)

        # 5 columns must be created and 5 metrics rendered
        mock_columns.assert_called_once_with(5)
        self.assertEqual(mock_metric.call_count, 5)
        self.assertEqual(metrics["rows"], 4)
        self.assertEqual(metrics["columns"], 2)
        self.assertEqual(metrics["missing_cells"], 1)
        self.assertEqual(metrics["duplicates"], 1)


if __name__ == "__main__":
    unittest.main()
