import cv2
import math
import numpy as np
import torch
from ultralytics import YOLO
import random
from deep_sort_pytorch.utils.parser import get_config
from deep_sort_pytorch.deep_sort import DeepSort
from deep_sort_pytorch.deep_sort.sort.tracker import Tracker
from collections import defaultdict
from Dependencies import download_files

# Call the function to download the required files
download_files.download_dependencies()

# Check if a GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if torch.cuda.is_available():
    print("GPU is available. Running on GPU.")
else:
    print("GPU is not available. Running on CPU.")

# Load the YOLOv8 model and move it to the appropriate device
model = YOLO("yolov9e.pt").to(device)
class_names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

deep_sort_weights = 'deep_sort_pytorch/deep_sort/deep/checkpoint/ckpt.t7'

# Define the field of view (FOV) for different perspectives
fov_degrees = {
    "front": 90,
    "left": 90,
    "right": 90,
    "leftmost": 90,
    "rightmost": 90,
}

threshold = random.randint(120, 140)
print("Threshold for motion detection:", threshold)

# Initialize previous frames for motion-based saliency for each perspective
previous_frames = {
    "front": None,
    "left": None,
    "right": None,
    "leftmost": None,
    "rightmost": None,
}

# Initialize dictionary to store centroid history for each track and each FOV
centroid_history = defaultdict(lambda: defaultdict(list))

def transform_perspective(frame, perspective):
    if perspective == "front":
        fov_center = {"x": frame_width // 2, "y": frame_height // 2}
    elif perspective == "left":
        fov_center = {"x": frame_width // 4, "y": frame_height // 2}
    elif perspective == "right":
        fov_center = {"x": 3 * frame_width // 4, "y": frame_height // 2}
    elif perspective == "leftmost":
        fov_center = {"x": frame_width // 8, "y": frame_height // 2}
    elif perspective == "rightmost":
        fov_center = {"x": 7 * frame_width // 8, "y": frame_height // 2}
    else:
        raise ValueError("Invalid perspective")

    fov_width = int(frame_width * fov_degrees[perspective] / 360)
    fov_height = int(frame_height * fov_degrees[perspective] / 360)

    perspective_frame = frame[
        fov_center["y"] - fov_height // 2 : fov_center["y"] + fov_height // 2,
        fov_center["x"] - fov_width // 2 : fov_center["x"] + fov_width // 2,
    ]

    return perspective_frame

def detect_saliency(frame, previous_frame):
    if previous_frame is None or previous_frame.size == 0:
        return 0
    previous_frame_resized = cv2.resize(previous_frame, (frame.shape[1], frame.shape[0]))
    saliency = np.mean(np.abs(frame - previous_frame_resized))
    return saliency

# Initialize dictionary to store trackers for each perspective
trackers = {
    "front": DeepSort(model_path=deep_sort_weights, max_age=5),
    "left": DeepSort(model_path=deep_sort_weights, max_age=5),
    "right": DeepSort(model_path=deep_sort_weights, max_age=5),
    "leftmost": DeepSort(model_path=deep_sort_weights, max_age=5),
    "rightmost": DeepSort(model_path=deep_sort_weights,max_age=5),
}

# Define colors for paths and bounding boxes
path_colors = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 255), (0, 0, 255)]  # Yellow, Cyan, Green, Magenta, Red
bbox_colors = [(255, 0, 255)]  # Magenta

motion_detected = {"front": False, "left": False, "right": False, "leftmost": False, "rightmost": False}

# Open the video file
video_path = "Dependencies/Test.mp4"
cap = cv2.VideoCapture(video_path)

# Get the width and height of the video frames
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initialize a global track ID counter
global_track_id = 0

# Dictionary to map perspective track IDs to global track IDs
global_id_map = defaultdict(dict)

while cap.isOpened():
    success, frame = cap.read()

    if success:
        for perspective, previous_frame in previous_frames.items():
            transformed_frame = transform_perspective(frame, perspective)
            saliency = detect_saliency(transformed_frame, previous_frame)

            if saliency > threshold:
                motion_detected[perspective] = True
                print(f"Saliency detected in {perspective}")

                tracker = trackers[perspective]

                results = model(transformed_frame, classes=[0, 2, 3], device=device)

                if isinstance(results, list) and len(results) > 0:
                    coordinates = results[0].boxes.cpu().numpy()

                    for coord in coordinates:
                        x1, y1, x2, y2 = coord.xyxy[0]
                        conf = coord.conf.item()
                        cls = coord.cls.item()
                        label = model.names[cls]
                        
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2

                        object_id = f"{perspective}_{cls}_{conf:.2f}"

                        theta = np.degrees((center_x / frame_width) * 360)
                        phi = np.degrees((center_y / frame_height) * 180)

                        cv2.putText(
                            transformed_frame,
                            f"[x: {theta:.2f}, y: {phi:.2f}]",
                            (int(x1), int(y1) - 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 0, 255),
                            2,
                        )

                conf = results[0].boxes.conf.detach().cpu().numpy()
                xywh = results[0].boxes.xywh.cpu().numpy()
                
                tracks = tracker.update(xywh, conf, transformed_frame, previous_frame)

                for track in tracker.tracker.tracks:
                    track_id = track.track_id
                    if track_id not in global_id_map[perspective]:
                        global_id_map[perspective][track_id] = global_track_id
                        global_track_id += 1
                    global_id = global_id_map[perspective][track_id]

                    hits = track.hits
                    x1, y1, x2, y2 = track.to_tlbr()
                    centroid_x = int((x1 + x2) / 2)
                    centroid_y = int(y2)

                    centroid_history[perspective][global_id].append((centroid_x, centroid_y))

                    for point1, point2 in zip(centroid_history[perspective][global_id], centroid_history[perspective][global_id][1:]):
                        cv2.line(transformed_frame, point1, point2, path_colors[global_id % len(path_colors)], 2)

                    cv2.rectangle(transformed_frame, (int(x1), int(y1)), (int(x2), int(y2)), bbox_colors[0], 2)

                    cv2.putText(transformed_frame, f"ID: {global_id}", (int(x1) + 10, int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)

                person_count = len(centroid_history[perspective])

                if perspective == "rightmost":
                    roi_width = transformed_frame.shape[1] // 2
                    overlap = 50  
                    roi = transformed_frame[:, roi_width - overlap:, :]
                    cv2.imshow(f"{perspective.capitalize()} Perspective", roi)
                else:
                    cv2.imshow(f"{perspective.capitalize()} Perspective", transformed_frame)

            previous_frames[perspective] = frame.copy()

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()