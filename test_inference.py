# test_inference.py
import time
from src.camera import CameraService
from src.classifier import ImageClassifier

def main():
    print("[Setup] Initialisiere Kamera und KI-Modell...")
    cam = CameraService(resolution=(640, 480))
    classifier = ImageClassifier(model_path="model/model.tflite", labels_path="model/labels.txt")
    print("[Setup] Startbereit. Druecke Strg+C zum Beenden.\n")

    try:
        while True:
            frame = cam.get_frame()
            label, confidence = classifier.classify_frame(frame)
            print(f"\rErkannt: {label:<15} ({confidence * 100:5.1f}%)", end="", flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[Beendet] Stoppe Kamera...")
    finally:
        cam.close()

if __name__ == "__main__":
    main()