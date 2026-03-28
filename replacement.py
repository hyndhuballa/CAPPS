import cv2
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"


def overlay(frame, asset, bbox):
    x1, y1, x2, y2 = bbox

    h, w = y2 - y1, x2 - x1
    asset = cv2.resize(asset, (w, h))

    if asset.shape[2] == 4:  # has alpha
        alpha = asset[:, :, 3] / 255.0
        alpha = alpha[:, :, None]

        rgb = asset[:, :, :3]

        frame[y1:y2, x1:x2] = (
            alpha * rgb +
            (1 - alpha) * frame[y1:y2, x1:x2]
        ).astype("uint8")

    else:
        frame[y1:y2, x1:x2] = asset

    return frame


prev_bbox = None

def apply_replacements(frame, detections):
    global prev_bbox

    for det in detections:
        if "replace_with" not in det:
            continue

        x1, y1, x2, y2 = det["bbox"]

        # ✅ smooth movement
        if prev_bbox is not None:
            x1 = int(0.7 * x1 + 0.3 * prev_bbox[0])
            y1 = int(0.7 * y1 + 0.3 * prev_bbox[1])
            x2 = int(0.7 * x2 + 0.3 * prev_bbox[2])
            y2 = int(0.7 * y2 + 0.3 * prev_bbox[3])

        prev_bbox = (x1, y1, x2, y2)

        asset_path = ASSETS / det["replace_with"]
        asset = cv2.imread(str(asset_path), cv2.IMREAD_UNCHANGED)

        if asset is None:
            continue

        frame = overlay(frame, asset, (x1, y1, x2, y2))

    return frame

def replace_poster(frame):
    import cv2
    from pathlib import Path

    asset_path = Path(__file__).parent / "assets" / "indian_cricket_poster.png"
    asset = cv2.imread(str(asset_path))

    if asset is None:
        return frame

    h, w, _ = frame.shape

    # Define fixed poster region (top center)
    x1, y1 = int(w * 0.3), int(h * 0.05)
    x2, y2 = int(w * 0.7), int(h * 0.3)

    asset = cv2.resize(asset, (x2 - x1, y2 - y1))
    frame[y1:y2, x1:x2] = asset

    return frame