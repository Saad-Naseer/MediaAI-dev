import queue
import re
import sys

from google.cloud import speech
from google.oauth2 import service_account
import pyaudio
import pycountry

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate=RATE, chunk=CHUNK):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)

def listen_print_loop(responses):
    """Iterates through server responses and prints them."""
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            print(transcript + overwrite_chars)
            num_chars_printed = 0

    return transcript

def capture_initial_audio(duration):
    """Capture initial audio for the given duration."""
    p = pyaudio.PyAudio()
    
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print(f"Capturing initial {duration} seconds of audio...")
    frames = []
    for _ in range(int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    return b''.join(frames)

def transcribe_initial_segment(audio_content):
    """Transcribe the initial audio segment to detect language."""
    credentials = service_account.Credentials.from_service_account_file('key.json')
    client = speech.SpeechClient(credentials=credentials)

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",  # Use English as a default for initial detection
    )

    response = client.recognize(config=config, audio=audio)

    # Get the first result (initial sentence)
    first_sentence = response.results[0].alternatives[0].transcript
    print(f"Initial detected text: {first_sentence}")
    
    return first_sentence

def get_language_code(language_name):
    """Get the BCP-47 language code from a language name using pycountry."""
    try:
        lang = pycountry.languages.get(name=language_name)
        if lang:
            return lang.alpha_2  # Use alpha-2 code for language
        else:
            print(f"Language '{language_name}' not found.")
            return None
    except LookupError:
        print(f"Language '{language_name}' not found.")
        return None

def main():
    """Transcribe speech with auto language detection."""
    # Step 1: Capture a short initial segment for language detection
    initial_duration = 5  # Capture the first 5 seconds
    initial_audio = capture_initial_audio(initial_duration)

    # Step 2: Transcribe the initial segment
    initial_text = transcribe_initial_segment(initial_audio)

    # Step 3: Get the language code from the transcribed text
    detected_language_name = initial_text.split()[0]  # Assume the first word is the language
    detected_language_code = get_language_code(detected_language_name)

    if detected_language_code:
        print(f"Detected language code: {detected_language_code}")

        # Step 4: Restart the recognition process with the detected language
        credentials = service_account.Credentials.from_service_account_file('key.json')
        client = speech.SpeechClient(credentials=credentials)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=detected_language_code,  # Use detected language
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            listen_print_loop(responses)
    else:
        print("Could not detect a valid language. Exiting...")

if __name__ == "__main__":
    main()
