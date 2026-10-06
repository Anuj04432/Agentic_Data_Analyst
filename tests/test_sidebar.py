"""
Unit tests for components/sidebar.py.
Verifies metadata extraction, badge HTML formatting, safe file parsing,
and Streamlit UI rendering functions with session state interactions.
"""

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import pandas as pd
import streamlit as st

from components.sidebar import (
    format_sidebar_badge_html,
    get_dataset_metadata,
    get_supported_file_extensions,
    load_dataset_file,
    render_active_dataset_card,
    render_data_source_picker,
    render_sidebar,
)
from utils.session_state import clear_dataset, get_dataset, init_session_state, set_dataset


class TestSidebarHelpers(unittest.TestCase):
    """Test suite for pure sidebar helper functions."""

    def test_get_supported_file_extensions(self):
        """Verifies supported file extensions include standard formats."""
        exts = get_supported_file_extensions()
        self.assertIn("csv", exts)
        self.assertIn("xlsx", exts)
        self.assertIn("json", exts)
        self.assertIn("feather", exts)
        self.assertIn("sqlite", exts)

    def test_get_dataset_metadata_none_or_empty(self):
        """Verifies default metadata dict when DataFrame is None or empty."""
        meta_none = get_dataset_metadata(None, None)
        self.assertEqual(meta_none["rows"], 0)
        self.assertEqual(meta_none["columns"], 0)
        self.assertEqual(meta_none["memory"], "0 B")
        self.assertFalse(meta_none["has_data"])
        self.assertTrue(meta_none["is_empty"])
        self.assertEqual(meta_none["filename"], "No dataset loaded")

        meta_empty = get_dataset_metadata(pd.DataFrame(), "empty.csv")
        self.assertEqual(meta_empty["rows"], 0)
        self.assertFalse(meta_empty["has_data"])
        self.assertTrue(meta_empty["is_empty"])

    def test_get_dataset_metadata_with_valid_df(self):
        """Verifies accurate metadata extraction on populated DataFrame."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "score": [88.5, 92.0, 79.5],
            "category": ["A", "B", "A"],
        })
        meta = get_dataset_metadata(df, "students.csv")
        self.assertEqual(meta["rows"], 3)
        self.assertEqual(meta["columns"], 3)
        self.assertEqual(meta["filename"], "students.csv")
        self.assertTrue(meta["has_data"])
        self.assertFalse(meta["is_empty"])
        self.assertIn("id", meta["numeric_columns"])
        self.assertIn("score", meta["numeric_columns"])
        self.assertIn("category", meta["categorical_columns"])
        self.assertGreater(meta["memory_bytes"], 0)
        self.assertNotEqual(meta["memory"], "0 B")

    def test_format_sidebar_badge_html_empty(self):
        """Verifies fallback badge HTML when no dataset is loaded."""
        meta = get_dataset_metadata(None, None)
        badge_html = format_sidebar_badge_html(meta)
        self.assertIn("No dataset currently active", badge_html)

    def test_format_sidebar_badge_html_with_data(self):
        """Verifies HTML structure and sanitized filename in populated badge."""
        df = pd.DataFrame({"col_a": [10, 20], "col_b": ["x", "y"]})
        meta = get_dataset_metadata(df, "test<file>.csv")
        badge_html = format_sidebar_badge_html(meta)
        self.assertIn("Active Dataset", badge_html)
        self.assertIn("test&lt;file&gt;.csv", badge_html)
        self.assertIn("Rows:", badge_html)
        self.assertIn("Cols:", badge_html)
        self.assertIn("Memory:", badge_html)

    def test_load_dataset_file_success(self):
        """Verifies load_dataset_file safely reads a valid CSV buffer."""
        csv_data = io.StringIO("a,b\n1,2\n3,4\n")
        df, name, err = load_dataset_file(csv_data, "test.csv")
        self.assertIsNone(err)
        self.assertEqual(name, "test.csv")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ["a", "b"])

    def test_load_dataset_file_unsupported(self):
        """Verifies load_dataset_file returns error message on unsupported extension."""
        dummy = io.StringIO("dummy")
        df, name, err = load_dataset_file(dummy, "test.unknown")
        self.assertIsNone(df)
        self.assertEqual(name, "test.unknown")
        self.assertIsNotNone(err)


class TestSidebarUI(unittest.TestCase):
    """Test suite for Streamlit UI rendering functions in components/sidebar.py."""

    def setUp(self):
        # Reset session state before each test
        if hasattr(st, "session_state"):
            st.session_state.clear()
        init_session_state()

    @patch("streamlit.markdown")
    def test_render_active_dataset_card_empty(self, mock_markdown):
        """Verifies render_active_dataset_card returns False when empty."""
        has_active = render_active_dataset_card(None, None)
        self.assertFalse(has_active)
        mock_markdown.assert_called_once()
        badge_content = mock_markdown.call_args[0][0]
        self.assertIn("No dataset currently active", badge_content)

    @patch("streamlit.button", return_value=False)
    @patch("streamlit.markdown")
    def test_render_active_dataset_card_loaded(self, mock_markdown, mock_button):
        """Verifies render_active_dataset_card renders badge and button when data exists."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        has_active = render_active_dataset_card(df, "sample.csv")
        self.assertTrue(has_active)
        mock_markdown.assert_called_once()
        mock_button.assert_called_once()

    @patch("streamlit.rerun")
    @patch("streamlit.button", return_value=True)
    @patch("streamlit.markdown")
    def test_render_active_dataset_card_unload_clicked(self, mock_markdown, mock_button, mock_rerun):
        """Verifies clicking unload calls clear_dataset and st.rerun."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        set_dataset(df, "sample.csv")
        self.assertTrue(st.session_state["df"] is not None)

        render_active_dataset_card(df, "sample.csv")
        self.assertIsNone(st.session_state["df"])
        self.assertIsNone(st.session_state["filename"])
        mock_rerun.assert_called_once()

    @patch("streamlit.toast")
    @patch("streamlit.rerun")
    @patch("streamlit.spinner")
    @patch("components.sidebar.save_history")
    @patch("streamlit.file_uploader")
    @patch("streamlit.radio", return_value="📤 Upload File")
    def test_render_data_source_picker_uploader(
        self, mock_radio, mock_uploader, mock_save, mock_spinner, mock_rerun, mock_toast
    ):
        """Verifies uploading a file updates session state."""
        csv_file = io.BytesIO(b"col1,col2\n10,20\n30,40\n")
        csv_file.name = "uploaded_test.csv"
        mock_uploader.return_value = csv_file

        render_data_source_picker()

        active_df, active_name = get_dataset()
        self.assertIsNotNone(active_df)
        self.assertEqual(active_name, "uploaded_test.csv")
        self.assertEqual(len(active_df), 2)
        mock_save.assert_called_once_with(csv_file)
        mock_rerun.assert_called_once()

    @patch("streamlit.toast")
    @patch("streamlit.rerun")
    @patch("streamlit.spinner")
    @patch("components.sidebar.get_sample_file_path")
    @patch("components.sidebar.get_sample_datasets", return_value=["sample1.csv", "sample2.csv"])
    @patch("streamlit.selectbox", return_value="sample1.csv")
    @patch("streamlit.radio", return_value="📚 Sample Datasets")
    def test_render_data_source_picker_sample_select(
        self, mock_radio, mock_select, mock_samples, mock_get_path, mock_spinner, mock_rerun, mock_toast
    ):
        """Verifies selecting a sample dataset loads it and triggers rerun."""
        # Mock sample file path to a temp csv
        mock_csv_path = Path(__file__).resolve().parent / "_test_dummy.csv"
        with open(mock_csv_path, "w") as f:
            f.write("x,y\n1,2\n3,4\n")

        try:
            mock_get_path.return_value = mock_csv_path
            render_data_source_picker()

            active_df, active_name = get_dataset()
            self.assertIsNotNone(active_df)
            self.assertEqual(active_name, "sample1.csv")
            self.assertEqual(len(active_df), 2)
            mock_rerun.assert_called_once()
        finally:
            if mock_csv_path.exists():
                mock_csv_path.unlink()

    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.header")
    @patch("components.sidebar.render_data_source_picker")
    @patch("components.sidebar.render_active_dataset_card")
    def test_render_sidebar(self, mock_badge, mock_picker, mock_header, mock_sub, mock_div):
        """Verifies render_sidebar calls header, badge, and source picker."""
        df = pd.DataFrame({"a": [1, 2]})
        set_dataset(df, "demo.csv")

        ret_df, ret_name = render_sidebar(title="Test Title")
        self.assertIsNotNone(ret_df)
        self.assertEqual(ret_name, "demo.csv")
        mock_header.assert_called_once_with("Test Title")
        mock_badge.assert_called_once()
        mock_picker.assert_called_once()


if __name__ == "__main__":
    unittest.main()
