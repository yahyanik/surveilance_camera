import os
import cv2
from base_camera import BaseCamera
from process import Process

class Camera(BaseCamera):
    video_source = 0
    args = None

    def __init__(self, args):
        Camera.set_args(args)
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def set_args(args):
        Camera.args = args

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        p = Process(Camera.args)


        while True:
            # read current frame
            _, img = camera.read()
            p.get_frames_always(img)

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
