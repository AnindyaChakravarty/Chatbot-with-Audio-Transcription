from pynput.keyboard import Key, Listener
from datetime import datetime
import threading
import time
import pyaudio
import wave


class Recorder:

    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 48000
    seconds = 3

    def __init__(self):
        self.isRecording = False        #Condition that will be used to stop recording and save it.
        self.worker_thread = None       #Thread (eventually) that will run parallel to keyboard listener
        self.frames = []
        self.streams = None
        self.p = pyaudio.PyAudio()
        self.filename = ""
        """Initialise as an instance variable instead of class attribute so that 
        if one instance closes the portAudio while another instance is running it 
        won't harm the other instance."""
    
    def start_recording(self):
        print("Recording Now...")
        self.frames = []              
        # Reset frames everytime before recording so that it is not reused in the same execution
        self.streams = self.p.open(
            format=Recorder.sample_format,
            channels=Recorder.channels,
            rate=Recorder.fs,
            frames_per_buffer=Recorder.chunk,
            #input_device_index=2 #Change manually if OS Default is not working.
            input=True)
        while self.isRecording:
            data = self.streams.read(Recorder.chunk, exception_on_overflow=False)       #exception_on_overflow=False fixes buffer overflow
            self.frames.append(data)
    
    def stop_recording(self):
        if self.streams is None:          # Safeguard in case self.streams is empty.
            return
        self.streams.stop_stream()
        self.streams.close()
        sample_width = self.p.get_sample_size(Recorder.sample_format)
        self.p.terminate()            # Terminate the PortAudio interface

        print('\nFinished recording')

        self.filename = f"output_{datetime.now().strftime('%Y%M%d-%H%M%S')}.wav"
        # Save the recorded data as a WAV file
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(Recorder.channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(Recorder.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def terminate(self):
        # Check first if p or streams were ever used to begin with. 
        # useful when user quits right away when script runs. 
        # Check independently so that if one is open and another isn't then we can handle that properly.
        if self.streams is not None:
            self.streams.stop_stream()
            self.streams.close()

        if self.p is not None:
            self.p.terminate()
        # Close any remaining open streams and terminate properly.

    def on_press(self, key):

        if key == Key.space:

            if not self.isRecording:
                self.isRecording = True
                self.worker_thread = threading.Thread(target=self.start_recording)
                self.worker_thread.start()
            
            else:
                self.isRecording = False
                if self.worker_thread is not None:
                    self.worker_thread.join()

                self.stop_recording()
                return False


        elif key == Key.esc:
            self.isRecording = False
            if self.worker_thread is not None:
                self.worker_thread.join()
            self.terminate()
            print("\nQuitting...")
            return False

        else:
            print("Invalid input...")

        return True
    
    def diagnostic(self):
        print("Available and Active Microphones:")
        print("-" * 40)

        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if self.p.get_default_input_device_info()["index"] == device_info["index"]:
                print("[ACTIVE]")
            if device_info["maxInputChannels"] > 0:
                print(f"Index: {device_info['index']} \nName : {device_info['name']} \nSample Rate: {device_info['defaultSampleRate']} \nChannels: {device_info['maxInputChannels']}")
                print("-" * 40)
        print(
            """Note down index of the device you want to use and change """
            """in class definition (inside start_recording() ->""" 
            """uncomment input_device_index -> change value to index you noted.)"""
            )
        self.p.terminate()

print("""
Welcome to our WIP Chatbot. 
1. To start speaking, press Space.
2. Once you are done press Space again start processing the audio.
3. You can press ESCAPE to quit recording. But you will lose your current (if any) recording.
X. You can run obj.diagnostic() to get a list of available and active microphones
""")
if __name__ == "__main__":
    recorder = Recorder() 
    # recorder.diagnostic()
    with Listener(on_press=recorder.on_press) as listener:
        listener.join()