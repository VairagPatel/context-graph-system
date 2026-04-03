# 🔐 Vercel Environment Variable Setup

## Add Your Groq API Key to Vercel

This will allow evaluators to use the demo without entering their own API key.

---

## ✅ Step-by-Step Instructions

### Method 1: Via Vercel Dashboard (Easiest)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Select your project: `dodge-ai-sooty`

2. **Open Settings**
   - Click the **Settings** tab at the top

3. **Add Environment Variable**
   - Click **Environment Variables** in the left sidebar
   - Click **Add New** button

4. **Configure the Variable**
   - **Key**: `GROQ_API_KEY`
   - **Value**: `gsk_your_actual_groq_api_key_here` (paste your key)
   - **Environments**: Check all three boxes:
     - ✅ Production
     - ✅ Preview
     - ✅ Development

5. **Save**
   - Click **Save** button

6. **Redeploy** (Important!)
   - Go to **Deployments** tab
   - Find the latest deployment
   - Click the **⋯** (three dots) menu
   - Click **Redeploy**
   - Wait for deployment to complete (~1-2 minutes)

7. **Test**
   - Visit: https://dodge-ai-sooty.vercel.app/
   - Go to AI Chat tab
   - Try asking a question WITHOUT entering an API key
   - Should work automatically!

---

### Method 2: Via Vercel CLI

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Add environment variable
vercel env add GROQ_API_KEY

# When prompted:
# - Enter your Groq API key (gsk_...)
# - Select environments: Production, Preview, Development (use spacebar to select all)

# Redeploy
vercel --prod
```

---

## 🧪 Testing

### Before Adding Environment Variable
- Users see: "Enter Groq API key to enable AI chat"
- Must enter their own key to use chat

### After Adding Environment Variable
- Users see: "Enter Groq API key (optional)"
- Message shows: "Using demo API key"
- Chat works immediately without entering a key
- Users can still enter their own key if they want

---

## 📝 What Changed in the Code

### Backend (`api/chat.js`)
```javascript
// Now uses environment variable as fallback
const apiKey = clientApiKey || process.env.GROQ_API_KEY;
```

### Frontend (`src/App.jsx`)
```javascript
// Removed apiKey requirement from sendChat
if(!msg||thinking||!db) return; // No longer checks !apiKey

// Sends undefined if no key, backend uses env var
apiKey: apiKey || undefined
```

---

## 🔒 Security Notes

### ✅ Safe
- Environment variables are stored securely on Vercel
- Not exposed in client-side code
- Only accessible by your serverless functions
- Not visible in browser DevTools or network requests

### ⚠️ Rate Limits
- Groq free tier: 30 requests/minute, 14,400 requests/day
- If many people use your demo simultaneously, you might hit limits
- Consider upgrading to Groq Pro if needed

### 💡 Best Practice
- Use environment variable for demo/evaluation
- Encourage users to get their own key for extended use
- Monitor usage in Groq dashboard: https://console.groq.com

---

## 🚀 Deployment Checklist

- [ ] Add `GROQ_API_KEY` to Vercel environment variables
- [ ] Select all environments (Production, Preview, Development)
- [ ] Save the variable
- [ ] Redeploy the application
- [ ] Test the live demo without entering a key
- [ ] Verify chat works automatically
- [ ] Push updated code to GitHub

---

## 📊 Vercel Environment Variables Dashboard

Your environment variables should look like this:

```
┌─────────────────┬──────────────────────┬─────────────────────────────┐
│ Key             │ Value                │ Environments                │
├─────────────────┼──────────────────────┼─────────────────────────────┤
│ GROQ_API_KEY    │ gsk_••••••••••••••   │ Production, Preview, Dev    │
└─────────────────┴──────────────────────┴─────────────────────────────┘
```

---

## 🎯 Benefits for Evaluators

1. **Immediate Access**: No need to create Groq account
2. **Seamless Experience**: Chat works right away
3. **Full Functionality**: All features available immediately
4. **Professional**: Shows production-ready deployment practices

---

## ❓ Troubleshooting

### Issue: Chat still asks for API key after deployment
**Solution**: Make sure you redeployed after adding the environment variable

### Issue: Getting 401 errors
**Solution**: Check that the environment variable name is exactly `GROQ_API_KEY` (case-sensitive)

### Issue: Environment variable not working
**Solution**: 
1. Verify it's added to Production environment
2. Check the value starts with `gsk_`
3. Redeploy the application

### Issue: Rate limit errors
**Solution**: You're hitting Groq's free tier limits. Either:
- Wait for the limit to reset
- Upgrade to Groq Pro
- Ask evaluators to use their own keys

---

## 📞 Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check browser console for errors
3. Verify environment variable is set correctly
4. Test with your own API key first

---

## ✅ Final Verification

After setup, verify:
- [ ] Environment variable added to Vercel
- [ ] Application redeployed
- [ ] Live demo works without entering key
- [ ] Message shows "Using demo API key"
- [ ] Chat responds to queries
- [ ] No console errors

---

**You're all set! Evaluators can now use your demo immediately without any setup.** 🎉
