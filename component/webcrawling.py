import requests
from dotenv import load_dotenv
import os

import warnings
warnings.filterwarnings("ignore")


url = r'https://r.jina.ai/https://www.linkedin.com/in/hargup/'
headers = {"Authorization": "Bearer jina_7bf51d2f9dd746d08efd729c1d0eb823VV4edy-8i2vh4Vx2wCqI87EPPYKg"}

response = requests.get(url, headers=headers)
print(response.text)