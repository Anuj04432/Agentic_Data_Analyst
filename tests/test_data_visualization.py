"""
Unit and integration tests for ui/Data_Visualization.py.

Verifies view rendering, empty-state guards, preset loading, and legacy compatibility.
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ui.Data_Visualization import (
    visualization_tab,
    visualization,
    _render_recommendations_section,
    _render_chart_output,
    _render_chart_summary,
)


class TestDataVisualizationView(unittest.TestCase):
    """Test suite for ui/Data_Visualization.py."""

    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        n = 30
        self.df = pd.DataFrame({
            "age": np.random.randint(20, 60, size=n),
            "salary": np.random.uniform(30000, 90000, size=n),
            "dept": np.random.choice(["IT", "HR", "Sales"], size=n),
        })

    @patch("streamlit.info")
    def test_visualization_tab_none_dataset(self, mock_info):
        """Verifies informative guard when no dataset is loaded."""
        with patch("ui.Data_Visualization.get_dataset", return_value=(None, None)):
            visualization_tab(None)
            mock_info.assert_called_once()
            self.assertIn("No dataset active", mock_info.call_args[0][0])

    @patch("streamlit.info")
    def test_visualization_tab_empty_dataset(self, mock_info):
        """Verifies guard when empty DataFrame is passed."""
        visualization_tab(pd.DataFrame())
        mock_info.assert_called_once()
        self.assertIn("No dataset active", mock_info.call_args[0][0])

    @patch("streamlit.plotly_chart")
    @patch("ui.Data_Visualization.render_chart_selector")
    def test_visualization_tab_renders_with_df(self, mock_selector, mock_plotly):
        """Verifies full visualization tab execution with active DataFrame."""
        mock_selector.return_value = {
            "chart_type": "Histogram",
            "x": "age",
            "bins": 20,
            "is_valid": True,
            "error_message": None,
        }
        visualization_tab(self.df)
        mock_plotly.assert_called_once()

    @patch("streamlit.info")
    def test_render_chart_output_invalid_config(self, mock_info):
        """Verifies warning message when config is invalid."""
        invalid_config = {"chart_type": "Scatter Plot", "is_valid": False, "error_message": "Missing Y"}
        _render_chart_output(self.df, invalid_config)
        mock_info.assert_called_once()

    @patch("streamlit.metric")
    def test_render_chart_summary_metrics(self, mock_metric):
        """Verifies summary metrics rendering without exceptions."""
        config = {
            "chart_type": "Scatter Plot",
            "x": "age",
            "y": "salary",
            "color": "dept",
            "is_valid": True,
        }
        _render_chart_summary(self.df, config)
        self.assertGreaterEqual(mock_metric.call_count, 3)

    @patch("ui.Data_Visualization.visualization_tab")
    def test_legacy_visualization_alias(self, mock_tab):
        """Verifies legacy visualization() entry point calls visualization_tab()."""
        visualization()
        mock_tab.assert_called_once()


if __name__ == "__main__":
    unittest.main()
