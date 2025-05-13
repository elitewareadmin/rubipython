import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const { audioUrl } = await req.json();

    // Here you would integrate with your voice processing service
    // For this example, we'll return a mock response
    const response = {
      transcript: "Hello, I'm Rubi. How can I help you today?",
      confidence: 0.95,
      language: "en-US",
      audioUrl: audioUrl
    };

    // Store the voice command in the database
    const { data, error } = await supabase
      .from('voice_prints')
      .insert([
        {
          user_id: req.headers.get('x-user-id'),
          frequencies: [440, 880, 1760], // Example frequencies
          amplitude: [0.5, 0.3, 0.2],    // Example amplitudes
          pitch: 440,                    // Example pitch
          timbre: [0.1, 0.2, 0.3]       // Example timbre values
        }
      ]);

    if (error) throw error;

    return new Response(
      JSON.stringify(response),
      { 
        headers: { 
          ...corsHeaders,
          'Content-Type': 'application/json'
        } 
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 400,
        headers: { 
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      }
    );
  }
});