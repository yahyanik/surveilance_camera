
import cv2
import os

# This will return video from the first webcam on your computer.
cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter(os.path.join("./video", 'output.avi'), fourcc, 20.0, (640, 480))

# loop runs if capturing has been initialized.
while (True):
    # reads frames from a camera
    # ret checks return at each frame
    ret, frame = cap.read()

    # Converts to grayscale space, OCV reads colors as BGR
    # frame is converted to gray

    # output the frame
    out.write(frame)


cv2.destroyAllWindows()