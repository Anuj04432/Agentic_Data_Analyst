"""
Unit tests for visualization/charts.py.

Verifies figure generation, edge cases, input validation, and the master
build_chart_from_config dispatcher.
"""

import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from visualization.charts import (
    create_histogram,
    create_boxplot,
    create_scatterplot,
    create_barchart,
    create_linechart,
    create_piechart,
    create_correlation_heatmap,
    build_chart_from_config,
)


class TestPlotlyCharts(unittest.TestCase):
    """Test suite for standardized Plotly chart builders."""

    def setUp(self):
        """Set up test dataset."""
        np.random.seed(42)
        n = 40
        self.df = pd.DataFrame({
            "age": np.random.randint(20, 65, size=n),
            "salary": np.random.uniform(30000, 120000, size=n),
            "department": np.random.choice(["IT", "HR", "Sales", "Finance"], size=n),
            "rating": np.random.choice([1, 2, 3, 4, 5], size=n),
            "date": pd.date_range("2025-01-01", periods=n, freq="D"),
        })

    def test_create_histogram_success(self):
        """Verifies histogram construction."""
        fig = create_histogram(self.df, x="age", bins=15, title="Age Dist")
        self.assertIsInstance(fig, go.Figure)
        self.assertIn("Age Dist", fig.layout.title.text)

    def test_create_histogram_with_color(self):
        """Verifies histogram with hue/color grouping."""
        fig = create_histogram(self.df, x="salary", color="department")
        self.assertIsInstance(fig, go.Figure)

    def test_create_histogram_empty_or_missing_col(self):
        """Verifies error handling for empty df and invalid column."""
        with self.assertRaises(ValueError):
            create_histogram(pd.DataFrame(), x="age")
        with self.assertRaises(ValueError):
            create_histogram(self.df, x="non_existent")

    def test_create_boxplot_success(self):
        """Verifies box plot construction."""
        fig = create_boxplot(self.df, y="salary", x="department", title="Salary Spread")
        self.assertIsInstance(fig, go.Figure)
        self.assertIn("Salary Spread", fig.layout.title.text)

    def test_create_boxplot_single_col(self):
        """Verifies single-column box plot without category grouping."""
        fig = create_boxplot(self.df, y="salary")
        self.assertIsInstance(fig, go.Figure)

    def test_create_scatterplot_success(self):
        """Verifies scatter plot construction."""
        fig = create_scatterplot(self.df, x="age", y="salary", color="department")
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(fig.layout.xaxis.title.text, "age")
        self.assertEqual(fig.layout.yaxis.title.text, "salary")

    def test_create_scatterplot_missing_col(self):
        """Verifies scatter plot raises ValueError on invalid column."""
        with self.assertRaises(ValueError):
            create_scatterplot(self.df, x="age", y="non_existent")

    def test_create_barchart_counts(self):
        """Verifies bar chart row count aggregation."""
        fig = create_barchart(self.df, x="department")
        self.assertIsInstance(fig, go.Figure)

    def test_create_barchart_aggregations(self):
        """Verifies bar chart metric aggregations (mean, sum, median)."""
        fig_mean = create_barchart(self.df, x="department", y="salary", agg="mean")
        self.assertIsInstance(fig_mean, go.Figure)

        fig_sum = create_barchart(self.df, x="department", y="salary", agg="sum")
        self.assertIsInstance(fig_sum, go.Figure)

        fig_median = create_barchart(self.df, x="department", y="salary", agg="median")
        self.assertIsInstance(fig_median, go.Figure)

    def test_create_barchart_horizontal(self):
        """Verifies horizontal bar chart orientation."""
        fig = create_barchart(self.df, x="department", orientation="h")
        self.assertIsInstance(fig, go.Figure)

    def test_create_linechart_success(self):
        """Verifies line chart construction."""
        fig = create_linechart(self.df, x="date", y="salary", color="department")
        self.assertIsInstance(fig, go.Figure)

    def test_create_piechart_counts(self):
        """Verifies pie/donut chart frequency generation."""
        fig = create_piechart(self.df, names="department")
        self.assertIsInstance(fig, go.Figure)

    def test_create_piechart_with_values(self):
        """Verifies pie/donut chart weighted by numeric values."""
        fig = create_piechart(self.df, names="department", values="salary")
        self.assertIsInstance(fig, go.Figure)

    def test_create_correlation_heatmap_success(self):
        """Verifies correlation heatmap generation."""
        fig = create_correlation_heatmap(self.df, columns=["age", "salary", "rating"])
        self.assertIsInstance(fig, go.Figure)

    def test_create_correlation_heatmap_insufficient_numeric_cols(self):
        """Verifies error when fewer than 2 numeric features are present."""
        sub_df = self.df[["department"]]
        with self.assertRaises(ValueError):
            create_correlation_heatmap(sub_df)

    def test_build_chart_from_config_all_types(self):
        """Verifies the master build_chart_from_config dispatcher across all chart types."""
        test_configs = [
            {"chart_type": "Histogram", "x": "age", "bins": 20},
            {"chart_type": "Box Plot", "x": "department", "y": "salary"},
            {"chart_type": "Scatter Plot", "x": "age", "y": "salary", "color": "department"},
            {"chart_type": "Bar Chart", "x": "department", "y": "salary", "agg": "mean"},
            {"chart_type": "Line Chart", "x": "date", "y": "salary"},
            {"chart_type": "Pie / Donut Chart", "x": "department", "y": None},
            {"chart_type": "Correlation Heatmap", "columns": ["age", "salary", "rating"]},
        ]

        for config in test_configs:
            with self.subTest(chart_type=config["chart_type"]):
                fig = build_chart_from_config(self.df, config)
                self.assertIsInstance(fig, go.Figure)

    def test_build_chart_from_config_invalid(self):
        """Verifies dispatcher error on unsupported chart type or empty config."""
        with self.assertRaises(ValueError):
            build_chart_from_config(self.df, {})

        with self.assertRaises(ValueError):
            build_chart_from_config(self.df, {"chart_type": "Radar Chart"})


if __name__ == "__main__":
    unittest.main()
