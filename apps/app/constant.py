GPIOOUT = [65, 68, 70, 71, 72, 73, 74, 76]
GPIOIN = [111, 112, 113, 114, 229, 117, 118, 75]
INPIN = { 111 : 1, 112 : 2, 113 : 3, 114 : 4, 229 : 5, 117 : 6, 118 : 7, 75 : 8 }
OUTPIN = { 1 : 65, 2: 68 , 3 : 70, 4 : 71, 5 : 72, 6 : 73, 7 : 74, 8 : 76 }

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

scheduleMedia = { 
    "startTime" : "",
    "endTime" : "",
    "FirstGPIOIN" : [],
    "LastGPIOIN" : [],
    "GPIOOUT":[],
    "Broadcast":{
        "TTS":"",
        "RTSP":"",
        "File":""
    }
}


GPIOMedia ={
    "GPIOOUT" : [],
    "Broadcast" : {
        "TTS" : "", "File": "", "RTSP" : "" 
    }
}

def handleUploadedFile(f,url,fname):
    with open(f'{url}/{fname}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)