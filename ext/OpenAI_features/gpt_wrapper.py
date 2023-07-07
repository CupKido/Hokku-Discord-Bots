import enum 
import json
import aiohttp
import requests

class role_options(enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

    @classmethod
    def get_role_message(instance, role, message):
        if role == instance.user:
            return {"role": instance.user.value, "content": message}
        elif role == instance.assistant:
            return {"role": instance.assistant.value, "content": message}
        else:
            raise Exception("Invalid role")


class gpt_wrapper:
    # TODO: add support for newer models 
    class supported_models(enum.Enum):
        gpt_3_5_turbo = "gpt-3.5-turbo"
        gpt_4 = "gpt-4"

    @classmethod
    def get_tokens_per_dollar(instance, model : supported_models):
        if model == instance.supported_models.gpt_3_5_turbo:
            return 500000
        if model == instance.supported_models.gpt_4:
            return 16666.7
        else:
            raise Exception("Invalid model name")
        
    @classmethod
    def tokens_to_dollars(instance, tokens, model : supported_models):
        return tokens / instance.get_tokens_per_dollar(model)

    @classmethod
    async def get_response_with_history_async(instance, user_history : list, model : supported_models, api_key, loaded=False, callback=None):
        refactored_user_history = [{"role": "system", "content": "You are a helpful assistant."}]
        if loaded:
            for message in user_history:
                refactored_user_history.append(message)
        else:
            for message in user_history:
                if message[0] == role_options.user:
                    refactored_user_history.append({"role":"user", "content" : message[1]})
                elif message[0] == role_options.assistant:
                    refactored_user_history.append({"role":"assistant", "content" : message[1]})
                elif message[0] == role_options.system:
                    refactored_user_history.append({"role":"system", "content" : message[1]})

        chatgpt_url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key  # Replace with your actual API key
        }
        
        data = {
            "model" : model.value,
            #"model" : "gpt-4-0314",
            "messages": refactored_user_history
        }
        async with aiohttp.ClientSession() as session:
            #print('getting image:\t' + prompt)
            async with session.post(chatgpt_url, headers=headers, data=json.dumps(data)) as response:
                if response.status == 200:
                    response_json = await response.json()
                    answer = response_json["choices"][0]["message"]["content"]
                    token_amount = response_json['usage']['total_tokens']
                    if callback is None:
                        return answer, token_amount
                    else:
                        await callback(answer, token_amount)
                else:
                    raise Exception("Sorry, we have encountered an error. Please try again")

    @classmethod
    async def get_response_async(instance, message : str, model : supported_models, api_key, callback=None):
        user_history = [(role_options.user, message)]
        return await instance.get_response_with_history(user_history, model, api_key, callback=callback)
    
    @classmethod
    def get_response_with_history(instance, user_history : list, model : supported_models, api_key, loaded=False):
        refactored_user_history = [{"role": "system", "content": "You are a helpful assistant."}]
        if loaded:
            for message in user_history:
                refactored_user_history.append(message)
        else:
            for message in user_history:
                if message[0] == role_options.user:
                    refactored_user_history.append({"role":"user", "content" : message[1]})
                elif message[0] == role_options.assistant:
                    refactored_user_history.append({"role":"assistant", "content" : message[1]})

        chatgpt_url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key  # Replace with your actual API key
        }
        
        data = {
            "model" : model.value,
            #"model" : "gpt-4-0314",
            "messages": refactored_user_history
        }
        response = requests.post(chatgpt_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json()
        answer = response_json["choices"][0]["message"]["content"]
        token_amount = response_json['usage']['total_tokens']
        return answer, token_amount
        
    @classmethod
    def get_response(instance, message : str, model : supported_models, api_key):
        user_history = [(role_options.user, message)]
        return instance.get_response_with_history(user_history, model, api_key)