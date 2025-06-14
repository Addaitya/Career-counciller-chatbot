import os
from functools import cache
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import yaml
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter

rate_limiter = InMemoryRateLimiter(
    requests_per_second=1,  # <-- Super slow! We can only make a request once every 10 seconds!!
    check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=5,  # Controls the maximum burst size.
)

load_dotenv()

LLM_API_KEY=os.getenv('LLM_API_KEY')

@cache
def get_llm():
    llm = ChatGroq(
        model='llama-3.3-70b-versatile',
        api_key=LLM_API_KEY,
        rate_limiter=rate_limiter
    )
    return llm

@cache
def get_prompts(path: str ='prompts.yaml'):
    try:
        with open(path, 'r') as f:
            prompts = yaml.safe_load(f)
        
        return prompts
    except Exception as e:
        print("Error loading prompts: \n{e}")