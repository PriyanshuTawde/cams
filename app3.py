import cv2
import threading
import numpy as np
from collections import deque
import time

# List of RTSP links
rtsp_links = [
"rtsp://localhost:8554/-5686015637569620976",
"rtsp://localhost:8554/-5686015637569620976",
"rtsp://localhost:8554/-5686015637569620976",
"rtsp://localhost:8554/-5686015637569620976",
]

# Resolution for each stream
width, height = 500, 250

# Buffer size for each stream to smooth out fluctuations
buffer_size = 100  # Increased buffer size

# Minimum number of frames to buffer before starting display
min_buffer_fill = 10

# Initialize a dictionary to store buffered frames from each stream
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

    retry_attempts = 5  # Number of retries for failed frame retrieval

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to retrieve frame from stream: {rtsp_link}. Retrying...")
            for _ in range(retry_attempts):
                time.sleep(0.1)  # Wait before retrying
                ret, frame = cap.read()
                if ret:
                    break
            if not ret:
                print(f"Failed to retrieve frame after {retry_attempts} attempts. Skipping this frame.")
                continue
        
        frame = cv2.resize(frame, (width, height))

        with frames_lock:
            if len(frame_buffers[index]) >= buffer_size:
                frame_buffers[index].popleft()  # Discard the oldest frame
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
                    # Use the latest frame from the buffer
                    frames.append(frame_buffers[i][-1])
                else:
                    # If buffer is empty, append a black frame
                    frames.append(np.zeros((height, width, 3), dtype=np.uint8))

        # Calculate the grid size
        num_streams = len(frames)
        grid_size = int(np.ceil(np.sqrt(num_streams)))
        grid_height = grid_size * height
        grid_width = grid_size * width

        # Create the grid frame
        grid_frame = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)

        # Populate the grid frame with the frames
        for idx, frame in enumerate(frames):
            row = idx // grid_size
            col = idx % grid_size
            grid_frame[row * height:(row + 1) * height, col * width:(col + 1) * width] = frame

        cv2.imshow("Multi RTSP Streams", grid_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# Create a thread for each RTSP stream
threads = []
for i, rtsp_link in enumerate(rtsp_links):
    thread = threading.Thread(target=play_stream, args=(rtsp_link, i))
    thread.daemon = True  # Allows thread to exit when main program exits
    thread.start()
    threads.append(thread)

# Create a separate thread for displaying the frames
display_thread = threading.Thread(target=display_frames)
display_thread.daemon = True  # Allows thread to exit when main program exits
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
