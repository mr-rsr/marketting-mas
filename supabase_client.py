"""
Supabase client helpers for authentication, database operations, and storage.
"""

import os
import json
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def _init_supabase() -> Client:
    """Create and cache a single Supabase client instance (shared across reruns)."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        st.error("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")
        st.stop()
    return create_client(url, key)


def get_supabase_client(auth: bool = False) -> Client:
    """Return the cached Supabase client. If auth=True, attach the user's
    access token so that RLS policies (auth.uid()) work correctly."""
    sb = _init_supabase()
    if auth:
        token = st.session_state.get("access_token")
        if token:
            sb.postgrest.auth(token)
    return sb


# ---------------------------------------------------------------------------
# Session persistence via cookies
# ---------------------------------------------------------------------------

def _get_cookie_controller():
    """Return the cookie controller (lazy import to avoid top-level side effects)."""
    from streamlit_cookies_controller import CookieController
    return CookieController()


def save_session_to_cookie():
    """Persist user info and access token to browser cookies."""
    controller = _get_cookie_controller()
    user = st.session_state.get("user")
    token = st.session_state.get("access_token")
    refresh = st.session_state.get("refresh_token")
    if user and token:
        controller.set("ma_user", json.dumps(user))
        controller.set("ma_token", token)
        if refresh:
            controller.set("ma_refresh", refresh)


def restore_session_from_cookie():
    """Try to restore the session from browser cookies on page load."""
    if st.session_state.get("user"):
        return True  # Already logged in

    controller = _get_cookie_controller()
    user_raw = controller.get("ma_user")
    token = controller.get("ma_token")

    if user_raw and token:
        try:
            user = json.loads(user_raw) if isinstance(user_raw, str) else user_raw
            st.session_state["user"] = user
            st.session_state["access_token"] = token
            refresh = controller.get("ma_refresh")
            if refresh:
                st.session_state["refresh_token"] = refresh
            return True
        except Exception:
            pass
    return False


def clear_session_cookie():
    """Remove auth cookies from the browser."""
    controller = _get_cookie_controller()
    for key in ["ma_user", "ma_token", "ma_refresh"]:
        controller.remove(key)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def sign_up(email: str, password: str):
    """Create a new user account. Returns (user, error_message)."""
    sb = get_supabase_client()
    try:
        res = sb.auth.sign_up({"email": email, "password": password})
        if res.user:
            return res.user, None
        return None, "Sign-up failed. Please try again."
    except Exception as e:
        return None, str(e)


def sign_in(email: str, password: str):
    """Sign in with email/password. Returns (session, error_message)."""
    sb = get_supabase_client()
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            return res.session, None
        return None, "Invalid credentials."
    except Exception as e:
        return None, str(e)


def sign_out():
    """Sign the current user out and clear session state + cookies."""
    sb = get_supabase_client()
    try:
        sb.auth.sign_out()
    except Exception:
        pass
    clear_session_cookie()
    for key in ["user", "access_token", "refresh_token",
                 "current_conversation_id", "messages", "display_history"]:
        st.session_state.pop(key, None)


def get_current_user():
    """Return the user dict stored in session state, or None."""
    return st.session_state.get("user")


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

def create_conversation(user_id: str, title: str) -> str | None:
    """Create a new conversation row. Returns the conversation id."""
    sb = get_supabase_client(auth=True)
    res = (
        sb.table("conversations")
        .insert({"user_id": user_id, "title": title})
        .execute()
    )
    if res.data:
        return res.data[0]["id"]
    return None


def get_conversations(user_id: str) -> list[dict]:
    """Return all conversations for a user, newest first."""
    sb = get_supabase_client(auth=True)
    res = (
        sb.table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def update_conversation_title(conversation_id: str, title: str):
    """Update a conversation's title."""
    sb = get_supabase_client(auth=True)
    sb.table("conversations").update({"title": title}).eq("id", conversation_id).execute()


def delete_conversation(conversation_id: str):
    """Delete a conversation and its messages."""
    sb = get_supabase_client(auth=True)
    sb.table("messages").delete().eq("conversation_id", conversation_id).execute()
    sb.table("conversations").delete().eq("id", conversation_id).execute()


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def save_message(conversation_id: str, role: str, content: str, logo_url: str | None = None):
    """Save a single message to the database."""
    sb = get_supabase_client(auth=True)
    row = {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
    }
    if logo_url:
        row["logo_url"] = logo_url
    sb.table("messages").insert(row).execute()


def get_messages(conversation_id: str) -> list[dict]:
    """Return all messages for a conversation, oldest first."""
    sb = get_supabase_client(auth=True)
    res = (
        sb.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
        .execute()
    )
    data = res.data or []
    data.reverse()
    return data


# ---------------------------------------------------------------------------
# Storage — Logo uploads
# ---------------------------------------------------------------------------

LOGO_BUCKET = "logos"


def upload_logo(user_id: str, conversation_id: str, image_bytes: bytes) -> str | None:
    """Upload logo bytes to Supabase Storage and return the public URL."""
    sb = get_supabase_client(auth=True)
    path = f"{user_id}/{conversation_id}/logo.png"
    try:
        sb.storage.from_(LOGO_BUCKET).upload(
            path,
            image_bytes,
            file_options={"content-type": "image/png", "upsert": "true"},
        )
        public_url = sb.storage.from_(LOGO_BUCKET).get_public_url(path)
        return public_url
    except Exception as e:
        print(f"Logo upload error: {e}")
        return None
