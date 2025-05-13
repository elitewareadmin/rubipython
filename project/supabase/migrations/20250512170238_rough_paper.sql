/*
  # Add chat settings table
  
  1. New Tables
    - `chat_settings`
      - `user_id` (uuid, primary key, references auth.users)
      - `notifications_enabled` (boolean)
      - `theme` (text)
      - `font_size` (text)
      - `language` (text)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
  
  2. Security
    - Enable RLS on `chat_settings` table
    - Add policies for users to manage their own settings
*/

-- Create chat settings table
CREATE TABLE IF NOT EXISTS chat_settings (
  user_id uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  notifications_enabled boolean DEFAULT true,
  theme text DEFAULT 'light',
  font_size text DEFAULT 'medium',
  language text DEFAULT 'en',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE chat_settings ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own chat settings"
  ON chat_settings FOR SELECT
  TO authenticated
  USING (chat_settings.user_id = auth.uid());

CREATE POLICY "Users can update own chat settings"
  ON chat_settings FOR UPDATE
  TO authenticated
  USING (chat_settings.user_id = auth.uid())
  WITH CHECK (chat_settings.user_id = auth.uid());

CREATE POLICY "Users can insert own chat settings"
  ON chat_settings FOR INSERT
  TO authenticated
  WITH CHECK (chat_settings.user_id = auth.uid());

-- Create trigger to update updated_at
CREATE OR REPLACE FUNCTION update_chat_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_chat_settings_timestamp
    BEFORE UPDATE ON chat_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_chat_settings_updated_at();