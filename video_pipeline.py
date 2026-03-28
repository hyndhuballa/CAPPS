import cv2
from detection import FrameDetector
from replacement import apply_replacements


def load_video(path):
    cap = cv2.VideoCapture(str(path))
    return {
        "cap": cap,
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "path": path
    }


def extract_frames(meta):
    frames = []
    cap = meta["cap"]

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    return frames


def detect_objects(frames):
    detector = FrameDetector()

    all_detections = []
    for frame in frames:
        dets = detector.detect(frame)
        all_detections.append(dets)

    return all_detections


def apply_user_rules(detections, user):
    decisions = []

    for frame_dets in detections:
        frame_decisions = []

        for det in frame_dets:
            label = det["label"]

            # Poster rule
            if label == "poster":
                if user["region"] == "India":
                    det["replace_with"] = "indian_cricket_poster.png"

            # Drink rule
            if label in ["cup", "bottle"]:
                if user["age"] < 18:
                    det["replace_with"] = "milk.png"
                else:
                    det["replace_with"] = "starbucks.png"

            frame_decisions.append(det)

        decisions.append(frame_decisions)

    return decisions


def replace_objects(frames, decisions):
    output_frames = []

    for frame, dets in zip(frames, decisions):
        new_frame = apply_replacements(frame, dets)
        output_frames.append(new_frame)

    return output_frames


def rebuild_video(frames, meta, output_path):
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(
        str(output_path),
        fourcc,
        meta["fps"],
        (meta["width"], meta["height"])
    )

    for f in frames:
        out.write(f)

    out.release()