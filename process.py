import os
import cv2
import time
import numpy as np
from sms import sms
import datetime
import socket

prototxt = "./MobileNetSSD_deploy.prototxt.txt"
model = "./MobileNetSSD_deploy.caffemodel"
confidence_thresh = 0.2
save_video_path = "./video"


class Process:
    video_source = 0

    def __init__(self):
        self.save_flag = False
        self.sendtext = False
        self.text_sent_timeout = time.time()
        self.saving_timeout = time.time()
        self.video_writter = None
        self.garbage = False
        self.frame = None

        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            self.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))

    def set_video_source(self, source):
        self.video_source = source

    def get_frames_always(self, img):
        """
        get the frames from camera regardless of the streaming
        """
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)

        # check to delete videos at 12:00 am
        t = datetime.datetime.now()
        if t.hour == 0 and t.minute == 0 and t.second == 0 and self.garbage:
            self.garbage = False
            self.gorbeg_video_delete()

        if t.hour == 1 and t.minute == 0 and t.second == 0:
            self.garbage = True

        self.tok = time.time()

        if self.save_flag:
            if time.time() - self.text_sent_timeout > 300:
                self.save_flag = False
                self.video_writter = None

            self.save_video(img)

        # send img for processing
        try:
            if self.tok - self.tik > 3:
                self.process_frame(img)
                self.tik = time.time()

        except Exception as e:
            self.process_frame(img)
            print(e)
            self.tik = time.time()

    def process_frame(self, frame):
        """
        run the processing to detect any humans in the frame
        """
        tok = time.time()
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()

        for i in np.arange(0, detections.shape[2]):
            idx, confidence = detections[0, 0, i, 1], detections[0, 0, i, 2]
            if confidence >= confidence_thresh and idx == 15:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

                if self.sendtext:
                    self.text_sent_timeout = time.time()
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    print(s.getsockname()[0])
                    video_name = f"{str(datetime.datetime.now())}.avi"
                    text = f'Camera activity: person detected.' \
                           f'time is {datetime.datetime.now()}' \
                           f'check feed at video: {video_name}.' \
                           f'link for the live video when on the VPN: ' \
                           f'<a href="{s.getsockname()[0]}:5000">Click here to text us!</a>'
                    s.close()

                    self.send_sms(text)
                    self.sendtext = False

                    # save 2 mins of video
                    self.save_flag = True
                    self.video_writter = cv2.VideoWriter(os.path.join(save_video_path, video_name),
                             cv2.VideoWriter_fourcc(*'MJPG'),
                             10, (640, 480))

        # send the text
        if tok - self.text_sent_timeout > 1800:
            self.sendtext = True

    def send_sms(self, text):
        sms.send(payload=text)

    def save_video(self, img):
        self.video_writter.write(img)


    def gorbeg_video_delete(self):
        for file in os.listdir(save_video_path):
            if file.endswith(".avi"):
                save_time_str = file[:-4]
                save_time = datetime.datetime.strptime(save_time_str, '%Y-%m-%d %H:%M:%S.%f')
                try:
                    if (datetime.datetime.now() - save_time).days > 7:
                        print(f"file: {file} is older than 7 days and is deleted.")

                except:
                    print(f"file: {file} not deleted")


if __name__ == "__main__":
    p = Process()
    p.get_frames_always()
