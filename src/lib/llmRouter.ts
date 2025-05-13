import { Groq } from 'groq-sdk';

export const callGroq = async (prompt: string) => {
  const groq = new Groq({
    apiKey: import.meta.env.VITE_GROQ_API_KEY,
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

  return completion.choices[0]?.message?.content || "I apologize, but I couldn't generate a response.";
};

export const askRubi = async (prompt: string, provider = "groq") => {
  switch (provider) {
    case "groq":
      return await callGroq(prompt);
    default:
      throw new Error("Provider not supported");
  }
};