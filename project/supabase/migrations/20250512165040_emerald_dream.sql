/*
  # Chat System Schema

  1. New Tables
    - user_profiles: User profile information
    - chat_rooms: Chat room details
    - chat_participants: Room membership
    - chat_messages: Chat messages
    - message_reactions: Message reactions

  2. Security
    - Enable RLS on all tables
    - Add policies for user access control
    - Secure message access to room participants only

  3. Features
    - Auto-updating timestamps
    - Message editing tracking
    - Cascading deletes
*/

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
  id uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  name text,
  avatar_url text,
  created_at timestamptz DEFAULT now()
);

-- Create chat_rooms table
CREATE TABLE IF NOT EXISTS chat_rooms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  created_by uuid REFERENCES auth.users ON DELETE CASCADE,
  type text NOT NULL CHECK (type IN ('direct', 'group')),
  created_at timestamptz DEFAULT now()
);

-- Create chat_participants table
CREATE TABLE IF NOT EXISTS chat_participants (
  room_id uuid REFERENCES chat_rooms ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users ON DELETE CASCADE,
  joined_at timestamptz DEFAULT now(),
  PRIMARY KEY (room_id, user_id)
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id uuid NOT NULL REFERENCES chat_rooms ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users ON DELETE CASCADE,
  content text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  is_edited boolean DEFAULT false
);

-- Create message_reactions table
CREATE TABLE IF NOT EXISTS message_reactions (
  message_id uuid REFERENCES chat_messages ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users ON DELETE CASCADE,
  reaction text NOT NULL,
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (message_id, user_id)
);

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_reactions ENABLE ROW LEVEL SECURITY;

-- User Profiles Policies
CREATE POLICY "Users can read any profile"
  ON user_profiles FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Chat Rooms Policies
CREATE POLICY "Users can read rooms they are in"
  ON chat_rooms FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM chat_participants
      WHERE room_id = chat_rooms.id 
      AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create rooms"
  ON chat_rooms FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = created_by);

-- Chat Participants Policies
CREATE POLICY "Users can see participants in their rooms"
  ON chat_participants FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM chat_participants AS cp
      WHERE cp.room_id = chat_participants.room_id 
      AND cp.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can join rooms"
  ON chat_participants FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Chat Messages Policies
CREATE POLICY "Users can read messages in their rooms"
  ON chat_messages FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM chat_participants cp
      WHERE cp.room_id = chat_messages.room_id 
      AND cp.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can send messages to their rooms"
  ON chat_messages FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM chat_participants cp
      WHERE cp.room_id = NEW.room_id 
      AND cp.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update own messages"
  ON chat_messages FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Message Reactions Policies
CREATE POLICY "Users can see reactions in their rooms"
  ON message_reactions FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM chat_messages m
      JOIN chat_participants cp ON cp.room_id = m.room_id
      WHERE m.id = message_reactions.message_id 
      AND cp.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can manage own reactions"
  ON message_reactions FOR ALL
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Create trigger to update updated_at and is_edited on chat messages
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    NEW.is_edited = true;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_chat_messages_updated_at
    BEFORE UPDATE ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();