import math
import cv2
from typing import Tuple
import wled
import numpy as np
from scipy.io import savemat

class ImageEngine:
    current_scan = 0
    current_ray = 0

    def __init__(self, fov: float, pixels: int) -> None:
        self.FOV = fov / 180 * math.pi

        # Initialize data structure for holding scanned data
        self.scan = {'metadata': [], 'rays': []}
        for i in range(0, pixels):
            self.scan['rays'].append({'vec': [], 'origin': []})
        pass

    def extractPoint(self, x: int, y: int, frame_shape) -> Tuple[int, int]:
        # Calculate screen space pixel coordinates
        frame_height, frame_width, _ = frame_shape
        screen_x = 2 * (x + 0.5) / frame_width - 1
        screen_y = 1 - 2 * (y + 0.5) / frame_height

        # Restore image aspect ratio / make pixels square again
        aspect_ratio = frame_width / frame_height
        screen_x /= aspect_ratio

        # Calculate FoV correction
        screen_x *= math.tan(self.FOV/2)
        screen_y *= math.tan(self.FOV/2)

        return (screen_x, screen_y)

    def beginScan(self, distance: float, height: float, rotation: float) -> None:
        self.current_ray = 0
        self.current_scan += 1

        # Precalculate rotation matrix
        rotation = rotation / 180 * math.pi
        self.rotationMat = np.array(
            ((math.cos(rotation), -math.sin(rotation), 0),
             (math.sin(rotation),  math.cos(rotation), 0),
             (0,                   0,                  1)))
             
        # Calculate camera position
        self.position = (distance * math.cos(rotation), distance * math.sin(-rotation), height)
        pass

    def saveRay(self, screen_x: float, screen_y:float) -> None:
        if self.scan is None:
            raise Exception()

        # Convert from camera to world coordinates
        vec = np.matmul((-1, screen_x, -screen_y), self.rotationMat)

        self.scan['rays'][self.current_ray]['vec'].append(vec / np.linalg.norm(vec))
        self.scan['rays'][self.current_ray]['origin'].append(self.position)

        self.current_ray += 1
        pass

    def export(self) -> None:
        if self.scan is None:
            raise Exception()
        
        # Export scanned data to mat file
        savemat('capture.mat', self.scan, appendmat=False)
        self.current_scan = 0
        pass

class Capture:
    def __init__(self, led_count: int, ip: str, port: int) -> None:
        self.led_count = led_count
        self.wled = wled.WLED(ip, port)
        pass

    def start(self) -> None:
        pass

    def notifyReady(self) -> None:
        self.ready = True
        pass

    def update(self) -> None:
        if not self.ready:
            pass

        self.ready = False

        self.wled.setLEDSingle(wled.Color(255,0,0), 0)
        
