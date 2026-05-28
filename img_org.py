#!/usr/bin/env python3
import os
import sys
import shutil
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS


IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
    ".webp", ".svg", ".ico", ".heic", ".heif", ".raw", ".cr2",
    ".nef", ".arw", ".dng", ".psd", ".avif",
}

def find_images(root_folder: str) -> list[Path]:
    root = Path(root_folder)

    if not root.exists():
        print(f"Error: '{root_folder}' does not exist.")
        sys.exit(1)
    if not root.is_dir():
        print(f"Error: '{root_folder}' is not a directory.")
        sys.exit(1)

    found = []
    for p in root.rglob("*"):
        if p.is_file():
            extension = p.suffix.lower()
            if extension in IMAGE_EXTENSIONS:
                found.append(p)
    return found

def get_date_taken(path):
    try:
        img = Image.open(path)
        exif_data = img._getexif()
    except Exception:
        return None
    
    if not exif_data:
        return None

    # Map tag IDs to human-readable names
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        if tag_name == "DateTimeOriginal":
            return value
    return None

def copy_images(images, destination):
    copied = 0
 
    for file in images:
        full_path = str(file.resolve())
        date_taken = get_date_taken(full_path)
 
        if date_taken:
            # date_taken format is "YYYY:MM:DD HH:MM:SS"
            parts = date_taken.split(" ")[0].split(":")
            year = parts[0]
            month = parts[1]
        else:
            year = "unknown"
            month = "unknown"
 
        dest_folder = destination / year / month
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_file = dest_folder / file.name
 
        if dest_file.exists():
            stem = file.stem  
            suffix = file.suffix 
            dup_count = 1
            while dest_file.exists():
                dest_file = dest_folder / f"{stem}_dup{dup_count}{suffix}"
                dup_count += 1
 
        shutil.copy2(full_path, dest_file)
        print(f"  Copied: {file.name} -> {dest_file}")
        copied += 1
 
    print(f"\nDone. {copied} copied.")


def main():
    source = input("Enter source directory: ")
    destination = input("Enter destination: ")
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    print(f"Searching for images in: {source}\nPutting them in: {destination}")
    
    cont = input("continue? y/n: ")
    if 'y' not in cont:
        print("exiting...")
        return

    images = find_images(source)


    if not images:
        print("No image files found.")
        return

    # Group by subfolder for a tidy printout
    by_folder: dict[Path, list[Path]] = {}
    for img in sorted(images):
        by_folder.setdefault(img.parent, []).append(img)

    total = 0
    for folder_path, files in sorted(by_folder.items()):
        print(f"======{folder_path}======")
        
        for file in files:
            size_kb = file.stat().st_size / 1024

            date_taken = get_date_taken(file)
            print(f"    {file} - {date_taken}  ({size_kb:.1f} KB)")

        total += len(files)

    print(f"\n\nFound {total} images across {len(by_folder)} folders.")
    
    cont = input(f"Do you want to copy these to {destination}? y/n: ")
    
    if 'y' not in cont:
        print("exiting...")
        return
    
    copy_images(images, destination)
    


if __name__ == "__main__":
    main()