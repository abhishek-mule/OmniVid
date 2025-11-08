"""
Test Script for RemotionAdapter

Comprehensive tests for validating end-to-end rendering functionality.
"""

import sys
from pathlib import Path
from base_engine import RenderConfig, RenderStatus
from remotion_adapter import RemotionAdapter


def test_environment_validation():
    """Test environment validation."""
    print("\n=== Test 1: Environment Validation ===")
    
    adapter = RemotionAdapter(
        remotion_root="./remotion_project",  # Update with your path
        composition_id="MyComposition"
    )
    
    validation = adapter.validate_environment()
    print(f"Valid: {validation['valid']}")
    print(f"Issues: {validation['issues']}")
    print(f"Version: {validation['version']}")
    
    return validation['valid']


def test_adapter_initialization():
    """Test adapter initialization."""
    print("\n=== Test 2: Adapter Initialization ===")
    
    adapter = RemotionAdapter(
        remotion_root="./remotion_project",  # Update with your path
        composition_id="MyComposition"
    )
    
    success = adapter.initialize()
    print(f"Initialized: {success}")
    print(f"Is Initialized: {adapter.is_initialized()}")
    print(f"Engine Type: {adapter.get_engine_type()}")
    
    return success, adapter


def test_asset_management(adapter):
    """Test asset management."""
    print("\n=== Test 3: Asset Management ===")
    
    # Test with a sample asset (create a dummy file if needed)
    test_asset_path = "./test_assets/sample.png"  # Update with actual path
    
    try:
        asset_id = adapter.add_asset(
            asset_path=test_asset_path,
            asset_type="image"
        )
        
        if asset_id:
            print(f"Asset added successfully: {asset_id}")
            return True
        else:
            print("Failed to add asset (file may not exist)")
            return False
    except Exception as e:
        print(f"Asset test skipped: {str(e)}")
        return False


def test_scene_configuration(adapter):
    """Test scene configuration."""
    print("\n=== Test 4: Scene Configuration ===")
    
    scene_config = {
        "id": "scene_1",
        "name": "Intro Scene",
        "duration": 5.0,
        "layers": [
            {"type": "text", "content": "Hello OMNIVID"},
            {"type": "background", "color": "#000000"}
        ],
        "transitions": {
            "in": "fade",
            "out": "fade"
        }
    }
    
    scene_id = adapter.add_scene(scene_config)
    print(f"Scene added: {scene_id}")
    
    return bool(scene_id)


def test_effects_and_animations(adapter):
    """Test effects and animations."""
    print("\n=== Test 5: Effects and Animations ===")
    
    # Add a dummy scene first
    scene_id = adapter.add_scene({"id": "test_scene", "name": "Test", "duration": 3.0})
    
    # Test effect
    effect_success = adapter.apply_effect(
        target_id=scene_id,
        effect_type="blur",
        intensity=0.5
    )
    print(f"Effect applied: {effect_success}")
    
    # Test animation
    animation_config = {
        "property": "opacity",
        "start_value": 0,
        "end_value": 1,
        "duration": 2.0,
        "easing": "easeInOut"
    }
    
    animation_success = adapter.animate(
        target_id=scene_id,
        animation_config=animation_config
    )
    print(f"Animation added: {animation_success}")
    
    return effect_success and animation_success


def test_render_configuration():
    """Test render configuration validation."""
    print("\n=== Test 6: Render Configuration ===")
    
    adapter = RemotionAdapter(
        remotion_root="./remotion_project",
        composition_id="MyComposition"
    )
    
    # Valid config
    valid_config = RenderConfig(
        output_path="./output/test_video.mp4",
        width=1920,
        height=1080,
        fps=30,
        quality="high"
    )
    
    is_valid = adapter.validate_config(valid_config)
    print(f"Valid config: {is_valid}")
    
    # Invalid config (negative dimensions)
    invalid_config = RenderConfig(
        output_path="./output/test_video.mp4",
        width=-1920,
        height=1080,
        fps=30
    )
    
    is_invalid = not adapter.validate_config(invalid_config)
    print(f"Invalid config rejected: {is_invalid}")
    
    return is_valid and is_invalid


def test_full_render(adapter):
    """Test full render process."""
    print("\n=== Test 7: Full Render (DRY RUN) ===")
    print("NOTE: This test requires a valid Remotion project setup")
    
    # Create output directory
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    config = RenderConfig(
        output_path="./output/test_render.mp4",
        width=1280,
        height=720,
        fps=30,
        quality="medium",
        additional_params={"timeout": 120}
    )
    
    print(f"Output path: {config.output_path}")
    print(f"Resolution: {config.width}x{config.height}")
    print(f"FPS: {config.fps}")
    print(f"Quality: {config.quality}")
    
    try:
        print("\nAttempting render...")
        result = adapter.render(config)
        
        print(f"Render status: {result.status.value}")
        
        if result.status == RenderStatus.COMPLETED:
            print(f"✓ Render successful!")
            print(f"Output: {result.output_path}")
            return True
        else:
            print(f"✗ Render failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"✗ Render error: {str(e)}")
        return False


def test_export_import(adapter):
    """Test project export and import."""
    print("\n=== Test 8: Project Export/Import ===")
    
    export_path = "./test_project_export.json"
    
    # Export
    export_success = adapter.export_project(export_path)
    print(f"Export successful: {export_success}")
    
    if export_success:
        # Import
        import_data = adapter.import_project(export_path)
        import_success = import_data is not None
        print(f"Import successful: {import_success}")
        
        # Cleanup
        Path(export_path).unlink(missing_ok=True)
        
        return export_success and import_success
    
    return False


def test_supported_formats(adapter):
    """Test supported formats and codecs."""
    print("\n=== Test 9: Supported Formats ===")
    
    formats = adapter.get_supported_formats()
    print(f"Supported formats: {', '.join(formats)}")
    
    codecs = adapter.get_supported_codecs()
    print(f"Supported codecs: {', '.join(codecs)}")
    
    return len(formats) > 0 and len(codecs) > 0


def test_cleanup(adapter):
    """Test cleanup."""
    print("\n=== Test 10: Cleanup ===")
    
    cleanup_success = adapter.cleanup()
    print(f"Cleanup successful: {cleanup_success}")
    print(f"Is initialized after cleanup: {adapter.is_initialized()}")
    
    return cleanup_success and not adapter.is_initialized()


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("OMNIVID RemotionAdapter Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Environment Validation
    results['environment'] = test_environment_validation()
    
    # Test 2: Initialization
    init_success, adapter = test_adapter_initialization()
    results['initialization'] = init_success
    
    if not init_success:
        print("\n❌ Initialization failed. Skipping remaining tests.")
        print("\nMake sure you have:")
        print("1. Node.js installed")
        print("2. A Remotion project in ./remotion_project")
        print("3. Updated the paths in this test script")
        return results
    
    # Test 3: Asset Management
    results['assets'] = test_asset_management(adapter)
    
    # Test 4: Scene Configuration
    results['scenes'] = test_scene_configuration(adapter)
    
    # Test 5: Effects and Animations
    results['effects'] = test_effects_and_animations(adapter)
    
    # Test 6: Configuration Validation
    results['config_validation'] = test_render_configuration()
    
    # Test 7: Full Render (if environment is ready)
    print("\nDo you want to test actual rendering? (y/n): ", end="")
    try:
        user_input = input().strip().lower()
        if user_input == 'y':
            results['full_render'] = test_full_render(adapter)
        else:
            print("Skipping full render test")
            results['full_render'] = None
    except:
        print("Skipping full render test")
        results['full_render'] = None
    
    # Test 8: Export/Import
    results['export_import'] = test_export_import(adapter)
    
    # Test 9: Supported Formats
    results['formats'] = test_supported_formats(adapter)
    
    # Test 10: Cleanup
    results['cleanup'] = test_cleanup(adapter)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "⊘ SKIPPED"
        elif result:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    print("\n🎬 Starting RemotionAdapter Tests...\n")
    
    try:
        results = run_all_tests()
        
        # Exit with error code if any tests failed
        failed_count = sum(1 for r in results.values() if r is False)
        sys.exit(0 if failed_count == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
