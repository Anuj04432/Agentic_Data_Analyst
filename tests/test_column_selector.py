"""
Unit tests for components/column_selector.py.
Verifies column type classification, type-based filtering, exclusion lists,
and Streamlit UI rendering functions (single-select, multiselect, and type-aware).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import pandas as pd
from components.column_selector import (
    classify_columns,
    filter_columns_by_type,
    render_column_select,
    render_column_multiselect,
    render_type_aware_selector,
)


class TestClassifyColumns(unittest.TestCase):
    """Test suite for classify_columns."""

    def setUp(self):
        self.mixed_df = pd.DataFrame({
            "age": [25, 30, 35],
            "salary": [50000.0, 60000.0, 75000.0],
            "name": ["Alice", "Bob", "Charlie"],
            "dept": pd.Series(["HR", "Engineering", "Marketing"], dtype="category"),
            "join_date": pd.to_datetime(["2020-01-15", "2021-06-01", "2022-11-20"]),
            "is_active": [True, False, True],
        })

    def test_none_and_empty_dataframe(self):
        """Test that None or empty input returns empty lists for all categories."""
        expected_empty = {
            "all": [],
            "numeric": [],
            "categorical": [],
            "datetime": [],
            "boolean": [],
        }
        self.assertEqual(classify_columns(None), expected_empty)
        self.assertEqual(classify_columns(pd.DataFrame()), expected_empty)

    def test_mixed_dataframe_classification(self):
        """Test accurate classification across all analytical data types."""
        result = classify_columns(self.mixed_df)

        self.assertEqual(result["all"], ["age", "salary", "name", "dept", "join_date", "is_active"])
        self.assertEqual(result["numeric"], ["age", "salary"])
        self.assertEqual(result["categorical"], ["name", "dept"])
        self.assertEqual(result["datetime"], ["join_date"])
        self.assertEqual(result["boolean"], ["is_active"])

    def test_single_type_dataframe(self):
        """Test dataset containing only numeric columns."""
        num_df = pd.DataFrame({"a": [1, 2], "b": [3.5, 4.2]})
        result = classify_columns(num_df)

        self.assertEqual(result["numeric"], ["a", "b"])
        self.assertEqual(result["categorical"], [])
        self.assertEqual(result["datetime"], [])
        self.assertEqual(result["boolean"], [])
        self.assertEqual(result["all"], ["a", "b"])


class TestFilterColumnsByType(unittest.TestCase):
    """Test suite for filter_columns_by_type."""

    def setUp(self):
        self.df = pd.DataFrame({
            "id": [1, 2, 3],
            "score": [88.5, 92.0, 79.5],
            "category": ["A", "B", "A"],
            "created_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
            "flag": [True, True, False],
        })

    def test_none_or_empty_dataframe(self):
        """Test that None or empty DataFrame returns an empty list."""
        self.assertEqual(filter_columns_by_type(None), [])
        self.assertEqual(filter_columns_by_type(pd.DataFrame()), [])

    def test_filter_all_types(self):
        """Test standard filter keywords."""
        self.assertEqual(filter_columns_by_type(self.df, "all"), ["id", "score", "category", "created_at", "flag"])
        self.assertEqual(filter_columns_by_type(self.df, "numeric"), ["id", "score"])
        self.assertEqual(filter_columns_by_type(self.df, "categorical"), ["category"])
        self.assertEqual(filter_columns_by_type(self.df, "datetime"), ["created_at"])
        self.assertEqual(filter_columns_by_type(self.df, "boolean"), ["flag"])

    def test_filter_type_aliases(self):
        """Test recognized type aliases and case-insensitivity."""
        self.assertEqual(filter_columns_by_type(self.df, "NUM"), ["id", "score"])
        self.assertEqual(filter_columns_by_type(self.df, "num"), ["id", "score"])
        self.assertEqual(filter_columns_by_type(self.df, "cat"), ["category"])
        self.assertEqual(filter_columns_by_type(self.df, "date"), ["created_at"])
        self.assertEqual(filter_columns_by_type(self.df, "bool"), ["flag"])
        self.assertEqual(filter_columns_by_type(self.df, "*"), ["id", "score", "category", "created_at", "flag"])

    def test_unknown_type_defaults_to_all(self):
        """Test that an unrecognized type falls back to all columns."""
        self.assertEqual(filter_columns_by_type(self.df, "unknown_type"), ["id", "score", "category", "created_at", "flag"])

    def test_exclude_columns(self):
        """Test excluding specific columns from candidate list."""
        # Exclude 'id' from numeric
        num_res = filter_columns_by_type(self.df, "numeric", exclude=["id"])
        self.assertEqual(num_res, ["score"])

        # Exclude multiple across all
        all_res = filter_columns_by_type(self.df, "all", exclude=["id", "flag"])
        self.assertEqual(all_res, ["score", "category", "created_at"])

        # Exclude non-existent column causes no error
        res_non_exist = filter_columns_by_type(self.df, "numeric", exclude=["ghost_col"])
        self.assertEqual(res_non_exist, ["id", "score"])


class TestRenderColumnSelect(unittest.TestCase):
    """Test suite for render_column_select with Streamlit mocked."""

    def setUp(self):
        self.df = pd.DataFrame({
            "feature1": [1.0, 2.0],
            "feature2": [10, 20],
            "text_col": ["a", "b"],
        })

    @patch("streamlit.info")
    def test_none_df_returns_none(self, mock_info):
        """Test that None DataFrame renders info message and returns None."""
        res = render_column_select(None)
        self.assertIsNone(res)
        mock_info.assert_called_once()

    @patch("streamlit.warning")
    def test_no_matching_columns_returns_none(self, mock_warning):
        """Test that absence of requested column type displays warning and returns None."""
        res = render_column_select(self.df, column_type="datetime")
        self.assertIsNone(res)
        mock_warning.assert_called_once()

    @patch("streamlit.selectbox")
    def test_successful_selection(self, mock_selectbox):
        """Test valid column selection returns chosen column."""
        mock_selectbox.return_value = "feature2"
        res = render_column_select(self.df, column_type="numeric", default="feature2")

        self.assertEqual(res, "feature2")
        mock_selectbox.assert_called_once()
        args, kwargs = mock_selectbox.call_args
        self.assertEqual(kwargs["options"], ["feature1", "feature2"])
        self.assertEqual(kwargs["index"], 1)

    @patch("streamlit.selectbox")
    def test_allow_none_selection(self, mock_selectbox):
        """Test allow_none prepends placeholder and returns None when selected."""
        mock_selectbox.return_value = "-- Select a column --"
        res = render_column_select(self.df, column_type="numeric", allow_none=True)

        self.assertIsNone(res)
        _, kwargs = mock_selectbox.call_args
        self.assertTrue("-- Select a column --" in kwargs["options"])


class TestRenderColumnMultiselect(unittest.TestCase):
    """Test suite for render_column_multiselect with Streamlit mocked."""

    def setUp(self):
        self.df = pd.DataFrame({
            "col1": [1, 2],
            "col2": [3, 4],
            "col3": [5, 6],
            "text": ["x", "y"],
        })

    @patch("streamlit.info")
    def test_none_df_returns_empty_list(self, mock_info):
        """Test None DataFrame returns empty list."""
        res = render_column_multiselect(None)
        self.assertEqual(res, [])
        mock_info.assert_called_once()

    @patch("streamlit.multiselect")
    def test_default_all_selection(self, mock_multiselect):
        """Test default_all selects all candidate columns by default."""
        mock_multiselect.return_value = ["col1", "col2", "col3"]
        res = render_column_multiselect(self.df, column_type="numeric", default_all=True)

        self.assertEqual(res, ["col1", "col2", "col3"])
        _, kwargs = mock_multiselect.call_args
        self.assertEqual(kwargs["default"], ["col1", "col2", "col3"])

    @patch("streamlit.multiselect")
    def test_default_columns_sanitization(self, mock_multiselect):
        """Test passing invalid column in default_columns gets pruned."""
        mock_multiselect.return_value = ["col1"]
        res = render_column_multiselect(
            self.df,
            column_type="numeric",
            default_columns=["col1", "invalid_col"],
        )

        self.assertEqual(res, ["col1"])
        _, kwargs = mock_multiselect.call_args
        self.assertEqual(kwargs["default"], ["col1"])


class TestRenderTypeAwareSelector(unittest.TestCase):
    """Test suite for render_type_aware_selector."""

    def setUp(self):
        self.df = pd.DataFrame({
            "num1": [1, 2],
            "cat1": ["a", "b"],
        })

    @patch("streamlit.pills", create=True)
    @patch("streamlit.selectbox")
    def test_type_aware_single_select(self, mock_selectbox, mock_pills):
        """Test type switcher filters single select."""
        mock_pills.return_value = "Numeric"
        mock_selectbox.return_value = "num1"

        res = render_type_aware_selector(self.df, multiselect=False)
        self.assertEqual(res, "num1")

    @patch("streamlit.pills", create=True)
    @patch("streamlit.multiselect")
    def test_type_aware_multiselect(self, mock_multiselect, mock_pills):
        """Test type switcher filters multiselect."""
        mock_pills.return_value = "Categorical"
        mock_multiselect.return_value = ["cat1"]

        res = render_type_aware_selector(self.df, multiselect=True)
        self.assertEqual(res, ["cat1"])


if __name__ == "__main__":
    unittest.main()
