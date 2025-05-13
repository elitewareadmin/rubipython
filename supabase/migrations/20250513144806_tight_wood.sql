/*
  # Chat System Enhancements

  1. New Tables
    - chat_rooms: Group and direct chat rooms
    - chat_participants: Room membership tracking
    - chat_reactions: Message reactions
    - chat_typing: Typing indicators
    - chat_settings: User preferences
  
  2. Updates
    - Add file support to chat_messages
    - Create storage bucket for files
    
  3. Security
    - Enable RLS
    - Add access policies
    - Add storage policies
*/

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

-- Create chat_reactions table
CREATE TABLE IF NOT EXISTS chat_reactions (
  message_id uuid REFERENCES chat_messages ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users ON DELETE CASCADE,
  reaction text NOT NULL,
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (message_id, user_id)
);

-- Create chat_typing table
CREATE TABLE IF NOT EXISTS chat_typing (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users ON DELETE CASCADE,
  room_id uuid REFERENCES chat_rooms ON DELETE CASCADE,
  is_typing boolean DEFAULT false,
  last_updated timestamptz DEFAULT now()
);

-- Create chat_settings table
CREATE TABLE IF NOT EXISTS chat_settings (
  user_id uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  notifications_enabled boolean DEFAULT true,
  theme text DEFAULT 'light',
  font_size text DEFAULT 'medium',
  language text DEFAULT 'en',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Add file columns to chat_messages
ALTER TABLE chat_messages
ADD COLUMN IF NOT EXISTS file_url text,
ADD COLUMN IF NOT EXISTS file_type text;

-- Create storage bucket for chat files
DO $$
BEGIN
  INSERT INTO storage.buckets (id, name, public)
  VALUES ('chat-files', 'chat-files', true)
  ON CONFLICT (id) DO NOTHING;
END $$;

-- Enable RLS
ALTER TABLE chat_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_reactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_typing ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_settings ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can read rooms they are in" ON chat_rooms;
DROP POLICY IF EXISTS "Users can create rooms" ON chat_rooms;
DROP POLICY IF EXISTS "Users can see participants in their rooms" ON chat_participants;
DROP POLICY IF EXISTS "Users can manage reactions" ON chat_reactions;
DROP POLICY IF EXISTS "Users can manage typing status" ON chat_typing;
DROP POLICY IF EXISTS "Users can manage own settings" ON chat_settings;
DROP POLICY IF EXISTS "Users can upload chat files" ON storage.objects;

-- Chat Rooms Policies
CREATE POLICY "Users can read rooms they are in"
  ON chat_rooms FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM chat_participants
      WHERE room_id = id AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create rooms"
  ON chat_rooms FOR INSERT
  TO authenticated
  WITH CHECK (created_by = auth.uid());

-- Chat Participants Policies
CREATE POLICY "Users can see participants in their rooms"
  ON chat_participants FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM chat_participants AS cp
      WHERE cp.room_id = room_id AND cp.user_id = auth.uid()
    )
  );

-- Chat Reactions Policies
CREATE POLICY "Users can manage reactions"
  ON chat_reactions FOR ALL
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Chat Typing Policies
CREATE POLICY "Users can manage typing status"
  ON chat_typing FOR ALL
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Chat Settings Policies
CREATE POLICY "Users can manage own settings"
  ON chat_settings FOR ALL
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Storage bucket policy
CREATE POLICY "Users can upload chat files"
  ON storage.objects FOR ALL
  TO authenticated
  USING (bucket_id = 'chat-files' AND auth.uid()::text = (storage.foldername(name))[1])
  WITH CHECK (bucket_id = 'chat-files' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Create trigger to clean up old typing status
CREATE OR REPLACE FUNCTION cleanup_typing_status()
RETURNS TRIGGER AS $$
BEGIN
  DELETE FROM chat_typing
  WHERE last_updated < NOW() - INTERVAL '1 minute';
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS cleanup_old_typing_status ON chat_typing;
CREATE TRIGGER cleanup_old_typing_status
  AFTER INSERT OR UPDATE ON chat_typing
  FOR EACH STATEMENT
  EXECUTE FUNCTION cleanup_typing_status();