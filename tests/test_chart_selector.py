"""
Unit tests for components/chart_selector.py.
Verifies available chart type discovery, configuration validation,
and Streamlit UI rendering functions.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import pandas as pd
from components.chart_selector import (
    get_available_chart_types,
    validate_chart_config,
    render_chart_selector,
)


class TestGetAvailableChartTypes(unittest.TestCase):
    """Test suite for get_available_chart_types."""

    def test_none_and_empty_dataframe(self):
        """Test that None or empty input returns an empty list."""
        self.assertEqual(get_available_chart_types(None), [])
        self.assertEqual(get_available_chart_types(pd.DataFrame()), [])

    def test_categorical_only(self):
        """Test dataset with only categorical columns."""
        df = pd.DataFrame({"city": ["Paris", "Tokyo"], "dept": ["HR", "IT"]})
        charts = get_available_chart_types(df)
        self.assertIn("Bar Chart", charts)
        self.assertIn("Pie / Donut Chart", charts)
        self.assertNotIn("Scatter Plot", charts)
        self.assertNotIn("Histogram", charts)
        self.assertNotIn("Correlation Heatmap", charts)

    def test_single_numeric_column(self):
        """Test dataset with only 1 numeric column."""
        df = pd.DataFrame({"score": [10, 20, 30]})
        charts = get_available_chart_types(df)
        self.assertIn("Histogram", charts)
        self.assertIn("Box Plot", charts)
        self.assertNotIn("Scatter Plot", charts)
        self.assertNotIn("Correlation Heatmap", charts)

    def test_multi_numeric_features(self):
        """Test dataset with multiple numeric columns."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]})
        charts = get_available_chart_types(df)
        self.assertIn("Scatter Plot", charts)
        self.assertIn("Correlation Heatmap", charts)
        self.assertIn("Histogram", charts)
        self.assertIn("Box Plot", charts)

    def test_datetime_and_numeric(self):
        """Test dataset with datetime and numeric columns."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
            "price": [100.0, 102.5, 105.0],
        })
        charts = get_available_chart_types(df)
        self.assertIn("Line Chart", charts)
        self.assertIn("Histogram", charts)


class TestValidateChartConfig(unittest.TestCase):
    """Test suite for validate_chart_config."""

    def test_empty_or_invalid_dict(self):
        """Test handling of None or non-dict input."""
        valid, msg = validate_chart_config({})
        self.assertFalse(valid)
        self.assertIsNotNone(msg)

        valid, msg = validate_chart_config(None)  # type: ignore
        self.assertFalse(valid)

    def test_missing_chart_type(self):
        """Test validation fails when chart_type is missing."""
        valid, msg = validate_chart_config({"x": "col1"})
        self.assertFalse(valid)
        self.assertIn("Chart type must be specified", msg)

    def test_scatter_plot_validation(self):
        """Test Scatter Plot requirements (both X and Y required)."""
        valid, msg = validate_chart_config({"chart_type": "Scatter Plot", "x": "a"})
        self.assertFalse(valid)
        self.assertIn("Y-axis", msg)

        valid, msg = validate_chart_config({"chart_type": "Scatter Plot", "y": "b"})
        self.assertFalse(valid)
        self.assertIn("X-axis", msg)

        valid, msg = validate_chart_config({"chart_type": "Scatter Plot", "x": "a", "y": "b"})
        self.assertTrue(valid)
        self.assertIsNone(msg)

    def test_line_chart_validation(self):
        """Test Line Chart requirements."""
        valid, msg = validate_chart_config({"chart_type": "Line Chart", "x": "date"})
        self.assertFalse(valid)
        self.assertIn("Y-axis", msg)

        valid, msg = validate_chart_config({"chart_type": "Line Chart", "x": "date", "y": "val"})
        self.assertTrue(valid)

    def test_bar_and_histogram_validation(self):
        """Test Bar and Histogram primary dimension."""
        valid, msg = validate_chart_config({"chart_type": "Bar Chart"})
        self.assertFalse(valid)

        valid, msg = validate_chart_config({"chart_type": "Bar Chart", "x": "category"})
        self.assertTrue(valid)

        valid, msg = validate_chart_config({"chart_type": "Histogram", "x": "age", "bins": 30})
        self.assertTrue(valid)

        valid, msg = validate_chart_config({"chart_type": "Histogram", "x": "age", "bins": -5})
        self.assertFalse(valid)
        self.assertIn("positive integer", msg)

    def test_box_plot_validation(self):
        """Test Box Plot numeric requirement."""
        valid, msg = validate_chart_config({"chart_type": "Box Plot"})
        self.assertFalse(valid)

        valid, msg = validate_chart_config({"chart_type": "Box Plot", "y": "salary"})
        self.assertTrue(valid)

    def test_correlation_heatmap_validation(self):
        """Test Correlation Heatmap multi-column requirements."""
        valid, msg = validate_chart_config({"chart_type": "Correlation Heatmap", "columns": ["a"]})
        self.assertFalse(valid)
        self.assertIn("at least 2", msg)

        valid, msg = validate_chart_config({"chart_type": "Correlation Heatmap", "columns": ["a", "b"]})
        self.assertTrue(valid)


class TestRenderChartSelector(unittest.TestCase):
    """Test suite for Streamlit render_chart_selector function."""

    def setUp(self):
        self.sample_df = pd.DataFrame({
            "age": [20, 30, 40],
            "income": [30000, 50000, 90000],
            "city": ["New York", "London", "Tokyo"],
        })

    @patch("components.chart_selector.st")
    def test_render_empty_dataframe(self, mock_st):
        """Test render with None or empty dataframe displays info message."""
        result = render_chart_selector(None)
        mock_st.info.assert_called_once()
        self.assertFalse(result["is_valid"])

    @patch("components.chart_selector.st")
    def test_render_scatter_plot_selection(self, mock_st):
        """Test rendering scatter plot configuration layout."""
        mock_st.selectbox.side_effect = ["Scatter Plot", "age", "income", None]
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]
        mock_st.text_input.return_value = "Income vs Age"

        result = render_chart_selector(self.sample_df, key_prefix="test")

        self.assertEqual(result["chart_type"], "Scatter Plot")
        self.assertEqual(result["x"], "age")
        self.assertEqual(result["y"], "income")
        self.assertTrue(result["is_valid"])
        self.assertIsNone(result["error_message"])


if __name__ == "__main__":
    unittest.main()
