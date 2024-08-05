import speech_recognition as sr
from threading import Thread
from PyQt6.QtCore import pyqtSignal, QObject

class SpeechRecognizer(QObject, Thread):
    status_update = pyqtSignal(str)
    text_update = pyqtSignal(str)
    
    def __init__(self, tool=None, language="en-EN", file_path=None):
        QObject.__init__(self)
        Thread.__init__(self)
        self.recognizer = sr.Recognizer()
        self.tool = tool
        self.language = language
        self.file_path = file_path

    def run(self):
        if self.tool == "mic":
            self.mic_to_text()
        elif self.tool == "file":
            if self.file_path:
                self.file_to_text(self.file_path)
        
    def set_status(self, status: str):
         print("emit")
         self.status_update.emit(status)

    def set_text(self, text: str):
         self.text_update.emit(text)
    def format_time(self, seconds):
        """Convert seconds to SRT time format."""
        millis = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

    def dict_to_srt(self, data):
        """Convert a dictionary with subtitle data to an SRT formatted string."""
        print("srt")
        srt = ""
        for i, segment in enumerate(data['segments']):
            start = self.format_time(segment['start'])
            end = self.format_time(segment['end'])
            text = segment['text'].strip()
            
            srt += f"{i + 1}\n{start} --> {end}\n{text}\n\n"
        
        return srt
    
    def dict_to_vtt(self, data):
        vtt = "WEBVTT\n\n"
        for i, segment in enumerate(data['segments']):
            start = self.format_time(segment['start'], '.')
            end = self.format_time(segment['end'], '.')
            text = segment['text'].strip()
            
            vtt += f"{i + 1}\n{start} --> {end}\n{text}\n\n"
        
        return vtt
    
    def mic_to_text(self):
        with sr.Microphone() as source:
            self.set_status("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=5)
            self.set_status("Listening... Speak into the mic")
            try:
                audio = self.recognizer.listen(source, timeout=10)
                self.set_status("Processing...")
                text = self.recognizer.recognize_google(audio, language=self.language)
                #print("Text: " + text)
                #with open("mic_to_text.txt", "w") as file:
                #    file.write(text)
                self.set_status("Done")
                self.set_text(str(text))

            
            except sr.WaitTimeoutError:
                self.set_status("No audio detected from mic")
            except sr.UnknownValueError:
                self.set_status("Google could not understand the audio")
            except sr.RequestError as e:
               self.set_status(f"Request to Google service failed: {e}")
            except Exception as e:
                 self.set_status(f"An error occurred: {e}")

    def file_to_text(self, file_path):
        with sr.AudioFile(file_path) as source:
            self.set_status("Processing...")
            try:
                audio = self.recognizer.listen(source, timeout=10)
                #text = self.recognizer.recognize_google(audio, language=self.language, show_all=True)
                text = self.recognizer.recognize_whisper(audio, language=self.language, show_dict=True, model="base")

                #with open("audio_file_to_text.txt", "w") as file:
                #    file.write(text)
                self.set_status("Done")
                self.set_text(str(text))
                #srt_output = self.dict_to_srt(text)
                #print("srt: ", srt_output)
            except sr.UnknownValueError:
                self.set_status("Google could not understand the audio")
            except sr.RequestError as e:
                self.set_status(f"Request to Google service failed: {e}")
            except Exception as e:
                self.set_status(f"An error occurred: {e}")
