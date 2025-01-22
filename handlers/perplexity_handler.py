import urequests as requests
import json
from config import Secrets 

class PerplexityAPI:
    def __init__(self):
        self.url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {Secrets.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def ask_question(self, question, system_prompt="Be precise and concise."):
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "search_domain_filter": ["perplexity.ai"],
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "month",
            "frequency_penalty": 1
        }
        
        try:
            response = requests.request("POST", 
                                     self.url, 
                                     json=payload, 
                                     headers=self.headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}