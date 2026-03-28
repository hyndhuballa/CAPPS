from ultralytics import YOLO

class FrameDetector:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def detect(self, frame):
        results = self.model(frame)[0]

        detections = []

        for box in results.boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # COCO class IDs
            if cls == 41:
                label = "cup"
            elif cls == 39:
                label = "bottle"
            else:
                continue

            detections.append({
                "label": label,
                "bbox": (x1, y1, x2, y2)
            })

        # Simple poster approximation
        h, w, _ = frame.shape
        

        return detections