import whisper

class Transcription:

    def __init__(self, model, filename):
        self.model = model
        self.result = None
        self.filename = filename

    def transcribe(self):
        print("\n\nStarting Transcription Service....\n\n")
        self.result = self.model.transcribe(self.filename, fp16=False)
        print("\n\nTranscription Concluded... Check Results below:\n\n")
        print(f"\n\n{self.result['text']}\n\n")
        return self.result["text"]


if __name__ == "__main__":
    asr_model = whisper.load_model("base")
    t = Transcription(asr_model, "output.wav")
    t.transcribe()