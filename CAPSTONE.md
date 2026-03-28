# 🎓 Capstone Project: AI-Powered Marketing Agency Assistant

## Problem Statement

Small businesses and solopreneurs lack access to affordable, comprehensive marketing expertise. They need branding, content, SEO, ad copy, and strategy — but hiring a full marketing team is expensive.

During the live session, we built an **AI Marketing Consultant** using **AWS Bedrock + LangGraph** that can generate:

- ✅ Marketing strategies
- ✅ Brand taglines & slogans
- ✅ Logos (via Amazon Titan Image Generator)
- ✅ Social media content
- ✅ Ad copy (Google Ads + Social)
- ✅ Email campaigns
- ✅ SEO keywords
- ✅ Domain suggestions

**However, the prototype has critical gaps for production readiness:**

1. **No authentication** — anyone can access it, no concept of "my account"
2. **No conversation memory** — refreshing the page loses all context
3. **No cloud storage** — generated logos are saved locally and lost
4. **Basic UI** — single page, no navigation, no landing experience
5. **No data isolation** — multiple users can't use the system independently

---

## 🎯 Your Objective

Transform this prototype into a **production-ready, multi-user SaaS application** by integrating **Supabase** for authentication, conversation persistence, and asset storage — with a polished multi-page UI.

**Use GitHub Copilot** to accelerate your development.

---

## 📋 Requirements

### 1. Authentication (Supabase Auth)

- Email/password sign-up and login
- Session management using Supabase Auth
- Protected routes — chatbot only accessible after login
- Logout functionality

### 2. Conversation Memory (Supabase Database)

- Store chat history per user in a `conversations` + `messages` table
- Load previous conversations on login so users can resume
- Support multiple conversation threads (new chat / history sidebar)
- Auto-generate conversation titles from the business name

### 3. Image Storage (Supabase Storage)

- Create a Supabase Storage bucket for generated assets
- Upload logos to Supabase Storage instead of saving locally
- Store the public URL in the database linked to user and conversation
- Display images from Supabase URLs in the chat UI

### 4. Multi-Page UI (Streamlit)

Build **3 pages** with proper navigation:

| Page | Description |
|------|-------------|
| **Home / Landing** | Hero section, feature highlights, CTA to sign up/login |
| **Login / Signup** | Auth forms powered by Supabase |
| **Chatbot** | Chat interface with conversation history sidebar, user info, and logout |

### 5. Use GitHub Copilot

- Use Copilot to generate boilerplate code
- Use Copilot Chat to debug and understand Supabase APIs
- Document at least **3 instances** where Copilot helped you (in your submission)

---

## 🌟 Bonus Features (Pick any for extra credit)

| Feature | Description |
|---------|-------------|
| **Export to PDF** | Export the full marketing plan (strategy + taglines + ad copy) as a downloadable PDF |
| **Dashboard** | Summary page showing all generated assets for a business in one view |
| **Multi-business support** | Allow one user to manage marketing for multiple businesses/brands |
| **Share / Collaborate** | Generate a shareable link for a marketing plan so teams can review |
| **Dark / Light theme** | Theme toggle for the UI |
| **Competitor Analysis** | New agent that takes a competitor URL and generates competitive analysis |

---


## 📝 Submission Checklist

- [ ] Supabase Auth working (signup + login + logout)
- [ ] Chat history persisted in Supabase database
- [ ] Conversations load on page refresh / re-login
- [ ] Logos uploaded to Supabase Storage and displayed from URL
- [ ] Home page with product description
- [ ] Login/Signup page
- [ ] Chatbot page with conversation sidebar
- [ ] At least 1 bonus feature implemented
- [ ] 3 documented instances of GitHub Copilot usage
- [ ] Code pushed to GitHub repository
- [ ] README updated with setup instructions

---

## 💡 Tips

1. **Start with Supabase setup** — create the project, run the SQL schema, get your keys
2. **Build auth first** — everything else depends on knowing who the user is
3. **Then add memory** — save/load messages to Supabase after each exchange
4. **Then storage** — modify `logo_agent.py` to upload to Supabase Storage
5. **Finally, polish the UI** — multi-page layout, sidebar, styling
6. **Use Copilot aggressively** — let it write the Supabase CRUD functions for you

Good luck! 🚀
