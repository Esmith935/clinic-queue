from google import genai

client = genai.Client(api_key='AIzaSyBDDsqJRL_tQn_0Zp-Dqu_drkP9gcAjaFg')

print("Checking available models...")
try:
    # This lists all models your key can access
    for model in client.models.list():
        if "generateContent" in model.supported_actions:
            print(f"✅ Available: {model.name}")
except Exception as e:
    print(f"Error: {e}")