import argparse
from pathlib import Path
import video_pipeline as pipeline
from user_profiles import get_user


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--video", required=True)
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    user = get_user(args.user)
    video_path = Path(args.video)

    print("Processing video...")
    meta = pipeline.load_video(video_path)

    print("Extracting frames...")
    frames = pipeline.extract_frames(meta)

    print("Detecting objects...")
    detections = pipeline.detect_objects(frames)

    print("Applying rules...")
    decisions = pipeline.apply_user_rules(detections, user)

    print("Replacing content...")
    modified_frames = pipeline.replace_objects(frames, decisions)

    print("Rebuilding video...")
    output_path = video_path.parent / f"output_{args.user}.avi"
    pipeline.rebuild_video(modified_frames, meta, output_path)

    print(f"Done → {output_path}")


if __name__ == "__main__":
    main()