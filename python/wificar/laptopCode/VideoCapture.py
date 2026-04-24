import cv2
import threading

class VideoStream:
    def __init__(self, src=0):
        # Use DirectShow for Windows for faster access
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        
        # EXTREME LATENCY TWEAKS
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)      # No queuing
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)            # High sample rate
        
        (self.grabbed, self.frame) = self.cap.read()
        self.running = False
        self.read_lock = threading.Lock()

    def start(self):
        if self.running: 
            return None
        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.running:
            (grabbed, frame) = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy() if self.frame is not None else None
            return self.grabbed, frame

    def stop(self):
        self.running = False
        self.thread.join()
