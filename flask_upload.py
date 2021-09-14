from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os, subprocess
from client import UDPClient
import json
app = Flask(__name__)
client = UDPClient()
client.create_socket()
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #파일 업로드 용량 제한 단위:바이트
#HTML 렌더링
@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/<ip>')
def device_page(ip):
    return render_template('device.html')

# 파일 리스트
@app.route('/<ip>/list')
def list_page(ip):
    json_data =None
    with open(f'./json/{ip}.json', 'r') as f:
        json_data = json.load(f)
    print(json.dumps(json_data) )
    html = """<center><a href="/">홈페이지</a><br><br>"""
    html += "file_list: {}".format(json_data) + "</center>"
    return html

#업로드 HTML 렌더링
@app.route('/file')
def fileupload_page():
    return render_template('file.html')

@app.route('/tts')
def ttsupload_page():
    return render_template('tts.html')

@app.route('/rtsp')
def rtspupload_page():
    return render_template('rtsp.html')

@app.route('/schedule')
def scheduleupload_page():
    return render_template('schedule.html')

#파일 업로드 처리
@app.route('/<ip>/fileUpload', methods = ['GET', 'POST'])
def upload_file(ip):
    if request.method == 'POST':
        print("upload file!")
        f = request.files['file']
        out =  request.form.getlist("GPIOOUT")
        In = int(request.form.getlist("GPIOIN")[0])
        sendOutArray = [0,0,0,0,0,0,0,0]
        for i in range(8):
            if str(i) in out:
                sendOutArray[i] = 1
            else:
                sendOutArray[i] = 0
        data_dic={"category": "File", "GPIO_IN": In, "GPIO_OUT": sendOutArray,"data": f"{secure_filename(f.filename)}"}
        print(f"sendto {ip} {data_dic}")
        ret = client.interact_with_server(ip, 8080, data_dic)
        #저장할 경로 + 파일명
        f.save('./uploads/' + secure_filename(f.filename))
        subprocess.getoutput(f"sshpass -p orangepi scp ./uploads/{secure_filename(f.filename)} orangepi@{ip}:/home/orangepi/IoT_target/ ")
    return render_template('check.html')

#파일 업로드 처리
@app.route('/<ip>/TTSUpload', methods = ['GET', 'POST'])
def upload_tts(ip):
    if request.method == 'POST':
        f = str(request.form.getlist("text")[0])
        out =  request.form.getlist("GPIOOUT")
        In = int(request.form.getlist("GPIOIN")[0])
        sendOutArray = [0,0,0,0,0,0,0,0]
        for i in range(8):
            if str(i) in out:
                sendOutArray[i] = 1
            else:
                sendOutArray[i] = 0
        data_dic={"category": "TTS", "GPIO_IN": In, "GPIO_OUT": sendOutArray,"data": f"{f}"}
        print(f"sendto {ip} {data_dic}")
        ret = client.interact_with_server(ip, 8080, data_dic)
        #저장할 경로 + 파일명
        print(ret)
    return render_template('check.html')

#파일 업로드 처리
@app.route('/<ip>/RTSPUpload', methods = ['GET', 'POST'])
def upload_rtsp(ip):
    if request.method == 'POST':
        f = str(request.form.getlist("text")[0])
        out =  request.form.getlist("GPIOOUT")
        In = int(request.form.getlist("GPIOIN")[0])
        sendOutArray = [0,0,0,0,0,0,0,0]
        for i in range(8):
            if str(i) in out:
                sendOutArray[i] = 1
            else:
                sendOutArray[i] = 0
        data_dic={"category": "rtsp", "GPIO_IN": In, "GPIO_OUT": sendOutArray,"data": f"{f}"}
        print(f"sendto {ip} {data_dic}")
        client.interact_with_server(ip, 8080, data_dic)
        #저장할 경로 + 파일명
    return render_template('check.html')

#파일 업로드 처리
@app.route('/<ip>/scheduleUpload', methods = ['GET', 'POST'])
def upload_schedule(ip):
    if request.method == 'POST':
        print("upload schedule!")
        f = request.files['file']
        data_dic = {}
        day =  str(request.form.getlist("DAY")[0])
        time = str(request.form.getlist("TIME")[0])
        data_dic={"category": "schedule", "day": day, "time": time, "data": f"{secure_filename(f.filename)}"}
        print(f"sendto {ip} {data_dic}")
        client.interact_with_server(ip, 8080, data_dic)
        #저장할 경로 + 파일명
        f.save('./uploads/' + secure_filename(f.filename))
        subprocess.getoutput(f"sshpass -p orangepi scp ./uploads/{secure_filename(f.filename)} orangepi@{ip}:/home/orangepi/IoT_target/ ")
    return render_template('check.html')

#서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)