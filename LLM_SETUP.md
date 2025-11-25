# LLM Configuration Guide

## Quick Setup

The ABA Security Oracle uses **ONE** AI LLM provider for analysis. Choose either:

### Option 1: Google Gemini (Recommended - Free Tier Available)

1. **Get API Key**
   - Go to: https://ai.google.dev/
   - Click "Get API Key"
   - Create new API key for free

2. **Configure `.env`**
   ```env
   LLM_PROVIDER=gemini
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Test**
   ```python
   from Brain.brain import oracle
   result = oracle.query("What are the main hotspots in Aba?")
   print(result)
   ```

---

### Option 2: Anthropic Claude (Most Advanced)

1. **Get API Key**
   - Go to: https://console.anthropic.com/
   - Sign up or login
   - Create API key in account settings

2. **Configure `.env`**
   ```env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **Test**
   ```python
   from Brain.brain import oracle
   result = oracle.query("What are the main hotspots in Aba?")
   print(result)
   ```

---

## Environment Variables

### Required
| Variable | Options | Default | Description |
|----------|---------|---------|-------------|
| `LLM_PROVIDER` | "gemini" or "anthropic" | "anthropic" | Which LLM to use |
| `GOOGLE_API_KEY` | string | (empty) | Google Gemini API key |
| `ANTHROPIC_API_KEY` | string | (empty) | Anthropic Claude API key |

### Optional
- If **both** keys are provided → Uses the one specified in `LLM_PROVIDER`
- If **no** key provided for selected provider → Falls back to rule-based analysis
- If **wrong provider** specified → Automatically uses mock analysis

---

## Using the Brain

### Initialize
```python
from Brain.brain import oracle

# Automatically uses LLM_PROVIDER from environment
# Falls back to rule-based if no API key configured
```

### Query Examples
```python
# Direct query
result = oracle.query("What are the security hotspots in Aba?")
print(result)

# With contextual data
data = {
    'incidents': [...],
    'hotspots': [...],
    'temporal_patterns': {...}
}
result = oracle.query("Analyze the risk level", data=data)

# Generate report
report = oracle.generate_report(data)
print(report)

# Analyze specific hotspots
hotspots = [...]
analysis = oracle.analyze_hotspots(hotspots)
print(analysis)
```

---

## Model Details

### Google Gemini
- **Model**: `gemini-pro`
- **Free Tier**: Yes (60 requests/minute)
- **Cost**: Free tier available
- **Speed**: Fast
- **Quality**: Good for general analysis

### Anthropic Claude
- **Model**: `claude-3-sonnet-20240229`
- **Free Tier**: Trial credits (limited)
- **Cost**: Pay-as-you-go
- **Speed**: Moderate
- **Quality**: Excellent for complex analysis

---

## Fallback Behavior

If no LLM is configured, the brain uses **rule-based analysis**:

```
Question → Keyword Matching → Rule-Based Response
                ↓
        Hotspot Analysis → Return pre-defined analysis
        Trend Analysis   → Return temporal patterns
        Risk Analysis    → Calculate risk score
        Recommendations  → Return security recommendations
```

Rule-based responses are:
- ✅ Fast (no API calls)
- ✅ Reliable (no API failures)
- ❌ Less personalized
- ❌ Limited to predefined patterns

---

## Switching Providers

To change from one LLM to another:

1. **Edit `.env`**
   ```env
   LLM_PROVIDER=gemini  # was: anthropic
   GOOGLE_API_KEY=sk-xxxxx  # provide new key
   ```

2. **Restart Application**
   ```bash
   streamlit run Frontend/app.py
   ```

3. **Verify**
   - New LLM is used automatically
   - Old API key is ignored

---

## Troubleshooting

### "LLM query failed, falling back to rule-based"
**Cause**: API key invalid or service unavailable

**Fix**:
1. Verify API key in `.env`
2. Check internet connection
3. Check API rate limits
4. Try rule-based mode: Just use the app, it will work

### "GOOGLE_API_KEY not found"
**Cause**: Environment variable not set

**Fix**:
1. Add to `.env`: `GOOGLE_API_KEY=your_key`
2. Restart application
3. Check `.env` file location (must be in project root)

### "Module not installed"
**Cause**: Required LLM package not installed

**Fix**:
```bash
# For Gemini:
pip install google-generativeai

# For Anthropic:
pip install anthropic

# Or install all:
pip install -r requirements.txt
```

---

## Cost Considerations

### Gemini (Google)
- **Free Tier**: 
  - 60 requests/minute
  - Limited tokens
  - Great for testing

- **Paid Tier**:
  - $0.0025 per 1K input tokens
  - $0.0075 per 1K output tokens
  - Scales with usage

### Claude (Anthropic)
- **Trial Credits**:
  - $5 in free credits
  - Valid for 3 months
  - Good for evaluation

- **Paid Tier**:
  - $3 per 1M input tokens
  - $15 per 1M output tokens
  - More expensive but higher quality

---

## API Key Security

⚠️ **Never commit API keys to version control!**

**Secure practices**:
1. ✅ Store in `.env` (already in `.gitignore`)
2. ✅ Use different keys for dev/prod
3. ✅ Rotate keys periodically
4. ✅ Monitor usage in provider dashboards
5. ✅ Use environment variables only
6. ✅ Never hardcode keys in source

---

## Next Steps

1. Choose a provider (Gemini recommended for free tier)
2. Get API key
3. Add to `.env` file
4. Restart dashboard
5. Test with `oracle.query("Your question")`

**Happy analyzing!** 🚀
