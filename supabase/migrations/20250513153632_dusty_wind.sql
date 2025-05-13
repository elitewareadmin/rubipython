/*
  # Voice and AI Features Schema

  1. New Tables
    - voice_prints: Store voice biometric data
    - ai_completions: Store AI interaction history
    - chat_typing: Track user typing status
    - chat_settings: User chat preferences

  2. Security
    - Enable RLS on all tables
    - Add policies for user access control
*/

-- Create voice_prints table
CREATE TABLE IF NOT EXISTS voice_prints (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users ON DELETE CASCADE,
  frequencies double precision[] NOT NULL,
  amplitude double precision[] NOT NULL,
  pitch double precision NOT NULL,
  timbre double precision[] NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create ai_completions table
CREATE TABLE IF NOT EXISTS ai_completions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users ON DELETE CASCADE,
  prompt text NOT NULL,
  response text NOT NULL,
  model text NOT NULL,
  tokens_used integer NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create chat_typing table
CREATE TABLE IF NOT EXISTS chat_typing (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users ON DELETE CASCADE,
  session_id uuid REFERENCES chat_sessions ON DELETE CASCADE,
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

-- Enable RLS
ALTER TABLE voice_prints ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_completions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_typing ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_settings ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX IF NOT EXISTS voice_prints_user_id_idx ON voice_prints(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS chat_typing_user_session_idx ON chat_typing(user_id, session_id);

-- Create policies
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'voice_prints' 
    AND policyname = 'Users can manage own voice prints'
  ) THEN
    CREATE POLICY "Users can manage own voice prints"
      ON voice_prints FOR ALL
      TO authenticated
      USING (user_id = auth.uid())
      WITH CHECK (user_id = auth.uid());
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'ai_completions' 
    AND policyname = 'Users can manage own AI completions'
  ) THEN
    CREATE POLICY "Users can manage own AI completions"
      ON ai_completions FOR ALL
      TO authenticated
      USING (user_id = auth.uid())
      WITH CHECK (user_id = auth.uid());
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'chat_typing' 
    AND policyname = 'Users can manage typing status'
  ) THEN
    CREATE POLICY "Users can manage typing status"
      ON chat_typing FOR ALL
      TO authenticated
      USING (user_id = auth.uid())
      WITH CHECK (user_id = auth.uid());
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'chat_settings' 
    AND policyname = 'Users can manage own settings'
  ) THEN
    CREATE POLICY "Users can manage own settings"
      ON chat_settings FOR ALL
      TO authenticated
      USING (user_id = auth.uid())
      WITH CHECK (user_id = auth.uid());
  END IF;
END $$;

-- Create trigger to clean up old typing status
CREATE OR REPLACE FUNCTION cleanup_typing_status()
RETURNS TRIGGER AS $$
BEGIN
  DELETE FROM chat_typing
  WHERE last_updated < NOW() - INTERVAL '1 minute';
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger 
    WHERE tgname = 'cleanup_old_typing_status'
  ) THEN
    CREATE TRIGGER cleanup_old_typing_status
      AFTER INSERT OR UPDATE ON chat_typing
      FOR EACH STATEMENT
      EXECUTE FUNCTION cleanup_typing_status();
  END IF;
END $$;