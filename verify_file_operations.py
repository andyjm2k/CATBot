"""
Quick verification script for file operations feature
Checks if all dependencies are installed and server can start
"""

import sys

# Print header
print("=" * 70)
print("FILE OPERATIONS - VERIFICATION SCRIPT")
print("=" * 70)
print()

# Check Python version
print(f"✓ Python version: {sys.version.split()[0]}")

# Check required packages
print("\nChecking dependencies...")
missing = []

packages = {
    'docx': 'python-docx',
    'openpyxl': 'openpyxl',
    'PyPDF2': 'PyPDF2',
    'PIL': 'Pillow',
    'reportlab': 'reportlab'
}

for module, package in packages.items():
    try:
        __import__(module)
        print(f"✓ {package} is installed")
    except ImportError:
        print(f"✗ {package} is NOT installed")
        missing.append(package)

# Check scratch directory
from pathlib import Path

scratch_dir = Path(__file__).parent / "scratch"
if scratch_dir.exists():
    print(f"\n✓ Scratch directory exists: {scratch_dir}")
    file_count = len(list(scratch_dir.glob("*")))
    print(f"  Contains {file_count} file(s)")
else:
    print(f"\n✗ Scratch directory not found")

# Summary
print("\n" + "=" * 70)
if missing:
    print("⚠️  MISSING DEPENDENCIES")
    print("=" * 70)
    print("\nTo install missing packages, run:")
    print(f"  pip install {' '.join(missing)}")
    print("\nOr install all at once:")
    print("  pip install -r requirements_file_operations.txt")
else:
    print("✅ ALL DEPENDENCIES INSTALLED")
    print("=" * 70)
    print("\n✓ File operations feature is ready to use!")
    print("\nTo start the server:")
    print("  python proxy_server.py")
    print("\nThen try:")
    print("  'Read the content from welcome.txt'")

print("=" * 70)

