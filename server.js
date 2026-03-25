import express from "express";
import cors from "cors";
import { createServer } from "http";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import Groq from "groq-sdk";

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();

app.use(cors());
app.use(express.json({ limit: "2mb" }));

// Serve static frontend
app.use(express.static(join(__dirname, "dist")));

// Groq API proxy endpoint
app.post("/api/chat", async (req, res) => {
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
    res.json({ content });

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
});

// Fallback to SPA
app.get("*", (_req, res) => {
  res.sendFile(join(__dirname, "dist", "index.html"));
});

const PORT = 3001;
createServer(app).listen(PORT, () => {
  console.log(`\n⚡ Dodge AI · SAP O2C Graph Explorer`);
  console.log(`   🚀 Server running at http://localhost:${PORT}`);
  console.log(`   🤖 LLM: Groq (llama3-70b-8192)`);
  console.log(`   🔑 API key required: gsk_...\n`);
});
