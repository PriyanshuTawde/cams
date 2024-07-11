import cv2
import numpy as np
import threading
import collections

# Replace these with your RTSP stream links
rtsp_urls = [
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
"rtsp://localhost:8554/2322744156181784774",
]

buffer_size = 5
frame_buffers = {i: collections.deque(maxlen=buffer_size) for i in range(len(rtsp_urls))}
frame_locks = {i: threading.Lock() for i in range(len(rtsp_urls))}

# frame_width, frame_height = 640, 480  # Adjust resolution as needed
frame_width, frame_height = 400, 250  # Adjust resolution as needed
num_cols = 5  # Number of columns in the grid display
num_rows = (len(rtsp_urls) + num_cols - 1) // num_cols  # Calculate number of rows dynamically

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

threads = []
for i, url in enumerate(rtsp_urls):
    thread = threading.Thread(target=capture_stream, args=(i, url))
    thread.start()
    threads.append(thread)

while True:
    grid_frame = np.zeros((num_rows * frame_height, num_cols * frame_width, 3), dtype=np.uint8)

    for i in range(len(rtsp_urls)):
        with frame_locks[i]:
            if frame_buffers[i]:
                frames[i] = frame_buffers[i][-1]

        row = i // num_cols
        col = i % num_cols

        grid_frame[row * frame_height:(row + 1) * frame_height, col * frame_width:(col + 1) * frame_width] = frames[i]

    cv2.imshow('RTSP Streams Grid', grid_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for thread in threads:
    thread.join()

cv2.destroyAllWindows()
