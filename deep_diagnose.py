#!/usr/bin/env python3
"""
Deep YOLO Dataset Diagnostic for Cityscapes Structure
Find exactly why YOLO isn't recognizing the labels
"""

import os
import yaml
from pathlib import Path
import cv2

def check_exact_file_matching():
    """Check exact file name matching between images and labels"""
    print("🔍 EXACT FILE MATCHING CHECK")
    print("=" * 40)
    
    for split in ['train', 'val', 'test']:
        print(f"\n📁 {split.upper()} SET:")
        
        img_dir = Path(f"cityscapes/images/{split}")
        label_dir = Path(f"cityscapes/labels/{split}")
        
        if not img_dir.exists() or not label_dir.exists():
            print(f"❌ Missing directories")
            print(f"  Images dir exists: {img_dir.exists()} ({img_dir.absolute()})")
            print(f"  Labels dir exists: {label_dir.exists()} ({label_dir.absolute()})")
            continue
        
        # Get all files (support multiple image formats)
        img_extensions = ["*.png", "*.jpg", "*.jpeg"]
        img_files = {}
        for ext in img_extensions:
            img_files.update({f.stem: f for f in img_dir.glob(ext)})
        
        label_files = {f.stem: f for f in label_dir.glob("*.txt")}
        
        print(f"Images: {len(img_files)}")
        print(f"Labels: {len(label_files)}")
        
        # Check exact matching
        matched = set(img_files.keys()) & set(label_files.keys())
        img_only = set(img_files.keys()) - set(label_files.keys())
        label_only = set(label_files.keys()) - set(img_files.keys())
        
        print(f"Matched pairs: {len(matched)}")
        print(f"Images without labels: {len(img_only)}")
        print(f"Labels without images: {len(label_only)}")
        
        if img_only:
            print(f"Examples of images without labels: {list(img_only)[:5]}")
        if label_only:
            print(f"Examples of labels without images: {list(label_only)[:5]}")
        
        # Test a few specific pairs
        print(f"\n🔍 Testing specific file pairs:")
        for stem in list(matched)[:3]:
            img_file = img_files[stem]
            label_file = label_files[stem]
            
            # Check if image can be read
            img = cv2.imread(str(img_file))
            img_readable = img is not None
            
            # Check label content
            try:
                with open(label_file, 'r') as f:
                    content = f.read().strip()
                label_valid = bool(content and len(content.split('\n')) > 0)
                label_lines = len([l for l in content.split('\n') if l.strip()])
            except:
                label_valid = False
                label_lines = 0
            
            print(f"  {stem}: img_ok={img_readable}, label_ok={label_valid}, objects={label_lines}")

def check_yolo_data_yaml():
    """Check if data.yaml is correctly formatted"""
    print(f"\n📋 DATA.YAML CHECK")
    print("=" * 20)
    
    yaml_path = Path("cityscapes/data.yaml")
    if not yaml_path.exists():
        print("❌ data.yaml not found!")
        return
    
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        print(f"✅ YAML loaded successfully")
        print(f"Path: {data.get('path', 'NOT SET')}")
        print(f"Train: {data.get('train', 'NOT SET')}")
        print(f"Val: {data.get('val', 'NOT SET')}")
        print(f"Test: {data.get('test', 'NOT SET')}")
        print(f"NC: {data.get('nc', 'NOT SET')}")
        
        # Check if paths exist
        base_path = Path(data.get('path', 'cityscapes'))
        train_path = base_path / data.get('train', 'images/train')
        val_path = base_path / data.get('val', 'images/val')
        test_path = base_path / data.get('test', 'images/test')
        
        print(f"Base path exists: {base_path.exists()} ({base_path.absolute()})")
        print(f"Train path exists: {train_path.exists()} ({train_path.absolute()})")
        print(f"Val path exists: {val_path.exists()} ({val_path.absolute()})")
        print(f"Test path exists: {test_path.exists()} ({test_path.absolute()})")
        
        # Expected label paths (Cityscapes structure)
        train_label_path = base_path / 'labels' / 'train'
        val_label_path = base_path / 'labels' / 'val'
        test_label_path = base_path / 'labels' / 'test'
        
        print(f"Train labels path: {train_label_path.exists()} ({train_label_path.absolute()})")
        print(f"Val labels path: {val_label_path.exists()} ({val_label_path.absolute()})")
        print(f"Test labels path: {test_label_path.exists()} ({test_label_path.absolute()})")
        
    except Exception as e:
        print(f"❌ Error reading YAML: {e}")

def simulate_yolo_label_search():
    """Simulate how YOLO searches for labels"""
    print(f"\n🔍 SIMULATING YOLO LABEL SEARCH")
    print("=" * 35)
    
    # Load YAML to get paths
    try:
        with open("cityscapes/data.yaml", 'r') as f:
            data = yaml.safe_load(f)
    except:
        print("❌ Cannot load cityscapes/data.yaml")
        return
    
    base_path = Path(data.get('path', 'cityscapes'))
    
    for split_name in ['train', 'val', 'test']:
        print(f"\n📁 {split_name.upper()} SIMULATION:")
        
        # Get image path
        img_path = base_path / data.get(split_name, f'images/{split_name}')
        print(f"Image path: {img_path.absolute()}")
        
        if not img_path.exists():
            print("❌ Image path doesn't exist!")
            continue
        
        # YOLO's label search logic
        # For Cityscapes structure, it should replace 'images' with 'labels'
        label_path = Path(str(img_path).replace('/images/', '/labels/'))
        print(f"Expected label path: {label_path.absolute()}")
        print(f"Label path exists: {label_path.exists()}")
        
        if label_path.exists():
            # Test a few files
            img_extensions = ["*.png", "*.jpg", "*.jpeg"]
            img_files = []
            for ext in img_extensions:
                img_files.extend(list(img_path.glob(ext))[:2])  # Get 2 files per extension
            
            img_files = img_files[:3]  # Limit to 3 total files
            
            for img_file in img_files:
                expected_label = label_path / f"{img_file.stem}.txt"
                label_exists = expected_label.exists()
                
                if label_exists:
                    try:
                        with open(expected_label, 'r') as f:
                            content = f.read().strip()
                        has_content = bool(content)
                        line_count = len([l for l in content.split('\n') if l.strip()])
                    except:
                        has_content = False
                        line_count = 0
                else:
                    has_content = False
                    line_count = 0
                
                print(f"  {img_file.name} -> {expected_label.name}: exists={label_exists}, content={has_content}, lines={line_count}")

def create_minimal_test_dataset():
    """Create a minimal test dataset to verify YOLO works"""
    print(f"\n🧪 CREATING MINIMAL TEST DATASET")
    print("=" * 35)
    
    test_dir = Path("test_cityscapes")
    test_dir.mkdir(exist_ok=True)
    
    # Create Cityscapes structure
    (test_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
    (test_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
    (test_dir / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (test_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)
    
    # Copy a few files from your dataset
    import shutil
    
    source_train_img = Path("cityscapes/images/train")
    source_train_labels = Path("cityscapes/labels/train")
    
    if source_train_img.exists() and source_train_labels.exists():
        # Copy first 3 files
        img_extensions = ["*.png", "*.jpg", "*.jpeg"]
        img_files = []
        for ext in img_extensions:
            img_files.extend(list(source_train_img.glob(ext))[:2])
        
        img_files = img_files[:3]  # Limit to 3 files
        
        copied_count = 0
        for img_file in img_files:
            label_file = source_train_labels / f"{img_file.stem}.txt"
            
            if label_file.exists():
                # Copy files
                shutil.copy2(img_file, test_dir / "images" / "train")
                shutil.copy2(label_file, test_dir / "labels" / "train")
                shutil.copy2(img_file, test_dir / "images" / "val") 
                shutil.copy2(label_file, test_dir / "labels" / "val")
                copied_count += 1
        
        if copied_count > 0:
            # Create test data.yaml
            test_yaml = {
                'path': str(test_dir.absolute()),
                'train': 'images/train',
                'val': 'images/val',
                'nc': 40,
                'names': {i: f'class_{i}' for i in range(40)}
            }
            
            with open(test_dir / "data.yaml", 'w') as f:
                yaml.dump(test_yaml, f, default_flow_style=False)
            
            print(f"✅ Test dataset created at: {test_dir.absolute()}")
            print(f"Files in train: {len(list((test_dir / 'images' / 'train').glob('*')))}")
            print(f"Labels in train: {len(list((test_dir / 'labels' / 'train').glob('*.txt')))}")
            
            print(f"\nTest with: yolo detect train data={test_dir}/data.yaml model=yolo11n.pt epochs=1")
        else:
            print("❌ No matching image-label pairs found to copy")
        
    else:
        print("❌ Cannot create test dataset - source files not found")
        print(f"  Train images: {source_train_img.exists()} ({source_train_img.absolute()})")
        print(f"  Train labels: {source_train_labels.exists()} ({source_train_labels.absolute()})")

def check_label_content_detailed():
    """Check label content in detail"""
    print(f"\n📝 DETAILED LABEL CONTENT CHECK")
    print("=" * 35)
    
    for split in ['train', 'val', 'test']:
        label_dir = Path(f"cityscapes/labels/{split}")
        if not label_dir.exists():
            print(f"\n❌ {split.upper()} labels directory doesn't exist: {label_dir.absolute()}")
            continue
            
        print(f"\n{split.upper()} labels:")
        
        label_files = list(label_dir.glob("*.txt"))
        if not label_files:
            print("❌ No label files found!")
            continue
        
        print(f"Found {len(label_files)} label files")
        
        # Check first 5 files in detail
        for label_file in label_files[:5]:
            print(f"\n📄 {label_file.name}:")
            
            try:
                with open(label_file, 'r') as f:
                    content = f.read()
                
                print(f"  Raw content length: {len(content)}")
                print(f"  Raw content (first 100 chars): {repr(content[:100])}")
                
                lines = content.strip().split('\n')
                valid_lines = [l for l in lines if l.strip()]
                
                print(f"  Lines after split: {len(lines)}")
                print(f"  Valid lines: {len(valid_lines)}")
                
                if valid_lines:
                    for i, line in enumerate(valid_lines[:3]):
                        parts = line.strip().split()
                        print(f"    Line {i+1}: {len(parts)} parts -> {parts}")
                        
                        if len(parts) == 5:
                            # Standard bounding box format
                            try:
                                class_id = int(parts[0])
                                coords = [float(x) for x in parts[1:]]
                                valid_format = (0 <= class_id <= 39 and 
                                              all(0 <= c <= 1 for c in coords))
                                print(f"      ✅ Bounding box format - Valid: {valid_format}")
                                if not valid_format:
                                    print(f"      Class ID range: {class_id} (should be 0-39)")
                                    print(f"      Coord ranges: {coords} (should be 0-1)")
                            except:
                                print(f"      ❌ Cannot parse numbers")
                        elif len(parts) >= 7 and len(parts) % 2 == 1:
                            # Polygon segmentation format (class_id + pairs of x,y coordinates)
                            try:
                                class_id = int(parts[0])
                                coords = [float(x) for x in parts[1:]]
                                num_points = len(coords) // 2
                                valid_format = (0 <= class_id <= 39 and 
                                              all(0 <= c <= 1 for c in coords))
                                print(f"      ✅ Polygon segmentation format - {num_points} points - Valid: {valid_format}")
                                if not valid_format:
                                    print(f"      Class ID range: {class_id} (should be 0-39)")
                                    invalid_coords = [c for c in coords if not (0 <= c <= 1)]
                                    if invalid_coords:
                                        print(f"      Invalid coordinates (should be 0-1): {invalid_coords[:10]}...")
                            except:
                                print(f"      ❌ Cannot parse numbers")
                        else:
                            print(f"      ❌ Invalid format - {len(parts)} parts")
                            print(f"        Expected: 5 parts (bbox) or odd number ≥7 (polygon)")
                            print(f"        For segmentation: class_id x1 y1 x2 y2 ... xn yn")
                else:
                    print("    ❌ No valid lines found")
            except Exception as e:
                print(f"  ❌ Error reading file: {e}")

def create_sample_data_yaml():
    """Create a sample data.yaml for Cityscapes structure"""
    print(f"\n📋 CREATING SAMPLE DATA.YAML")
    print("=" * 30)
    
    sample_yaml = {
        'path': 'cityscapes',  # Root directory containing images and labels folders
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': 40,  # Number of classes (adjust as needed)
        'names': {
            0: 'person', 1: 'motorcyclegroup', 2: 'terrain', 3: 'ridergroup', 4: 'road',
            5: 'motorcycle', 6: 'building', 7: 'truck', 8: 'caravan', 9: 'license plate',
            10: 'pole', 11: 'vegetation', 12: 'dynamic', 13: 'cargroup', 14: 'polegroup',
            15: 'train', 16: 'bicycle', 17: 'truckgroup', 18: 'bicyclegroup', 19: 'out of roi',
            20: 'guard rail', 21: 'ego vehicle', 22: 'rectification border', 23: 'sky', 24: 'bridge',
            25: 'wall', 26: 'fence', 27: 'trailer', 28: 'tunnel', 29: 'car',
            30: 'ground', 31: 'parking', 32: 'traffic sign', 33: 'persongroup', 34: 'static',
            35: 'rider', 36: 'traffic light', 37: 'sidewalk', 38: 'bus', 39: 'rail track'
        }
    }
    
    yaml_path = Path("cityscapes/cityscapes_data.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(sample_yaml, f, default_flow_style=False)
    
    print(f"✅ Sample data.yaml created: {yaml_path.absolute()}")
    print("📝 Content:")
    with open(yaml_path, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    print("🔍 CITYSCAPES YOLO DIAGNOSTIC")
    print("=" * 50)
    
    # Check if cityscapes directory exists
    cityscapes_dir = Path("cityscapes")
    if not cityscapes_dir.exists():
        print(f"❌ Cityscapes directory not found: {cityscapes_dir.absolute()}")
        print("Please make sure your dataset is in the 'cityscapes' folder")
        exit(1)
    
    # Run all checks
    check_yolo_data_yaml()
    check_exact_file_matching()
    simulate_yolo_label_search()
    check_label_content_detailed()
    
    print(f"\n" + "=" * 50)
    print("OPTIONS:")
    print("1. Create minimal test dataset (y)")
    print("2. Create sample data.yaml (s)")
    print("3. Both (b)")
    print("4. None (n)")
    
    response = input("Choose option: ").lower().strip()
    
    if response in ['y', 'b']:
        create_minimal_test_dataset()
    
    if response in ['s', 'b']:
        create_sample_data_yaml()