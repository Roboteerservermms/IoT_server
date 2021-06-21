from flask import Flask, render_template
app = Flask(__name__)

@app.route("/") #route 데코레이터 - 어떤 URL이 펑션을 호출할지 알려준다.
@app.route("/index")#두가지 URL를 적어도 되네...
def main_index():
	return render_template('main.html')

@app.route("/broadcast")
def broadcast():
	return render_template('broadcast.html')

@app.route("/board")
def raspberrypi():
	return render_template('board.html')
  
if __name__ == '__main__':  # 모듈이 실행 됨을 알림
   app.run('0.0.0.0',port=5000,debug=True)
   # 서버 실행, 파라미터로 debug 여부, port 설정 가능