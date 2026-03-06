import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
 
modelsToTry = [
    "gemini-2.5-flash", 
    "gemini-3.1-flash-lite-preview", 
    "gemini-2.5-pro"
]

for modelName in modelsToTry:
    try:
        print(f"Testing {modelName}...")
        response = client.models.generate_content(
            model=modelName, 
            contents="Say 'Arena Online' if you can hear me."
        )
        print(f"✅ Success with {modelName}!")
        print(f"🤖 Gemini says: {response.text.strip()}")
        break 
    except Exception as e: 
        print(f"❌ {modelName} failed: {e}\n")