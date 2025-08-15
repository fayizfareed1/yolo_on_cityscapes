from ultralytics import YOLO

# Load a model
model = YOLO("cityscapes_detection/train2/weights/best.pt")  # pretrained YOLOv7 model
# model = YOLO("yolo11n.pt")  # pretrained YOLO11n model
# model = YOLO("yolo11n-seg.pt")  # pretrained YOLO11n classification model

# Run batched inference on a list of images
results = model(["100.jpg", "105.png", "143.png"])  # return a list of Results objects

# Process results list
print(results.count)  # number of images processed
for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs
    obb = result.obb  # Oriented boxes object for OBB outputs
    result.show()  # display to screen
    result.save(filename="result.jpg")  # save to disk