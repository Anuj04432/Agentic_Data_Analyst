"""
Chat interface component for Agentic Data Analyst.
Provides modular Streamlit widgets for conversational data exploration,
including thought traces, collapsible code blocks, tabular views, and figure rendering.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st


def create_chat_message(
    role: str,
    content: str,
    thought: Optional[str] = None,
    code: Optional[str] = None,
    data: Optional[pd.DataFrame] = None,
    figures: Optional[List[Any]] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Constructs a standardized chat message dictionary.

    Args:
        role: Message author ("user" or "assistant").
        content: Primary markdown message content.
        thought: Optional reasoning or planning process.
        code: Optional generated Python code block.
        data: Optional DataFrame resulting from code execution.
        figures: Optional list of figures (Plotly/Matplotlib).
        error: Optional execution or generation error text.

    Returns:
        Structured message dictionary.
    """
    return {
        "role": role,
        "content": content,
        "thought": thought,
        "code": code,
        "data": data,
        "figures": figures or [],
        "error": error,
    }


def validate_chat_message(message: Any) -> bool:
    """
    Validates whether an object is a properly structured chat message.

    Args:
        message: Object to validate.

    Returns:
        True if valid message dict, False otherwise.
    """
    if not isinstance(message, dict):
        return False
    if "role" not in message or "content" not in message:
        return False
    if message["role"] not in ("user", "assistant", "system"):
        return False
    return True


def render_single_message(message: Dict[str, Any]) -> None:
    """
    Renders an individual chat message with all its rich artifacts.

    Args:
        message: Structured message dictionary.
    """
    if not validate_chat_message(message):
        return

    role = message.get("role", "assistant")
    avatar = "🧑‍💻" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        # 1. Thought / Reasoning Trace (assistant only)
        thought = message.get("thought")
        if thought and role == "assistant":
            with st.expander("💭 Agent Reasoning & Plan", expanded=False):
                st.markdown(thought)

        # 2. Primary Markdown Response
        content = message.get("content", "")
        if content:
            st.markdown(content)

        # 3. Generated Executable Code
        code = message.get("code")
        if code:
            with st.expander("💻 Generated Python Code", expanded=False):
                st.code(code, language="python")

        # 4. Resulting Data Table
        data = message.get("data")
        if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
            st.dataframe(data, use_container_width=True)

        # 5. Resulting Visualizations (Plotly or Matplotlib)
        figures = message.get("figures", [])
        if figures:
            for fig in figures:
                try:
                    # Check if Plotly figure
                    if hasattr(fig, "to_plotly_json") or "plotly" in str(type(fig)).lower():
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.pyplot(fig)
                except Exception as exc:
                    st.caption(f"⚠️ Could not render figure: {exc}")

        # 6. Error Notice
        error = message.get("error")
        if error:
            st.error(f"⚠️ **Execution Notice:** {error}")


def render_chat_history(messages: List[Dict[str, Any]]) -> None:
    """
    Renders the complete sequence of chat messages in order.

    Args:
        messages: List of structured message dictionaries.
    """
    if not messages:
        return

    for message in messages:
        render_single_message(message)


def render_chat_empty_state(
    suggested_prompts: Optional[List[str]] = None,
) -> Optional[str]:
    """
    Renders an inviting empty state with clickable prompt suggestion pills.

    Args:
        suggested_prompts: List of starter questions.

    Returns:
        Selected prompt text if clicked, else None.
    """
    st.info("👋 Ask any question about your active dataset. The agent can calculate statistics, generate charts, or extract trends.")

    default_prompts = [
        "📊 Provide an executive summary of this dataset.",
        "❓ Which columns have missing values or anomalies?",
        "🔗 What are the strongest correlations between features?",
        "📈 Plot the distribution of the primary numeric column.",
    ]
    prompts = suggested_prompts or default_prompts

    st.markdown("**Suggested questions to get started:**")
    selected_prompt: Optional[str] = None
    cols = st.columns(len(prompts))

    for idx, prompt_text in enumerate(prompts):
        with cols[idx]:
            if st.button(prompt_text, key=f"starter_prompt_{idx}", use_container_width=True):
                selected_prompt = prompt_text

    return selected_prompt


def render_chat_interface(
    messages: Optional[List[Dict[str, Any]]] = None,
    placeholder: str = "Ask a question about your data...",
    disabled: bool = False,
    key_prefix: str = "chat",
    suggested_prompts: Optional[List[str]] = None,
) -> Optional[str]:
    """
    Main composite component that manages conversation history,
    starter prompts, and the chat input bar.

    Args:
        messages: List of chat messages (defaults to st.session_state["messages"]).
        placeholder: Prompt input placeholder text.
        disabled: Whether the input widget should be disabled (e.g. while processing).
        key_prefix: Unique key prefix for widget scoping.
        suggested_prompts: Optional list of prompt suggestion strings.

    Returns:
        User prompt string if submitted this run, else None.
    """
    # Fallback to session state messages if None provided
    if messages is None:
        if "messages" not in st.session_state:
            st.session_state["messages"] = []
        messages = st.session_state["messages"]

    # Header controls (Clear conversation button)
    if messages:
        col_title, col_clear = st.columns([0.85, 0.15])
        with col_clear:
            if st.button("🗑️ Clear Chat", key=f"{key_prefix}_clear_btn", use_container_width=True):
                messages.clear()
                st.session_state["messages"] = []
                st.rerun()

    # Render history or empty state
    clicked_prompt: Optional[str] = None
    if not messages:
        clicked_prompt = render_chat_empty_state(suggested_prompts)
    else:
        render_chat_history(messages)

    # Chat Input bar
    user_query = st.chat_input(placeholder, key=f"{key_prefix}_input", disabled=disabled)

    # Return clicked prompt or typed query
    return user_query or clicked_prompt
