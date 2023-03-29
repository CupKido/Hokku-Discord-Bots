import os
import openai
from dotenv import dotenv_values
config = dotenv_values('.env')

openai.api_key = config["OPENAI_KEY"]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
  messages=[{"role":"user", "content" : "How are you doing today?"}],
  temperature=0,
  max_tokens=100,
  top_p=1,
  frequency_penalty=0.0,
  presence_penalty=0.0,
  stop=["\n"]
)
print(response)
