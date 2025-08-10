from google import genai
from dotenv import load_dotenv

load_dotenv()

class GenaiService:
    def __init__(self):
        self.client = genai.Client()
    
    def basic_request(self, text: str):
        response = self.client.models.generate_content(
        model="gemini-2.5-flash", contents=text)
        print(response.text)