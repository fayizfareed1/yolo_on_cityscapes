# YOLO Training on Cityscapes Dataset

This repository is primarily focused on training a dataset for YOLO segmentation tasks. Specifically, it includes training the `yolo11n-seg.pt` model on the Cityscapes dataset in YOLO format.

### ⚙️ Setup

Before running any scripts, please install the required Python packages using:
`pip install -r requirements.txt`

### 🔗 Dataset

- Download the Cityscapes dataset in YOLO format from this [Kaggle link](https://www.kaggle.com/datasets/rifqinaufalabdjul/cityscapes-in-yolo-format/data)
- After downloading, place the dataset in the `cityscapes/` directory.

### 🧠 Model Training

- Pretrained YOLOv11 segmentation model used: `yolo11n-seg.pt` (found in the `yolo_models/` directory).
- Trained model output:
`cityscapes_segmentation/train2/weights/best.pt`
- Exported ONNX model:
`cityscapes_segmentation/train2/weights/best.onnx`
- Segmentation class names:
Defined in `cityscapes/data.yaml`.

### 🛠️ Train Command (Segmentation)

`yolo task=segment mode=train model=yolo11n-seg.pt data=cityscapes/data.yaml epochs=150 imgsz=640 project=cityscapes_segmentation patience=0 device="mps"`

`mps` for mac. If you have powerfull gpu change it to gpu.

⚠️ If you face any warnings related to the device, try switching to CPU:
`device="cpu"`

### 🛠️ Train Command (Object Detection)

`yolo detect train data=data/data.yaml model=yolo11n.pt epochs=150 imgsz=640 batch=16 device=cpu project=traffic_detection name=yolo11_19class patience=0`

### 🔄 Export to ONNX

To convert the trained model to ONNX format:
`yolo export model=cityscapes_segmentation/train2/weights/best.pt format=onnx imgsz=640`

### 📁 Folder & File Structure
| File/Folder                | Description                                                     |
| -------------------------- | --------------------------------------------------------------- |
| `cityscapes/`              | Place your downloaded dataset here.                             |
| `cityscapes_segmentation/` | YOLO training outputs, including `.pt` and `.onnx` files.       |
| `test_images/`             | Sample images for testing model predictions.                    |
| `yolo_models/`             | Contains YOLOv11 models. `yolo11n-seg.pt` is used for training. |

### 🔧 Utility Scripts
| Script                         | Purpose                                                                |
| ------------------------------ | ---------------------------------------------------------------------- |
| `clear_yolo_cache_complete.sh` | Clears YOLO cache. Use if errors occur during training. <br>Run using: `chmod +x clear_yolo_cache_complete.sh`  `./clear_yolo_cache_complete.sh`|


``` |
| `config_issue_fix.py` | Diagnoses and helps resolve YOLO config file issues. |
| `deep_diagnose.py` | Advanced diagnostic tool to identify why YOLO isn't recognizing labels. |
| `detect.py` | Run inference on images using a trained model. |
| `diagnose.py` | Basic diagnostic tool for dataset structure and label issues. |
| `label_format_fix.py` | Fixes label formatting. Handles both bounding boxes and segmentation polygons. |
| `label_issue_fix.py` | Identifies and resolves empty label files in the dataset. |
| `masks_to_yolo_covertor.py` | Converts colored PNG segmentation masks to YOLO `.txt` label files. |
| `trainyolo.py` | Script-based training alternative to CLI. |
| `verify_training.py` | Validates if training output includes all expected classes. |
```

---

## ✅ Summary

This repo offers a full pipeline for:

- Preparing and fixing YOLO datasets (Cityscapes format)
- Training a segmentation model with YOLOv11
- Exporting to ONNX
- Running inference and diagnostics

---

### ⚠️ Note:
All code in this repository is designed to work with the folder structure shown below.
Please ensure you perform all operations using this structure.
If your folder layout is different, modify the paths in the code accordingly before running any scripts.


cityscapes/
├── images/
│   ├── train/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   └── val/
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── image1.txt
│   │   ├── image2.txt
│   │   └── ...
│   └── val/
│       ├── image1.txt
│       ├── image2.txt
│       └── ...
└── data.yaml

---