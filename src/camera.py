# src/camera.py
"""Kamera-Service ausschliesslich fuer Raspberry Pi OS mit Picamera2."""

import cv2
import numpy as np
from picamera2 import Picamera2


class CameraService:
    """Kapselt die Hardware-Ansteuerung der Raspberry-Pi-Kamera."""

    def __init__(self, resolution: tuple[int, int] = (640, 480)):
        """Initialisiert das Kameramodul mit der gewuenschten Aufloesung.

        Args:
            resolution (tuple[int, int]): Aufloesung als (Breite, Hoehe).
        """
        self.resolution = resolution
        self.picam2 = Picamera2()

        # RGB-Vorschaukonfiguration fuer Machine Learning und Bildverarbeitung
        config = self.picam2.create_preview_configuration(
            main={"size": self.resolution, "format": "RGB888"}
        )
        self.picam2.configure(config)
        self.picam2.start()
        print("[CameraService] Raspberry Pi Kamera erfolgreich gestartet.")

    def get_frame(self) -> np.ndarray:
        """Erfasst ein aktuelles Einzelbild von der Kamera.

        Returns:
            np.ndarray: Bilddaten im OpenCV-Standardformat (BGR).
        """
        # Picamera2 liefert Rohdaten im RGB-Format
        rgb_frame = self.picam2.capture_array()
        # In BGR konvertieren, damit OpenCV und Bilddateien farblich korrekt sind
        return cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

    def close(self) -> None:
        """Stoppt die Kamera und gibt die Hardwareressourcen frei."""
        self.picam2.stop()
        self.picam2.close()
        print("[CameraService] Raspberry Pi Kamera ordnungsgemaess gestoppt.")


if __name__ == "__main__":
    cam = CameraService()
    try:
        frame = cam.get_frame()
        cv2.imwrite("src/picture_ai/kamera_test.jpg", frame)
        print(f"[Test] Testbild 'kamera_test.jpg' erfolgreich gespeichert. Aufloesung: {frame.shape[1]}x{frame.shape[0]}")
    finally:
        cam.close()