// Test endpoint to debug the request
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { apiKey, systemPrompt, userMessage, conversationHistory = [] } = req.body;

  return res.status(200).json({
    debug: {
      apiKeyPresent: !!apiKey,
      apiKeyValid: apiKey?.startsWith('gsk_'),
      systemPromptLength: systemPrompt?.length,
      userMessageLength: userMessage?.length,
      historyLength: conversationHistory?.length,
      history: conversationHistory,
      totalPayloadSize: JSON.stringify(req.body).length
    }
  });
}
