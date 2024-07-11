from flask import Flask, request, jsonify
import subprocess
import redis

app = Flask(__name__)

# Connect to the Redis server
try:
    cache = redis.StrictRedis(host='localhost', port=6379, db=0)
    cache.ping()
    print("Connected to Redis")
except redis.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")

# Function to start FFmpeg process for restreaming
def start_ffmpeg_server(rtsp_input_url, rtsp_output_url):
    command = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',  # Use TCP for RTSP
        '-i', rtsp_input_url,  # Input URL
        '-c:v', 'copy',  # Copy the video codec
        '-f', 'rtsp',  # Output format
        rtsp_output_url  # Output URL
    ]
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # No need to store process ID in Redis for this example

@app.route('/start_streams', methods=['POST'])
def start_streams():
    data = request.get_json()
    rtsp_urls = data.get('rtsp_url')

    if not rtsp_urls:
        return jsonify({"error": "Missing 'rtsp_url' in request body"}), 400

    rtsp_server_url = "rtsp://localhost:8554"
    output_urls = {}

    for rtsp_url in rtsp_urls:
        if rtsp_url:
            rtsp_output_url = f"{rtsp_server_url}/{hash(rtsp_url)}"
            start_ffmpeg_server(rtsp_url, rtsp_output_url)
            output_urls[rtsp_url] = rtsp_output_url

    return jsonify({"rtsp_output_urls": output_urls})

# Stop stream endpoint (unchanged)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
