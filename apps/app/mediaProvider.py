import pyttsx3
import time as t
def TTS(rawData, mainJson):
    engine = pyttsx.init()
    nowTime = t.strftime("%Y%m%d_%H%M%S")
    fileName=f"{BASE_DIR}{nowTime}.mp3"
    engine.save_to_file(rawData,fileName)
    return fileName


def rtsp(inMsg, mainJson):
    m = { "OUTPUT" : inMsg["GPIO_OUT"], "media": inMsg["data"] }
    mainJson['GPIO'][str(inMsg["GPIO_IN"])].append(m)

def broadcast(inMsg, mainJson):
    m = { "OUTPUT" : inMsg["GPIO_OUT"], "media": inMsg["data"] }
    mainJson['GPIO'][str(inMsg["GPIO_IN"])].append(m)

def scheduleAdd(rawData):
    m = { "time" : inMsg["time"], "media": inMsg["data"] }
    mainJson['schedule'][inMsg["day"]].append(m)