#!/usr/bin/env python3
"""
Fix Empty Label Files Script for Cityscapes Structure
Identifies and handles empty label files in YOLO dataset
"""

import os
from pathlib import Path

def analyze_empty_labels(data_root="cityscapes"):
    """Analyze empty label files in the dataset"""
    print("🔍 Analyzing Cityscapes Label Files")
    print("=" * 40)
    
    data_path = Path(data_root)
    labels_dir = data_path / 'labels'
    images_dir = data_path / 'images'
    
    if not labels_dir.exists():
        print(f"❌ Labels directory not found: {labels_dir}")
        return False
    
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return False
    
    total_empty = 0
    total_valid = 0
    total_corrupted = 0
    
    for split in ['train', 'val', 'test']:
        print(f"\n📊 {split.upper()} SET:")
        print("-" * 20)
        
        label_dir = labels_dir / split
        if not label_dir.exists():
            print(f"❌ Labels directory not found: {label_dir}")
            continue
        
        label_files = list(label_dir.glob('*.txt'))
        empty_files = []
        valid_files = []
        corrupted_files = []
        
        for label_file in label_files:
            try:
                with open(label_file, 'r') as f:
                    content = f.read().strip()
                    
                if not content:
                    empty_files.append(label_file)
                else:
                    # Check if content is valid
                    lines = content.split('\n')
                    is_valid = True
                    
                    for line in lines:
                        if line.strip():  # Skip empty lines
                            parts = line.strip().split()
                            
                            # Check bounding box format (5 parts)
                            if len(parts) == 5:
                                try:
                                    class_id = int(parts[0])
                                    coords = [float(x) for x in parts[1:]]
                                    if class_id < 0 or class_id >= 40:  # 40 classes (0-39)
                                        is_valid = False
                                        break
                                    if any(c < 0 or c > 1 for c in coords):
                                        is_valid = False
                                        break
                                except ValueError:
                                    is_valid = False
                                    break
                            
                            # Check polygon segmentation format (odd number >= 7)
                            elif len(parts) >= 7 and len(parts) % 2 == 1:
                                try:
                                    class_id = int(parts[0])
                                    coords = [float(x) for x in parts[1:]]
                                    if class_id < 0 or class_id >= 40:  # 40 classes (0-39)
                                        is_valid = False
                                        break
                                    if any(c < 0 or c > 1 for c in coords):
                                        is_valid = False
                                        break
                                except ValueError:
                                    is_valid = False
                                    break
                            
                            else:
                                is_valid = False
                                break
                    
                    if is_valid:
                        valid_files.append(label_file)
                    else:
                        corrupted_files.append(label_file)
                        
            except Exception as e:
                print(f"Error reading {label_file.name}: {e}")
                corrupted_files.append(label_file)
        
        print(f"Total label files: {len(label_files)}")
        print(f"✅ Valid labels: {len(valid_files)}")
        print(f"❌ Empty labels: {len(empty_files)}")
        print(f"⚠️  Corrupted labels: {len(corrupted_files)}")
        
        total_empty += len(empty_files)
        total_valid += len(valid_files)
        total_corrupted += len(corrupted_files)
        
        # Show examples
        if empty_files:
            print(f"Empty files examples: {[f.name for f in empty_files[:5]]}")
        if corrupted_files:
            print(f"Corrupted files examples: {[f.name for f in corrupted_files[:5]]}")
    
    print(f"\n📈 SUMMARY:")
    print(f"Total valid labels: {total_valid}")
    print(f"Total empty labels: {total_empty}")
    print(f"Total corrupted labels: {total_corrupted}")
    
    return total_empty > 0 or total_corrupted > 0

def fix_empty_labels(data_root="cityscapes", action="remove"):
    """
    Fix empty label files
    Actions:
    - 'remove': Remove empty label files and corresponding images
    - 'skip': Keep empty files but move images to separate folder
    - 'manual': List empty files for manual review
    """
    print(f"\n🔧 Fixing Empty Labels (Action: {action})")
    print("=" * 40)
    
    data_path = Path(data_root)
    labels_dir = data_path / 'labels'
    images_dir = data_path / 'images'
    
    for split in ['train', 'val', 'test']:
        label_dir = labels_dir / split
        img_dir = images_dir / split
        
        if not label_dir.exists() or not img_dir.exists():
            print(f"❌ Skipping {split} - missing directories")
            continue
        
        print(f"\n{split.upper()} SET:")
        
        label_files = list(label_dir.glob('*.txt'))
        empty_files = []
        corrupted_files = []
        
        # Find empty and corrupted files
        for label_file in label_files:
            try:
                with open(label_file, 'r') as f:
                    content = f.read().strip()
                
                if not content:
                    empty_files.append(label_file)
                else:
                    # Check if content is valid
                    lines = content.split('\n')
                    is_valid = True
                    
                    for line in lines:
                        if line.strip():  # Skip empty lines
                            parts = line.strip().split()
                            
                            # Valid formats: 5 parts (bbox) or odd number >= 7 (polygon)
                            if len(parts) == 5:
                                try:
                                    class_id = int(parts[0])
                                    coords = [float(x) for x in parts[1:]]
                                    if class_id < 0 or class_id >= 40 or any(c < 0 or c > 1 for c in coords):
                                        is_valid = False
                                        break
                                except ValueError:
                                    is_valid = False
                                    break
                            elif len(parts) >= 7 and len(parts) % 2 == 1:
                                try:
                                    class_id = int(parts[0])
                                    coords = [float(x) for x in parts[1:]]
                                    if class_id < 0 or class_id >= 40 or any(c < 0 or c > 1 for c in coords):
                                        is_valid = False
                                        break
                                except ValueError:
                                    is_valid = False
                                    break
                            else:
                                is_valid = False
                                break
                    
                    if not is_valid:
                        corrupted_files.append(label_file)
                        
            except Exception:
                empty_files.append(label_file)
        
        problematic_files = empty_files + corrupted_files
        print(f"Found {len(empty_files)} empty and {len(corrupted_files)} corrupted label files")
        
        if not problematic_files:
            print("✅ No problematic files to fix!")
            continue
        
        if action == "remove":
            removed_images = 0
            for label_file in problematic_files:
                # Find corresponding image(s)
                img_name = label_file.stem
                img_extensions = ['*.png', '*.jpg', '*.jpeg']
                img_files = []
                for ext in img_extensions:
                    img_files.extend(list(img_dir.glob(f"{img_name}.{ext[2:]}")))
                
                # Remove label file
                file_type = "empty" if label_file in empty_files else "corrupted"
                label_file.unlink()
                print(f"Removed {file_type} label: {label_file.name}")
                
                # Remove corresponding image(s)
                for img_file in img_files:
                    img_file.unlink()
                    print(f"Removed image: {img_file.name}")
                    removed_images += 1
            
            print(f"✅ Removed {len(problematic_files)} label files and {removed_images} image files")
        
        elif action == "skip":
            # Create backup folder
            backup_dir = data_path / f"{split}_problematic"
            backup_img_dir = backup_dir / "images"
            backup_label_dir = backup_dir / "labels"
            backup_img_dir.mkdir(parents=True, exist_ok=True)
            backup_label_dir.mkdir(parents=True, exist_ok=True)
            
            moved_images = 0
            for label_file in problematic_files:
                # Move label file
                file_type = "empty" if label_file in empty_files else "corrupted"
                dest_label = backup_label_dir / label_file.name
                label_file.rename(dest_label)
                print(f"Moved {file_type} label: {label_file.name}")
                
                # Move corresponding image(s)
                img_name = label_file.stem
                img_extensions = ['*.png', '*.jpg', '*.jpeg']
                img_files = []
                for ext in img_extensions:
                    img_files.extend(list(img_dir.glob(f"{img_name}.{ext[2:]}")))
                
                for img_file in img_files:
                    dest_img = backup_img_dir / img_file.name
                    img_file.rename(dest_img)
                    print(f"Moved image: {img_file.name}")
                    moved_images += 1
            
            print(f"✅ Moved {len(problematic_files)} label files and {moved_images} images to {backup_dir}")
        
        elif action == "manual":
            print("Problematic label files for manual review:")
            for i, label_file in enumerate(problematic_files[:20]):  # Show first 20
                file_type = "empty" if label_file in empty_files else "corrupted"
                print(f"  {i+1}. {label_file.name} ({file_type})")
            if len(problematic_files) > 20:
                print(f"  ... and {len(problematic_files) - 20} more")

def verify_dataset(data_root="cityscapes"):
    """Verify dataset after fixes"""
    print(f"\n✅ VERIFICATION AFTER FIXES")
    print("=" * 30)
    
    data_path = Path(data_root)
    images_dir = data_path / 'images'
    labels_dir = data_path / 'labels'
    
    if not images_dir.exists() or not labels_dir.exists():
        print("❌ Missing main directories")
        return
    
    total_images = 0
    total_labels = 0
    
    for split in ['train', 'val', 'test']:
        img_dir = images_dir / split
        label_dir = labels_dir / split
        
        if not img_dir.exists() or not label_dir.exists():
            continue
        
        # Count images
        img_extensions = ['*.png', '*.jpg', '*.jpeg']
        images = []
        for ext in img_extensions:
            images.extend(list(img_dir.glob(ext)))
        
        # Count valid labels
        labels = list(label_dir.glob('*.txt'))
        valid_labels = 0
        bbox_annotations = 0
        polygon_annotations = 0
        
        for label_file in labels:
            try:
                with open(label_file, 'r') as f:
                    content = f.read().strip()
                if content:
                    valid_labels += 1
                    # Count annotation types
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip():
                            parts = line.strip().split()
                            if len(parts) == 5:
                                bbox_annotations += 1
                            elif len(parts) >= 7 and len(parts) % 2 == 1:
                                polygon_annotations += 1
            except Exception:
                pass
        
        print(f"{split.upper()}: {len(images)} images, {valid_labels} valid labels")
        if bbox_annotations > 0:
            print(f"  └─ {bbox_annotations} bounding box annotations")
        if polygon_annotations > 0:
            print(f"  └─ {polygon_annotations} polygon annotations")
        
        total_images += len(images)
        total_labels += valid_labels
    
    print(f"\n📊 TOTAL: {total_images} images, {total_labels} valid labels")
    
    # Check for matching pairs
    print(f"\n🔍 MATCHING CHECK:")
    for split in ['train', 'val', 'test']:
        img_dir = images_dir / split
        label_dir = labels_dir / split
        
        if not img_dir.exists() or not label_dir.exists():
            continue
        
        # Get image stems
        img_extensions = ['*.png', '*.jpg', '*.jpeg']
        img_stems = set()
        for ext in img_extensions:
            img_stems.update([f.stem for f in img_dir.glob(ext)])
        
        # Get label stems
        label_stems = {f.stem for f in label_dir.glob('*.txt')}
        
        matched = len(img_stems & label_stems)
        unmatched = len(img_stems - label_stems)
        
        print(f"  {split.upper()}: {matched} matched pairs, {unmatched} images without labels")

if __name__ == "__main__":
    print("🔧 Cityscapes Empty Label Files Handler")
    print("=" * 40)
    
    # Analyze the issue
    has_issues = analyze_empty_labels()
    
    if has_issues:
        print("\n" + "=" * 50)
        print("🛠️  FIX OPTIONS:")
        print("1. Remove empty/corrupted label files and their corresponding images")
        print("2. Move images with empty/corrupted labels to separate folder (keep for later)")
        print("3. List problematic files for manual review")
        print("4. Exit without changes")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            confirm = input("⚠️  This will DELETE files. Continue? (y/N): ").lower().strip()
            if confirm == 'y':
                fix_empty_labels(action="remove")
                verify_dataset()
            else:
                print("Cancelled.")
        elif choice == "2":
            fix_empty_labels(action="skip")
            verify_dataset()
        elif choice == "3":
            fix_empty_labels(action="manual")
        else:
            print("👋 Exiting without changes...")
    else:
        print("\n✅ No empty or corrupted label files found. Your dataset should work fine!")
        verify_dataset()