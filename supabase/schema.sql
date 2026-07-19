-- NIA Sovereign Memory Schema
-- Run this in your Supabase SQL Editor to create the 'nia_memory' table.

-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create the Memory Schema table
create table if not exists public.nia_memory (
    id uuid default gen_random_uuid() primary key,
    user_id text not null,               -- Links the memory to a specific user or session
    content text not null,               -- The actual string content of the memory/insight
    vector_embedding vector(1536),       -- Assuming 1536 dimensions for standard OpenAI/HuggingFace embeddings
    timestamp timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Optional: Create an index for faster similarity searches (L2 distance)
create index if not exists nia_memory_embedding_idx 
on public.nia_memory 
using hnsw (vector_embedding vector_l2_ops);

-- RLS (Row Level Security) Policies
alter table public.nia_memory enable row level security;

-- Allow read/write for authenticated services or users 
-- Setup your specific RLS policies according to your Next.js/Python backend auth logic.
create policy "Users can access own memories" on public.nia_memory
    for all using (auth.uid()::text = user_id);

-- NIA Personalization Settings
create table if not exists public.nia_settings (
    id uuid default gen_random_uuid() primary key,
    user_id text unique not null,               -- Links the settings to a specific user/session ID
    language text default 'en-IN',
    voice_id text default 'hi-IN-Wavenet-A',    -- Default fallback
    greeting_en text default 'Hello! How can I help you today?',
    greeting_hi text default 'नमस्कार! बॉस, मैं आज आपकी मदद कैसे कर सकता हूँ?',
    persona_name text default 'NIA',
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- RLS for settings
alter table public.nia_settings enable row level security;
create policy "Users can access own settings" on public.nia_settings
    for all using (auth.uid()::text = user_id);
