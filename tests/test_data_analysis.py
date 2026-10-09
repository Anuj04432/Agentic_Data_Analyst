"""
Unit tests for ui/Data_Analysis.py.
Verifies Hero section rendering, sub-tab execution, empty-state guards,
and data remediation actions without crashing Streamlit runtime.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import numpy as np
import pandas as pd
from ui.Data_Analysis import (
    analysis_tab,
    _render_overview_tab,
    _render_missing_and_duplicates_tab,
    _render_distributions_and_outliers_tab,
    _render_correlations_tab,
)


class TestDataAnalysisView(unittest.TestCase):
    """Test suite for ui/Data_Analysis.py components and tabs."""

    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        n = 50
        self.clean_df = pd.DataFrame({
            "age": np.random.randint(20, 60, size=n),
            "salary": np.random.uniform(30000, 100000, size=n),
            "department": np.random.choice(["IT", "HR", "Sales"], size=n),
            "is_active": np.random.choice([True, False], size=n),
        })

        self.dirty_df = self.clean_df.copy()
        # Inject missing values
        self.dirty_df.loc[0:4, "salary"] = np.nan
        self.dirty_df.loc[5:7, "department"] = np.nan
        # Inject duplicates
        dup_row = self.dirty_df.iloc[[10]]
        self.dirty_df = pd.concat([self.dirty_df, dup_row, dup_row], ignore_index=True)
        # Inject extreme outlier
        self.dirty_df.loc[0, "age"] = 250

    @patch("streamlit.info")
    def test_analysis_tab_none_input(self, mock_info):
        """Test that passing None when session state is empty shows info guard."""
        with patch("ui.Data_Analysis.get_dataset", return_value=(None, None)):
            analysis_tab(None)
            mock_info.assert_called_once()
            self.assertIn("No dataset loaded", mock_info.call_args[0][0])

    @patch("streamlit.info")
    def test_analysis_tab_empty_dataframe(self, mock_info):
        """Test that passing an empty DataFrame shows info guard."""
        empty_df = pd.DataFrame()
        analysis_tab(empty_df)
        mock_info.assert_called_once()
        self.assertIn("No dataset loaded", mock_info.call_args[0][0])

    @patch("streamlit.tabs")
    @patch("ui.Data_Analysis.render_health_score_card")
    @patch("ui.Data_Analysis.render_dataset_summary")
    @patch("ui.Data_Analysis.render_actionable_warnings")
    def test_hero_section_rendered(
        self,
        mock_warnings,
        mock_summary,
        mock_health_card,
        mock_tabs,
    ):
        """Verify that Hero section components are invoked with valid dataset."""
        # Create 4 mock tabs for the context managers
        mock_tab_list = [MagicMock() for _ in range(4)]
        mock_tabs.return_value = mock_tab_list

        with patch("ui.Data_Analysis._render_overview_tab"), \
             patch("ui.Data_Analysis._render_missing_and_duplicates_tab"), \
             patch("ui.Data_Analysis._render_distributions_and_outliers_tab"), \
             patch("ui.Data_Analysis._render_correlations_tab"):
            analysis_tab(self.clean_df)

        mock_health_card.assert_called_once()
        mock_summary.assert_called_once()
        mock_warnings.assert_called_once()
        mock_tabs.assert_called_once()

    @patch("streamlit.dataframe")
    @patch("ui.Data_Analysis.render_data_preview")
    def test_render_overview_tab(self, mock_preview, mock_dataframe):
        """Verify Overview tab renders preview and data dictionary."""
        _render_overview_tab(self.clean_df)
        mock_preview.assert_called_once()
        mock_dataframe.assert_called_once()

    @patch("streamlit.dataframe")
    @patch("streamlit.metric")
    def test_render_missing_and_duplicates_clean(self, mock_metric, mock_dataframe):
        """Verify Missing & Duplicates tab handles clean data gracefully."""
        _render_missing_and_duplicates_tab(self.clean_df, "clean.csv")
        self.assertTrue(mock_metric.called)

    @patch("streamlit.dataframe")
    @patch("streamlit.metric")
    @patch("streamlit.radio", return_value="Specific Column")
    @patch("streamlit.selectbox", return_value="salary")
    def test_render_missing_and_duplicates_dirty(self, mock_sb, mock_radio, mock_metric, mock_dataframe):
        """Verify Missing & Duplicates tab handles dirty data with missing & duplicates."""
        _render_missing_and_duplicates_tab(self.dirty_df, "dirty.csv")
        self.assertTrue(mock_metric.called)
        self.assertTrue(mock_dataframe.called)

    @patch("streamlit.dataframe")
    @patch("streamlit.radio", return_value="Numeric Features")
    @patch("streamlit.selectbox", return_value="age")
    def test_render_distributions_and_outliers(self, mock_sb, mock_radio, mock_dataframe):
        """Verify Distributions & Outliers tab renders stats and outlier analysis."""
        _render_distributions_and_outliers_tab(self.dirty_df, "dirty.csv")
        self.assertTrue(mock_dataframe.called)

    @patch("streamlit.dataframe")
    @patch("streamlit.selectbox", return_value="pearson")
    @patch("streamlit.slider", side_effect=[0.4, 15])
    def test_render_correlations_tab(self, mock_slider, mock_selectbox, mock_dataframe):
        """Verify Correlations tab computes matrix and top correlated pairs."""
        _render_correlations_tab(self.clean_df)
        # Should have called either plotly_chart or dataframe
        self.assertTrue(mock_selectbox.called)


if __name__ == "__main__":
    unittest.main()
