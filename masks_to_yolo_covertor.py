#!/usr/bin/env python3
"""
Convert segmentation masks to YOLO bounding box format
Converts colored PNG masks to .txt files with bounding boxes
"""

import cv2
import numpy as np
from pathlib import Path
import json
from collections import defaultdict

# Your 19-class mapping (adjust colors based on your actual mask colors)
CLASS_MAPPING = {
    0: "road",           # Often black or dark gray
    1: "sidewalk",       # Light gray
    2: "building",       # Various colors
    3: "wall",          
    4: "fence",         
    5: "pole",          
    6: "traffic_light", 
    7: "traffic_sign",  
    8: "vegetation",     # Green
    9: "terrain",       
    10: "sky",          # Blue/cyan
    11: "person",       # Often red/pink
    12: "rider",        
    13: "car",          # Often blue
    14: "truck",        
    15: "bus",          
    16: "train",        
    17: "motorcycle",   
    18: "bicycle"       
}

def analyze_mask_colors(mask_dir, sample_size=10):
    """Analyze unique colors in mask files to create color mapping"""
    print("🎨 Analyzing mask colors...")
    
    mask_files = list(Path(mask_dir).glob("*.png"))[:sample_size]
    all_colors = set()
    
    for mask_file in mask_files:
        mask = cv2.imread(str(mask_file))
        if mask is None:
            continue
            
        # Get unique colors
        mask_reshaped = mask.reshape(-1, 3)
        unique_colors = np.unique(mask_reshaped, axis=0)
        
        for color in unique_colors:
            all_colors.add(tuple(color))
    
    print(f"Found {len(all_colors)} unique colors:")
    for i, color in enumerate(sorted(all_colors)):
        print(f"  Color {i}: RGB{color} -> BGR{color[::-1]}")
    
    return sorted(all_colors)

def create_color_to_class_mapping():
    """Create mapping from colors to class IDs - CUSTOMIZE THIS"""
    # Common Cityscapes-like color mapping (BGR format for OpenCV)
    color_to_class = {
        (128, 64, 128): 0,   # road - purple
        (244, 35, 232): 1,   # sidewalk - pink
        (70, 70, 70): 2,     # building - dark gray
        (102, 102, 156): 3,  # wall - light purple
        (190, 153, 153): 4,  # fence - light brown
        (153, 153, 153): 5,  # pole - gray
        (250, 170, 30): 6,   # traffic light - orange
        (220, 220, 0): 7,    # traffic sign - yellow
        (107, 142, 35): 8,   # vegetation - olive green
        (152, 251, 152): 9,  # terrain - light green
        (70, 130, 180): 10,  # sky - steel blue
        (220, 20, 60): 11,   # person - crimson
        (255, 0, 0): 12,     # rider - red
        (0, 0, 142): 13,     # car - dark blue
        (0, 0, 70): 14,      # truck - darker blue
        (0, 60, 100): 15,    # bus - blue
        (0, 80, 100): 16,    # train - teal
        (0, 0, 230): 17,     # motorcycle - bright blue
        (119, 11, 32): 18,   # bicycle - dark red
    }
    return color_to_class

def find_closest_color(target_color, color_mapping, threshold=50):
    """Find closest color in mapping"""
    min_distance = float('inf')
    closest_class = None
    
    for color, class_id in color_mapping.items():
        # Calculate Euclidean distance
        distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(target_color, color)))
        if distance < min_distance and distance < threshold:
            min_distance = distance
            closest_class = class_id
    
    return closest_class

def mask_to_bounding_boxes(mask_path, color_to_class, use_closest_color=True):
    """Convert segmentation mask to bounding boxes"""
    mask = cv2.imread(str(mask_path))
    if mask is None:
        return []
    
    height, width = mask.shape[:2]
    bboxes = []
    
    # Get unique colors in the mask
    mask_reshaped = mask.reshape(-1, 3)
    unique_colors = np.unique(mask_reshaped, axis=0)
    
    for color in unique_colors:
        color_tuple = tuple(color)
        
        # Find class ID for this color
        class_id = None
        if color_tuple in color_to_class:
            class_id = color_to_class[color_tuple]
        elif use_closest_color:
            class_id = find_closest_color(color_tuple, color_to_class)
        
        if class_id is None:
            continue
        
        # Create binary mask for this color
        binary_mask = np.all(mask == color, axis=2).astype(np.uint8)
        
        # Find contours
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) < 50:  # Skip very small objects
                continue
                
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Convert to YOLO format (normalized coordinates)
            x_center = (x + w / 2) / width
            y_center = (y + h / 2) / height
            box_width = w / width
            box_height = h / height
            
            bboxes.append([class_id, x_center, y_center, box_width, box_height])
    
    return bboxes

def convert_dataset(data_root="data", create_backup=True):
    """Convert entire dataset from masks to YOLO format"""
    print("🔄 Converting segmentation masks to YOLO format")
    print("=" * 50)
    
    data_path = Path(data_root)
    color_to_class = create_color_to_class_mapping()
    
    # First, analyze colors in a few sample masks
    sample_mask_dir = None
    for split in ['train', 'val']:
        label_dir = data_path / split / 'labels'
        if label_dir.exists():
            mask_files = list(label_dir.glob("*.png"))
            if mask_files:
                sample_mask_dir = label_dir
                break
    
    if sample_mask_dir:
        unique_colors = analyze_mask_colors(sample_mask_dir)
        print(f"\n📋 Update color mapping in the script if needed!")
        
        # Suggest color mapping
        print("\nSuggested color mapping (add to create_color_to_class_mapping()):")
        for i, color in enumerate(unique_colors[:19]):  # Max 19 classes
            print(f"    {color}: {i},  # class_{i} - {CLASS_MAPPING.get(i, 'unknown')}")
    
    conversion_stats = defaultdict(int)
    
    for split in ['train', 'val']:
        print(f"\n📁 Processing {split.upper()} set...")
        
        img_dir = data_path / split / 'img'
        label_dir = data_path / split / 'labels'
        
        if not img_dir.exists() or not label_dir.exists():
            print(f"❌ Missing directories for {split}")
            continue
        
        # Create backup of original masks
        if create_backup:
            backup_dir = label_dir.parent / f"labels_masks_backup"
            backup_dir.mkdir(exist_ok=True)
        
        # Get all PNG mask files
        mask_files = list(label_dir.glob("*.png"))
        print(f"Found {len(mask_files)} mask files")
        
        converted = 0
        skipped = 0
        
        for mask_file in mask_files:
            try:
                # Convert mask to bounding boxes
                bboxes = mask_to_bounding_boxes(mask_file, color_to_class)
                
                if bboxes:
                    # Create .txt file
                    txt_file = mask_file.with_suffix('.txt')
                    
                    # Backup original mask
                    if create_backup:
                        backup_file = backup_dir / mask_file.name
                        if not backup_file.exists():
                            mask_file.rename(backup_file)
                    else:
                        mask_file.unlink()  # Delete original mask
                    
                    # Write YOLO format
                    with open(txt_file, 'w') as f:
                        for bbox in bboxes:
                            f.write(f"{bbox[0]} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f} {bbox[4]:.6f}\\n")
                    
                    converted += 1
                    conversion_stats[f"{split}_converted"] += 1
                    conversion_stats[f"{split}_objects"] += len(bboxes)
                else:
                    print(f"⚠️  No objects found in {mask_file.name}")
                    skipped += 1
                    
            except Exception as e:
                print(f"❌ Error converting {mask_file.name}: {e}")
                skipped += 1
        
        print(f"✅ Converted: {converted} files")
        print(f"⚠️  Skipped: {skipped} files")
    
    # Print summary
    print(f"\n📊 CONVERSION SUMMARY:")
    for key, value in conversion_stats.items():
        print(f"{key}: {value}")

def verify_conversion(data_root="data"):
    """Verify the conversion worked correctly"""
    print(f"\n✅ VERIFICATION")
    print("=" * 20)
    
    data_path = Path(data_root)
    
    for split in ['train', 'val']:
        img_dir = data_path / split / 'img'
        label_dir = data_path / split / 'labels'
        
        if not img_dir.exists() or not label_dir.exists():
            continue
        
        images = list(img_dir.glob('*.png')) + list(img_dir.glob('*.jpg'))
        txt_labels = list(label_dir.glob('*.txt'))
        png_masks = list(label_dir.glob('*.png'))
        
        # Count non-empty labels
        valid_labels = 0
        total_objects = 0
        
        for label_file in txt_labels:
            try:
                with open(label_file, 'r') as f:
                    lines = f.read().strip().split('\\n')
                    if lines and lines[0]:
                        valid_labels += 1
                        total_objects += len([l for l in lines if l.strip()])
            except Exception:
                pass
        
        print(f"{split.upper()}:")
        print(f"  Images: {len(images)}")
        print(f"  TXT labels: {len(txt_labels)} ({valid_labels} non-empty)")
        print(f"  PNG masks remaining: {len(png_masks)}")
        print(f"  Total objects: {total_objects}")

if __name__ == "__main__":
    print("🎭 Segmentation Mask to YOLO Converter")
    print("=" * 40)
    
    # Check if masks exist
    data_path = Path("data")
    has_masks = False
    
    for split in ['train', 'val']:
        label_dir = data_path / split / 'labels'
        if label_dir.exists():
            masks = list(label_dir.glob("*.png"))
            if masks:
                has_masks = True
                print(f"Found {len(masks)} mask files in {split}/labels/")
    
    if not has_masks:
        print("❌ No PNG mask files found in labels directories!")
        print("Make sure your segmentation masks are in:")
        print("  - data/train/labels/*.png")
        print("  - data/val/labels/*.png")
        exit(1)
    
    print("\\n⚠️  IMPORTANT: Review the color mapping in create_color_to_class_mapping()")
    print("Update the colors to match your actual mask colors!")
    
    response = input("\\nContinue with conversion? (y/N): ").lower().strip()
    if response == 'y':
        convert_dataset()
        verify_conversion()
        
        print("\\n🎉 Conversion complete!")
        print("You can now train with: yolo detect train data=data/data.yaml model=yolo11n.pt ...")
    else:
        print("👋 Cancelled. Update the color mapping first!")