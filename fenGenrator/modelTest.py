
import cv2
from ultralytics import YOLO

# Load the model
model = YOLO('../model/weights/best.pt')

class_names = ['bishop', 'black', 'blank-piece', 'king', 'knight', 'pawn', 'queen', 'rook']


def warm_up_model():
    # Create a small dummy image
    dummy_image = cv2.imread('divided_output/g7.jpg')  # Replace with a valid small image path
    if dummy_image is None:
        print("Dummy image not found, skipping warm-up.")
        return

    # Run a dummy prediction
    model.predict(dummy_image, conf=0.5, iou=0.7, max_det=1, imgsz=96)
    print("Model warm-up completed.")



warm_up_model()


def detect_obj(image_path_cropped):
    image_path = image_path_cropped
    results = model.predict(image_path, conf=0.5, iou=0.7, max_det=1, save_conf=True, imgsz=96)

    image = cv2.imread(image_path)

    detections = []
    if isinstance(results, list):
        for result in results:
            if hasattr(result, 'boxes') and result.boxes:
                for box in result.boxes:
                    if hasattr(box, 'cls') and hasattr(box, 'conf'):
                        detections.append({
                            "class": class_names[int(box.cls)],
                            "confidence": float(box.conf)
                        })
    else:
        print("Unexpected results type:", type(results))

    if not detections:
        detections.append({
            "class": "rook",
            "confidence": 1.0 
        })
    else:
        print(f"Detections found for {image_path}: {detections}")

    return detections


#print (detect_obj("divided_output/h1.jpg"))
