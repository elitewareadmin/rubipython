import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { Groq } from "npm:groq-sdk";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { prompt, provider = "groq" } = await req.json();
    let response;

    if (provider === "groq") {
      const groq = new Groq({
        apiKey: Deno.env.get("GROQ_API_KEY"),
      });

      const completion = await groq.chat.completions.create({
        messages: [
          {
            role: "system",
            content: "You are Rubi, a professional AI assistant that is helpful, knowledgeable, and precise."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        model: "mixtral-8x7b-32768",
        temperature: 0.7,
        max_tokens: 2048,
      });

      response = completion.choices[0]?.message?.content || "I apologize, but I couldn't generate a response.";
    } else {
      // Fallback to Llama
      const llamaResponse = await fetch("http://localhost:11434/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "llama2",
          prompt: `You are Rubi, a professional AI assistant. ${prompt}`,
          stream: false
        })
      });

      const data = await llamaResponse.json();
      response = data.response;
    }

    // Store the completion in the database
    const { error: dbError } = await supabase
      .from('ai_completions')
      .insert([
        {
          user_id: req.headers.get('x-user-id'),
          prompt: prompt,
          response: response,
          model: provider === "groq" ? "mixtral-8x7b-32768" : "llama2",
          tokens_used: 0 // Token count not available in this context
        }
      ]);

    if (dbError) throw dbError;

    return new Response(
      JSON.stringify({ response }),
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