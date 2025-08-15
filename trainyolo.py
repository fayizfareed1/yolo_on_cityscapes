# Training with YOLOv11 using all Cityscapes classes
from ultralytics import YOLO

# Load model
model = YOLO('yolo11n.pt')

# Train with all 19 Cityscapes classes using your folder structure
results = model.train(
    data='cityscapes_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='cityscapes_yolo'
)