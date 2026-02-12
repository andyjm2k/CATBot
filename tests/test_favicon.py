"""
Unit tests for favicon generation script.
Tests that favicon files are created correctly from the logo.
"""
import os
import pytest
from pathlib import Path
from PIL import Image
from scripts.create_favicon import create_favicon, FAVICON_SIZES, LOGO_PATH, PROJECT_ROOT

class TestFaviconGeneration:
    """Test class for favicon generation functionality."""
    
    def test_logo_file_exists(self):
        """Test that the logo file exists before generating favicons."""
        assert os.path.exists(LOGO_PATH), f"Logo file {LOGO_PATH} should exist"
    
    def test_favicon_creation(self):
        """Test that favicon creation function runs without errors."""
        # This test verifies the function completes successfully
        result = create_favicon()
        assert result is True, "Favicon creation should return True on success"
    
    def test_favicon_files_created(self):
        """Test that all expected favicon files are created."""
        # Check that all PNG favicon files exist in project root
        for size, filename in FAVICON_SIZES:
            path = PROJECT_ROOT / filename
            assert path.exists(), f"Favicon file {filename} should be created"
    
    def test_favicon_ico_exists(self):
        """Test that the standard favicon.ico file is created."""
        assert (PROJECT_ROOT / 'favicon.ico').exists(), "favicon.ico should be created"
    
    def test_favicon_sizes_correct(self):
        """Test that each favicon file has the correct dimensions."""
        for size, filename in FAVICON_SIZES:
            path = PROJECT_ROOT / filename
            if path.exists():
                img = Image.open(path)
                assert img.size == (size, size), f"{filename} should be {size}x{size} pixels"
    
    def test_favicon_format(self):
        """Test that favicon files are in PNG format."""
        for size, filename in FAVICON_SIZES:
            path = PROJECT_ROOT / filename
            if path.exists():
                img = Image.open(path)
                assert img.format == 'PNG', f"{filename} should be in PNG format"
    
    def test_apple_touch_icon_exists(self):
        """Test that Apple touch icon is created."""
        assert (PROJECT_ROOT / 'apple-touch-icon.png').exists(), "Apple touch icon should be created"
    
    def test_android_chrome_icons_exist(self):
        """Test that Android Chrome icons are created."""
        assert (PROJECT_ROOT / 'android-chrome-192x192.png').exists(), "Android Chrome 192x192 icon should be created"
        assert (PROJECT_ROOT / 'android-chrome-512x512.png').exists(), "Android Chrome 512x512 icon should be created"

if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
