import time
import streamlit as st
import whisper
from llama_cpp import Llama
from chatbot.llm import Llm
from chatbot.asr import Transcription

#**************STREAMLIT APP LAYOUT AND FUNCTIONALITY**************#

# WE CACHE OUR MODEL(s) SO THAT IT IS NOT RELOADED EVERY TIME THE SCRIPT RUNS.

@st.cache_resource
def load_model(persist="disk"):
    return Llama(
        model_path="./models/model.gguf",
        verbose=False,
        chat_format="chatml"
    )

@st.cache_resource
def load_asr(persist="disk"):
    return whisper.load_model("base")

#**************INITIALIZE CHAT HISTORY AS A LIST**************#

# WE NEED STREAMLIT AND THE LLM TO RUN IN A STATEFUL MANNER IN ORDER TO:
# * RENDER OLDER MESSAGES IN THE CONVERSATION (STREAMLIT)
# * SUPPLY THE LLM WITH THE ENTIRE CONVERSATION, SO THAT WE CAN ACTUALLY HOLD A PROPER CONVERSATION

def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []

#**************SHOW CONVERSATION HISTORY EVERY TIME THE SCRIPT RERUNS**************#

# * STREAMLIT RERUNS THE SCRIPT EVERY TIME THE USER TAKES AN ACTION
# * SO THIS FUNCTION SERVES TO RENDER ALL THE OLD MESSAGES EACH TIME

def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

#**************HANDLE USER SIDE PROMPTS**************#

# THE USER CAN RECORD AN AUDIO DIRECTLY FROM STREAMLIT INTERFACE
# THE STREAMLIT-CREATED AUDIO HAS MANY METHODS BUT WE WANT TO ACCESS ITS BYTE VALUE IN ORDER TO SAVE IT AS A .wav FILE

def user_prompt():
    if prompt := st.chat_input(placeholder="What's on your mind?", accept_audio=True):
        # CHECK IF SUPPLIED PROMPT IS AUDIO
        if prompt.audio:
            audio_bytes = prompt.audio.getvalue()   #GET AUDIO VALUE IN BYTES. BYTE VALUES CAN BE ACCESSED FROM STREAMLIT RECORDED AUDIO.
            with open("audio.wav", "wb") as f:
                f.write(audio_bytes)        #SAVE AS WAV FILE -> FILENAME - audio.wav -> STORED IN ROOT OF APP
            
            # CALL WHISPER TRANSCRIPTION MODULE TO TRANSCRIBE SUPPLIED AUDIO
            transcription = Transcription(asr, "audio.wav")
            transcribed_text = transcription.transcribe()
            
            # SHOW THE RECORDED AUDIO WHICH CAN BE PLAYED BACK IN THE BROWSER USING ITS DEFAULT SPEAKER
            with st.chat_message("user"):
                st.audio(prompt.audio)
            if transcribed_text:
                st.chat_message("user").markdown(transcribed_text)
                st.session_state.messages.append({"role": "user", "content": transcribed_text})
                ai_response(transcribed_text)
            else:
                st.chat_message("user").markdown("Couldn't transcribe audio...")
        else:
            with st.chat_message("user"):
                st.markdown(prompt.text)
            st.session_state.messages.append({"role": "user", "content": prompt.text})        # EVERYTIME THERE IS A MESSAGE IT IS APPENDED TO THE CONVERSATION HISTORY.
            # IMPORTANT - 'prompt' CONTAINS NOT ONLY TEXT BUT MULTIPLE ELEMENTS AND WE HAVE TO ACCESS EACH ONE OF THEM INDIVIDUALLY.
            # THIS HAPPENS BECAUSE WE HAVE ALLOWED IT TO CONTAIN AUDIO.
            ai_response(prompt.text)

#**************HANDLE LLM SIDE PROMPTS**************#

def ai_response(user_input):
    response = f"Echo: {user_input}"
    bot_response = Llm(llm_model, st.session_state.messages)                # CALL THE LLM FROM THE RELEVANT MODULE. 
    # WE PASS THE CACHED MODEL AND THE CONVERSATION HISTORY WE CREATED ABOVE.
    with st.chat_message("assistant"):
        response = st.write_stream(bot_response.llm_response())
    st.session_state.messages.append({"role": "assistant", "content": response})        # EVERYTIME THERE IS A MESSAGE IT IS APPENDED TO THE CONVERSATION HISTORY.


# LOAD THE MODELS ONCE AND PASS THEM WHENEVER NEEDED

llm_model = load_model()
asr = load_asr()

# ENTER THE COMMAND: streamlit run main.py TO RUN THIS APP USING STREAMLIT

initialize_chat_history()
display_chat_history()
user_prompt()




