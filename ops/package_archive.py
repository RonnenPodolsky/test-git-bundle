#!/usr/bin/env python3
"""
Package Archive Creation - Compression and optional splitting

Handles 7z compression, splitting, and base64 encoding for USB transfer.
"""

import os
import subprocess
import base64
import hashlib
from pathlib import Path


def run_cmd(cmd, check=True):
    """Run shell command."""
    print(f"  → {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=True, text=True)
    return result


def calculate_sha256(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def compress_package(package_dir, output_path):
    """
    Compress package directory to .7z file (preferred) or .tar.gz (fallback).

    Args:
        package_dir: directory to compress
        output_path: output .7z file path

    Returns:
        path to compressed file
    """
    package_dir = Path(package_dir).resolve()
    output_path = Path(output_path).resolve()

    print(f"\n🗜️  Compressing package...")
    print(f"   Source: {package_dir}")
    print(f"   Output: {output_path}")

    # Check if 7z is available (PREFERRED)
    try:
        subprocess.run(["7z", "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("   ✅ 7z found - using 7z compression (recommended)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ⚠️  7z not found!")
        print("   ℹ️  Install 7-Zip for better compression:")
        print("       macOS: brew install p7zip")
        print("       Windows: https://www.7-zip.org/download.html")
        print("   📦 Falling back to tar.gz...")
        return compress_with_tar(package_dir, output_path)

    # Compress with 7z
    run_cmd([
        "7z", "a",
        "-t7z",           # 7z format
        "-mx=9",          # Maximum compression
        str(output_path),
        str(package_dir / "*")
    ])

    compressed_size = os.path.getsize(output_path)
    print(f"   ✅ Compressed: {compressed_size:,} bytes ({compressed_size / 1024 / 1024:.2f} MB)")

    return str(output_path)


def compress_with_tar(package_dir, output_path):
    """Fallback compression using tar.gz."""
    output_path = Path(str(output_path).replace('.7z', '.tar.gz'))

    run_cmd([
        "tar", "czf",
        str(output_path),
        "-C", str(package_dir.parent),
        package_dir.name
    ])

    compressed_size = os.path.getsize(output_path)
    print(f"   ✅ Compressed (tar.gz): {compressed_size:,} bytes ({compressed_size / 1024 / 1024:.2f} MB)")

    return str(output_path)


def split_archive(archive_path, split_size_mb=2000):
    """
    Split archive into chunks (for FAT32 USB drives).

    Args:
        archive_path: path to archive file
        split_size_mb: size of each chunk in MB (default: 2000 MB = 2GB)

    Returns:
        list of chunk file paths
    """
    archive_path = Path(archive_path)

    print(f"\n✂️  Splitting archive into {split_size_mb} MB chunks...")

    # Split using the 'split' command
    chunk_prefix = f"{archive_path}.part"

    run_cmd([
        "split",
        "-b", f"{split_size_mb}m",  # Size per chunk
        str(archive_path),
        chunk_prefix
    ])

    # Find all chunks
    chunks = sorted(archive_path.parent.glob(f"{archive_path.name}.part*"))

    print(f"   ✅ Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        chunk_size = os.path.getsize(chunk)
        print(f"      {i}. {chunk.name} ({chunk_size:,} bytes)")

    # Delete original archive (optional)
    # archive_path.unlink()

    return [str(c) for c in chunks]


def base64_encode_file(file_path):
    """
    Encode file as base64 (for email/security scanning).

    Args:
        file_path: file to encode

    Returns:
        path to .b64 file
    """
    file_path = Path(file_path)
    output_path = file_path.with_suffix(file_path.suffix + '.b64')

    print(f"\n🔐 Base64 encoding: {file_path.name}")

    with open(file_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            base64.encode(f_in, f_out)

    encoded_size = os.path.getsize(output_path)
    original_size = os.path.getsize(file_path)
    overhead = (encoded_size - original_size) / original_size * 100

    print(f"   Original: {original_size:,} bytes")
    print(f"   Encoded:  {encoded_size:,} bytes (+{overhead:.1f}% overhead)")
    print(f"   ✅ Saved to: {output_path.name}")

    return str(output_path)


def create_checksums(files, output_path):
    """
    Create SHA256 checksums file.

    Args:
        files: list of file paths
        output_path: where to save CHECKSUMS.sha256

    Returns:
        path to checksums file
    """
    output_path = Path(output_path)

    print(f"\n🔒 Generating checksums...")

    with open(output_path, 'w') as f:
        for file_path in files:
            file_path = Path(file_path)
            if not file_path.exists():
                continue

            print(f"   Computing SHA256: {file_path.name}")
            checksum = calculate_sha256(file_path)
            f.write(f"{checksum}  {file_path.name}\n")

    print(f"   ✅ Checksums saved to: {output_path.name}")
    return str(output_path)


def create_reconstruction_instructions(archive_name, num_chunks, output_path):
    """Create Windows-compatible instructions for extracting the package."""
    output_path = Path(output_path)

    # Determine if split or base64 encoded
    is_split = num_chunks > 1
    is_base64 = '.b64' in archive_name

    instructions = f"""# Package Extraction Instructions

**Package:** {archive_name}
**For:** Windows (Tohad deployment)

---

## Quick Start

### Using 7-Zip GUI (Easiest)

1. **Right-click** on `{archive_name}`
2. Choose **7-Zip** → **Extract Here**
3. Done! You can now access the package contents.

---

## Alternative: Command Line

### Using Git Bash or PowerShell:

```bash
# Extract the package
7z x {archive_name}

# Change to extracted directory
cd {archive_name.replace('.7z', '')}

# Verify contents
ls
# You should see:
# - bundles/
# - manifest.yaml
# - RELEASE_NOTES.md
```

---

## Verify Package Integrity (Recommended)

**Using Git Bash:**
```bash
sha256sum -c CHECKSUMS.sha256
```

**Using PowerShell:**
```powershell
Get-Content CHECKSUMS.sha256 | ForEach-Object {{
    $hash, $file = $_ -split '  '
    $actual = (Get-FileHash $file -Algorithm SHA256).Hash.ToLower()
    if ($actual -eq $hash) {{
        Write-Host "OK: $file" -ForegroundColor Green
    }} else {{
        Write-Host "FAILED: $file" -ForegroundColor Red
    }}
}}
```

All files should show "OK".

---

## Package Contents

After extraction, you'll find:

- **bundles/** - Git bundle files for each repository
- **manifest.yaml** - Package metadata and version information
- **RELEASE_NOTES.md** - Changelog and deployment information

---

## Deploying Bundles to GitHub

### First Release (Full Bundle)

If this is your first deployment, clone from the bundle and push to your remote repository:

```bash
# Example: deploying mock-app bundle
cd /c/Tohad/workspace

# Clone from the bundle file
git clone /c/Tohad/Releases/v1.0.0/bundles/mock-app.bundle mock-app-tohad

# Navigate to the cloned repo
cd mock-app-tohad

# Add your remote repository
git remote remove origin  # Remove bundle origin
git remote add origin https://github.com/YourOrg/mock-app-tohad.git

# Push everything to GitHub
git push -u origin main
git push origin --tags
```

### Incremental Updates (Diff Bundle)

If this is an update, fetch changes from the bundle and merge:

```bash
# Example: updating existing mock-app-tohad repo
cd /c/Tohad/workspace/mock-app-tohad

# Verify you're on main branch
git status

# Fetch new commits from the bundle
git fetch /c/Tohad/Releases/v2.0.0/bundles/mock-app.bundle refs/heads/main

# Merge the updates
git merge FETCH_HEAD -m "Merge v2.0.0 from bundle"

# Push to GitHub
git push origin main
git push origin --tags
```

**Note:** Check `manifest.yaml` to see if bundles are `type: full` or `type: incremental`.

---

## Prerequisites

- **7-Zip installed:** https://www.7-zip.org/download.html
- **Git for Windows:** https://git-scm.com/download/win
- **GitHub access:** Configured with SSH keys or personal access token

---

## Troubleshooting

### "7z is not recognized"

**Solution:** Install 7-Zip from https://www.7-zip.org/

### "Cannot extract - file is corrupt"

**Solution:**
1. Verify checksums (see above)
2. Re-download the package
3. Try extracting with GUI instead of command line

### Files extracted but can't find bundles/

**Solution:**
1. Check you're in the correct directory
2. The structure should be:
   ```
   v1.0.0/
   ├── bundles/
   ├── manifest.yaml
   └── RELEASE_NOTES.md
   ```

---

**For detailed deployment instructions, refer to the separate deployment guide.**
"""

    with open(output_path, 'w') as f:
        f.write(instructions)

    print(f"   ✅ Instructions saved to: {output_path.name}")
    return str(output_path)


def package_archive(package_dir, output_dir, split=False, split_size_mb=2000, base64_encode=False):
    """
    Complete packaging workflow: compress, split, encode, checksum.

    Args:
        package_dir: directory to package
        output_dir: where to save final output
        split: whether to split into chunks
        split_size_mb: chunk size in MB
        base64_encode: whether to base64 encode

    Returns:
        dict with output file paths
    """
    package_dir = Path(package_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Package Archive Creation")
    print(f"{'='*60}")

    # Step 1: Compress
    archive_name = f"{package_dir.name}.7z"
    archive_path = output_dir / archive_name
    actual_archive_path = compress_package(package_dir, archive_path)

    files_to_ship = [Path(actual_archive_path)]

    # Step 2: Split (optional)
    if split:
        chunk_paths = split_archive(archive_path, split_size_mb)
        files_to_ship = chunk_paths

    # Step 3: Base64 encode (optional)
    if base64_encode:
        encoded_files = []
        for file_path in files_to_ship:
            encoded_path = base64_encode_file(file_path)
            encoded_files.append(encoded_path)
        files_to_ship = encoded_files

    # Step 4: Checksums
    checksums_path = output_dir / "CHECKSUMS.sha256"
    create_checksums(files_to_ship, checksums_path)
    files_to_ship.append(checksums_path)

    # Step 5: Reconstruction instructions
    instructions_path = output_dir / "RECONSTRUCTION_INSTRUCTIONS.txt"
    num_chunks = len([f for f in files_to_ship if 'part' in str(f)])
    if num_chunks == 0:
        num_chunks = 1
    create_reconstruction_instructions(archive_name, num_chunks, instructions_path)
    files_to_ship.append(instructions_path)

    print(f"\n{'='*60}")
    print(f"✅ Package ready for USB transfer!")
    print(f"{'='*60}")
    print(f"\nFiles to copy to USB:")
    for f in files_to_ship:
        f_path = Path(f)
        if f_path.exists():
            size = os.path.getsize(f)
            print(f"  - {f_path.name} ({size:,} bytes)")

    return {
        "files": [str(f) for f in files_to_ship],
        "total_size": sum(os.path.getsize(f) for f in files_to_ship if Path(f).exists())
    }


if __name__ == "__main__":
    # Test
    result = package_archive(
        package_dir="../releases/v1.0.0",
        output_dir="../releases/final",
        split=False,
        base64_encode=False
    )

    print(f"\n📊 Total package size: {result['total_size']:,} bytes")
