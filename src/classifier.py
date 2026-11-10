# src/classifier.py
"""Klassifikations-Service fuer Teachable-Machine-TFLite-Modelle."""

from pathlib import Path
import cv2
import numpy as np

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        from tensorflow.lite.python.interpreter import Interpreter


class ImageClassifier:
    def __init__(self, model_path: str = "model/model.tflite", labels_path: str = "model/labels.txt"):
        self.model_path = Path(model_path)
        self.labels_path = Path(labels_path)

        with open(self.labels_path, "r", encoding="utf-8") as f:
            self.labels = [line.strip().split(" ", 1)[-1] for line in f.readlines() if line.strip()]

        self.interpreter = Interpreter(model_path=str(self.model_path))
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        _, self.input_height, self.input_width, _ = self.input_details[0]["shape"]

    def classify_frame(self, frame_bgr: np.ndarray) -> tuple[str, float]:
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        resized_frame = cv2.resize(rgb_frame, (self.input_width, self.input_height), interpolation=cv2.INTER_AREA)

        # Gleitkomma-Normalisierung fuer Teachable Machine: [-1.0, 1.0]
        input_data = (resized_frame.astype(np.float32) / 127.5) - 1.0
        input_data = np.expand_dims(input_data, axis=0)

        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])[0]
        top_idx = int(np.argmax(output_data))
        confidence = float(output_data[top_idx])
        label = self.labels[top_idx]

        return label, confidence