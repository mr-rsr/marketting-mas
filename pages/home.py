import streamlit as st

# ---------------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .hero-title { font-size: 3rem; font-weight: 800; margin-bottom: 0; }
    .hero-sub   { font-size: 1.25rem; color: #666; margin-top: 0.25rem; }
    .feature-card {
        background: #f8f9fa; border-radius: 12px; padding: 1.5rem;
        text-align: center; height: 100%;
    }
    .feature-card h3 { margin-top: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown('<p class="hero-title">AI Marketing Agency</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Your all-in-one AI marketing consultant — strategy, branding, '
        "content, SEO, ads & more. Powered by AWS Bedrock + LangGraph.</p>",
        unsafe_allow_html=True,
    )
    st.write("")
    user = st.session_state.get("user")
    if user:
        if st.button("Open Chatbot →", type="primary", use_container_width=False):
            st.switch_page("pages/chatbot.py")
    else:
        if st.button("Get Started — Sign Up Free →", type="primary", use_container_width=False):
            st.switch_page("pages/login.py")



st.divider()

# ---------------------------------------------------------------------------
# Feature Highlights
# ---------------------------------------------------------------------------
st.subheader("What You Get")

features = [
    ("📊", "Marketing Strategy", "Comprehensive plans tailored to your business, audience, and goals."),
    ("✍️", "Brand Taglines", "Catchy slogans and elevator pitches that capture your essence."),
    ("🎨", "Logo Design", "AI-generated professional logos via Amazon Titan Image Generator."),
    ("📱", "Social Media Content", "Platform-specific posts for Instagram, LinkedIn, Twitter & Facebook."),
    ("📢", "Ad Copy", "High-converting copy for Google Ads and social media campaigns."),
    ("📧", "Email Campaigns", "3-email nurture sequences — welcome, value, and conversion."),
    ("🔍", "SEO Keywords", "Keyword research, meta descriptions, and content topic ideas."),
    ("🌐", "Domain Suggestions", "Creative, available domain name ideas for your brand."),
]

cols = st.columns(4)
for i, (icon, title, desc) in enumerate(features):
    with cols[i % 4]:
        st.markdown(
            f'<div class="feature-card">'
            f"<h2>{icon}</h2><h3>{title}</h3><p>{desc}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.write("")

st.divider()

# ---------------------------------------------------------------------------
# How It Works
# ---------------------------------------------------------------------------
st.subheader("How It Works")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 1. Sign Up")
    st.write("Create a free account in seconds.")
with c2:
    st.markdown("### 2. Tell Us About Your Business")
    st.write("Our AI consultant asks the right questions to understand your brand.")
with c3:
    st.markdown("### 3. Get Your Marketing Kit")
    st.write("Receive a full marketing plan — strategy, content, logo, ads & more.")

st.divider()
st.caption("Built with ❤️ using AWS Bedrock, LangGraph & Streamlit")
