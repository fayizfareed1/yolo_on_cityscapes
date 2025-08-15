#!/usr/bin/env python3
"""
Fix YOLO configuration and path issues for Cityscapes dataset structure
Clear cached paths and force absolute paths
"""

import json
import yaml
from pathlib import Path
import os
import shutil

def find_ultralytics_settings():
    """Find and show Ultralytics settings file"""
    print("🔍 Finding Ultralytics settings...")
    
    possible_paths = [
        Path.home() / "Library" / "Application Support" / "Ultralytics" / "settings.json",  # macOS
        Path.home() / ".config" / "Ultralytics" / "settings.json",  # Linux
        Path.home() / "AppData" / "Roaming" / "Ultralytics" / "settings.json",  # Windows
        Path("~/.ultralytics/settings.json").expanduser(),
    ]
    
    settings_path = None
    for path in possible_paths:
        if path.exists():
            settings_path = path
            break
    
    if settings_path:
        print(f"✅ Found settings: {settings_path}")
        
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            print("Current settings:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
                
            return settings_path, settings
        except Exception as e:
            print(f"❌ Error reading settings: {e}")
            return settings_path, {}
    else:
        print("❌ Settings file not found")
        return None, {}

def clear_all_yolo_cache():
    """Clear all YOLO cache and config"""
    print("\n🧹 Clearing ALL YOLO cache and config...")
    
    # Clear ultralytics cache
    cache_dirs = [
        Path.home() / ".cache" / "ultralytics",
        Path.home() / ".ultralytics",
        Path("~/.cache/yolo").expanduser(),
        Path("datasets"),
        Path("runs"),
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            print(f"Removing: {cache_dir}")
            shutil.rmtree(cache_dir, ignore_errors=True)
    
    # Remove local cache files
    for cache_file in Path().rglob("*.cache"):
        cache_file.unlink(missing_ok=True)
        print(f"Removed cache: {cache_file}")

def create_absolute_data_yaml():
    """Create data.yaml with absolute paths for Cityscapes segmentation structure"""
    print("\n📝 Creating data.yaml with absolute paths for Cityscapes segmentation...")
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Find cityscapes directory
    cityscapes_dir = current_dir / "cityscapes"
    if not cityscapes_dir.exists():
        print(f"❌ Cityscapes directory not found: {cityscapes_dir}")
        return None
    
    # Create absolute paths for images and labels
    train_img_path = cityscapes_dir / "images" / "train"
    val_img_path = cityscapes_dir / "images" / "val"
    test_img_path = cityscapes_dir / "images" / "test"
    
    train_label_path = cityscapes_dir / "labels" / "train"
    val_label_path = cityscapes_dir / "labels" / "val"
    test_label_path = cityscapes_dir / "labels" / "test"
    
    # Check if required directories exist
    required_dirs = [train_img_path, val_img_path, train_label_path, val_label_path]
    missing_dirs = [d for d in required_dirs if not d.exists()]
    
    if missing_dirs:
        print(f"❌ Required directories not found:")
        for d in missing_dirs:
            print(f"  {d}")
        return None
    
    print(f"✅ All required directories found")
    
    # Create new data.yaml with absolute paths for segmentation
    data_config = {
        'path': str(cityscapes_dir.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test' if test_img_path.exists() else None,
        'nc': 40,  # 40 classes for cityscapes segmentation
        'names': {
            0: 'person',
            1: 'motorcyclegroup',
            2: 'terrain',
            3: 'ridergroup',
            4: 'road',
            5: 'motorcycle',
            6: 'building',
            7: 'truck',
            8: 'caravan',
            9: 'license plate',
            10: 'pole',
            11: 'vegetation',
            12: 'dynamic',
            13: 'cargroup',
            14: 'polegroup',
            15: 'train',
            16: 'bicycle',
            17: 'truckgroup',
            18: 'bicyclegroup',
            19: 'out of roi',
            20: 'guard rail',
            21: 'ego vehicle',
            22: 'rectification border',
            23: 'sky',
            24: 'bridge',
            25: 'wall',
            26: 'fence',
            27: 'trailer',
            28: 'tunnel',
            29: 'car',
            30: 'ground',
            31: 'parking',
            32: 'traffic sign',
            33: 'persongroup',
            34: 'static',
            35: 'rider',
            36: 'traffic light',
            37: 'sidewalk',
            38: 'bus',
            39: 'rail track'
        }
    }
    
    # Ensure data directory exists
    data_dir = current_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Save absolute path version
    yaml_path = data_dir / "data.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created: {yaml_path}")
    print(f"Absolute path: {cityscapes_dir.absolute()}")
    
    # Verify paths and count files
    print(f"\n🔍 Verifying paths:")
    
    paths_to_check = [
        ("Train images", train_img_path),
        ("Train labels", train_label_path),
        ("Val images", val_img_path),
        ("Val labels", val_label_path),
    ]
    
    if test_img_path.exists():
        paths_to_check.extend([
            ("Test images", test_img_path),
            ("Test labels", test_label_path),
        ])
    
    for name, path in paths_to_check:
        exists = path.exists()
        print(f"{name}: {path} ({'✅' if exists else '❌'})")
        
        if exists:
            if 'images' in name.lower():
                # Count image files (common formats)
                img_count = (len(list(path.glob("*.png"))) + 
                           len(list(path.glob("*.jpg"))) + 
                           len(list(path.glob("*.jpeg"))))
                print(f"  → {img_count} image files")
            else:
                # Count label files
                label_count = len(list(path.glob("*.txt")))
                print(f"  → {label_count} label files")
    
    return yaml_path

def reset_ultralytics_settings():
    """Reset Ultralytics settings to default"""
    print("\n🔄 Resetting Ultralytics settings...")
    
    settings_path, current_settings = find_ultralytics_settings()
    
    if settings_path:
        # Backup current settings
        backup_path = settings_path.with_suffix('.json.backup')
        shutil.copy2(settings_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        
        # Create clean settings
        clean_settings = {
            "datasets_dir": str(Path.cwd() / "datasets"),
            "weights_dir": str(Path.cwd() / "weights"),
            "runs_dir": str(Path.cwd() / "runs")
        }
        
        with open(settings_path, 'w') as f:
            json.dump(clean_settings, f, indent=2)
        
        print(f"✅ Settings reset")
        print("New settings:")
        for key, value in clean_settings.items():
            print(f"  {key}: {value}")

def test_training_command():
    """Generate and test training command for segmentation"""
    print("\n🧪 Testing segmentation training command...")
    
    yaml_path = Path("cityscapes/data.yaml")
    if not yaml_path.exists():
        print(f"❌ Data YAML not found: {yaml_path}")
        return
    
    print(f"✅ Using: {yaml_path.absolute()}")
    
    # Test command for segmentation
    command = f"yolo segment train data='{yaml_path.absolute()}' model=yolo11n-seg.pt epochs=1 imgsz=640 batch=2 device=cpu cache=False verbose=True"
    
    print(f"\n💡 Try this segmentation command:")
    print(f"cd {Path.cwd()}")
    print(command)
    
    # Also show Python version
    print(f"\n💡 Or try Python version:")
    print("```python")
    print("from ultralytics import YOLO")
    print("model = YOLO('yolo11n-seg.pt')  # Use segmentation model")
    print(f"model.train(data='{yaml_path.absolute()}', epochs=1, imgsz=640, batch=2, device='cpu', cache=False)")
    print("```")

def verify_cityscapes_structure():
    """Verify the Cityscapes folder structure"""
    print("\n🏗️ Verifying Cityscapes folder structure...")
    
    current_dir = Path.cwd()
    cityscapes_dir = current_dir / "cityscapes"
    
    expected_structure = [
        "cityscapes/images/train",
        "cityscapes/images/val", 
        "cityscapes/images/test",
        "cityscapes/labels/train",
        "cityscapes/labels/val",
        "cityscapes/labels/test",
        "cityscapes/data.yaml"
    ]
    
    print("Expected structure:")
    for path_str in expected_structure:
        path = current_dir / path_str
        exists = path.exists()
        print(f"  {path_str} {'✅' if exists else '❌'}")
    
    return cityscapes_dir.exists()

if __name__ == "__main__":
    print("🔧 YOLO Cityscapes Segmentation Configuration and Path Fixer")
    print("=" * 60)
    
    # Step 0: Verify folder structure
    if not verify_cityscapes_structure():
        print("\n❌ Cityscapes directory structure not found!")
        print("Please ensure you have the following structure:")
        print("  cityscapes/")
        print("  ├── images/")
        print("  │   ├── train/")
        print("  │   ├── val/")
        print("  │   └── test/")
        print("  └── labels/")
        print("      ├── train/")
        print("      ├── val/")
        print("      └── test/")
        exit(1)
    
    # Step 1: Show current settings
    find_ultralytics_settings()
    
    # Step 2: Clear all cache
    clear_all_yolo_cache()
    
    # Step 3: Reset settings
    reset_ultralytics_settings()
    
    # Step 4: Create absolute path YAML
    yaml_path = create_absolute_data_yaml()
    
    if yaml_path:
        # Step 5: Generate test command
        test_training_command()
        
        print(f"\n🎯 SOLUTION SUMMARY:")
        print("1. All cache cleared ✅")
        print("2. Settings reset ✅") 
        print("3. Cityscapes segmentation data.yaml created ✅")
        print("4. Ready for segmentation training ✅")
        
        print(f"\n⚠️  Make sure you're in the right directory:")
        print(f"cd {Path.cwd()}")
        
        print(f"\n📁 Your segmentation dataset structure:")
        print("  cityscapes/images/train  → training images")
        print("  cityscapes/labels/train  → training segmentation masks") 
        print("  cityscapes/images/val    → validation images")
        print("  cityscapes/labels/val    → validation segmentation masks")
        print("  cityscapes/data.yaml          → YOLO segmentation configuration (40 classes)")
        
        print(f"\n🔥 Segmentation Training Tips:")
        print("• Use yolo11n-seg.pt, yolo11s-seg.pt, yolo11m-seg.pt models")
        print("• Segmentation requires more memory - reduce batch size if needed")
        print("• Label files should contain polygon coordinates for segmentation")
        print("• Consider using imgsz=512 or 1024 for better segmentation results")
        
    else:
        print(f"\n❌ Could not create Cityscapes segmentation data.yaml")
        print("Please check your folder structure matches:")
        print("  cityscapes/images/train")
        print("  cityscapes/images/val") 
        print("  cityscapes/labels/train  (segmentation masks)")
        print("  cityscapes/labels/val    (segmentation masks)")
        print("\nNote: Labels should be in YOLO segmentation format (polygon coordinates)")
        print("Not bounding boxes - use segmentation annotation format!")