-- =============================================================
-- Supabase SQL Schema for Marketing Agency AI Assistant
-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor)
-- =============================================================

-- 1. Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title       TEXT NOT NULL DEFAULT 'New Chat',
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 2. Messages table
CREATE TABLE IF NOT EXISTS messages (
    id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id  UUID REFERENCES conversations(id) ON DELETE CASCADE NOT NULL,
    role             TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content          TEXT NOT NULL,
    logo_url         TEXT,
    created_at       TIMESTAMPTZ DEFAULT now()
);

-- 3. Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- 4. Row Level Security (RLS) — users can only access their own data
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Conversations: users can CRUD their own rows
CREATE POLICY "Users can view own conversations"
    ON conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own conversations"
    ON conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own conversations"
    ON conversations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own conversations"
    ON conversations FOR DELETE
    USING (auth.uid() = user_id);

-- Messages: users can access messages in their own conversations
CREATE POLICY "Users can view own messages"
    ON messages FOR SELECT
    USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own messages"
    ON messages FOR INSERT
    WITH CHECK (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own messages"
    ON messages FOR DELETE
    USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );

-- 5. Storage bucket for logos (run in SQL or create via Dashboard → Storage)
-- Note: Create a bucket named "logos" in Supabase Dashboard → Storage
-- Set it to PUBLIC so logos can be displayed via public URLs.
-- Add a storage policy allowing authenticated users to upload to their own folder:
--   Policy name: "Users can upload logos"
--   Allowed operation: INSERT
--   Policy: (bucket_id = 'logos') AND (auth.uid()::text = (storage.foldername(name))[1])
