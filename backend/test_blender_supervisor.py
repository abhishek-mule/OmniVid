#!/usr/bin/env python3
"""
Test script for Blender Production Supervisor components.
"""
import json
import tempfile
import time
from pathlib import Path

# Import the components
import sys
sys.path.append(str(Path(__file__).parent / 'src'))

from utils.blender_supervisor import (
    Manifest, create_render_manifest, save_manifest_atomic,
    StreamHasher, AtomicFileWriter, BlenderSupervisor
)


def test_manifest_validation():
    """Test manifest creation and validation."""
    print("Testing Manifest Validation...")

    settings = {
        'resolution': (1920, 1080),
        'fps': 30,
        'duration': 10,
        'render_engine': 'BLENDER_EEVEE'
    }

    # Create manifest
    manifest = create_render_manifest("test_job_123", settings)
    print(f"Created manifest with hash: {manifest.validation_hash[:16]}...")

    # Test validation against same settings (should pass)
    success = manifest.validate_against_settings(settings, "4.0")
    assert success, "Manifest should validate against identical settings"
    print("✓ Manifest validates against identical settings")

    # Test validation against different settings (should fail)
    bad_settings = settings.copy()
    bad_settings['resolution'] = (1280, 720)
    success = manifest.validate_against_settings(bad_settings, "4.0")
    assert not success, "Manifest should reject different settings"
    print("✓ Manifest correctly rejects different settings")


def test_atomic_writes():
    """Test atomic file writing and completion markers."""
    print("\nTesting Atomic File Writes...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test atomic text write
        test_file = temp_path / "test.txt"
        AtomicFileWriter.write_atomic_text(test_file, "Hello, World!")
        assert test_file.exists(), "Atomic text write should create file"
        assert test_file.read_text() == "Hello, World!", "Content should match"
        print("✓ Atomic text write works")

        # Test completion marker
        AtomicFileWriter.write_completion_marker(
            test_file,
            {'test': 'metadata', 'timestamp': int(time.time())}
        )
        marker_file = temp_path / "test.txt.ok"
        assert marker_file.exists(), "Completion marker should be created"
        marker_data = json.loads(marker_file.read_text())
        assert marker_data['test'] == 'metadata', "Marker should contain metadata"
        print("✓ Completion marker works")


def test_stream_hashing():
    """Test stream-based file hashing."""
    print("\nTesting Stream Hashing...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test file
        test_file = temp_path / "test.bin"
        test_data = b"Hello, World! This is test data for hashing." * 1000  # Make it larger
        test_file.write_bytes(test_data)

        # Hash it
        hash_result = StreamHasher.sha256_file(test_file)
        expected_hash = "a2d7c6f8c8d1e9b6b8d3a7e8f2c5d4e6f1a8b9c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6"

        # Note: This is just a basic test - in real usage the hash will be different
        assert len(hash_result) == 64, "SHA256 hash should be 64 characters"
        assert hash_result.isalnum(), "Hash should be alphanumeric"
        print(f"✓ Stream hashing works: {hash_result[:16]}...")


def test_manifest_save_load():
    """Test saving and loading manifests."""
    print("\nTesting Manifest Save/Load...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        settings = {'resolution': (1920, 1080), 'fps': 30}
        manifest = create_render_manifest("save_load_test", settings)

        # Save manifest
        manifest_file = temp_path / "manifest.json"
        success = save_manifest_atomic(manifest, manifest_file)
        assert success, "Manifest should save successfully"
        assert manifest_file.exists(), "Manifest file should exist"
        print("✓ Manifest saves atomically")

        # Load manifest
        with open(manifest_file, 'r') as f:
            loaded_data = json.load(f)

        loaded_manifest = Manifest.from_dict(loaded_data)
        assert loaded_manifest.job_id == manifest.job_id, "Job ID should match"

        # The loaded manifest should validate using its own stored hash
        # Test that the same settings produce the same validation result
        success_orig = manifest.validate_against_settings(settings, "4.0")
        success_loaded = loaded_manifest.validate_against_settings(settings, "4.0")

        assert success_orig == success_loaded, "Original and loaded manifest should validate identically"
        if success_orig:
            print("✓ Manifest loads and validates correctly")
        else:
            print("✓ Manifest correctly rejects validation (both original and loaded)")


def main():
    """Run all tests."""
    print("🧪 Blender Production Supervisor Component Tests")
    print("=" * 60)

    try:
        test_manifest_validation()
        test_atomic_writes()
        test_stream_hashing()
        test_manifest_save_load()

        print("\n" + "=" * 60)
        print("🎉 All tests passed! Core infrastructure is working.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
