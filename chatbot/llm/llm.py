from llama_cpp import Llama
import time

class Llm:

    def __init__(self, llm, messages):
        self.llm = llm      # The LLM model is passed as an argument here so that it is not loaded every time especially if using Streamlit
        self.response = None
        self.messages = messages    # We pass a particularly structured nested dictionary containing clearly demarcated roles.
        # We can change the system prompt here or use any of the getter/setter functions to change them.
        self.system_prompt = """You are a funny, sarcastic and helpful assistant. 
        Answer the question briefly. If you don't know the answer, simply state that you don't know."""
    
    # GETTTER METHOD TO READ CURRENT SYSTEM PROMPT

    def get_system_prompt(self):
        return self.system_prompt

    # SETTER METHOD TO SAFELY CHANGE CURRENT SYSTEM PROMPT
    # * Future updates would include a more comprehensively verified method
    # * Another idea is to load it externally from a file stored locally so that the code needn't be opened or 
    # * Use the streamlit UI to enable users to change it directly from the browser.

    def set_system_prompt(self):
        try:
            self.system_prompt = input("Enter system prompt...")
            print(f"System Prompt set successfully!\nCurrent system prompt: {self.system_prompt}")
        except:
            print("There was an error! Try again later...")

    # METHOD TO QUERY THE LARGE LANGUAGE MODEL

    def llm_response(self):
        stream = self.llm.create_chat_completion(
            
            messages = [
                {
                    'role' : 'system',
                    'content' : self.system_prompt
                }
            ] + self.messages, 
            stream=True
        )
        # self.messages contains the list of messages so far in the conversation. It is separated by user+prompt and assistant+response. 
        # Future updates would include loading different conversations from disk into memory.

        # Since the response can be streamed, we are filtering our stream to only send out the data. 
        # Future updates would include filtering out the <think></think> tags (Qwen) and its contents and response time out features to combat thinking loops. 

        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]



if __name__== '__main__':
    user_prompt = [{'role': 'user', 'content': input("What's your question?\n")}]
    #EXAMPLE MODEL USED - Qwen3.5-9B-Q4_K_M
    #PLACE MODEL (IN GGUF) IN models FOLDER AND RENAME IT TO model.gguf OR ELSE CHANGE NAME BELOW
    #Model is loaded once when an object instance is created.
    #Model's characteristics can be changed from within the code now. 
    #Future updates would allow users to change these metrics from a text file. The script would load this file to adjust these settings.
    model = Llama(
            model_path="./models/model.gguf",
            n_ctx=32000, 
            verbose=False)
    agent = Llm(model, user_prompt)
    for c in agent.llm_response():
        print(c, end='', flush=True)