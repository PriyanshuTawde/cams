from flask import Flask, request, jsonify, Response
import subprocess
import redis
import socket

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
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Store the process ID in Redis with an expiration time of 1 second
    cache.set(rtsp_input_url, process.pid, ex=1)

# @app.route('/start_stream', methods=['POST'])
# def start_stream():
#     data = request.get_json()
#     rtsp_url = data.get('rtsp_url')

#     if not rtsp_url:
#         return jsonify({"error": "Missing 'rtsp_url' in request body"}), 400

#     # Construct the output URL for the RTSP server
#     rtsp_server_url = "rtsp://localhost:8554"
#     rtsp_output_url = f"{rtsp_server_url}/{hash(rtsp_url)}"

#     # Start FFmpeg server to restream
#     start_ffmpeg_server(rtsp_url, rtsp_output_url)
#     print(rtsp_output_url)

#     return jsonify({"rtsp_output_url": rtsp_output_url})

@app.route('/start_streams', methods=['POST'])
def start_streams():
    data = request.get_json()
    rtsp_urls = data.get('rtsp_url')  # Change 'rtsp_urls' to 'rtsp_url'

    if not rtsp_urls:
        return jsonify({"error": "Missing 'rtsp_url' in request body"}), 400

    # Construct the output URL base for the RTSP server
    rtsp_server_url = "rtsp://localhost:8554"

    output_urls = {}
    for rtsp_url in rtsp_urls:
        if rtsp_url:
            # Construct the output URL for each RTSP stream
            rtsp_output_url = f"{rtsp_server_url}/{hash(rtsp_url)}"
            # Start FFmpeg server to restream
            start_ffmpeg_server(rtsp_url, rtsp_output_url)
            output_urls[rtsp_url] = rtsp_output_url
            # print(rtsp_output_url)

    return jsonify({"rtsp_output_urls": output_urls})



@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    data = request.get_json()
    rtsp_url = data.get('rtsp_url')

    if not rtsp_url:
        return jsonify({"error": "Missing 'rtsp_url' in request body"}), 400

    # Get the process ID from Redis
    process_id = cache.get(rtsp_url)
    if process_id:
        # Terminate the process
        process = subprocess.Popen(['taskkill', '/F', '/PID', process_id])
        process.wait()
        # Remove the process ID from Redis
        cache.delete(rtsp_url)
        return jsonify({"message": "Stream stopped"})
    else:
        return jsonify({"error": "Stream not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
