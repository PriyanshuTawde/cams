from flask import Flask, Response
import cv2

app = Flask(__name__)

@app.route('/')
def index():
    return "RTSP Proxy Server"

def generate_frames(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream')
def stream():
    rtsp_url = "rtsp://admin:india*123@103.232.27.206:554/Streaming/channels/102"
    return Response(generate_frames(rtsp_url), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)







#C:\Users\priyn\Downloads\mediamtx_v1.8.3_windows_amd64>.\mediamtx.exe























