import os
import requests
import json
import openai
import urllib.request
import asyncio
import aiohttp
import base64
from dotenv import dotenv_values
config = dotenv_values('.env')
  

def send_to_GPT3_5_requests(message):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + config["OPENAI_KEY"]  # Replace with your actual API key
    }

    data = {
        "model" : "gpt-3.5-turbo",
        "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.content.decode('utf-8'))
        return response_json["choices"][0]["message"]["content"]
    else:
        return "Error:\n" + str(response.content)

def generate_image(prompt):
    openai.api_key = config["OPENAI_KEY"]
    response = openai.Image.create(
    prompt=prompt,
    n=1,
    size="1024x1024"
    )
    image_url = response['data'][0]['url']
    filename = "last_image.jpg"
    urllib.request.urlretrieve(image_url, filename)
    return image_url

async def generate_image_aio(prompt):
    url = 'https://api.openai.com/v1/images/generations'

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + config["OPENAI_KEY"]  # Replace with your actual API key
    }

    data = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }

    async with aiohttp.ClientSession() as session:
        print('getting image:\t' + prompt)
        async with session.post(url, headers=headers, data=json.dumps(data)) as response:
            if response.status == 200:
                response_json = await response.json()
                print('got image:\t' + prompt)
                return response_json['data']
            else:
                return "Error:\n" + str(response.content)
    

def get_models():
    url = "https://api.openai.com/v1/models"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + config["OPENAI_KEY"]  # Replace with your actual API key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_json = json.loads(response.content.decode('utf-8'))
        return response_json['data']
    else:
        return "Error:\n" + str(response.content)

async def main():
    task1 = asyncio.create_task(generate_image_aio("a white siamese cat"))
    task2 = asyncio.create_task(generate_image_aio("a blue cute dog"))
    asyncio
    await asyncio.gather(task1, task2)

def generate_image_3(text):
    dream_studio_key = config["DREAM_STUDIO_KEY"]
    engine_id = 'stable-diffusion-v1-5'
    url = f'https://api.stability.ai/v1/generation/{engine_id}/text-to-image'

    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {dream_studio_key}"
    }
    json={
        "text_prompts": [
            {
                "text": text
            }
        ],
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30,
    }
    response = requests.post(url, headers=headers, json=json)
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    for i, image in enumerate(data["artifacts"]):
        with open(f"v1_txt2img_{i}.png", "wb+") as f:
            f.write(base64.b64decode(image["base64"]))

def get_page(url):
    url = 'https://studio.youtube.com/channel/UCqBsLOEVt_GU7p_XI2WkB2A'
    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + "abcd"  # Replace with your actual API key
    }
    # get session cookie
    response = requests.get(url, headers=header)
    a = 3



response = requests.get("http://images.igdb.com/igdb/image/upload/t_cover_big/co1wzo.jpg")
with open("test.jpg", "wb") as f:
    f.write(response.content)
#generate_image_3("drawing of an attractive girl")
#models = get_models()
#for x in range(len(models)):
#    print(models[x]['id'] + '\t' + str(x+1))
#print(send_to_GPT3_5_requests("Hello, my name is John and I am a software"))
#print(generate_image("a white siamese cat"))