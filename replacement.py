import cv2
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"


def overlay(frame, asset, bbox):
    x1, y1, x2, y2 = bbox

    # Safety clamp
    x1 = max(0, x1)
    y1 = max(0, y1)

    asset = cv2.resize(asset, (x2 - x1, y2 - y1))

    frame[y1:y2, x1:x2] = asset
    return frame


def apply_replacements(frame, detections):
    for det in detections:
        if "replace_with" not in det:
            continue

        asset_path = ASSETS / det["replace_with"]
        asset = cv2.imread(str(asset_path))

        if asset is None:
            continue

        frame = overlay(frame, asset, det["bbox"])

    return frame