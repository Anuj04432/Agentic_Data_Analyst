"""
Unit tests for components/chat_interface.py.
Verifies message creation, validation, individual message rendering,
history iteration, and composite chat interface behavior.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
import pandas as pd
from components.chat_interface import (
    create_chat_message,
    validate_chat_message,
    render_single_message,
    render_chat_history,
    render_chat_empty_state,
    render_chat_interface,
)


class TestChatMessageModels(unittest.TestCase):
    """Test suite for message construction and validation."""

    def test_create_chat_message_defaults(self):
        """Test default values when constructing a chat message."""
        msg = create_chat_message("user", "What is the average price?")
        self.assertEqual(msg["role"], "user")
        self.assertEqual(msg["content"], "What is the average price?")
        self.assertIsNone(msg["thought"])
        self.assertIsNone(msg["code"])
        self.assertIsNone(msg["data"])
        self.assertEqual(msg["figures"], [])
        self.assertIsNone(msg["error"])

    def test_create_chat_message_full(self):
        """Test full artifact assignment in message dict."""
        sample_df = pd.DataFrame({"a": [1, 2]})
        msg = create_chat_message(
            role="assistant",
            content="Computed averages.",
            thought="Calculated group means.",
            code="df.mean()",
            data=sample_df,
            figures=["mock_fig"],
            error="None",
        )
        self.assertEqual(msg["role"], "assistant")
        self.assertEqual(msg["code"], "df.mean()")
        self.assertIs(msg["data"], sample_df)
        self.assertEqual(len(msg["figures"]), 1)

    def test_validate_chat_message_valid(self):
        """Test valid message structures return True."""
        self.assertTrue(validate_chat_message({"role": "user", "content": "hi"}))
        self.assertTrue(validate_chat_message({"role": "assistant", "content": "hello"}))
        self.assertTrue(validate_chat_message({"role": "system", "content": "instructions"}))

    def test_validate_chat_message_invalid(self):
        """Test non-dict or incomplete messages return False."""
        self.assertFalse(validate_chat_message(None))
        self.assertFalse(validate_chat_message("plain string"))
        self.assertFalse(validate_chat_message({"role": "user"}))  # missing content
        self.assertFalse(validate_chat_message({"content": "hi"}))  # missing role
        self.assertFalse(validate_chat_message({"role": "admin", "content": "hi"}))  # invalid role


class TestRenderChatMessages(unittest.TestCase):
    """Test suite for Streamlit rendering calls."""

    @patch("components.chat_interface.st")
    def test_render_single_user_message(self, mock_st):
        """Test user message triggers chat_message container and markdown."""
        mock_container = MagicMock()
        mock_st.chat_message.return_value.__enter__.return_value = mock_container

        msg = create_chat_message("user", "Show me outliers")
        render_single_message(msg)

        mock_st.chat_message.assert_called_once_with("user", avatar="🧑‍💻")
        mock_st.markdown.assert_called_with("Show me outliers")

    @patch("components.chat_interface.st")
    def test_render_single_assistant_message_with_code_and_table(self, mock_st):
        """Test assistant message renders thought, code expander, and dataframe."""
        mock_container = MagicMock()
        mock_st.chat_message.return_value.__enter__.return_value = mock_container
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander

        sample_df = pd.DataFrame({"x": [10, 20]})
        msg = create_chat_message(
            role="assistant",
            content="Found 2 outliers.",
            thought="Step 1: calculate IQR",
            code="outliers = df[df['val'] > upper]",
            data=sample_df,
        )
        render_single_message(msg)

        mock_st.chat_message.assert_called_once_with("assistant", avatar="🤖")
        mock_st.code.assert_called_once_with("outliers = df[df['val'] > upper]", language="python")
        mock_st.dataframe.assert_called_once_with(sample_df, use_container_width=True)

    @patch("components.chat_interface.st")
    def test_render_chat_history(self, mock_st):
        """Test rendering an ordered sequence of messages."""
        messages = [
            create_chat_message("user", "Hello"),
            create_chat_message("assistant", "Hi there"),
        ]
        render_chat_history(messages)
        self.assertEqual(mock_st.chat_message.call_count, 2)


class TestRenderChatInterface(unittest.TestCase):
    """Test suite for top-level chat interface widget."""

    @patch("components.chat_interface.st")
    def test_empty_messages_renders_starter_prompts(self, mock_st):
        """Test empty conversation prompts user with starter questions."""
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        mock_st.chat_input.return_value = None

        messages = []
        result = render_chat_interface(messages=messages)

        mock_st.info.assert_called_once()
        self.assertIsNone(result)

    @patch("components.chat_interface.st")
    def test_chat_input_submission(self, mock_st):
        """Test typed chat query is returned by the component."""
        mock_st.chat_input.return_value = "What is the median salary?"
        messages = [create_chat_message("user", "Previous question")]
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.return_value = False

        result = render_chat_interface(messages=messages)
        self.assertEqual(result, "What is the median salary?")


if __name__ == "__main__":
    unittest.main()
