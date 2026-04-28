import whisper
from llama_cpp import Llama
from llm import Llm
from asr import Transcription
from recorder import Recorder
from pynput.keyboard import Listener

#**************RUN APP USING BUILT IN RECORDER**************#

# * KEEPS THE ENTIRE PROCESS IN THE CLI BUT WORKS EXCLUSIVELY VIA VOICE RECOGNITION
# * TO CHAT WITH THE LLM VIA KEYBOARD RUN THE llm.py SCRIPT INSTEAD
# * KEEP IN MIND, NEITHER llm.py NOR THIS FUNCTION HAVE CONVERSATION MEMORY
# * THAT MEANS ONLY ONE QUESTION AND ONE ANSWER BEFORE TERMINATION
# * WE CAN INCLUDE FEATURES TO FACILITATE PROPER CONVERSATIONS IN THE CLI
# * I WILL NEVER IMPLEMENT THAT BECAUSE USING AN UI WAS ALWAYS THE GOAL BEHIND THE PROJECT



def no_gui(llm_model, asr_model):
    # START RECORDING USING RECORDER SCRIPT
    voice_record = Recorder()
    with Listener(on_press=voice_record.on_press) as listener:
        listener.join()
    audio_name = voice_record.filename

    # SEND RECORDING TO WHISPER
    whisper = Transcription(asr_model, audio_name)
    whisper_text = whisper.transcribe()
    final_prompt = [{"role": "user", "content": whisper_text}]

    # SEND TRANSCRIBED TEXT TO LLM
    ai_response = Llm(llm_model, final_prompt)
    for chunk in ai_response.llm_response():
        print(chunk, end='', flush=True)

def load_model(persist="disk"):
    return Llama(
        model_path="./models/model.gguf",
        verbose=False,
        chat_format="chatml"
    )

def load_asr(persist="disk"):
    return whisper.load_model("base")



llm_model = load_model()
asr = load_asr()
no_gui(llm_model, asr)





