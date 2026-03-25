// Vercel serverless function
export default async function handler(req, res) {
  // Dynamic import for ES modules in Vercel
  const { default: Groq } = await import("groq-sdk");
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { apiKey, systemPrompt, userMessage, conversationHistory = [] } = req.body;

  console.log("📨 Incoming chat request");
  console.log("  - API key present:", !!apiKey);
  console.log("  - User message length:", userMessage?.length || 0);
  console.log("  - History length:", conversationHistory?.length || 0);

  // Validate API key
  if (!apiKey || !apiKey.startsWith("gsk_")) {
    console.error("❌ Invalid API key format");
    return res.status(401).json({ error: "Invalid or missing Groq API key. Must start with gsk_" });
  }

  // Validate required fields
  if (!systemPrompt || !userMessage) {
    console.error("❌ Missing required fields");
    return res.status(400).json({ error: "Missing systemPrompt or userMessage" });
  }

  try {
    // Initialize Groq client with user's API key
    const groq = new Groq({ apiKey });

    // Build messages array
    const messages = [
      { role: "system", content: systemPrompt },
      ...conversationHistory,
      { role: "user", content: userMessage }
    ];

    console.log("🚀 Calling Groq API with llama3-70b-8192");
    
    // Call Groq API
    const completion = await groq.chat.completions.create({
      model: "llama3-70b-8192",
      messages,
      temperature: 0,
      max_tokens: 1000,
    });

    const content = completion.choices[0]?.message?.content || "{}";
    
    console.log("✅ Groq API response received");
    console.log("  - Response length:", content.length);

    // Return plain JSON content string
    res.status(200).json({ content });

  } catch (err) {
    console.error("❌ Groq API error:", err.message);
    console.error("  - Error type:", err.constructor.name);
    
    if (err.status === 401) {
      return res.status(401).json({ 
        error: "Invalid Groq API key", 
        detail: "Please check your API key at console.groq.com" 
      });
    }
    
    res.status(502).json({ 
      error: "Failed to reach Groq API", 
      detail: err.message 
    });
  }
}
