/*
  # Chat System Schema Updates

  1. New Tables
    - chat_typing: Track user typing status
    - chat_settings: User chat preferences
  
  2. Updates
    - Add file support to chat_messages
    - Add cleanup trigger for typing status
*/

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

-- Enable RLS
ALTER TABLE chat_typing ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_settings ENABLE ROW LEVEL SECURITY;

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

-- Create trigger to clean up old typing status
CREATE OR REPLACE FUNCTION cleanup_typing_status()
RETURNS TRIGGER AS $$
BEGIN
  DELETE FROM chat_typing
  WHERE last_updated < NOW() - INTERVAL '1 minute';
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cleanup_old_typing_status
  AFTER INSERT OR UPDATE ON chat_typing
  FOR EACH STATEMENT
  EXECUTE FUNCTION cleanup_typing_status();