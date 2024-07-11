from flask import Flask, request, jsonify, Response
import subprocess
import redis
import socket
import cv2
import threading
import numpy as np
from collections import deque
import time

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

# OpenCV code for displaying multiple streams
rtsp_links = [
"rtsp://localhost:8554/7335619937905155938",
"rtsp://localhost:8554/7335619937905155938",
# Add more links as needed
]

width, height = 500, 250
buffer_size = 200  # Increased buffer size
min_buffer_fill = 20  # Increased minimum buffer fill

frame_buffers = {i: deque(maxlen=buffer_size) for i in range(len(rtsp_links))}
frames_lock = threading.Lock()

def play_stream(rtsp_link, index):
    print(f"Attempting to open stream: {rtsp_link}")
    cap = cv2.VideoCapture(rtsp_link)
    if not cap.isOpened():
        print(f"Unable to open stream: {rtsp_link}")
        return

    # Set the desired resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to retrieve frame from stream: {rtsp_link}")
            continue
        
        frame = cv2.resize(frame, (width, height))

        with frames_lock:
            frame_buffers[index].append(frame)

        time.sleep(0.05)  # Control the frame rate to reduce load

    cap.release()
    print(f"Stream closed: {rtsp_link}")

def display_frames():
    while True:
        frames = []
        with frames_lock:
            for i in range(len(rtsp_links)):
                if len(frame_buffers[i]) > 0:
                    frames.append(frame_buffers[i][-1])
                else:
                    frames.append(np.zeros((height, width, 3), dtype=np.uint8))

        num_streams = len(frames)
        grid_size = int(np.ceil(np.sqrt(num_streams)))
        grid_height = grid_size * height
        grid_width = grid_size * width

        grid_frame = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)

        for idx, frame in enumerate(frames):
            row = idx // grid_size
            col = idx % grid_size
            grid_frame[row * height:(row + 1) * height, col * width:(col + 1) * width] = frame

        cv2.imshow("Multi RTSP Streams", grid_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

threads = []
for i, rtsp_link in enumerate(rtsp_links):
    thread = threading.Thread(target=play_stream, args=(rtsp_link, i))
    thread.daemon = True
    thread.start()
    threads.append(thread)

    display_thread = threading.Thread(target=display_frames)
    display_thread.daemon = True
    thread.start()
    threads.append(thread)

    # Create a separate thread for displaying the frames
    display_thread = threading.Thread(target=display_frames)
    display_thread.daemon = True
    display_thread.start()

# Wait for all threads to complete
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")

for thread in threads:
    thread.join()

display_thread.join()
