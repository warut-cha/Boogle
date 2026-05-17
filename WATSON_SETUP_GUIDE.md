# IBM Watson/watsonx.ai Setup Guide

## 🎯 Overview

This guide explains how to configure Bob Sentinel to use real IBM watsonx.ai for AI-powered security analysis instead of mock responses.

---

## 📋 Current Status

**Default Configuration:**
- ✅ Bob AI is **enabled** but in **mock mode**
- ✅ Full pipeline runs automatically on startup
- ✅ Mock responses are generated based on incident data
- ⚠️ Real AI inference is **not active** (mock_mode: true)

**What You Get with Mock Mode:**
- Realistic-looking analysis based on incident patterns
- All features work end-to-end
- No external API calls or costs
- Perfect for development and testing

**What You Get with Real watsonx.ai:**
- Actual AI reasoning and inference
- More intelligent and context-aware analysis
- Better recommendations and insights
- Learns from patterns more effectively

---

## 🔧 How to Enable Real AI Reasoning

### Step 1: Get IBM watsonx.ai Credentials

1. **Sign up for IBM Cloud:**
   - Go to https://cloud.ibm.com
   - Create an account or sign in

2. **Create a watsonx.ai project:**
   - Navigate to watsonx.ai service
   - Create a new project
   - Note your **Project ID**

3. **Get API credentials:**
   - Go to IBM Cloud → Manage → Access (IAM)
   - Create an API key
   - Save your **API Key** securely

4. **Get service URL:**
   - Default: `https://us-south.ml.cloud.ibm.com`
   - Or check your watsonx.ai service instance for the correct URL

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# IBM watsonx.ai Credentials
WATSONX_API_KEY=your-api-key-here
WATSONX_PROJECT_ID=your-project-id-here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

**Security Note:** Never commit `.env` file to git! It's already in `.gitignore`.

### Step 3: Update Configuration

Edit `config/config.yaml`:

```yaml
ai_engine:
  bob:
    enabled: true
    mock_mode: false  # ← Change this to false
    model_id: "ibm/granite-13b-chat-v2"  # Or your preferred model
    project_id: "${WATSONX_PROJECT_ID}"
    api_key: "${WATSONX_API_KEY}"
    url: "${WATSONX_URL}"
    max_tokens: 2000
    temperature: 0.7
```

### Step 4: Install watsonx.ai SDK

```bash
# Activate virtual environment
source venv/bin/activate

# Install IBM watsonx.ai SDK
pip install ibm-watsonx-ai

# Verify installation
python -c "from ibm_watsonx_ai import APIClient; print('✓ SDK installed')"
```

### Step 5: Test Configuration

```bash
# Start the server
python src/api_server.py
```

You should see:
```
🔄 Running full security analysis pipeline...
  → Step 1: Scanning for security findings...
    ✓ Found X security findings
  → Step 2: Correlating findings into incidents...
    ✓ Created X incidents
  ...
  → Step 6: Running Bob AI analysis...
    ✓ Bob AI analysis complete (X incidents analyzed)
```

If Bob is configured correctly, you'll see real AI inference happening!

---

## 🔍 Verify Real AI is Working

### Check 1: Server Logs

Look for these messages:
```
IBM Bob client initialized with model: ibm/granite-13b-chat-v2
Sending request to IBM Bob...
Successfully received and parsed Bob response
```

### Check 2: API Health Check

```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "bob_enabled": true,
  "bob_mock_mode": false  ← Should be false
}
```

### Check 3: Analysis Quality

Real AI responses will be:
- More contextual and specific
- Better formatted
- More intelligent recommendations
- Vary based on actual incident details

Mock responses are:
- Template-based
- Generic recommendations
- Same structure every time

---

## 🎛️ Configuration Options

### Model Selection

Available models (as of 2026):
```yaml
model_id: "ibm/granite-13b-chat-v2"      # Recommended for security
model_id: "ibm/granite-20b-multilingual" # For multilingual support
model_id: "meta-llama/llama-2-70b-chat"  # More powerful, slower
```

### Generation Parameters

```yaml
max_tokens: 2000      # Maximum response length
temperature: 0.7      # Creativity (0.0-1.0, lower = more focused)
top_p: 0.9           # Nucleus sampling
top_k: 50            # Top-k sampling
```

**For Security Analysis:**
- Use lower temperature (0.5-0.7) for more consistent, focused responses
- Higher max_tokens (2000-3000) for detailed reports

---

## 💰 Cost Considerations

### Mock Mode (Current)
- **Cost:** $0
- **Speed:** Instant
- **Quality:** Good for testing

### Real watsonx.ai
- **Cost:** Pay per token (input + output)
- **Speed:** 2-5 seconds per analysis
- **Quality:** Superior AI reasoning

**Estimated Costs:**
- Small scan (5 incidents): ~$0.10
- Medium scan (20 incidents): ~$0.50
- Large scan (100 incidents): ~$2.50

**Cost Optimization:**
- Use mock mode for development
- Enable real AI for production/important scans
- Cache Bob analysis results
- Adjust max_tokens based on needs

---

## 🔄 Switching Between Mock and Real

### Quick Toggle

**Enable Mock Mode (Free):**
```yaml
# config/config.yaml
ai_engine:
  bob:
    mock_mode: true
```

**Enable Real AI:**
```yaml
# config/config.yaml
ai_engine:
  bob:
    mock_mode: false
```

Restart the server after changing.

### Runtime Toggle (Advanced)

You can also toggle via environment variable:
```bash
export BOB_MOCK_MODE=false
python src/api_server.py
```

---

## 🐛 Troubleshooting

### Error: "IBM watsonx.ai SDK not available"

**Solution:**
```bash
pip install ibm-watsonx-ai
```

### Error: "watsonx.ai credentials not configured"

**Solution:**
1. Check `.env` file exists with correct values
2. Verify environment variables are loaded:
   ```bash
   echo $WATSONX_API_KEY
   ```
3. Restart the server

### Error: "Failed to initialize IBM Bob client"

**Possible causes:**
1. Invalid API key
2. Invalid project ID
3. Network connectivity issues
4. Service region mismatch

**Solution:**
1. Verify credentials in IBM Cloud console
2. Check service URL matches your region
3. Test API key:
   ```bash
   curl -X GET "https://us-south.ml.cloud.ibm.com/ml/v1/deployments" \
     -H "Authorization: Bearer $(ibmcloud iam oauth-tokens --output json | jq -r .iam_token)"
   ```

### Bob Returns Generic Responses

**If mock_mode is false but responses seem generic:**
1. Check server logs for "Sending request to IBM Bob..."
2. Verify API calls are actually being made
3. Check token limits aren't being hit
4. Increase max_tokens if responses are cut off

---

## 📊 Monitoring AI Usage

### Check Bob Status

```bash
# Via API
curl http://localhost:8000/api/stats

# Response includes:
{
  "bob_analysis_count": 5,
  "bob_enabled": true,
  "bob_mock_mode": false
}
```

### View AI Memory

```bash
curl http://localhost:8000/api/memory
```

Shows what Bob has learned from past incidents.

---

## 🚀 Best Practices

### Development
- ✅ Use mock mode
- ✅ Test full pipeline locally
- ✅ Verify all features work

### Staging
- ✅ Enable real AI with small datasets
- ✅ Compare mock vs real responses
- ✅ Monitor costs

### Production
- ✅ Use real AI for critical scans
- ✅ Cache analysis results
- ✅ Set up cost alerts
- ✅ Monitor API usage

---

## 📚 Additional Resources

- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [watsonx.ai Python SDK](https://ibm.github.io/watsonx-ai-python-sdk/)
- [Granite Models](https://www.ibm.com/granite)
- [API Reference](https://cloud.ibm.com/apidocs/watsonx-ai)

---

## ✅ Summary

**Current Setup (Mock Mode):**
```
✓ Bob AI enabled
✓ Full pipeline runs on startup
✓ Mock responses generated
✓ No external API calls
✓ $0 cost
```

**To Enable Real AI:**
1. Get IBM watsonx.ai credentials
2. Create `.env` file with credentials
3. Set `mock_mode: false` in config
4. Install `ibm-watsonx-ai` package
5. Restart server

**The system works perfectly in both modes!** Mock mode is great for development, real AI is better for production analysis.

---

**Made with ❤️ by Bob**