import time as t
from gtts import gTTS
import subprocess
from django.conf import settings
def File(f,url,fname):
    fileName = f"{url}/{fname}"
    with open(fileName, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return fileName

def TTS(recvText):
    fileName = f"{settings.MEDIA_ROOT}/{recvText}.mp3"
    tts = gTTS( text=recvText, lang='ko', slow=False )
    tts.save(fileName)
    return fileName

def directTTS(text):
    subprocess.call(["espeak", "-v", "ko", text])
