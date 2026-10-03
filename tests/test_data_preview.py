"""
Unit tests for components/data_preview.py.
Verifies column filtering, literal row search, pagination math,
boundary safety, and Streamlit component rendering.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import pandas as pd
from components.data_preview import (
    filter_preview_data,
    paginate_data,
    render_data_preview,
)


class TestFilterPreviewData(unittest.TestCase):
    """Test suite for filter_preview_data."""

    def setUp(self):
        self.df = pd.DataFrame({
            "name": ["Alice Smith", "Bob Jones", "Charlie Brown", "Alice Cooper"],
            "age": [25, 30, 35, 40],
            "salary": ["$1,000", "$2,500", "$3,000", "$1,000"],
            "active": [True, False, True, False],
        })

    def test_none_and_empty_dataframe(self):
        """Test that None or empty input returns an empty DataFrame."""
        self.assertTrue(filter_preview_data(None).empty)
        self.assertTrue(filter_preview_data(pd.DataFrame()).empty)

    def test_default_columns_when_none_or_empty(self):
        """Test that passing None or empty list keeps all columns."""
        res_none = filter_preview_data(self.df, selected_columns=None)
        self.assertEqual(list(res_none.columns), list(self.df.columns))

        res_empty = filter_preview_data(self.df, selected_columns=[])
        self.assertEqual(list(res_empty.columns), list(self.df.columns))

    def test_selected_columns_subset(self):
        """Test projecting a subset of valid columns."""
        res = filter_preview_data(self.df, selected_columns=["name", "age"])
        self.assertEqual(list(res.columns), ["name", "age"])
        self.assertEqual(len(res), 4)

    def test_invalid_selected_columns_fallback(self):
        """Test fallback when given column names that don't exist in DataFrame."""
        res = filter_preview_data(self.df, selected_columns=["non_existent_col"])
        self.assertEqual(list(res.columns), list(self.df.columns))

    def test_empty_and_whitespace_search_term(self):
        """Test that None, empty string, or whitespace query returns all rows."""
        self.assertEqual(len(filter_preview_data(self.df, search_term=None)), 4)
        self.assertEqual(len(filter_preview_data(self.df, search_term="")), 4)
        self.assertEqual(len(filter_preview_data(self.df, search_term="   ")), 4)

    def test_case_insensitive_literal_search(self):
        """Test search is case-insensitive across all column types."""
        # Lowercase search matches "Alice Smith" and "Alice Cooper"
        res_alice = filter_preview_data(self.df, search_term="alice")
        self.assertEqual(len(res_alice), 2)

        # Number search matches age 30 ("Bob Jones")
        res_num = filter_preview_data(self.df, search_term="30")
        self.assertEqual(len(res_num), 1)

        # Substring search matches "Brown"
        res_brown = filter_preview_data(self.df, search_term="brown")
        self.assertEqual(len(res_brown), 1)

    def test_regex_special_characters_search(self):
        """Test that special regex characters ($?*()) don't cause errors."""
        res = filter_preview_data(self.df, search_term="$1,000")
        self.assertEqual(len(res), 2)

        # Characters that would break regex if regex=True
        res_bracket = filter_preview_data(self.df, search_term="[unknown]")
        self.assertEqual(len(res_bracket), 0)

    def test_search_with_column_subset(self):
        """Test search restricted to selected columns."""
        # "Bob" is in 'name', but if we only select 'age' and 'salary', it shouldn't match
        res = filter_preview_data(self.df, search_term="Bob", selected_columns=["age", "salary"])
        self.assertEqual(len(res), 0)


class TestPaginateData(unittest.TestCase):
    """Test suite for paginate_data."""

    def setUp(self):
        self.df = pd.DataFrame({"id": list(range(1, 101))})  # 100 rows

    def test_empty_or_none_df(self):
        """Test that empty or None returns empty df and zeroed metadata."""
        sliced_df, meta = paginate_data(None)
        self.assertTrue(sliced_df.empty)
        self.assertEqual(meta["total_rows"], 0)
        self.assertEqual(meta["total_pages"], 1)

    def test_all_page_size(self):
        """Test selecting 'All' rows."""
        sliced_df, meta = paginate_data(self.df, page_size="All")
        self.assertEqual(len(sliced_df), 100)
        self.assertEqual(meta["total_pages"], 1)
        self.assertEqual(meta["page"], 1)
        self.assertEqual(meta["display_start"], 1)
        self.assertEqual(meta["display_end"], 100)
        self.assertFalse(meta["has_prev"])
        self.assertFalse(meta["has_next"])

    def test_pagination_pages(self):
        """Test standard page slicing and metadata."""
        sliced_df, meta = paginate_data(self.df, page=2, page_size=20)
        self.assertEqual(len(sliced_df), 20)
        self.assertEqual(meta["total_pages"], 5)
        self.assertEqual(meta["page"], 2)
        self.assertEqual(meta["display_start"], 21)
        self.assertEqual(meta["display_end"], 40)
        self.assertTrue(meta["has_prev"])
        self.assertTrue(meta["has_next"])

    def test_last_page_partial_slice(self):
        """Test last page slice when total rows is not an exact multiple."""
        df_35 = pd.DataFrame({"id": list(range(35))})
        sliced_df, meta = paginate_data(df_35, page=4, page_size=10)
        self.assertEqual(len(sliced_df), 5)
        self.assertEqual(meta["total_pages"], 4)
        self.assertEqual(meta["page"], 4)
        self.assertEqual(meta["display_start"], 31)
        self.assertEqual(meta["display_end"], 35)
        self.assertTrue(meta["has_prev"])
        self.assertFalse(meta["has_next"])

    def test_out_of_bounds_page_clamping(self):
        """Test page number clamping below 1 and above total_pages."""
        # Page < 1 clamps to 1
        _, meta_low = paginate_data(self.df, page=-5, page_size=25)
        self.assertEqual(meta_low["page"], 1)

        # Page > total_pages clamps to total_pages
        _, meta_high = paginate_data(self.df, page=999, page_size=25)
        self.assertEqual(meta_high["page"], 4)


class TestRenderDataPreview(unittest.TestCase):
    """Test suite for render_data_preview Streamlit UI."""

    @patch("components.data_preview.st.info")
    def test_empty_df_shows_info(self, mock_info):
        """Test that empty dataset renders st.info and returns empty DataFrame."""
        res = render_data_preview(None)
        mock_info.assert_called_once()
        self.assertTrue(res.empty)

    @patch("components.data_preview.st.download_button")
    @patch("components.data_preview.st.dataframe")
    @patch("components.data_preview.st.selectbox")
    @patch("components.data_preview.st.multiselect")
    @patch("components.data_preview.st.text_input")
    @patch("components.data_preview.st.columns")
    def test_populated_dataframe_renders_ui(
        self,
        mock_cols,
        mock_text,
        mock_multi,
        mock_select,
        mock_df,
        mock_download,
    ):
        """Test that valid DataFrame renders search, table, and download button."""
        mock_cols.side_effect = lambda spec: [MagicMock() for _ in range(len(spec) if isinstance(spec, list) else spec)]
        mock_text.return_value = ""
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["A", "B", "C"]})
        mock_multi.return_value = list(df.columns)
        mock_select.return_value = 25

        res = render_data_preview(df)

        self.assertEqual(len(res), 3)
        mock_df.assert_called_once()
        mock_download.assert_called_once()


if __name__ == "__main__":
    unittest.main()
