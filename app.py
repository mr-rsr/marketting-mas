import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from supabase_client import restore_session_from_cookie

st.set_page_config(
    page_title="AI Marketing Agency",
    page_icon="🚀",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Restore session from browser cookie (survives page refresh)
# ---------------------------------------------------------------------------
restore_session_from_cookie()

# ---------------------------------------------------------------------------
# Page definitions
# ---------------------------------------------------------------------------
home_page = st.Page("pages/home.py", title="Home", icon="🏠")
login_page = st.Page("pages/login.py", title="Login / Sign Up", icon="🔐")
chatbot_page = st.Page("pages/chatbot.py", title="Chatbot", icon="💬", default=True)

# ---------------------------------------------------------------------------
# Navigation — show chatbot only when logged in
# ---------------------------------------------------------------------------
user = st.session_state.get("user")

if user:
    nav = st.navigation({"Menu": [chatbot_page, home_page]})
else:
    nav = st.navigation({"Menu": [home_page, login_page]})

nav.run()
