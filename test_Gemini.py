import os
import dotenv
dotenv.load_dotenv()

from google import genai
from google.genai import types
from pydantic import BaseModel
import json
import time

class UserIntentSchema(BaseModel):
    action: str
    cnic: str

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

user_text = "مرس نیسی ہے 5 4 4 0 1 5 2 9 2 9 8 0 1"

prompt = f"""
Extract the user's login intent and CNIC number from this spoken text:
"{user_text}"

Rules:
1. Extract only the digits present (ignore surrounding words like CNIC/hai).
2. Set 'action' to 'login' if any digits were found.
3. If no digits found, set 'action' to 'unknown' and 'cnic' to "".
"""

max_attempts = 3
for attempt in range(max_attempts):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UserIntentSchema,
            ),
        )
        print("GEMINI RESULT:", response.text)
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")
        if attempt < max_attempts - 1:
            print("Retrying in 5 seconds...")
            time.sleep(5)