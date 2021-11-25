GPIOOUT = [65, 68, 70, 71, 72, 73, 74, 76]
GPIOIN = [111, 112, 113, 114, 229, 117, 118, 75]
INPIN = { 0 : 75, 1: 111, 2 : 112, 3 : 113, 4 : 114, 5: 229, 6: 117, 7: 118 }
OUTPIN = {1 : 65, 2: 68 , 3 : 70, 4 : 71, 5 : 72, 6 : 73, 7 : 74 , 8 : 76  }

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

mediaOrder = ['File', 'rtsp','TTS']