"""
Interactive Streamlit UI preview for testing components/chat_interface.py.
Run with:
    streamlit run tests/test_chat_interface_ui.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from components.chat_interface import (
    create_chat_message,
    render_chat_interface,
)


def init_demo_state():
    """Seed demo messages into session state if empty."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "demo_seeded" not in st.session_state:
        st.session_state["demo_seeded"] = True

        # Preload realistic conversation with code, dataframe, and chart
        df_sample = pd.DataFrame({
            "department": ["Engineering", "Sales", "Marketing", "HR"],
            "avg_salary": [115000, 92000, 84000, 71000],
            "headcount": [45, 60, 25, 12],
        })
        fig_sample = px.bar(
            df_sample,
            x="department",
            y="avg_salary",
            color="department",
            title="Average Salary by Department",
        )

        st.session_state["messages"] = [
            create_chat_message(
                role="user",
                content="What is the average salary breakdown across departments?",
            ),
            create_chat_message(
                role="assistant",
                content="Here is the breakdown of average salaries and headcount by department. Engineering has the highest compensation at $115,000, followed by Sales at $92,000.",
                thought="1. Group by department\n2. Compute mean salary and headcount count\n3. Generate bar visualization for immediate comparison",
                code="dept_summary = df.groupby('department').agg(avg_salary=('salary', 'mean'), headcount=('id', 'count')).reset_index()\nfig = px.bar(dept_summary, x='department', y='avg_salary', color='department')",
                data=df_sample,
                figures=[fig_sample],
            ),
        ]


def main():
    st.set_page_config(
        page_title="Chat Interface Component Preview",
        page_icon="💬",
        layout="wide",
    )

    st.title("💬 Chat Interface Component Preview")
    st.caption("Interactive preview for validating `components/chat_interface.py`.")

    init_demo_state()

    # Sidebar controls
    st.sidebar.header("🧪 Test Controls")
    if st.sidebar.button("➕ Inject Mock AI Response", use_container_width=True):
        st.session_state["messages"].append(
            create_chat_message(
                role="user",
                content="Check for any missing values.",
            )
        )
        missing_df = pd.DataFrame({
            "column": ["bonus", "performance_score", "department"],
            "missing_count": [12, 4, 0],
            "missing_pct": ["6.0%", "2.0%", "0.0%"],
        })
        st.session_state["messages"].append(
            create_chat_message(
                role="assistant",
                content="Found 16 missing values across 2 columns. Column `bonus` has the highest missing rate at 6.0%.",
                thought="1. Checked null count per column\n2. Filtered columns with > 0 missing values\n3. Formatted percentages",
                code="missing_summary = df.isnull().sum().to_frame(name='missing_count')\nmissing_summary['missing_pct'] = (missing_summary['missing_count'] / len(df) * 100).round(1)",
                data=missing_df,
            )
        )
        st.rerun()

    if st.sidebar.button("🔄 Reset to Default Messages", use_container_width=True):
        st.session_state["demo_seeded"] = False
        st.session_state["messages"] = []
        st.rerun()

    # Render Component
    user_prompt = render_chat_interface()

    # Handle submitted query
    if user_prompt:
        st.session_state["messages"].append(
            create_chat_message(role="user", content=user_prompt)
        )
        # Mock simulated assistant reply
        st.session_state["messages"].append(
            create_chat_message(
                role="assistant",
                content=f"Received your query: *\"{user_prompt}\"*. This preview verifies that user input streams into the conversation history seamlessly.",
                thought=f"Parsed user prompt: '{user_prompt}' -> Triggering simulated agent execution pipeline.",
                code="# Simulated agent execution\nresult = df.describe()",
            )
        )
        st.rerun()


if __name__ == "__main__":
    main()
