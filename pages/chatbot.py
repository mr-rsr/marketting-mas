import asyncio
import os

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from fpdf import FPDF

from graph.graph import graph
from supabase_client import (
    get_current_user,
    sign_out,
    create_conversation,
    get_conversations,
    get_messages,
    save_message,
    update_conversation_title,
    delete_conversation,
)

# ---------------------------------------------------------------------------
# Auth guard — redirect if not logged in
# ---------------------------------------------------------------------------
user = get_current_user()
if not user:
    st.warning("Please log in to access the chatbot.")
    st.switch_page("pages/login.py")
    st.stop()


# ---------------------------------------------------------------------------
# Helper — load a conversation from DB into session state
# ---------------------------------------------------------------------------
def _load_conversation(conversation_id: str):
    """Load messages from Supabase into session state."""
    st.session_state["current_conversation_id"] = conversation_id
    db_messages = get_messages(conversation_id)
    lang_messages = []
    display_history = []
    for msg in db_messages:
        role = msg["role"]
        content = msg["content"]
        logo_url = msg.get("logo_url")

        if role == "user":
            lang_messages.append(HumanMessage(content=content))
            display_history.append(("user", content))
        else:
            lang_messages.append(AIMessage(content=content))
            extras = {}
            if logo_url:
                extras["logo_url"] = logo_url
            display_history.append(("assistant", {"text": content, **extras}))

    st.session_state["messages"] = lang_messages
    st.session_state["display_history"] = display_history


# ---------------------------------------------------------------------------
# Helper — build PDF from conversation
# ---------------------------------------------------------------------------
def _build_pdf() -> bytes:
    """Generate a PDF of the current conversation."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Marketing Plan", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    for role, content in st.session_state.get("display_history", []):
        text = content["text"] if isinstance(content, dict) else content
        pdf.set_font("Helvetica", "B", 11)
        label = "You" if role == "user" else "AI Consultant"
        pdf.cell(0, 8, f"{label}:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        # Encode to latin-1 for fpdf compatibility, replace unsupported chars
        safe_text = text.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_text)
        pdf.ln(3)

    return pdf.output()


# ---------------------------------------------------------------------------
# Render extras (logo images)
# ---------------------------------------------------------------------------
def _render_extras(extras: dict):
    logo_url = extras.get("logo_url")
    if logo_url:
        st.image(logo_url, caption="Generated Logo", width=300)
    elif extras.get("show_logo") and os.path.exists("logo.png"):
        st.image("logo.png", caption="Generated Logo", width=300)


# ---------------------------------------------------------------------------
# Streaming helper
# ---------------------------------------------------------------------------
async def run_agent_stream(messages):
    """Stream tokens from the graph using astream_events."""
    full_response = ""
    placeholder = st.empty()

    async for event in graph.astream_events(
        {"messages": messages},
        version="v2",
    ):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            content = chunk.content
            if isinstance(content, list):
                text = "".join(
                    block.get("text", "") if isinstance(block, dict) else str(block)
                    for block in content
                )
            else:
                text = content or ""
            if text:
                full_response += text
                placeholder.markdown(full_response + "▌")

        elif kind == "on_tool_start":
            tool_name = event.get("name", "tool")
            placeholder.markdown(full_response + f"\n\n⏳ *Running {tool_name}...*")

    placeholder.markdown(full_response)
    return full_response


# ---------------------------------------------------------------------------
# Initialise session state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "display_history" not in st.session_state:
    st.session_state.display_history = []


# ---------------------------------------------------------------------------
# Sidebar — user info, conversation list, new chat, logout
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"**Logged in as** {user['email']}")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.pop("current_conversation_id", None)
        st.session_state["messages"] = []
        st.session_state["display_history"] = []
        st.rerun()

    st.divider()
    st.subheader("Conversations")

    conversations = get_conversations(user["id"])
    current_conv_id = st.session_state.get("current_conversation_id")

    for conv in conversations:
        col_title, col_del = st.columns([5, 1])
        with col_title:
            label = conv["title"] or "Untitled"
            is_active = conv["id"] == current_conv_id
            if st.button(
                f"{'▶ ' if is_active else ''}{label}",
                key=f"conv_{conv['id']}",
                use_container_width=True,
            ):
                _load_conversation(conv["id"])
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{conv['id']}"):
                delete_conversation(conv["id"])
                if current_conv_id == conv["id"]:
                    st.session_state.pop("current_conversation_id", None)
                    st.session_state["messages"] = []
                    st.session_state["display_history"] = []
                st.rerun()

    st.divider()

    # Export to PDF button — only build PDF when user clicks
    if st.session_state.get("display_history"):
        if st.button("📄 Export to PDF", use_container_width=True):
            pdf_bytes = _build_pdf()
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name="marketing_plan.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    if st.button("Logout", use_container_width=True):
        sign_out()
        st.rerun()


# ---------------------------------------------------------------------------
# Chat header
# ---------------------------------------------------------------------------
st.title("💬 Marketing Agency AI Assistant")
st.caption("Powered by AWS Bedrock + LangGraph")


# ---------------------------------------------------------------------------
# Render existing messages
# ---------------------------------------------------------------------------
for role, content in st.session_state.display_history:
    with st.chat_message(role):
        if isinstance(content, dict):
            st.write(content["text"])
            _render_extras(content)
        else:
            st.write(content)


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
if prompt := st.chat_input("Ask about domains, logos, strategy, social media, email campaigns, SEO, ads, or taglines..."):
    st.chat_message("user").write(prompt)
    st.session_state.display_history.append(("user", prompt))
    st.session_state.messages.append(HumanMessage(content=prompt))

    # Auto-create conversation on first user message
    conv_id = st.session_state.get("current_conversation_id")
    if not conv_id:
        title = prompt[:50] + ("..." if len(prompt) > 50 else "")
        conv_id = create_conversation(user["id"], title)
        st.session_state["current_conversation_id"] = conv_id

    # Save user message to DB
    save_message(conv_id, "user", prompt)

    # Run the agent
    with st.chat_message("assistant"):
        full_response = asyncio.run(run_agent_stream(st.session_state.messages))

        answer_lower = full_response.lower()
        show_logo = "logo" in answer_lower and (
            "generated" in answer_lower or "saved" in answer_lower
        )

        logo_url = None
        if show_logo and st.session_state.get("last_logo_url"):
            logo_url = st.session_state.pop("last_logo_url")
            st.image(logo_url, caption="Generated Logo", width=300)
        elif show_logo and os.path.exists("logo.png"):
            st.image("logo.png", caption="Generated Logo", width=300)

        extras = {"show_logo": show_logo}
        if logo_url:
            extras["logo_url"] = logo_url

    st.session_state.messages.append(AIMessage(content=full_response))
    st.session_state.display_history.append(
        ("assistant", {"text": full_response, **extras})
    )

    # Save assistant message to DB
    save_message(conv_id, "assistant", full_response, logo_url=logo_url)
