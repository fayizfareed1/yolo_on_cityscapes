from ultralytics import YOLO

model = YOLO("cityscapes_segmentation/train2/weights/best.pt")

print(f"Number of classes: {model.model.yaml['nc']}")
print(f"Class names: {model.names}")
