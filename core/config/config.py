from dotenv import load_dotenv
import os

load_dotenv()

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "")