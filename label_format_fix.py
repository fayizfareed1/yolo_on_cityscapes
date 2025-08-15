#!/usr/bin/env python3
"""
Fix YOLO label format for Cityscapes structure - separate bounding boxes into individual lines
Handles both bbox (5 parts) and polygon segmentation formats
"""

import os
from pathlib import Path

def fix_label_format(label_file):
    """Fix a single label file format"""
    try:
        with open(label_file, 'r') as f:
            content = f.read().strip()
        
        if not content:
            return False, "Empty file"
        
        # Check if file is already in correct format
        lines = content.split('\n')
        if len(lines) > 1:
            # Check first line
            first_line_parts = lines[0].strip().split()
            if len(first_line_parts) == 5 or (len(first_line_parts) >= 7 and len(first_line_parts) % 2 == 1):
                return True, "Already correct format"
        
        # Fix the format - split by newlines within the single line
        # The issue is that multiple annotations are on one line separated by \n
        fixed_lines = []
        
        # Split the content by \n characters (both literal \n and actual newlines)
        all_annotations = content.replace('\\n', '\n').split('\n')
        
        for annotation_line in all_annotations:
            annotation_line = annotation_line.strip()
            if not annotation_line:
                continue
                
            parts = annotation_line.split()
            
            # Handle bounding box format (5 values: class_id x y w h)
            if len(parts) == 5:
                try:
                    class_id = int(parts[0])
                    coords = [float(x) for x in parts[1:]]
                    
                    # Validate values for 40 classes
                    if 0 <= class_id <= 39 and all(0 <= c <= 1 for c in coords):
                        fixed_lines.append(f"{class_id} {coords[0]:.6f} {coords[1]:.6f} {coords[2]:.6f} {coords[3]:.6f}")
                except ValueError:
                    continue
            
            # Handle polygon segmentation format (odd number >= 7: class_id + pairs of x,y)
            elif len(parts) >= 7 and len(parts) % 2 == 1:
                try:
                    class_id = int(parts[0])
                    coords = [float(x) for x in parts[1:]]
                    
                    # Validate values for 40 classes
                    if 0 <= class_id <= 39 and all(0 <= c <= 1 for c in coords):
                        # Keep original precision for polygon coordinates
                        coord_str = ' '.join(f"{c:.6f}" for c in coords)
                        fixed_lines.append(f"{class_id} {coord_str}")
                except ValueError:
                    continue
        
        if fixed_lines:
            # Write back the corrected format
            with open(label_file, 'w') as f:
                f.write('\n'.join(fixed_lines) + '\n')
            return True, f"Fixed {len(fixed_lines)} annotations"
        else:
            return False, "No valid annotations found"
            
    except Exception as e:
        return False, f"Error: {e}"

def fix_all_labels(data_root="cityscapes"):
    """Fix all label files in the dataset"""
    print("🔧 Fixing Cityscapes YOLO label format")
    print("=" * 40)
    
    data_path = Path(data_root)
    labels_dir = data_path / 'labels'
    
    if not labels_dir.exists():
        print(f"❌ Labels directory not found: {labels_dir}")
        return
    
    stats = {
        'fixed': 0,
        'already_correct': 0,
        'errors': 0,
        'empty': 0
    }
    
    for split in ['train', 'val', 'test']:
        print(f"\n📁 Processing {split.upper()} set...")
        
        label_dir = labels_dir / split
        if not label_dir.exists():
            print(f"❌ Labels directory not found: {label_dir}")
            continue
        
        label_files = list(label_dir.glob('*.txt'))
        print(f"Found {len(label_files)} label files")
        
        for label_file in label_files:
            success, message = fix_label_format(label_file)
            
            if success:
                if "Already correct" in message:
                    stats['already_correct'] += 1
                else:
                    stats['fixed'] += 1
                    print(f"✅ {label_file.name}: {message}")
            else:
                if "Empty file" in message:
                    stats['empty'] += 1
                    print(f"⚠️  {label_file.name}: Empty file")
                else:
                    stats['errors'] += 1
                    print(f"❌ {label_file.name}: {message}")
    
    print(f"\n📊 SUMMARY:")
    print(f"Fixed: {stats['fixed']}")
    print(f"Already correct: {stats['already_correct']}")
    print(f"Empty files: {stats['empty']}")
    print(f"Errors: {stats['errors']}")

def verify_fixed_format(data_root="cityscapes"):
    """Verify that the format is now correct"""
    print(f"\n✅ VERIFICATION")
    print("=" * 20)
    
    data_path = Path(data_root)
    labels_dir = data_path / 'labels'
    
    if not labels_dir.exists():
        print(f"❌ Labels directory not found: {labels_dir}")
        return
    
    for split in ['train', 'val', 'test']:
        label_dir = labels_dir / split
        if not label_dir.exists():
            print(f"❌ {split.upper()} labels directory not found")
            continue
        
        label_files = list(label_dir.glob('*.txt'))
        valid_files = 0
        total_objects = 0
        bbox_count = 0
        polygon_count = 0
        
        for label_file in label_files:
            try:
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                if not lines:
                    continue
                
                file_valid = True
                file_objects = 0
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    parts = line.split()
                    
                    # Check bounding box format (5 parts)
                    if len(parts) == 5:
                        try:
                            class_id = int(parts[0])
                            coords = [float(x) for x in parts[1:]]
                            if not (0 <= class_id <= 39) or not all(0 <= c <= 1 for c in coords):
                                file_valid = False
                                break
                            file_objects += 1
                            bbox_count += 1
                        except ValueError:
                            file_valid = False
                            break
                    
                    # Check polygon segmentation format (odd number >= 7)
                    elif len(parts) >= 7 and len(parts) % 2 == 1:
                        try:
                            class_id = int(parts[0])
                            coords = [float(x) for x in parts[1:]]
                            if not (0 <= class_id <= 39) or not all(0 <= c <= 1 for c in coords):
                                file_valid = False
                                break
                            file_objects += 1
                            polygon_count += 1
                        except ValueError:
                            file_valid = False
                            break
                    
                    else:
                        file_valid = False
                        break
                
                if file_valid and file_objects > 0:
                    valid_files += 1
                    total_objects += file_objects
                    
            except Exception:
                continue
        
        print(f"{split.upper()}:")
        print(f"  Total label files: {len(label_files)}")
        print(f"  Valid label files: {valid_files}")
        print(f"  Total annotations: {total_objects}")
        print(f"  Bounding boxes: {bbox_count}")
        print(f"  Polygons: {polygon_count}")
        
        # Show sample of corrected format
        if valid_files > 0:
            sample_file = None
            for label_file in label_files:
                try:
                    with open(label_file, 'r') as f:
                        content = f.read().strip()
                    if content and len(content.split('\n')) > 0:
                        sample_file = label_file
                        break
                except:
                    continue
            
            if sample_file:
                print(f"  Sample ({sample_file.name}):")
                with open(sample_file, 'r') as f:
                    lines = f.readlines()[:3]  # Show first 3 lines
                for i, line in enumerate(lines):
                    parts = line.strip().split()
                    if len(parts) == 5:
                        format_type = "BBOX"
                    elif len(parts) >= 7 and len(parts) % 2 == 1:
                        format_type = f"POLYGON({(len(parts)-1)//2} points)"
                    else:
                        format_type = "UNKNOWN"
                    print(f"    Line {i+1} ({format_type}): {line.strip()[:80]}...")

def manual_fix_example():
    """Show how to manually fix a problematic file"""
    print("\n🛠️  MANUAL FIX EXAMPLES")
    print("=" * 25)
    
    print("BBOX FORMAT:")
    print("WRONG (all on one line with \\n):")
    example_wrong_bbox = "10 0.347656 0.281250 0.562500 0.395833\\n12 0.091797 0.515625 0.058594 0.093750"
    print(f"'{example_wrong_bbox}'")
    
    print("\nCORRECT (separate lines):")
    example_correct_bbox = """10 0.347656 0.281250 0.562500 0.395833
12 0.091797 0.515625 0.058594 0.093750"""
    print(f"'{example_correct_bbox}'")
    
    print("\n" + "-"*40)
    print("POLYGON FORMAT:")
    print("WRONG (all on one line with \\n):")
    example_wrong_poly = "4 0.029785 0.425781 0.284180 0.412109 0.313477 0.407227\\n5 0.566406 0.373047 0.597656 0.390625"
    print(f"'{example_wrong_poly}'")
    
    print("\nCORRECT (separate lines):")
    example_correct_poly = """4 0.029785 0.425781 0.284180 0.412109 0.313477 0.407227
5 0.566406 0.373047 0.597656 0.390625"""
    print(f"'{example_correct_poly}'")

def detect_annotation_type(data_root="cityscapes"):
    """Detect what type of annotations are in the dataset"""
    print("\n🔍 DETECTING ANNOTATION TYPE")
    print("=" * 30)
    
    data_path = Path(data_root)
    labels_dir = data_path / 'labels'
    
    if not labels_dir.exists():
        print(f"❌ Labels directory not found: {labels_dir}")
        return
    
    bbox_files = 0
    polygon_files = 0
    mixed_files = 0
    invalid_files = 0
    
    for split in ['train', 'val', 'test']:
        label_dir = labels_dir / split
        if not label_dir.exists():
            continue
        
        for label_file in label_dir.glob('*.txt'):
            try:
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                if not lines:
                    continue
                
                has_bbox = False
                has_polygon = False
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        has_bbox = True
                    elif len(parts) >= 7 and len(parts) % 2 == 1:
                        has_polygon = True
                
                if has_bbox and has_polygon:
                    mixed_files += 1
                elif has_bbox:
                    bbox_files += 1
                elif has_polygon:
                    polygon_files += 1
                else:
                    invalid_files += 1
                    
            except:
                invalid_files += 1
    
    print(f"📊 ANNOTATION TYPE SUMMARY:")
    print(f"  Bounding box files: {bbox_files}")
    print(f"  Polygon segmentation files: {polygon_files}")
    print(f"  Mixed format files: {mixed_files}")
    print(f"  Invalid/empty files: {invalid_files}")
    
    if polygon_files > 0:
        print(f"\n💡 TRAINING RECOMMENDATION:")
        print(f"  Use segmentation model: yolo segment train data=cityscapes/data.yaml model=yolo_models/yolo11n-seg.pt")
    elif bbox_files > 0:
        print(f"\n💡 TRAINING RECOMMENDATION:")
        print(f"  Use detection model: yolo detect train data=cityscapes/data.yaml model=yolo_models/yolo11n.pt")

if __name__ == "__main__":
    print("🔧 Cityscapes YOLO Label Format Fixer")
    print("=" * 40)
    
    # Detect annotation type first
    detect_annotation_type()
    
    # Show example of the problem
    manual_fix_example()
    
    # Check current status
    print("\n🔍 Current status check...")
    verify_fixed_format()
    
    # Ask user if they want to fix
    response = input("\nFix the label format? (y/N): ").lower().strip()
    if response == 'y':
        fix_all_labels()
        verify_fixed_format()
        
        print("\n🎉 Format fixing complete!")
        print("\n💡 TRAINING COMMANDS:")
        print("For segmentation (if you have polygon labels):")
        print("yolo segment train data=cityscapes/data.yaml model=yolo11n-seg.pt epochs=150 imgsz=640 batch=16")
        print("\nFor detection (if you have bbox labels):")
        print("yolo detect train data=cityscapes/data.yaml model=yolo11n.pt epochs=150 imgsz=640 batch=16")
    else:
        print("👋 No changes made.")