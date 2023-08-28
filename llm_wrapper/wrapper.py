import time
import requests
import openai
import dotenv
import os
import pdb
from langchain.vectorstores.weaviate import Weaviate
import weaviate

class LLMWrapper:
    """Wrapper class for the LLM API."""
    def __init__(self, max_tokens=1000, model="gpt-3.5-turbo", max_try=2, temprature=0):
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temprature
        self.max_try = max_try
        self.history = False

    def _send_request(self, system_prompt="", user_prompt="", vectorstore=None):
        for _ in range(self.max_try):
            try:
                if self.history:
                    batch_size = 5
                    class_name = "Chat"
                    class_properties = ["conversation", "chatIndex"]
                    
                    query = (
                        vectorstore.query
                        .get(class_name, class_properties)
                        .with_near_text({"concepts": [user_prompt]})
                        .with_limit(batch_size)
                    )

                    chat_history = query.do()["data"]["Get"]["Chat"]
                    chat_history = sorted(chat_history, key=lambda x: x["chatIndex"])
                    chat_history = [c["conversation"] for c in chat_history]

                    CHAT_HISTORY_PROMPT = [{"role": "system", "content": """You are a smart AI conversation summarizer. 
                                            Your goal is to summarize the conversation between the user and the AI assistant keeping the context of the conversation."""}, 
                                           {"role": "user", "content": f"""The following is a conversation with an AI assistant.
                                            summarize it as a single conversation in following format:
                                            ----------------
                                            User: 
                                            AI: 
                                            ----------------
                                            below is the conversation delimited by []:
                                            {chat_history},
                                            """}]
                    print(CHAT_HISTORY_PROMPT, "printing chat history")
                    chat_summary = response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=CHAT_HISTORY_PROMPT,
                        max_tokens=1000,
                        temperature=self.temperature,
                        stream=False,
                    )
                    chat_summary = chat_summary.choices[0].message["content"]
                    print(chat_summary, "printing chat summary")

                    GENERAL_CHAT_PROMPT = [{"role": "system", "content": system_prompt}, 
                                           {"role": "user", "content": f"""Below is the summary conversation between the user and the AI assistant. 
                                            Consider this as the context delimited by <> of the conversation and answer the users question.
                                            <{chat_summary}>
                                            ----------------
                                            User: {user_prompt}
                                            """}]
                    print(GENERAL_CHAT_PROMPT, "printing general chat prompt")
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=GENERAL_CHAT_PROMPT,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        stream=True,
                    )
                    return response 
                else:
                    CHAT_PROMPT = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
                    print(CHAT_PROMPT, "printing chat prompt")
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=CHAT_PROMPT,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        stream=True,
                    )
                    return response

            except openai.error.RateLimitError as e:
                self._handle_rate_limit()
                return self._send_request(CHAT_PROMPT, vectorstore)
            
            except openai.error.InvalidRequestError as e:
                if len(prompt) > self.max_tokens:
                    print("Prompt too long. Truncating...")
                    prompt = prompt[:self.max_tokens]
                    return self._send_request(prompt, vectorstore)
                print("Invalid request:", e)
                return {'error': 'invalid_request'}
            
            except Exception as e:
                print("Unhandled exception:", e)
                return {'error': 'unknown'}

    def _handle_rate_limit(self):
        print("Rate limit exceeded. Waiting before retrying...")
        time.sleep(60) 

    def generate_response(self, user_input, vectorstore, k=10):
        batch_size = k
        class_name = "Mails"
        class_properties = ["mailBody", "mailSubject"]
        query = (
            vectorstore.query
            .get(class_name, class_properties)
            .with_near_text({"concepts": ["Internship applications"]})
            .with_limit(batch_size)
        )

        context = query.do()["data"]["Get"]["Mails"]

        SYSTEM_PROMPT = f"""Use following pieces of context to answer the users question, following contexts are summarised texts from users inbox. If question is not relevant to context answer by yourself.
                    ----------------
                    {context}""" 
        conversation = user_input
        response = self._send_request(SYSTEM_PROMPT, conversation, vectorstore)
        
        return response

    def reset_history(self):
        self.history = False

if __name__ == "__main__":
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_APIKEY")
    API_TOKEN = os.getenv("HUGGINGFACE_APIKEY")

    wrapper = LLMWrapper()
    vectrstore = weaviate.Client("http://localhost:8080",
            additional_headers={
                "X-HuggingFace-Api-Key": API_TOKEN
    })

    index = 0
    while True:
        user_input = input("\nUser: ")    
        response = wrapper.generate_response(user_input, vectrstore, 3)

        response_msg = ""
        for r in response:
            if r["choices"][0]["delta"] == {}:
                break
            msg = r["choices"][0]["delta"]["content"]
            response_msg += msg
            print(msg, end="", flush=True)
        wrapper.history = True
        vectrstore.data_object.create({
            "conversation": str({"User": user_input,
                                 "AI": response_msg}), 
            "chatIndex": index
            }, "Chat")
        index += 1