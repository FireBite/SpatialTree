import numpy as np
import cv2
import depthai
from threading import Timer
import wled as wl
import ImageEngine

# Camera settings
FOV_DEG = 69

# WLED settings
IP   = "4.3.2.1"
PORT = 21324
LED_COUNT = 129

wled = wl.WLED(IP, PORT)
engine = ImageEngine.ImageEngine(FOV_DEG, LED_COUNT)

# Init DepthAI / MyriadX image pipeline
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

start = False
current_led = 0

with depthai.Device(pipeline) as device:
    q_cam = device.getOutputQueue("video")
    q_still = device.getOutputQueue("still")
    q_control = device.getInputQueue('control')

    # Set camera settings for optimal data capture
    ctrl = depthai.CameraControl()
    ctrl.setAutoExposureCompensation(-2)
    q_control.send(ctrl)

    print("Init done! Commands:")
    print("   c - start capture")
    print("   s - save scanned data")
    print("   q - quit")

    while True:
        cam_frames = q_cam.tryGetAll()
        still_frames = q_still.tryGetAll()

        # Video preview
        for cam_frame in cam_frames:
            cv2.imshow("video", cam_frame.getCvFrame())

        # Render still and find the LED
        for still_frame in still_frames:
            img = cv2.imdecode(still_frame.getData(), cv2.IMREAD_UNCHANGED)

            # Reduce noise
            img = cv2.GaussianBlur(img,(9,9),0)

            # Convert to HSV
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

            # Threshold the HSV image to get only white and vibrant red pixels
            lower = np.array([30,0,240])
            upper = np.array([150,255,255])
            mask = cv2.inRange(hsv, lower, upper)
            
            # Mask the original image
            frame = cv2.bitwise_and(img, img, mask=mask)

            # Find contours
            frame = cv2.extractChannel(frame, 1)
            contours, _ = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            contour_valid = False
            screen_x = 0
            screen_y = 0

            if len(contours) != 0:
                # Draw detected contours
                cv2.drawContours(img, contours, -1, (0,255,0), 10)
                
                # Find the biggest countour by the area and draw it
                c = max(contours, key = cv2.contourArea)
                x,y,w,h = cv2.boundingRect(c)

                # Decide if contour is valid
                contour_valid = w * h > 100

            # Draw contour bounding box
            if contour_valid:    
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 10)
                screen_x, screen_y = engine.extractPoint(x + w, y + h, img.shape)

            # Downsample frame and display it
            img = cv2.pyrDown(img)
            img = cv2.pyrDown(img)

            # Draw overlay
            if contour_valid:
                cv2.putText(img, f'X: {"%.5f" % screen_x}', (0,40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), thickness=3)
                cv2.putText(img, f'Y: {"%.5f" % screen_y}', (0,80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), thickness=3)
                print(f'LED {current_led} - x: {"%.5f" % screen_x} y: {"%.5f" % screen_y}')   
            else:
                cv2.putText(img, "No contours detected!", (0,40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), thickness=3)
                print(f'WARN: LED {current_led} not visible')

            # Display data and save it
            cv2.imshow("still", img)
            engine.saveRay(screen_x, screen_y);            

            # Prepare next led to be shown
            current_led += 1

            if current_led != LED_COUNT:
                wled.setLEDSingle(wl.Color(255,0,0), current_led)

                ctrl.setCaptureStill(True)
                q_control.send(ctrl)
            else:
                start = False
                print("---- Capture ----")
                print("- Capture done! -")

        key = cv2.waitKey(1)
        if key == ord('q'):
            print("Exiting...")
            break
        elif key == ord('c'):
            if start:
                continue

            print("---- Capture ----")

            start = True
            current_led = 0

            d = float(input("Distance: "))
            h = float(input("Height: "))
            r = float(input("Rotation: "))

            print("-----------------")

            engine.beginScan(d, h, r)

            wled.setLEDSingle(wl.Color(255,0,0), current_led)

            ctrl.setCaptureStill(True)
            q_control.send(ctrl)

        elif key == ord('s'):
            if start:
                print("Scan is in progress, cannot save")
                continue

            engine.export()
            print("Capture exported")

