import cv2
import numpy as np
import threading
import collections

# Replace these with your RTSP stream links
rtsp_urls = [
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    "rtsp://localhost:8554/7263969742911368228",
    # Add more URLs as needed
]

# Buffer size for each stream to smooth out fluctuations
buffer_size = 5  # Adjust buffer size as needed for smoothing

# Initialize a dictionary to store buffered frames from each stream
frame_buffers = {i: collections.deque(maxlen=buffer_size) for i in range(len(rtsp_urls))}
frame_locks = {i: threading.Lock() for i in range(len(rtsp_urls))}

# Define grid dimensions (e.g., 2x2 grid for 4 streams)
grid_rows, grid_cols = 5, 5
frame_width, frame_height = 350, 200  # Desired size for each frame

# Initialize a list to store frames
frames = [np.zeros((frame_height, frame_width, 3), dtype=np.uint8) for _ in rtsp_urls]

def capture_stream(index, url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"Error: Unable to open RTSP stream {index} ({url})")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Unable to read frame from stream {index} ({url})")
            break

        frame = cv2.resize(frame, (frame_width, frame_height))
        with frame_locks[index]:
            frame_buffers[index].append(frame)

    cap.release()

# Create and start a thread for each stream
threads = []
for i, url in enumerate(rtsp_urls):
    thread = threading.Thread(target=capture_stream, args=(i, url))
    thread.start()
    threads.append(thread)

while True:
    # Create a black canvas for the grid
    grid_frame = np.zeros((grid_rows * frame_height, grid_cols * frame_width, 3), dtype=np.uint8)

    for i in range(len(rtsp_urls)):
        with frame_locks[i]:
            if frame_buffers[i]:
                frames[i] = frame_buffers[i][-1]  # Get the latest frame from the buffer

        # Calculate grid cell position
        row = i // grid_cols
        col = i % grid_cols

        # Place the frame in the correct position in the grid
        grid_frame[row * frame_height:(row + 1) * frame_height, col * frame_width:(col + 1) * frame_width] = frames[i]

    # Display the combined grid frame
    cv2.imshow('RTSP Streams Grid', grid_frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Wait for all threads to complete
for thread in threads:
    thread.join()

cv2.destroyAllWindows()
