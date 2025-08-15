import torch
import onnx
import onnxruntime
import numpy as np
import sys

# === Configuration ===
PT_MODEL_PATH = "cityscapes_segmentation/train2/weights/best.pt"       # Path to your YOLOv11n-cls PyTorch model
ONNX_MODEL_PATH = "yolov11n-city-seg.onnx"   # Output path for ONNX model
INPUT_SIZE = (1, 3, 224, 224)           # Adjust if your model uses a different size
OPSET_VERSION = 12

# === Load Model ===
try:
    model = torch.load(PT_MODEL_PATH, map_location="cpu", weights_only=False)
    
    # If it's a checkpoint (state_dict), wrap in model definition here:
    if isinstance(model, dict) and "model" in model:
        model = model["model"]
    
    model = model.float()
    model.eval()
except Exception as e:
    print(f"Failed to load model: {e}")
    sys.exit(1)

# === Create Dummy Input ===
dummy_input = torch.randn(INPUT_SIZE)

# === Export to ONNX ===
try:
    torch.onnx.export(
        model,
        dummy_input,
        ONNX_MODEL_PATH,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "output": {0: "batch_size"},
        },
        opset_version=OPSET_VERSION
    )
    print(f"Model successfully exported to {ONNX_MODEL_PATH}")
except Exception as e:
    print(f"Failed to export ONNX model: {e}")
    sys.exit(1)

# === Verify ONNX Model ===
try:
    onnx_model = onnx.load(ONNX_MODEL_PATH)
    onnx.checker.check_model(onnx_model)
    print("ONNX model is valid ✅")
except Exception as e:
    print(f"ONNX model validation failed: {e}")
    sys.exit(1)

# === Test with ONNX Runtime (Optional) ===
try:
    ort_session = onnxruntime.InferenceSession(ONNX_MODEL_PATH)
    inputs = {ort_session.get_inputs()[0].name: dummy_input.numpy()}
    outputs = ort_session.run(None, inputs)
    print("ONNX Runtime output shape:", [o.shape for o in outputs])
except Exception as e:
    print(f"ONNX Runtime test failed: {e}")
