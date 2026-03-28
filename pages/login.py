import streamlit as st
from supabase_client import sign_up, sign_in, save_session_to_cookie

st.title("🔐 Login / Sign Up")

# If already logged in, redirect to chatbot
if st.session_state.get("user"):
    st.success(f"Already logged in as **{st.session_state['user']['email']}**")
    st.rerun()

tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

# ---------------------------------------------------------------------------
# Login Tab
# ---------------------------------------------------------------------------
with tab_login:
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

    if submitted:
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            with st.spinner("Logging in..."):
                session, err = sign_in(email, password)
            if err:
                st.error(err)
            else:
                st.session_state["user"] = {
                    "id": session.user.id,
                    "email": session.user.email,
                }
                st.session_state["access_token"] = session.access_token
                st.session_state["refresh_token"] = session.refresh_token
                save_session_to_cookie()
                st.success("Logged in successfully!")
                st.rerun()

# ---------------------------------------------------------------------------
# Sign Up Tab
# ---------------------------------------------------------------------------
with tab_signup:
    with st.form("signup_form"):
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

    if submitted:
        if not new_email or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            with st.spinner("Creating account..."):
                user, err = sign_up(new_email, new_password)
            if err:
                st.error(err)
            else:
                st.success(
                    "Account created! Check your email for a confirmation link, "
                    "then come back and log in."
                )
