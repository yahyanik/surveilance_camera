import cv2
import time
import numpy as np
import socket
import imutils
from utils import *

prototxt = "./MobileNetSSD_deploy.prototxt.txt"
model = "./MobileNetSSD_deploy.caffemodel"
confidence_thresh = 0.15
save_video_path = "./detection_video"
motion_save_video_path = "./motion_video"
HOW_MANY_DAYS_KEEP_VIDEO = 3



class Process:
    video_source = 0

    def __init__(self, args):
        self.args = args
        if self.args["save"] == 1:
            self.args["nightsave"] = 0

        self.backgrond_sub = cv2.createBackgroundSubtractorMOG2()
        self.first_frame = None
        self.save_flag = False
        self.sendtext = True
        self.text_sent_timeout = time.time()
        self.saving_timeout = time.time()
        self.video_writter = None
        self.garbage = False
        self.frame = None
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.motion_video_writter = None
        self.save_motion_video = False
        self.motion_video_name = ""

    def get_frames_always(self, img):
        """
        get the frames from camera regardless of the streaming
        """

        # check to delete videos at 12:00 am
        t = datetime.datetime.now()
        if t.hour == 0 and t.minute == 0 and 0 < t.second < 2:
            self.gorbeg_video_delete()

        self.tok = time.time()

        if self.save_flag:
            self.save_video(img)

        if self.args["nightsave"] == 1:
            if t.hour < 8 or t.hour > 23:
                self.args["save"] = 1
            else:
                self.args["save"] = 0


        if self.motion_detection(img) and self.motion_video_writter is None and self.args["save"] == 1:
            self.save_motion_video = True
            self.motion_video_name = f"{str(datetime.datetime.now())}.avi"
            self.motion_video_writter = cv2.VideoWriter(os.path.join(motion_save_video_path, self.motion_video_name),
                                                 cv2.VideoWriter_fourcc(*'MJPG'),
                                                 10, (640, 480))

        elif not self.motion_detection(img):
            self.save_motion_video = False
            if self.motion_video_name != "":
                size_video = os.stat(os.path.join(motion_save_video_path, self.motion_video_name)).st_size
                if size_video < 1000000:
                    os.remove(os.path.join(motion_save_video_path, self.motion_video_name))
                    print("deleted small motion video")
            self.motion_video_writter = None
            self.motion_video_name = ""
        
        if self.save_motion_video:
            self.motion_save_video(img)

        # send img for processing
        try:
            if (self.tok - self.tik > 3) and (self.args["detection"] == 1):
                self.process_frame(img)
                self.tik = time.time()

        except Exception as e:
            if self.args["detection"] == 1:
                self.process_frame(img)
            print(e)
            self.tik = time.time()

    def process_frame(self, frame):
        """
        run the processing to detect any humans in the frame using Mobilebet SSD on caffe
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
                video_name = f"{str(datetime.datetime.now())}.avi"

                if self.sendtext:
                    self.text_sent_timeout = time.time()
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    print(s.getsockname()[0])
                    text = f'Camera activity: person detected.' \
                           f'time is {datetime.datetime.now()}' \
                           f'check feed at video: {video_name}.' \
                           f'link for the live video when on the VPN: ' \
                           f'<a href="{s.getsockname()[0]}:5000">Click here to text us!</a>'
                    s.close()
                    self.send_sms(text)
                    self.sendtext = False

                # save 2 mins of video
                if self.args["save"] == 1:
                    self.save_flag = True
                    self.video_writter = cv2.VideoWriter(os.path.join(save_video_path, video_name),
                             cv2.VideoWriter_fourcc(*'MJPG'),
                             10, (640, 480))

        # send the text
        if tok - self.text_sent_timeout > 120:
            self.sendtext = True
            self.save_flag = False
            self.video_writter = None

    def send_sms(self, text):
        if self.args["sms"]:
            sms.send(payload=text)

    def save_video(self, img):
        self.video_writter.write(img)

    def motion_save_video(self, img):
        self.motion_video_writter.write(img)

    def gorbeg_video_delete(self):
        video_delete(HOW_MANY_DAYS_KEEP_VIDEO, save_video_path, motion_save_video_path)

    def motion_detection(self, frame):
        # frame = imutils.resize(frame, width=500)
        (h, w) = frame.shape[:2]
        gray = imutils.resize(frame, width=400)
        # gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.first_frame is None:
            self.first_frame = gray
            return False

        # frameDelta = cv2.absdiff(self.first_frame, gray)
        # thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # thresh = cv2.dilate(thresh, None, iterations=2)
        # cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        #                        cv2.CHAIN_APPROX_SIMPLE)
        fgmask = self.backgrond_sub.apply(gray)
        _, thresh = cv2.threshold(fgmask, 105, 255, 50)
        cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cnts = imutils.grab_contours(cnts)
        for c in cnts:
            
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 400:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            box = [x, y, (x + w), (y + h)] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)
            return True

        return False


if __name__ == "__main__":
    p = Process()
    p.get_frames_always()
