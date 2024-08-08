# MediaAI
## Libraries Required
### To use google_service_api:
```pip install SpeechRecognition PyAudio PyQt6```
### To use whisper
```pip install SpeechRecognition[whisper-api] PyAudio PyQt6 NumPy==1.26.4```
### To use vosk
```pip install vosk```
## To run the software
```git clone https://github.com/Saad-Naseer/MediaAI.git```

```python main.py```
## To Generate exe file:
```PyInstaller --onefile --add-data "path_to_whisper\\whisper\\assets:whisper\assets" .\main.py```
## Features
- [x] Audio (mic, .wav, .mp3, .AIFF, .AIFF-C, FLAC) to Text (.txt, .srt, .vvt) Converter 
