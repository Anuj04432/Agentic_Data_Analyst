"""
Unit tests for visualization/chart_recommender.py.

Verifies smart rule-based heuristics, schema contracts, priority ranking,
and graceful handling of empty or edge-case DataFrames.
"""

import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from visualization.chart_recommender import recommend_charts


class TestChartRecommender(unittest.TestCase):
    """Test suite for automated chart recommender."""

    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        n = 50
        self.multimodal_df = pd.DataFrame({
            "timestamp": pd.date_range("2025-01-01", periods=n, freq="D"),
            "revenue": np.random.uniform(1000, 5000, size=n),
            "units_sold": np.random.randint(10, 100, size=n),
            "region": np.random.choice(["North", "South", "East", "West"], size=n),
            "is_promo": np.random.choice([True, False], size=n),
        })

    def test_recommend_charts_empty_or_none(self):
        """Verifies empty list returned on None or empty DataFrame."""
        self.assertEqual(recommend_charts(None), [])
        self.assertEqual(recommend_charts(pd.DataFrame()), [])

    def test_recommend_charts_schema(self):
        """Verifies each recommendation matches the expected contract keys."""
        recs = recommend_charts(self.multimodal_df, max_recommendations=5)
        self.assertGreater(len(recs), 0)
        self.assertLessEqual(len(recs), 5)

        expected_keys = {
            "chart_type", "x", "y", "color", "agg", "bins", "columns",
            "title", "reason", "icon", "priority"
        }
        for rec in recs:
            for k in expected_keys:
                self.assertIn(k, rec)
            self.assertIsInstance(rec["priority"], int)
            self.assertIsInstance(rec["title"], str)
            self.assertIsInstance(rec["reason"], str)

    def test_temporal_dataset_recommends_line_chart(self):
        """Verifies line chart is recommended when datetime & numeric columns exist."""
        recs = recommend_charts(self.multimodal_df)
        chart_types = [r["chart_type"] for r in recs]
        self.assertIn("Line Chart", chart_types)

        line_rec = next(r for r in recs if r["chart_type"] == "Line Chart")
        self.assertEqual(line_rec["x"], "timestamp")
        self.assertEqual(line_rec["priority"], 1)

    def test_numeric_pairs_recommends_scatter(self):
        """Verifies scatter plot is recommended when multiple numeric columns exist."""
        recs = recommend_charts(self.multimodal_df)
        chart_types = [r["chart_type"] for r in recs]
        self.assertIn("Scatter Plot", chart_types)

    def test_categorical_breakdown_recommends_barchart(self):
        """Verifies bar chart is recommended for categorical breakdown."""
        recs = recommend_charts(self.multimodal_df)
        chart_types = [r["chart_type"] for r in recs]
        self.assertIn("Bar Chart", chart_types)

    def test_multivariate_numeric_recommends_heatmap(self):
        """Verifies heatmap recommendation when >= 3 numeric features exist."""
        df_num = pd.DataFrame({
            "a": np.random.randn(30),
            "b": np.random.randn(30),
            "c": np.random.randn(30),
            "d": np.random.randn(30),
        })
        recs = recommend_charts(df_num, max_recommendations=6)
        chart_types = [r["chart_type"] for r in recs]
        self.assertIn("Correlation Heatmap", chart_types)

    def test_max_recommendations_limit(self):
        """Verifies max_recommendations parameter is respected."""
        recs_2 = recommend_charts(self.multimodal_df, max_recommendations=2)
        self.assertEqual(len(recs_2), 2)


if __name__ == "__main__":
    unittest.main()
