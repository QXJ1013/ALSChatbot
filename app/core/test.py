from dotenv import load_dotenv
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

print("HF_API_TOKEN Loaded:", os.getenv("HF_API_TOKEN"))
