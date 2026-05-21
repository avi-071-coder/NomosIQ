from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
try:
    models = client.models.list()
    for m in models:
        if 'flash' in m.name.lower():
            print(m.name)
except Exception as e:
    print(e)
