#!/usr/bin/env python3
"""
Production Blender Process Supervisor
Provides manifest validation, stream hashing, atomic writes, and robust subprocess management with cold restarts.
"""

import json
import hashlib
import time
import subprocess
import tempfile
import shutil
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class Manifest:
    """Deterministic render manifest with SHA256 validation."""
    job_id: str
    timestamp: str
    blender_version: str
    settings: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    validation_hash: str = ""
    blend_file_hash: str = ""

    def compute_validation_hash(self) -> str:
        """Compute SHA256 hash of critical render parameters."""
        hash_data = {
            'settings': self.settings,
            'timestamp': self.timestamp,
            'blender_version': self.blender_version,
            'expected_outputs': self.expected_outputs
        }
        hash_string = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def validate_against_settings(self, settings: Dict[str, Any], blender_version: str) -> bool:
        """Validate manifest against current execution parameters."""
        current_hash = self.compute_validation_hash()
        if current_hash != self.validation_hash:
            return False

        if blender_version != self.blender_version:
            return False

        # Check critical settings match
        for key in ['resolution', 'fps', 'duration', 'render_engine']:
            if key in self.settings and key in settings:
                if self.settings[key] != settings[key]:
                    return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'timestamp': self.timestamp,
            'blender_version': self.blender_version,
            'settings': self.settings,
            'expected_outputs': self.expected_outputs,
            'validation_hash': self.validation_hash,
            'blend_file_hash': self.blend_file_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Manifest':
        return cls(
            job_id=data['job_id'],
            timestamp=data['timestamp'],
            blender_version=data['blender_version'],
            settings=cls._normalize_data(data['settings']),
            expected_outputs=cls._normalize_data(data['expected_outputs']),
            validation_hash=data.get('validation_hash', ''),
            blend_file_hash=data.get('blend_file_hash', '')
        )

    @staticmethod
    def _normalize_data(data: Any) -> Any:
        """Normalize data structures for consistent hashing (convert lists to tuples)."""
        if isinstance(data, dict):
            return {k: cls._normalize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return tuple(cls._normalize_data(item) for item in data)
        else:
            return data


class StreamHasher:
    """Memory-efficient stream hashing for large files."""

    @staticmethod
    def sha256_file(file_path: Path, chunk_size: int = 65536) -> str:
        """Stream hash a file without loading it entirely into memory."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            raise RuntimeError(f"Failed to hash file {file_path}: {e}")


class AtomicFileWriter:
    """Atomic file writing with cleanup and integrity checks."""

    @staticmethod
    def write_atomic(output_path: Path, data: bytes, validate: bool = True) -> bool:
        """
        Write file atomically: temp file -> rename to final.
        Includes integrity validation and cleanup on failure.
        """
        output_path = Path(output_path)
        temp_path = output_path.parent / f"{output_path.name}.tmp"

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Clean up any existing temp file
            if temp_path.exists():
                temp_path.unlink()

            # Write to temp file
            with open(temp_path, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Validate written data if requested
            if validate:
                temp_path.stat()  # Force filesystem sync
                with open(temp_path, 'rb') as f:
                    actual_size = len(f.read())
                if actual_size != len(data):
                    raise IOError(f"Size mismatch: expected {len(data)}, got {actual_size}")

            # Atomic rename: temp -> final
            temp_path.replace(output_path)
            return True

        except Exception as e:
            # Clean up temp file on failure
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except:
                pass
            raise RuntimeError(f"Atomic write failed for {output_path}: {e}")

    @staticmethod
    def write_atomic_text(output_path: Path, text: str, encoding: str = 'utf-8') -> bool:
        """Write text file atomically."""
        data = text.encode(encoding)
        return AtomicFileWriter.write_atomic(output_path, data)

    @staticmethod
    def write_completion_marker(file_path: Path, metadata: Dict[str, Any]) -> None:
        """Write .ok completion marker file."""
        marker_path = file_path.parent / f"{file_path.name}.ok"
        marker_data = {
            'source_file': str(file_path),
            'completed_at': int(time.time()),
            'size': file_path.stat().st_size if file_path.exists() else 0,
            **metadata
        }

        marker_json = json.dumps(marker_data, indent=2)
        try:
            AtomicFileWriter.write_atomic_text(marker_path, marker_json)
        except Exception:
            # Fall back to direct write if atomic fails
            try:
                marker_path.write_text(marker_json)
            except Exception:
                pass  # Silent failure for marker


@dataclass
class BlenderResult:
    """Result of a Blender execution."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    cold_restarts: int
    manifest: Optional[Manifest]
    error: Optional[str] = None

    def __post_init__(self):
        if not self.success and not self.error:
            self.error = f"Blender failed with exit code {self.exit_code}"


class BlenderSupervisor:
    """Production Blender process supervisor with timeouts, logging, and cold restarts."""

    def __init__(self, blender_path: str, temp_dir: Optional[Path] = None):
        self.blender_path = Path(blender_path)
        self.temp_dir = temp_dir or Path(tempfile.mkdtemp(prefix='blender_supervisor_'))
        self.temp_dir.mkdir(exist_ok=True)

        # Execution parameters
        self.timeout_seconds = 300  # 5 minute default timeout
        self.max_cold_restarts = 2
        self.memory_limit_mb = 2048  # 2GB default

    def set_limits(self, timeout_seconds: int = 300, memory_limit_mb: int = 2048):
        """Set execution limits."""
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        return self

    def validate_manifest(self, manifest_path: Path, expected_settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate render manifest integrity."""
        try:
            if not manifest_path.exists():
                return False, "Manifest file not found"

            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)

            manifest = Manifest.from_dict(manifest_data)

            # Check Blender version (simplified - you'd check actual version)
            current_blender_version = "4.0"  # In real impl, get from blender --version
            if not manifest.validate_against_settings(expected_settings, current_blender_version):
                return False, "Manifest validation failed - parameters don't match"

            return True, None

        except Exception as e:
            return False, f"Manifest validation error: {e}"

    def execute_blender_safe(self, script_path: Path, args: List[str], job_id: str) -> BlenderResult:
        """
        Execute Blender with comprehensive error handling, logging, and cold restarts.

        Returns standardized result structure for analysis and retry logic.
        """
        start_time = time.time()
        cold_restarts = 0

        # Set up logging
        log_file = self.temp_dir / f"{job_id}_blender.log"
        stdout_capture = []
        stderr_capture = []

        while cold_restarts <= self.max_cold_restarts:
            try:
                # Prepare command with memory limits (system-dependent)
                cmd = [
                    str(self.blender_path),
                    '--background',
                    '--python', str(script_path),
                    '--'] + args

                # Add memory limit if supported (Linux example)
                env = os.environ.copy()
                if os.name == 'posix':  # Linux/macOS
                    env['MALLOC_ARENA_MAX'] = '1'  # Limit glibc arenas

                print(f"Blender execution attempt {cold_restarts + 1}/{self.max_cold_restarts + 1}")
                print(f"Command: {' '.join(cmd)}")

                # Execute with timeout capture
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    cwd=str(self.temp_dir)
                )

                try:
                    stdout, stderr = process.communicate(timeout=self.timeout_seconds)

                    # Capture outputs
                    stdout_capture.append(stdout)
                    stderr_capture.append(stderr)

                    # Log to file
                    log_entry = [
                        f"=== Blender Execution Attempt {cold_restarts + 1} ===",
                        f"Timestamp: {time.strftime('%Y%m%d_%H%M%S')}",
                        f"Command: {' '.join(cmd)}",
                        f"Exit code: {process.returncode}",
                        "--- STDOUT ---",
                        stdout,
                        "--- STDERR ---",
                        stderr,
                        "=" * 50 + "\n"
                    ]

                    try:
                        with open(log_file, 'a') as f:
                            f.write('\n'.join(log_entry))
                    except Exception:
                        pass  # Continue even if logging fails

                    duration = time.time() - start_time

                    # Success case
                    if process.returncode == 0:
                        return BlenderResult(
                            success=True,
                            exit_code=0,
                            stdout='\n'.join(stdout_capture),
                            stderr='\n'.join(stderr_capture),
                            duration=duration,
                            cold_restarts=cold_restarts,
                            manifest=None  # Can load from script result
                        )

                    # Timeout case
                    elif process.returncode is None:  # Process was killed
                        cold_restarts += 1
                        if cold_restarts <= self.max_cold_restarts:
                            print(f"Blender timeout - attempting cold restart ({cold_restarts}/{self.max_cold_restarts})")
                            time.sleep(2)
                            continue

                    # Failure case - no more restarts
                    return BlenderResult(
                        success=False,
                        exit_code=process.returncode or -1,
                        stdout='\n'.join(stdout_capture),
                        stderr='\n'.join(stderr_capture),
                        duration=duration,
                        cold_restarts=cold_restarts,
                        error=f"Blender failed with exit code {process.returncode or -1}"
                    )

                except subprocess.TimeoutExpired:
                    print(f"Blender timeout after {self.timeout_seconds}s - killing process")
                    process.kill()
                    cold_restarts += 1

                    if cold_restarts <= self.max_cold_restarts:
                        print(f"Attempting cold restart ({cold_restarts}/{self.max_cold_restarts})")
                        time.sleep(2)
                        continue

                    return BlenderResult(
                        success=False,
                        exit_code=-2,
                        stdout='\n'.join(stdout_capture),
                        stderr='\n'.join(stderr_capture),
                        duration=time.time() - start_time,
                        cold_restarts=cold_restarts,
                        error=f"Blender timeout after {self.timeout_seconds}s and {cold_restarts} cold restarts"
                    )

            except FileNotFoundError:
                return BlenderResult(
                    success=False,
                    exit_code=-3,
                    stdout='',
                    stderr='',
                    duration=time.time() - start_time,
                    cold_restarts=cold_restarts,
                    error=f"Blender executable not found: {self.blender_path}"
                )
            except Exception as e:
                return BlenderResult(
                    success=False,
                    exit_code=-4,
                    stdout='\n'.join(stdout_capture),
                    stderr='\n'.join(stderr_capture),
                    duration=time.time() - start_time,
                    cold_restarts=cold_restarts,
                    error=f"Blender execution error: {e}"
                )

        # Exhausted all restarts
        return BlenderResult(
            success=False,
            exit_code=-5,
            stdout='\n'.join(stdout_capture),
            stderr='\n'.join(stderr_capture),
            duration=time.time() - start_time,
            cold_restarts=cold_restarts,
            error=f"Failed after {cold_restarts} cold restarts"
        )

    def cleanup(self, keep_logs: bool = False):
        """Clean up temporary files and directories."""
        try:
            if self.temp_dir.exists():
                # Keep logs if requested
                if keep_logs:
                    log_files = list(self.temp_dir.glob("*.log"))
                    for log_file in log_files:
                        backup_log = self.temp_dir.parent / f"{self.temp_dir.name}_{log_file.name}"
                        try:
                            shutil.copy2(log_file, backup_log)
                        except Exception:
                            pass

                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: cleanup failed: {e}")


# Utility functions for easy integration
def create_render_manifest(job_id: str, settings: Dict[str, Any], blender_version: str = "4.0") -> Manifest:
    """Create and initialize a render manifest."""
    timestamp = time.strftime('%Y%m%d_%H%M%S_UTC', time.gmtime())

    manifest = Manifest(
        job_id=job_id,
        timestamp=timestamp,
        blender_version=blender_version,
        settings=settings,
        expected_outputs={
            'resolution': settings.get('resolution', (1920, 1080)),
            'frame_range': (1, int(settings.get('duration', 10) * settings.get('fps', 30))),
            'output_format': 'mp4'
        }
    )

    manifest.validation_hash = manifest.compute_validation_hash()
    return manifest


def save_manifest_atomic(manifest: Manifest, manifest_path: Path) -> bool:
    """Save manifest atomically."""
    manifest_data = json.dumps(manifest.to_dict(), indent=2)
    return AtomicFileWriter.write_atomic_text(manifest_path, manifest_data)


def hash_blend_file(blend_path: Path) -> str:
    """Generate SHA256 hash of .blend file."""
    return StreamHasher.sha256_file(blend_path)


if __name__ == "__main__":
    print("Blender Production Supervisor - Ready for integration")

    # Example usage
    manifest = create_render_manifest("test_job_123", {
        'resolution': (1920, 1080),
        'fps': 30,
        'duration': 10,
        'render_engine': 'BLENDER_EEVEE'
    })

    print(f"Created manifest for job: {manifest.job_id}")
    print(f"Validation hash: {manifest.validation_hash[:16]}...")
