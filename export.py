import torch

# Load your YOLOv11n-seg model
model = torch.load('cityscapes_segmentation/train2/weights/best.pt', weights_only=False)['model'].float()
model.eval()

# Create dummy input tensor (batch size 1, 3 color channels, 640x640 image)
dummy_input = torch.randn(1, 3, 640, 640)

# Export model to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "yolo11n-city-seg.onnx",
    input_names=['input'],
    output_names=['output'],
    opset_version=12,
    dynamic_axes={'input': {0: 'batch'}, 'output': {0: 'batch'}}
)
