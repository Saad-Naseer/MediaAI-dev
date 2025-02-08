import speech_recognition as sr
from threading import Thread
from PyQt6.QtCore import pyqtSignal, QObject
import ast
from tools.audio_to_text.microphone import MicrophoneStream
from tools.audio_to_text.vosk_recognizer import vosk_recognizer
import speech_recognition as sr
import mimetypes
import ffmpeg
import wave
import io
import numpy as np

start_vosk = False

class SpeechRecognizer(QObject, Thread):
    status_update = pyqtSignal(str)
    text_update = pyqtSignal(dict)
    def __init__(self, tool=None, language="en-EN", file_path=None, model=None, engine=None):
        QObject.__init__(self)
        Thread.__init__(self)
        self.recognizer = sr.Recognizer()
        self.tool = tool
        self.language = language
        self.file_path = file_path
        self.model = model
        self.engine = engine
    
    def get_file_type(self):
        mime_type, _ = mimetypes.guess_type(self.file_path)
        
        if mime_type:
            if mime_type.startswith("audio"):
                return "audio"
            elif mime_type.startswith("video"):
                return "video"
        return "unknown"
    
    def extract_audio(self):
        try:
            # Run FFmpeg command to extract raw audio as PCM data
            process = (
                ffmpeg.input(self.file_path)
                .output("pipe:", format="wav", acodec="pcm_s16le")  # PCM 16-bit WAV
                .run(capture_stdout=True, capture_stderr=True)
            )

            audio_bytes = process[0]  # Extracted audio as bytes
            return audio_bytes
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None
   
    def run(self):
        if self.tool == "mic":
            self.mic_to_text(language=self.language, engine=self.engine, model=self.model)
        elif self.tool == "file":
            if self.file_path:
                if self.get_file_type() == "video":
                    self.video_to_text(file_path=self.file_path, language=self.language, engine=self.engine, model=self.model)
        
                if self.get_file_type() == "audio":
                    self.audio_to_text(file_path=self.file_path, language=self.language, engine=self.engine, model=self.model)
        
    def set_status(self, status: str):
        self.status_update.emit(status)

    def set_text(self, text):
          # Ensure the emitted type is dict
        if not isinstance(text, dict):
            raise TypeError("Expected dict type for text_update signal")
        self.text_update.emit(text)
        

    def dict_to_text(self, data):
        text = data['text']
        return text

    def format_time(self, seconds, separator=','):
        """Convert seconds to SRT or VTT time format."""
        millis = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}{separator}{millis:03}"

    def dict_to_srt(self, data):
        """Convert a dictionary with subtitle data to an SRT formatted string."""
        srt = ""
        for i, segment in enumerate(data['segments']):
            start = self.format_time(segment['start'], ',')
            end = self.format_time(segment['end'], ',')
            text = segment['text'].strip()
            
            srt += f"{i + 1}\n{start} --> {end}\n{text}\n\n"
        
        return srt
    
    def dict_to_vtt(self, data):
        """Convert a dictionary with subtitle data to a VTT formatted string."""
        vtt = "WEBVTT\n\n"
        for i, segment in enumerate(data['segments']):
            start = self.format_time(segment['start'], '.')
            end = self.format_time(segment['end'], '.')
            text = segment['text'].strip()
            
            vtt += f"{start} --> {end}\n{text}\n\n"
        
        return vtt
    
    def mic_to_text(self, language, engine, model):
        global start_vosk
        if engine == "whisper":
            self.set_status("starting whisper...")
            start_vosk = False

            print(start_vosk)
            with sr.Microphone() as source:
                self.set_status("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=5)
                self.set_status("Listening... Speak into the mic")
                audio = self.recognizer.listen(source=source, timeout=10)
                text = self.recognizer.recognize_whisper(audio_data=audio, language=language, show_dict=True, model=model)
                self.set_status("Done")
                self.set_text(text)
        if engine == "vosk":
            start_vosk = True
            print(start_vosk)
            self.set_status("starting vosk...")
            self.vosk = vosk_recognizer()
            mic_stream = MicrophoneStream()
            self.set_status("Listening... Speak into the mic")
            try:
                while start_vosk:
                    print(start_vosk)
                    audio = mic_stream.read()
                    if audio:            
                        self.vosk.data(data=audio)
                        text = self.vosk.get_partial_result()
                        text = ast.literal_eval(text)
                        text['text'] = text.pop('partial')
                        #self.set_status("Done")
                        self.set_text(text)
                    else:
                        print("No audio data captured")  # Debug: No audio data case
            except Exception as e:
                self.set_status(f"An error occurred: {e}")
            finally:
                mic_stream.stop()
                    


    def audio_to_text(self, file_path, language, engine, model):
        global start_vosk
        start_vosk = False
        with sr.AudioFile(file_path) as source:
            audio = self.recognizer.record(source)
            self.set_status("Processing...")
            try:
                if engine == "whisper":
                    text = self.recognizer.recognize_whisper(audio_data=audio, language=language, show_dict=True, model=model)
                if engine == "vosk":
                    text = self.recognizer.recognize_vosk(audio_data=audio, language=language)
                    text = ast.literal_eval(text)
                    
                self.set_status("Done")
                self.set_text(text)
           
            except sr.UnknownValueError:
                self.set_status("Google could not understand the audio")
            except sr.RequestError as e:
                self.set_status(f"Request to Google service failed: {e}")
            except Exception as e:
                self.set_status(f"An error occurred: {e}")
                #print(e)



    def extract_audio_from_video(self, file_path):
        """
        Extracts audio from a video file and returns raw PCM data.
        
        Returns:
            tuple: (audio_bytes, sample_rate, sample_width)
        """
        # Extract audio using FFmpeg
        out, _ = (
            ffmpeg
            .input(file_path)
            .output("pipe:", format="wav", ac=1, ar=16000)  # Mono, 16kHz
            .run(capture_stdout=True, capture_stderr=True)
        )

        # Load audio into a wave file (in memory)
        with wave.open(io.BytesIO(out), "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()
            audio_bytes = wav_file.readframes(wav_file.getnframes())

        return audio_bytes, sample_rate, sample_width



    def video_to_text(self, file_path, language, engine, model):
        global start_vosk
        start_vosk = False

        # Extract audio from video
        audio_bytes, sample_rate, sample_width = self.extract_audio_from_video(file_path)
        if not audio_bytes:
            self.set_status("Failed to extract audio from video.")
            return
        
        # Convert to AudioData (used for speech recognition)
        audio_data = sr.AudioData(audio_bytes, sample_rate, sample_width)

        self.set_status("Processing...")
        
        try:
            if engine == "whisper":
                text = self.recognizer.recognize_whisper(audio_data=audio_data, language=language, show_dict=True, model=model)
            elif engine == "vosk":
                text = self.recognizer.recognize_vosk(audio_data=audio_data, language=language)
                text = ast.literal_eval(text)
            else:
                self.set_status("Unsupported engine selected.")
                return
                    
            self.set_status("Done")
            self.set_text(text)

        except sr.UnknownValueError:
            self.set_status("Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            self.set_status(f"Request to service failed: {e}")
        except Exception as e:
            self.set_status(f"An error occurred: {e}")
