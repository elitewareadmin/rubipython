import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { prompt } = await req.json();

    // Call Llama API
    const response = await fetch("http://localhost:11434/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "llama2",
        prompt: `You are Rubi, a professional AI assistant. ${prompt}`,
        stream: false
      })
    });

    const data = await response.json();

    // Store the completion in the database
    const { error: dbError } = await supabase
      .from('ai_completions')
      .insert([
        {
          user_id: req.headers.get('x-user-id'),
          prompt: prompt,
          response: data.response,
          model: "llama2",
          tokens_used: data.tokens || 0
        }
      ]);

    if (dbError) throw dbError;

    return new Response(
      JSON.stringify({ response: data.response }),
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
        status: 500,
        headers: { 
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      }
    );
  }
});