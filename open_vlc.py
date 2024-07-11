import subprocess
import time

# List of RTSP URLs
rtsp_urls = [
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
"rtsp://localhost:8554/-964351764716334017",
]

# Path to the VLC executable
vlc_path = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"  # Use raw string to handle backslashes

# Function to open RTSP stream in VLC
def open_vlc(rtsp_url):
    subprocess.Popen([vlc_path, rtsp_url])


# Iterate over the RTSP URLs and open each one in VLC
for url in rtsp_urls:
 
    open_vlc(url)
    time.sleep(2)  # Wait for 5 seconds before opening the next stream
