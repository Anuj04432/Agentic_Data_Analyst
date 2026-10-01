import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import pandas as pd
import numpy as np
from analysis.profiling import calculate_health_score, generate_dataset_audit


class TestCalculateHealthScore(unittest.TestCase):
    """Test suite for calculate_health_score in analysis/profiling.py."""

    def test_empty_and_none(self):
        """Test that empty or None DataFrame returns the default structure."""
        res_none = calculate_health_score(None)
        self.assertEqual(res_none["health_score"], 0.0)
        self.assertEqual(res_none["grade"], "N/A")
        self.assertEqual(res_none["summary"], "Dataset is empty or None.")
        self.assertEqual(res_none["deductions"]["missing"], 0.0)

        res_empty = calculate_health_score(pd.DataFrame())
        self.assertEqual(res_empty["health_score"], 0.0)
        self.assertEqual(res_empty["grade"], "N/A")

    def test_perfect_dataset(self):
        """Test a clean dataset with no missing values, duplicates, outliers, or constants."""
        df = pd.DataFrame({
            "feature1": [10, 20, 30, 40, 50, 60, 70, 80],
            "feature2": [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8],
            "category": ["A", "B", "C", "D", "E", "F", "G", "H"],
        })
        res = calculate_health_score(df)
        self.assertEqual(res["health_score"], 100.0)
        self.assertEqual(res["grade"], "A")
        self.assertEqual(res["deductions"]["missing"], 0.0)
        self.assertEqual(res["deductions"]["duplicates"], 0.0)
        self.assertEqual(res["deductions"]["outliers"], 0.0)
        self.assertEqual(res["deductions"]["constant_cols"], 0.0)
        self.assertIn("excellent condition", res["summary"].lower())

    def test_missing_values_deduction(self):
        """Test missing values deduction: min(30.0, round(missing_pct * 1.5, 1))."""
        # 10 rows, 2 columns = 20 total cells. 2 missing cells = 10% missing.
        # Expected deduction: 10 * 1.5 = 15.0
        df = pd.DataFrame({
            "a": [1, 2, 3, 4, 5, 6, 7, 8, None, 10],
            "b": [1, 2, 3, 4, 5, 6, 7, 8, 9, None],
        })
        res = calculate_health_score(df)
        self.assertEqual(res["deductions"]["missing"], 15.0)

    def test_duplicate_rows_deduction(self):
        """Test duplicate rows deduction: min(20.0, round(duplicate_pct * 2.0, 1))."""
        # 10 rows, 1 duplicate row = 10% duplicates.
        # Expected deduction: 10 * 2.0 = 20.0
        df = pd.DataFrame({
            "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 9],
            "b": [10, 20, 30, 40, 50, 60, 70, 80, 90, 90],
        })
        res = calculate_health_score(df)
        self.assertEqual(res["deductions"]["duplicates"], 20.0)

    def test_outliers_deduction(self):
        """
        Test outlier deduction: min(20.0, round((cols_with_severe_outliers / total_num_cols) * 20.0, 1)).
        1 out of 2 numeric columns has severe outliers (>5% outlier rate).
        Expected deduction: (1 / 2) * 20.0 = 10.0 points.
        """
        vals = [10, 11, 12, 11, 10, 12, 11, 10, 12, 11, 10, 12, 11, 10, 12, 11, 10, 12, 100, 150]
        df = pd.DataFrame({
            "col1": vals,
            "col2": list(range(20)),
        })
        res = calculate_health_score(df)
        self.assertEqual(res["deductions"]["outliers"], 10.0)

    def test_no_numeric_columns(self):
        """Test that datasets with only categorical columns incur 0 outlier deduction."""
        df = pd.DataFrame({
            "cat1": ["apple", "banana", "cherry", "date"],
            "cat2": ["red", "yellow", "red", "brown"],
        })
        res = calculate_health_score(df)
        self.assertEqual(res["deductions"]["outliers"], 0.0)

    def test_constant_columns_deduction(self):
        """Test constant column deduction: min(15.0, round(constant_cols_count * 5.0, 1))."""
        # 1 constant column -> 5.0 deduction
        df = pd.DataFrame({
            "varying": [1, 2, 3, 4, 5, 6],
            "constant": [99, 99, 99, 99, 99, 99],
        })
        res = calculate_health_score(df)
        self.assertEqual(res["deductions"]["constant_cols"], 5.0)

    def test_deduction_caps(self):
        """Test that all deductions respect their maximum caps (30, 20, 20, 15) and floor of 0."""
        # 100% missing dataset
        df = pd.DataFrame({
            "a": [np.nan, np.nan, np.nan, np.nan],
            "b": [np.nan, np.nan, np.nan, np.nan],
        })
        res = calculate_health_score(df)
        self.assertLessEqual(res["deductions"]["missing"], 30.0)
        self.assertLessEqual(res["deductions"]["duplicates"], 20.0)
        self.assertLessEqual(res["deductions"]["outliers"], 20.0)
        self.assertLessEqual(res["deductions"]["constant_cols"], 15.0)
        self.assertGreaterEqual(res["health_score"], 0.0)

    def test_grade_mapping(self):
        """Test letter grade assignments for various score thresholds (A, B, C, D, F)."""
        # Grade A: 90 - 100
        df_a = pd.DataFrame({"a": range(10), "b": range(10)})
        self.assertEqual(calculate_health_score(df_a)["grade"], "A")

        # Grade B: 80 - 89 (deduct 15 via missing)
        # 20 rows, 2 cols = 40 cells. 4 missing = 10%. Deduct 15. Score 85.
        df_b = pd.DataFrame({
            "id": list(range(20)),
            "val": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, None, None, None, None],
        })
        res_b = calculate_health_score(df_b)
        self.assertEqual(res_b["grade"], "B")
        self.assertEqual(res_b["health_score"], 85.0)

        # Grade F: < 60 (100% missing -> missing=30, constant=10, duplicates=20 -> total=60 -> score 40)
        df_f = pd.DataFrame({"a": [np.nan] * 10, "b": [np.nan] * 10})
        res_f = calculate_health_score(df_f)
        self.assertEqual(res_f["grade"], "F")
        self.assertLess(res_f["health_score"], 60.0)

    def test_summary_reflects_issues(self):
        """Test that the summary string mentions the specific issues detected."""
        df = pd.DataFrame({
            "a": [1, 1, 1, 1, 1, 1],
            "b": [1, 2, None, 4, 5, 6],
        })
        res = calculate_health_score(df)
        summary = res["summary"].lower()
        self.assertIn("penalties applied for", summary)
        self.assertTrue("constant" in summary or "missing" in summary)


class TestGenerateDatasetAudit(unittest.TestCase):
    """Test suite for generate_dataset_audit in analysis/profiling.py."""

    def test_audit_empty_and_none(self):
        """Test that empty and None DataFrame returns safe audit default structure."""
        res_none = generate_dataset_audit(None)
        self.assertEqual(res_none["shape"]["rows"], 0)
        self.assertEqual(res_none["shape"]["columns"], 0)
        self.assertEqual(res_none["memory"]["formatted"], "0 B")
        self.assertIn("warnings", res_none)
        self.assertEqual(res_none["warnings"], ["Dataset is empty or None."])

        res_empty = generate_dataset_audit(pd.DataFrame())
        self.assertEqual(res_empty["shape"]["rows"], 0)
        self.assertEqual(res_empty["warnings"], ["Dataset is empty or None."])

    def test_audit_shape_and_memory(self):
        """Test shape and memory calculations."""
        df = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": ["x", "y", "z", "w", "v"],
        })
        res = generate_dataset_audit(df)
        self.assertEqual(res["shape"]["rows"], 5)
        self.assertEqual(res["shape"]["columns"], 2)
        self.assertGreater(res["memory"]["bytes"], 0)
        self.assertTrue(res["memory"]["formatted"].endswith("B"))

    def test_audit_column_types(self):
        """Test column type classification."""
        df = pd.DataFrame({
            "num": [1, 2, 3],
            "cat": ["a", "b", "c"],
            "flag": [True, False, True],
        })
        res = generate_dataset_audit(df)
        self.assertIn("num", res["column_types"]["num_cols"])
        self.assertIn("cat", res["column_types"]["cat_cols"])
        self.assertIn("flag", res["column_types"]["boolean"])

    def test_audit_duplicates(self):
        """Test duplicates summary in audit."""
        df = pd.DataFrame({
            "a": [1, 2, 2],
            "b": [10, 20, 20],
        })
        res = generate_dataset_audit(df)
        self.assertEqual(res["duplicates"]["duplicate_count"], 1)
        self.assertTrue(res["duplicates"]["has_duplicates"])
        self.assertAlmostEqual(res["duplicates"]["duplicate_pct"], 33.33, places=1)

    def test_audit_warnings(self):
        """Test actionable warnings generation."""
        # 10 rows:
        # col_high_missing has 5 missing (>30%)
        # col_constant has identical value across all 10 rows
        # col_outlier has severe outlier (100)
        # col_corr1 and col_corr2 are perfectly correlated (r = 1.0)
        df = pd.DataFrame({
            "col_corr1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "col_corr2": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "col_high_missing": [None, None, None, None, None, "a", "b", "c", "d", "e"],
            "col_constant": ["fixed"] * 10,
            "col_outlier": [10, 10, 11, 10, 11, 10, 11, 10, 11, 150],
        })
        res = generate_dataset_audit(df)
        warnings_text = " ".join(res["warnings"]).lower()

        # Check high missing warning
        self.assertIn("high missing data", warnings_text)
        self.assertIn("col_high_missing", warnings_text)

        # Check constant column warning
        self.assertIn("constant", warnings_text)
        self.assertIn("col_constant", warnings_text)

        # Check severe outlier warning
        self.assertIn("severe outliers", warnings_text)
        self.assertIn("col_outlier", warnings_text)

        # Check multicollinearity warning
        self.assertIn("multicollinearity", warnings_text)

    def test_audit_health_integration(self):
        """Test health score integration within the audit."""
        df = pd.DataFrame({"a": range(10), "b": range(10)})
        res = generate_dataset_audit(df)
        self.assertEqual(res["health"]["health_score"], 100.0)
        self.assertEqual(res["health"]["grade"], "A")


if __name__ == "__main__":
    unittest.main()
