#!/usr/bin/env python3
"""
YOLO Dataset Diagnostic and Fix Script for Cityscapes Structure
Diagnoses issues with YOLO dataset structure and label files
"""

import os
import glob
from pathlib import Path

def diagnose_dataset(data_root="cityscapes"):
    """Comprehensive dataset diagnosis for Cityscapes structure"""
    print("🔍 CITYSCAPES YOLO Dataset Diagnostic Report")
    print("=" * 50)
    
    # Check main structure
    data_path = Path(data_root)
    if not data_path.exists():
        print(f"❌ Dataset root '{data_root}' not found!")
        return
    
    print(f"📁 Dataset root: {data_path.absolute()}")
    
    # Check images and labels directories exist
    images_dir = data_path / 'images'
    labels_dir = data_path / 'labels'
    
    print(f"Images root exists: {'✅' if images_dir.exists() else '❌'} {images_dir}")
    print(f"Labels root exists: {'✅' if labels_dir.exists() else '❌'} {labels_dir}")
    
    # Check train, val, and test directories
    for split in ['train', 'val', 'test']:
        print(f"\n📊 {split.upper()} SET:")
        print("-" * 20)
        
        img_dir = images_dir / split
        label_dir = labels_dir / split
        
        # Check directories exist
        print(f"Images dir exists: {'✅' if img_dir.exists() else '❌'} {img_dir}")
        print(f"Labels dir exists: {'✅' if label_dir.exists() else '❌'} {label_dir}")
        
        if not img_dir.exists():
            continue
            
        # Count files
        image_files = list(img_dir.glob('*.png')) + list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.jpeg'))
        print(f"Image files found: {len(image_files)}")
        
        if len(image_files) > 0:
            print(f"First few images: {[f.name for f in image_files[:3]]}")
        
        if label_dir.exists():
            label_files = list(label_dir.glob('*.txt'))
            print(f"Label files found: {len(label_files)}")
            
            if len(label_files) > 0:
                print(f"First few labels: {[f.name for f in label_files[:3]]}")
                
                # Check matching
                matched = 0
                unmatched_images = []
                unmatched_labels = []
                
                image_stems = {f.stem for f in image_files}
                label_stems = {f.stem for f in label_files}
                
                matched = len(image_stems & label_stems)
                unmatched_images = image_stems - label_stems
                unmatched_labels = label_stems - image_stems
                
                print(f"Matched pairs: {matched}")
                print(f"Images without labels: {len(unmatched_images)}")
                print(f"Labels without images: {len(unmatched_labels)}")
                
                if len(unmatched_images) > 0:
                    print(f"Examples of images without labels: {list(unmatched_images)[:5]}")
                if len(unmatched_labels) > 0:
                    print(f"Examples of labels without images: {list(unmatched_labels)[:5]}")
                
                # Check label content
                if label_files:
                    sample_label = label_files[0]
                    try:
                        with open(sample_label, 'r') as f:
                            content = f.read().strip()
                            if content:
                                lines = content.split('\n')
                                print(f"Sample label content ({sample_label.name}):")
                                print(f"  Lines: {len(lines)}")
                                print(f"  First line: '{lines[0]}'")
                                
                                # Validate format
                                parts = lines[0].split()
                                
                                # Check for bounding box format (5 parts)
                                if len(parts) == 5:
                                    try:
                                        class_id = int(parts[0])
                                        coords = [float(x) for x in parts[1:]]
                                        print(f"  Format: ✅ BBOX - class_id={class_id}, coords={coords}")
                                        if class_id < 0 or class_id >= 40:
                                            print(f"  ⚠️  Class ID {class_id} outside valid range (0-39)")
                                        if any(c < 0 or c > 1 for c in coords):
                                            print(f"  ⚠️  Coordinates not normalized (should be 0-1)")
                                    except ValueError as e:
                                        print(f"  ❌ Invalid bbox format: {e}")
                                
                                # Check for polygon segmentation format (odd number >= 7)
                                elif len(parts) >= 7 and len(parts) % 2 == 1:
                                    try:
                                        class_id = int(parts[0])
                                        coords = [float(x) for x in parts[1:]]
                                        num_points = len(coords) // 2
                                        print(f"  Format: ✅ POLYGON - class_id={class_id}, points={num_points}")
                                        if class_id < 0 or class_id >= 40:
                                            print(f"  ⚠️  Class ID {class_id} outside valid range (0-39)")
                                        if any(c < 0 or c > 1 for c in coords):
                                            print(f"  ⚠️  Coordinates not normalized (should be 0-1)")
                                    except ValueError as e:
                                        print(f"  ❌ Invalid polygon format: {e}")
                                
                                else:
                                    print(f"  ❌ Invalid format: {len(parts)} parts")
                                    print(f"      Expected: 5 (bbox) or odd number ≥7 (polygon)")
                                    
                            else:
                                print(f"  ❌ Empty label file!")
                    except Exception as e:
                        print(f"  ❌ Error reading label: {e}")
            else:
                print("❌ No label files found!")
        else:
            print("❌ Labels directory doesn't exist!")
    
    # Check data.yaml
    print(f"\n📋 DATA.YAML CHECK:")
    print("-" * 20)
    yaml_file = data_path / 'data.yaml'
    print(f"data.yaml exists: {'✅' if yaml_file.exists() else '❌'} {yaml_file}")
    
    if yaml_file.exists():
        try:
            with open(yaml_file, 'r') as f:
                content = f.read()
                print("✅ data.yaml is readable")
                if 'images/train' in content:
                    print("✅ Contains Cityscapes-style paths")
                else:
                    print("⚠️  May need path updates for Cityscapes structure")
        except Exception as e:
            print(f"❌ Error reading data.yaml: {e}")

def fix_common_issues(data_root="cityscapes"):
    """Fix common dataset issues for Cityscapes structure"""
    print("\n🔧 ATTEMPTING COMMON FIXES")
    print("=" * 30)
    
    data_path = Path(data_root)
    images_dir = data_path / 'images'
    labels_dir = data_path / 'labels'
    
    # Create main structure if missing
    if not images_dir.exists():
        print(f"📁 Creating missing images directory: {images_dir}")
        images_dir.mkdir(parents=True, exist_ok=True)
    
    if not labels_dir.exists():
        print(f"📁 Creating missing labels directory: {labels_dir}")
        labels_dir.mkdir(parents=True, exist_ok=True)
    
    for split in ['train', 'val', 'test']:
        img_dir = images_dir / split
        label_dir = labels_dir / split
        
        if not img_dir.exists():
            continue
            
        # Create labels subdirectory if missing
        if not label_dir.exists():
            print(f"📁 Creating missing labels subdirectory: {label_dir}")
            label_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for labels in wrong locations
        wrong_locations = [
            img_dir,                    # labels in images directory
            data_path / split,          # labels directly in cityscapes/train, etc.
            data_path,                  # labels in cityscapes root
            images_dir,                 # labels in images root
        ]
        
        for wrong_dir in wrong_locations:
            if wrong_dir == label_dir:
                continue
                
            wrong_labels = list(wrong_dir.glob('*.txt'))
            if wrong_labels:
                print(f"📦 Found {len(wrong_labels)} label files in wrong location: {wrong_dir}")
                print("   Moving to correct location...")
                
                for label_file in wrong_labels:
                    dest = label_dir / label_file.name
                    if not dest.exists():
                        try:
                            label_file.rename(dest)
                            print(f"   ✅ Moved: {label_file.name}")
                        except Exception as e:
                            print(f"   ❌ Failed to move {label_file.name}: {e}")

def create_empty_labels(data_root="cityscapes"):
    """Create empty label files for images without labels (for testing)"""
    print("\n⚠️  EMERGENCY FIX: Creating empty labels")
    print("=" * 40)
    print("This creates empty .txt files for images without labels.")
    print("Use this only for testing - you need real annotations for training!")
    
    response = input("Continue? (y/N): ").lower().strip()
    if response != 'y':
        return
    
    data_path = Path(data_root)
    images_dir = data_path / 'images'
    labels_dir = data_path / 'labels'
    
    for split in ['train', 'val', 'test']:
        img_dir = images_dir / split
        label_dir = labels_dir / split
        
        if not img_dir.exists():
            continue
            
        label_dir.mkdir(parents=True, exist_ok=True)
        
        image_files = (list(img_dir.glob('*.png')) + 
                      list(img_dir.glob('*.jpg')) + 
                      list(img_dir.glob('*.jpeg')))
        created = 0
        
        for img_file in image_files:
            label_file = label_dir / f"{img_file.stem}.txt"
            if not label_file.exists():
                label_file.touch()  # Create empty file
                created += 1
        
        print(f"Created {created} empty label files in {split}/labels/")

def create_sample_data_yaml(data_root="cityscapes"):
    """Create a sample data.yaml file for Cityscapes"""
    print("\n📋 CREATING SAMPLE DATA.YAML")
    print("=" * 30)
    
    data_path = Path(data_root)
    yaml_file = data_path / 'data.yaml'
    
    if yaml_file.exists():
        response = input(f"data.yaml already exists. Overwrite? (y/N): ").lower().strip()
        if response != 'y':
            return
    
    yaml_content = f"""# Cityscapes YOLO Dataset Configuration
path: {data_root}  # dataset root dir
train: images/train  # train images (relative to 'path')
val: images/val      # val images (relative to 'path')
test: images/test    # test images (relative to 'path') [optional]

# Classes (40 classes for Cityscapes)
nc: 40  # number of classes
names:
  0: person
  1: motorcyclegroup
  2: terrain
  3: ridergroup
  4: road
  5: motorcycle
  6: building
  7: truck
  8: caravan
  9: nse plate
  10: pole
  11: vegetation
  12: dynamic
  13: cargroup
  14: polegroup
  15: train
  16: bicycle
  17: truckgroup
  18: bicyclegroup
  19: out of roi
  20: guard rail
  21: ego vehicle
  22: rectification border
  23: sky
  24: bridge
  25: wall
  26: fence
  27: trailer
  28: tunnel
  29: car
  30: ground
  31: parking
  32: traffic sign
  33: persongroup
  34: static
  35: rider
  36: traffic light
  37: sidewalk
  38: bus
  39: rail track
"""
    
    try:
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        print(f"✅ Created data.yaml: {yaml_file.absolute()}")
    except Exception as e:
        print(f"❌ Failed to create data.yaml: {e}")

if __name__ == "__main__":
    # Run diagnosis
    diagnose_dataset()
    
    # Offer fixes
    print("\n" + "=" * 50)
    print("🛠️  AVAILABLE FIXES:")
    print("1. Fix common structural issues")
    print("2. Create empty labels (testing only)")
    print("3. Create sample data.yaml")
    print("4. All fixes (1 + 3)")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        fix_common_issues()
        print("\n🔄 Re-running diagnosis after fixes...")
        diagnose_dataset()
    elif choice == "2":
        create_empty_labels()
        print("\n🔄 Re-running diagnosis after creating empty labels...")
        diagnose_dataset()
    elif choice == "3":
        create_sample_data_yaml()
        print("\n🔄 Re-running diagnosis after creating data.yaml...")
        diagnose_dataset()
    elif choice == "4":
        fix_common_issues()
        create_sample_data_yaml()
        print("\n🔄 Re-running diagnosis after all fixes...")
        diagnose_dataset()
    else:
        print("👋 Exiting...")