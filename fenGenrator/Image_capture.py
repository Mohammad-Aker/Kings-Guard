import os
import cv2 as cv
import numpy as np
import depthai as dai
import datetime
import threading
import Image_divide_preprocess

latest_frame = None
frame_lock = threading.Lock()


def initialize_camera():
    global latest_frame, frame_lock
    try:
        print("Setting up pipeline...")
        pipeline = dai.Pipeline()

        cam_rgb = pipeline.createColorCamera()
        cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_13_MP)

        cam_rgb.setIspScale(1, 1)  # Full resolution

        xout_video = pipeline.createXLinkOut()
        xout_video.setStreamName("video")
        cam_rgb.video.link(xout_video.input)

        cam_control = pipeline.createXLinkIn()
        cam_control.setStreamName("control")
        cam_control.out.link(cam_rgb.inputControl)

        with dai.Device(pipeline) as device:
            print("Pipeline started, allowing camera to focus...")
            q_rgb = device.getOutputQueue(name="video", maxSize=4, blocking=True)
            q_control = device.getInputQueue(name="control")

            # Configure initial manual settings
            control = dai.CameraControl()
            control.setManualExposure(20000, 100)  # Exposure time (µs), ISO
            control.setAutoFocusMode(dai.CameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
            control.setAutoWhiteBalanceMode(dai.CameraControl.AutoWhiteBalanceMode.AUTO)
            control.setAntiBandingMode(dai.CameraControl.AntiBandingMode.MAINS_60_HZ)
            control.setBrightness(1)
            control.setContrast(2)
            control.setSaturation(1)
            control.setSharpness(1)
            control.setLumaDenoise(1)
            control.setChromaDenoise(0)
            # control.setSceneMode(dai.CameraControl.SceneMode.LANDSCAPE)

            q_control.send(control)

            while True:
                in_rgb = q_rgb.get()
                frame = in_rgb.getCvFrame()

                with frame_lock:
                    latest_frame = frame.copy()

                try:
                    # cv.imshow("video", frame)
                    pass
                except cv.error as e:
                    print(f"OpenCV error: {e}")

                if cv.waitKey(1) == ord('q'):
                    break
    except Exception as e:
        print(f"Error capturing image: {e}")
        raise


def capture_and_process_image(save_dir):
    global latest_frame, frame_lock
    try:
        with frame_lock:
            if latest_frame is None:
                raise Exception("No frame captured yet")

            frame = latest_frame.copy()
            #timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = f"full_board.png"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            cv.imwrite(os.path.join(save_dir, image_name), frame)
            print(f"Image saved as {os.path.join(save_dir, image_name)}")
            cv.destroyAllWindows()
            Image_divide_preprocess.board_divider(os.path.join(save_dir, image_name))

    except Exception as e:
        print(f"Error capturing image: {e}")
        raise
