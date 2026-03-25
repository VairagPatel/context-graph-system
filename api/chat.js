// Vercel serverless function - direct fetch to Groq API
export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { apiKey, systemPrompt, userMessage, conversationHistory = [] } = req.body;

    console.log('=== Request Debug ===');
    console.log('API Key present:', !!apiKey);
    console.log('API Key starts with gsk_:', apiKey?.startsWith('gsk_'));
    console.log('System prompt length:', systemPrompt?.length);
    console.log('User message length:', userMessage?.length);
    console.log('History length:', conversationHistory?.length);
    console.log('History:', JSON.stringify(conversationHistory, null, 2));

    // Validate API key
    if (!apiKey || !apiKey.startsWith("gsk_")) {
      return res.status(401).json({ error: "Invalid or missing Groq API key" });
    }

    // Validate required fields
    if (!systemPrompt || !userMessage) {
      return res.status(400).json({ error: "Missing systemPrompt or userMessage" });
    }

    // Build messages array - filter out any invalid messages
    const messages = [
      { role: "system", content: systemPrompt },
      ...conversationHistory.filter(msg => 
        msg && 
        msg.role && 
        msg.content && 
        typeof msg.content === 'string' &&
        msg.content.trim().length > 0 &&
        (msg.role === 'user' || msg.role === 'assistant')
      ),
      { role: "user", content: userMessage }
    ];

    console.log('Final messages array:', JSON.stringify(messages, null, 2));
    console.log('Total payload size:', JSON.stringify(messages).length, 'bytes');

    // Call Groq API directly with fetch
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.1-70b-versatile',
        messages: messages,
        temperature: 0,
        max_tokens: 1000,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Groq API error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorData,
        messageCount: messages.length,
        totalLength: JSON.stringify(messages).length
      });
      return res.status(response.status).json({ 
        error: 'Groq API error',
        detail: errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`
      });
    }

    const data = await response.json();
    const content = data.choices[0]?.message?.content || "{}";

    return res.status(200).json({ content });

  } catch (err) {
    console.error('Error:', err);
    return res.status(500).json({ 
      error: 'Internal server error', 
      detail: err.message 
    });
  }
}
