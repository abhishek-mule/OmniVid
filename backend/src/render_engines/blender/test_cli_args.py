#!/usr/bin/env python3
"""
Smoke test for CLI argument parsing logic in Blender templates.
Tests various argument patterns that Blender might receive.
"""

import sys
import os
from pathlib import Path

def test_blender_arg_parsing_all_patterns():
    """Test the CLI argument parsing logic from the Blender templates."""

    print("🔥 SMOKE TEST: Blender CLI Argument Parsing")
    print("=" * 50)

    # The argument parsing logic from create_scene_data_api.py
    def parse_blender_args(args):
        """Reproduction of the logic from create_scene_data_api.py"""
        script_args_start = 0
        for i, arg in enumerate(args):
            if arg == '--':
                script_args_start = i + 1
                break
        else:
            script_args_start = len([arg for arg in args if not arg.startswith('-')])

        if len(args) < script_args_start + 2:
            print("Usage: blender --background --python script.py -- <settings.json> <output.blend>", file=sys.stderr)
            return None

        settings_path = args[script_args_start]
        blend_path = args[script_args_start + 1]
        return settings_path, blend_path

    # Test cases covering different Blender invocation patterns
    test_cases = [
        {
            "name": "Standard with -- separator",
            "args": ["blender", "--background", "--python", "create_scene.py", "--", "settings.json", "output.blend"],
            "expected": ("settings.json", "output.blend")
        },
        {
            "name": "Direct script execution",
            "args": ["blender", "--background", "create_scene.py", "settings.json", "output.blend"],
            "expected": ("settings.json", "output.blend")
        },
        {
            "name": "With extra Blender flags before --",
            "args": ["blender", "--background", "--factory-startup", "--python", "create_scene.py", "--", "settings.json", "output.blend"],
            "expected": ("settings.json", "output.blend")
        },
        {
            "name": "With GPU flags",
            "args": ["blender", "--background", "--python", "create_scene.py", "settings.json", "output.blend"],
            "expected": ("settings.json", "output.blend")
        },
        {
            "name": "Docker-style invocation",
            "args": ["blender", "--background", "--python", "create_scene.py", "--", "/app/config/settings.json", "/app/output/scene.blend"],
            "expected": ("/app/config/settings.json", "/app/output/scene.blend")
        },
        {
            "name": "CI environment with paths",
            "args": ["blender", "--background", "--python", "create_scene.py", "--", "/workspace/settings/prod.json", "/tmp/output.blend"],
            "expected": ("/workspace/settings/prod.json", "/tmp/output.blend")
        },
        {
            "name": "Windows-style paths",
            "args": ["blender", "--background", "--python", "create_scene.py", "--", "C:\\config\\settings.json", "D:\\output\\scene.blend"],
            "expected": ("C:\\config\\settings.json", "D:\\output\\scene.blend")
        }
    ]

    # Edge cases that should fail
    failure_cases = [
        {
            "name": "Missing arguments",
            "args": ["blender", "--background", "--python", "create_scene.py", "--"],
            "should_fail": True
        },
        {
            "name": "Only one argument",
            "args": ["blender", "--background", "--python", "create_scene.py", "--", "settings.json"],
            "should_fail": True
        },
        {
            "name": "No -- separator and wrong order",
            "args": ["blender", "--background", "settings.json", "--python", "create_scene.py"],
            "should_fail": True
        }
    ]

    all_passed = True

    print("\n✅ VALID PATTERNS:")
    print("-" * 30)

    # Test valid cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Command: {' '.join(test_case['args'])}")

        try:
            result = parse_blender_args(test_case['args'])
            if result == test_case['expected']:
                print(f"   ✅ PASS: settings='{result[0]}', blend='{result[1]}'")
            else:
                print(f"   ❌ FAIL: Expected {test_case['expected']}, got {result}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_passed = False

    print("\n❌ FAILURE CASES (should fail gracefully):")
    print("-" * 45)

    # Test failure cases
    for i, test_case in enumerate(failure_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Command: {' '.join(test_case['args'])}")

        try:
            result = parse_blender_args(test_case['args'])
            if result is None:
                print("   ✅ PASS: Correctly failed with None")
            else:
                print(f"   ❌ FAIL: Should have failed but returned {result}")
                all_passed = False
        except Exception as e:
            print(f"   ✅ PASS: Correctly raised exception: {e}")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED - CLI Argument parsing is solid!")
        return True
    else:
        print("💥 SOME TESTS FAILED - CLI parsing needs fixes")
        return False


def test_render_template_args():
    """Test argument parsing for render template"""
    print("\n🔄 TESTING RENDER TEMPLATE ARGUMENTS")
    print("-" * 40)

    def parse_render_args(args):
        """Logic from render_production.py"""
        if len(sys.argv) < 4:
            print("Usage: render_production.py <settings.json> <blend_file> <output_path>", file=sys.stderr)
            return None

        settings_path = sys.argv[2]
        blend_path = sys.argv[3]
        output_path = sys.argv[4] if len(sys.argv) > 4 else "output.mp4"
        return settings_path, blend_path, output_path

    # Mock sys.argv for different scenarios
    test_cases = [
        {
            "argv": ["render_production.py", "settings.json", "scene.blend", "output.mp4"],
            "expected": ("settings.json", "scene.blend", "output.mp4")
        },
        {
            "argv": ["render_production.py", "config/prod.json", "scenes/job_123.blend", "/outputs/video.mp4"],
            "expected": ("config/prod.json", "scenes/job_123.blend", "/outputs/video.mp4")
        },
        {
            "argv": ["render_production.py", "/tmp/settings.json", "/tmp/scene.blend"],  # Missing output
            "expected": ("/tmp/settings.json", "/tmp/scene.blend", "output.mp4")  # Default
        }
    ]

    all_passed = True
    original_argv = sys.argv.copy()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing render args: {' '.join(test_case['argv'])}")
        sys.argv = test_case['argv']

        try:
            result = parse_render_args(test_case['argv'])
            if result == test_case['expected']:
                print(f"   ✅ PASS: {result}")
            else:
                print(f"   ❌ FAIL: Expected {test_case['expected']}, got {result}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_passed = False

    # Restore original argv
    sys.argv = original_argv

    return all_passed


if __name__ == "__main__":
    print("🚀 Blender CLI Argument Parsing Smoke Test")
    print("Testing argument parsing logic from production templates\n")

    success1 = test_blender_arg_parsing_all_patterns()
    success2 = test_render_template_args()

    print("\n" + "=" * 60)

    if success1 and success2:
        print("🎯 ALL SMOKE TESTS PASSED!")
        print("CLI argument parsing is theoretically sound and ready for real Blender testing.")
        sys.exit(0)
    else:
        print("🚨 SMOKE TESTS FAILED!")
        print("Argument parsing logic needs fixes before deployment.")
        sys.exit(1)
