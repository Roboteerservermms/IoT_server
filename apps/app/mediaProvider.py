import time as t

import subprocess

def File(f,url,fname):
    fileName = f"{url}/{fname}"
    with open(fileName, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return fileName

def TTS(text, path):
    fileName = f"{path}/{t.strftime('%y%m%d%H%M%S')}.mp3"
    subprocess.call(["espeak", "-v ko", "-w"+fileName+".mp3", text])
    return fileName

def directTTS(text):
    subprocess.call(["espeak", "-v", "ko", text]) 