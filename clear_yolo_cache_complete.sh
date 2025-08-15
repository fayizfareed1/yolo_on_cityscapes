#!/bin/bash

echo "🧹 Complete YOLO Cache Cleanup and Rescan"
echo "=========================================="

# 1. Remove ALL YOLO cache files
echo "🗑️  Removing all YOLO cache files..."
rm -rf ~/.cache/yolo*
rm -rf ~/.cache/ultralytics*
rm -rf .cache/
find . -name "*.cache" -delete
find . -name "*.pkl" -delete

# 2. Remove dataset-specific cache files
echo "🗑️  Removing dataset cache files..."
find ./data -name "*.cache" -delete
find ./data -name "*.pkl" -delete

# 3. Remove training runs cache
echo "🗑️  Removing training runs..."
rm -rf runs/
rm -rf cityscapes_segmentation/

# 4. Remove Python cache
echo "🗑️  Removing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 5. Clear pip cache
echo "🗑️  Clearing pip cache..."
pip cache purge 2>/dev/null

echo ""
echo "✅ All caches cleared!"
echo ""
echo "🔍 Verifying current dataset..."

# Check dataset structure
echo "📊 Dataset Statistics:"
echo "Training images: $(find data/train/img -name "*.png" 2>/dev/null | wc -l)"
echo "Training labels: $(find data/train/labels -name "*.txt" 2>/dev/null | wc -l)"
echo "Validation images: $(find data/val/img -name "*.png" 2>/dev/null | wc -l)"
echo "Validation labels: $(find data/val/labels -name "*.txt" 2>/dev/null | wc -l)"

echo ""
echo "📝 Sample label content:"
SAMPLE_LABEL=$(find data/train/labels -name "*.txt" | head -1)
if [ -f "$SAMPLE_LABEL" ]; then
    echo "File: $(basename "$SAMPLE_LABEL")"
    head -3 "$SAMPLE_LABEL"
else
    echo "No label files found!"
fi

echo ""
echo "🚀 Ready for fresh training!"
echo "Run: yolo task=segment mode=train model=yolo_models/yolo11n-seg.pt data=cityscapes/data.yaml epochs=150 imgsz=640 project=cityscapes_segmentation patience=0;"