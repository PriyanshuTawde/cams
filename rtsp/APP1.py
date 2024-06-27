from flask import Flask, request, jsonify, Response
import subprocess
import os

app = Flask(__name__)

# Dictionary to keep track of running FFmpeg processes
processes = {}

# Function to start FFmpeg process for restreaming
def start_ffmpeg_server(rtsp_input_url, rtsp_output_url):
    # Command to start FFmpeg for restreaming
    command = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',  # Use TCP for RTSP
        '-i', rtsp_input_url,  # Input URL
        '-c:v', 'copy',  # Copy the video codec
        '-f', 'rtsp',  # Output format
        rtsp_output_url  # Output URL
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes[rtsp_input_url] = process

@app.route('/start_stream', methods=['POST'])
def start_stream():
    # Get the RTSP URL from the request
    data = request.get_json()
    rtsp_url = data.get('rtsp_url')

    if not rtsp_url:
        return Response({"error": "Missing 'rtsp_url' in request body"}), 400

    # Construct the output URL for the RTSP server
    rtsp_server_url = "rtsp://localhost:8554"
    rtsp_output_url = f"{rtsp_server_url}/{hash(rtsp_url)}"

    # Start FFmpeg server to restream
    start_ffmpeg_server(rtsp_url, rtsp_output_url)
    print(rtsp_output_url)

    return Response({rtsp_output_url})

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    # Get the RTSP URL from the request
    data = request.get_json()
    rtsp_url = data.get('rtsp_url')

    if not rtsp_url:
        return jsonify({"error": "Missing 'rtsp_url' in request body"}), 400

    # Stop the FFmpeg process if it's running
    process = processes.pop(rtsp_url, None)
    if process:
        process.terminate()
        process.wait()
        return jsonify({"message": "Stream stopped"})
    else:
        return jsonify({"error": "Stream not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, threaded=True)  # Run the Flask app using the built-in development server
