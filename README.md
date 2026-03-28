# AI Marketing Agency Assistant

A production-ready, multi-user SaaS application that provides AI-powered marketing consulting. Built with **AWS Bedrock**, **LangGraph**, **Streamlit**, and **Supabase**.

## Features

- **8 AI Marketing Agents**: Strategy, Taglines, Logo, Social Media, Ad Copy, Email Campaigns, SEO Keywords, Domain Suggestions
- **Authentication**: Email/password signup, login, logout via Supabase Auth
- **Conversation Memory**: Chat history persisted per user in Supabase database
- **Cloud Logo Storage**: Generated logos uploaded to Supabase Storage
- **Multi-Page UI**: Landing page, Auth page, Chatbot with conversation sidebar
- **Export to PDF**: Download your marketing plan as a PDF

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd MA_MAS
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Supabase

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the contents of `schema.sql` to create tables and RLS policies
3. Go to **Storage** and create a public bucket named `logos`
4. Add a storage policy to allow authenticated users to upload:
   - Policy name: `Users can upload logos`
   - Operation: INSERT
   - Policy: `(bucket_id = 'logos') AND (auth.uid()::text = (storage.foldername(name))[1])`

### 4. Configure Environment Variables

Add these to your `.env` file:

```env
# AWS Bedrock
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 5. Run the App

```bash
streamlit run app.py
```

## Project Structure

```
MA_MAS/
├── app.py                  # Main entry point with page navigation
├── supabase_client.py      # Supabase auth, DB, and storage helpers
├── schema.sql              # Database schema (run in Supabase SQL Editor)
├── pages/
│   ├── home.py             # Landing page with feature highlights
│   ├── login.py            # Login / Sign Up page
│   └── chatbot.py          # Chat interface with conversation sidebar
├── agents/
│   ├── strategy_agent.py   # Marketing strategy generation
│   ├── tagline_agent.py    # Brand taglines & slogans
│   ├── logo_agent.py       # Logo generation (Titan + Supabase Storage)
│   ├── social_media_agent.py
│   ├── ad_copy_agent.py
│   ├── email_campaign_agent.py
│   ├── seo_agent.py
│   └── domain_agent.py
├── graph/
│   ├── state.py            # LangGraph state definition
│   ├── prompt.py           # System prompt for the AI consultant
│   └── graph.py            # LangGraph workflow (agent + tools)
└── requirements.txt
```

## GitHub Copilot Usage

### Instance 1: Supabase CRUD Functions
Copilot was used to generate the boilerplate for `supabase_client.py` — all CRUD operations for conversations and messages, including the Supabase query builder syntax (`sb.table().select().eq().order().execute()`).

### Instance 2: Streamlit Multi-Page Navigation
Copilot assisted in setting up the `st.navigation` + `st.Page` pattern for conditional page routing based on authentication state, including the `st.switch_page()` redirects.

### Instance 3: PDF Export Feature
Copilot helped generate the `_build_pdf()` function using the `fpdf2` library, including proper encoding handling for non-ASCII characters and the multi-cell layout for conversation content.

## Bonus Feature: Export to PDF

Users can export their entire marketing plan conversation as a downloadable PDF file directly from the chatbot sidebar.
