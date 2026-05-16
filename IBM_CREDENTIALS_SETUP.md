# IBM watsonx.ai Credentials Setup Guide

## 🎯 Goal

Get your IBM watsonx.ai API credentials to enable real AI inference in Bob Sentinel.

---

## 📋 What You Need

1. **IBM Cloud Account** (you have the passcode: `Iht6jJVwdx`)
2. **watsonx.ai Project ID**
3. **IBM Cloud API Key**
4. **Service URL** (usually `https://us-south.ml.cloud.ibm.com`)

---

## 🚀 Step-by-Step Setup

### Step 1: Install IBM Cloud CLI (Optional but Recommended)

```bash
# macOS
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh

# Linux
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh

# Verify installation
ibmcloud --version
```

### Step 2: Login to IBM Cloud

**Option A: Via CLI (if installed)**
```bash
ibmcloud login -a https://cloud.ibm.com -u passcode -p Iht6jJVwdx
```

**Option B: Via Web Console**
1. Go to https://cloud.ibm.com
2. Click "Log in"
3. Use your IBM Cloud credentials

### Step 3: Get API Key

**Via Web Console (Easiest):**
1. Go to https://cloud.ibm.com/iam/apikeys
2. Click "Create +"
3. Name it: "Bob Sentinel API Key"
4. Click "Create"
5. **Copy and save the API key** (you won't see it again!)

**Via CLI:**
```bash
# Create API key
ibmcloud iam api-key-create bob-sentinel-key -d "API key for Bob Sentinel"

# Output will show your API key - SAVE IT!
```

### Step 4: Create watsonx.ai Project

1. Go to https://dataplatform.cloud.ibm.com/wx/home
2. Click "Create a project" or "New project"
3. Choose "Create an empty project"
4. Name it: "Bob Sentinel Security Analysis"
5. Click "Create"
6. Once created, click on the project
7. Go to "Manage" tab → "General"
8. **Copy the Project ID** (looks like: `12345678-1234-1234-1234-123456789abc`)

### Step 5: Get Service URL

**Default URL:** `https://us-south.ml.cloud.ibm.com`

**To verify your region:**
1. In your watsonx.ai project
2. Go to "Manage" → "Services and integrations"
3. Look for "Watson Machine Learning" service
4. Note the region (us-south, eu-de, jp-tok, etc.)

**Region URLs:**
- US South: `https://us-south.ml.cloud.ibm.com`
- EU Germany: `https://eu-de.ml.cloud.ibm.com`
- Japan Tokyo: `https://jp-tok.ml.cloud.ibm.com`

---

## 🔧 Configure Bob Sentinel

### Step 1: Create `.env` File

Create a file named `.env` in the project root:

```bash
# IBM watsonx.ai Credentials
WATSONX_API_KEY=your-api-key-here
WATSONX_PROJECT_ID=your-project-id-here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

**Example:**
```bash
WATSONX_API_KEY=abc123xyz789_your_actual_key_here
WATSONX_PROJECT_ID=12345678-1234-1234-1234-123456789abc
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### Step 2: Update Configuration

Edit `config/config.yaml`:

```yaml
ai_engine:
  bob:
    enabled: true
    mock_mode: false  # ← Change to false
    model_id: "ibm/granite-13b-chat-v2"
    project_id: "${WATSONX_PROJECT_ID}"
    api_key: "${WATSONX_API_KEY}"
    url: "${WATSONX_URL}"
```

### Step 3: Install SDK

```bash
# Activate virtual environment
source venv/bin/activate

# Install IBM watsonx.ai SDK
pip install ibm-watsonx-ai

# Verify
python -c "from ibm_watsonx_ai import APIClient; print('✓ SDK installed')"
```

### Step 4: Test Connection

Create a test script `test_watson.py`:

```python
import os
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# Load credentials
api_key = os.getenv('WATSONX_API_KEY')
project_id = os.getenv('WATSONX_PROJECT_ID')
url = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')

print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not set")
print(f"Project ID: {project_id}")
print(f"URL: {url}")

# Test connection
try:
    credentials = Credentials(api_key=api_key, url=url)
    client = APIClient(credentials)
    
    model = ModelInference(
        model_id="ibm/granite-13b-chat-v2",
        api_client=client,
        project_id=project_id
    )
    
    # Test inference
    response = model.generate_text(prompt="Hello, this is a test.")
    print(f"\n✅ Connection successful!")
    print(f"Response: {response[:100]}...")
except Exception as e:
    print(f"\n❌ Connection failed: {str(e)}")
```

Run it:
```bash
python test_watson.py
```

---

## 🎉 Start Using Real AI

Once configured, restart the server:

```bash
# Stop current server (Ctrl+C)

# Start with real AI
python src/api_server.py
```

You should see:
```
IBM Bob client initialized with model: ibm/granite-13b-chat-v2
🔄 Running full security analysis pipeline...
  → Step 6: Running Bob AI analysis...
    Sending request to IBM Bob...
    Successfully received and parsed Bob response
    ✓ Bob AI analysis complete
```

---

## 🔍 Verify Real AI is Working

### Check 1: Server Logs

Look for:
```
IBM Bob client initialized with model: ibm/granite-13b-chat-v2
Sending request to IBM Bob...
Successfully received and parsed Bob response
```

### Check 2: Dashboard

1. Open http://localhost:3001
2. Enter a path in the scan input
3. Click "Scan Now"
4. Check the Bob AI Analysis tab
5. The analysis should be more detailed and contextual

### Check 3: API Response

```bash
curl http://localhost:8000/api/incidents/INC-001/analyze-with-bob | jq .
```

Real AI responses will have:
- More specific recommendations
- Context-aware analysis
- Varied responses based on actual data

---

## 💰 Cost Management

### Pricing

IBM watsonx.ai charges per token:
- Input tokens: ~$0.0005 per 1K tokens
- Output tokens: ~$0.0015 per 1K tokens

### Estimated Costs

**Per Scan:**
- Small (5 incidents): ~$0.10
- Medium (20 incidents): ~$0.50
- Large (100 incidents): ~$2.50

### Cost Optimization

1. **Use mock mode for development:**
   ```yaml
   mock_mode: true  # Free
   ```

2. **Reduce max_tokens:**
   ```yaml
   max_tokens: 1000  # Instead of 2000
   ```

3. **Cache results:**
   - Backend already caches Bob analysis
   - Results persist until server restart

4. **Selective AI analysis:**
   - Only run Bob on critical incidents
   - Use `use_bob: false` for quick scans

---

## 🐛 Troubleshooting

### Error: "API key not found"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check environment variables are loaded
echo $WATSONX_API_KEY

# Restart server to reload .env
```

### Error: "Project not found"

**Solution:**
1. Verify Project ID in watsonx.ai console
2. Ensure you have access to the project
3. Check project is in the same region as your API key

### Error: "Model not found"

**Solution:**
Try a different model:
```yaml
model_id: "meta-llama/llama-2-70b-chat"  # Alternative
```

### Error: "Rate limit exceeded"

**Solution:**
1. Wait a few minutes
2. Reduce scan frequency
3. Use mock mode temporarily

### Still Getting Mock Responses?

**Check:**
1. `mock_mode: false` in config.yaml
2. `.env` file has correct credentials
3. Server was restarted after config changes
4. Check server logs for "IBM Bob client initialized"

---

## 📚 Additional Resources

- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [Python SDK Documentation](https://ibm.github.io/watsonx-ai-python-sdk/)
- [Granite Models](https://www.ibm.com/granite)
- [Pricing Calculator](https://www.ibm.com/cloud/watson-machine-learning/pricing)

---

## ✅ Quick Checklist

- [ ] IBM Cloud account accessible
- [ ] API key created and saved
- [ ] watsonx.ai project created
- [ ] Project ID copied
- [ ] `.env` file created with credentials
- [ ] `config.yaml` updated (`mock_mode: false`)
- [ ] `ibm-watsonx-ai` package installed
- [ ] Test script runs successfully
- [ ] Server restarted
- [ ] Real AI responses verified

---

**Made with ❤️ by Bob**