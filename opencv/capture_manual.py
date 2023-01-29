import numpy as np
import cv2
import depthai
import math
import ImageEngine
import wled as wl

# Camera settings
FOV_DEG = 69
FOV     = FOV_DEG / 180 * math.pi

# WLED settings
IP   = "4.3.2.1"
PORT = 21324

wled = wl.WLED(IP, PORT)

# DepthAI / MyriadX image pipeline
pipeline = depthai.Pipeline()

# Camera init
cam = pipeline.create(depthai.node.ColorCamera)
cam.setBoardSocket(depthai.CameraBoardSocket.RGB)
cam.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_4_K)
cam.setColorOrder(depthai.ColorCameraProperties.ColorOrder.BGR)
cam.setPreviewSize(1080, 720)

# Preview video output
video_out = pipeline.create(depthai.node.XLinkOut)
video_out.setStreamName("video")

# Stills encoding and output for opencv analysis
still_encoder = pipeline.create(depthai.node.VideoEncoder)
still_encoder.setDefaultProfilePreset(10, depthai.VideoEncoderProperties.Profile.MJPEG)

still_out = pipeline.create(depthai.node.XLinkOut)
still_out.setStreamName("still")

# Camera control input
control_in = pipeline.create(depthai.node.XLinkIn)
control_in.setStreamName('control')

# Link streams
cam.preview.link(video_out.input)
cam.still.link(still_encoder.input)
still_encoder.bitstream.link(still_out.input)
control_in.out.link(cam.inputControl)

with depthai.Device(pipeline) as device:
    q_cam = device.getOutputQueue("video")
    q_still = device.getOutputQueue("still")
    q_control = device.getInputQueue('control')

    # Set camera settings for optimal data capture
    ctrl = depthai.CameraControl()
    ctrl.setAutoExposureCompensation(-2)
    q_control.send(ctrl)

    while True:
        cam_frames = q_cam.tryGetAll()
        still_frames = q_still.tryGetAll()

        # Video preview
        for cam_frame in cam_frames:
            wled.setLEDSingle(wl.Color(255,0,0), 1)
            cv2.imshow("video", cam_frame.getCvFrame())

        # Render still and find the LED
        for still_frame in still_frames:
            img = cv2.imdecode(still_frame.getData(), cv2.IMREAD_UNCHANGED)

            img = cv2.GaussianBlur(img,(9,9),0)

            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            lower = np.array([30,0,240])
            upper = np.array([150,255,255])

            # Threshold the HSV image to get only blue colors
            mask = cv2.inRange(hsv, lower, upper)
            # Bitwise-AND mask and original image
            frame = cv2.bitwise_and(img, img, mask=mask)

            frame = cv2.extractChannel(frame, 1)

            contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img, contours, -1, (0,255,0), 10)

            x = None
            y = None

            if len(contours) != 0:
                # Find the biggest countour by the area and draw it
                c = max(contours, key = cv2.contourArea)
                x,y,w,h = cv2.boundingRect(c)

                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 10)

                # Calculate screen space pixel coordinates
                frame_height, frame_width, _ = img.shape
                screen_x = 2 * (x + w + 0.5) / frame_width - 1
                screen_y = 1 - 2 * (y + h + 0.5) / frame_height

                # Restore image aspect ratio / make pixels square again
                aspect_ratio = frame_width / frame_height
                screen_x /= aspect_ratio

                # Calculate FoV correction
                screen_x *= math.tan(FOV/2)
                screen_y *= math.tan(FOV/2)

            # Downsample frame and display it
            img = cv2.pyrDown(img)
            img = cv2.pyrDown(img)

            # Draw overlay
            if len(contours) != 0:
                cv2.putText(img, f'X: {"%.5f" % screen_x}', (0,40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), thickness=3)
                cv2.putText(img, f'Y: {"%.5f" % screen_y}', (0,80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), thickness=3)
            else:
                cv2.putText(img, "No contours detected!", (0,40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), thickness=3)

            cv2.imshow("still", img)           

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('c'):
            ctrl.setCaptureStill(True)
            q_control.send(ctrl)