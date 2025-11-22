#!/usr/bin/env python3
"""
Structured logging for render jobs with proper JSON output and log levels.
Provides observability for debugging render job failures and performance issues.
"""

import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class StructuredLogger:
    """Structured JSON logger for render job observability."""

    def __init__(self, job_id: str, log_file: Optional[Path] = None):
        self.job_id = job_id
        self.log_file = log_file
        self.start_time = time.time()

    def _format_log(self, level: str, message: str, extra_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format log entry as structured JSON."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "job_id": self.job_id,
            "message": message,
            "elapsed_seconds": time.time() - self.start_time
        }

        if extra_data:
            log_entry.update(extra_data)

        return log_entry

    def _write_log(self, log_entry: Dict[str, Any]) -> None:
        """Write log entry to both stdout and file if configured."""
        # JSON output to stdout (for log aggregation)
        json_line = json.dumps(log_entry, default=str)
        print(json_line, file=sys.stdout, flush=True)

        # Also write to file if configured (human readable)
        if self.log_file:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    timestamp = log_entry['timestamp']
                    level = log_entry['level']
                    msg = log_entry['message']
                    elapsed = ".1f"
                    f.write(f"[{timestamp}] [{level}] {msg} (elapsed: {elapsed}s)\n")
                    f.flush()
            except Exception:
                # Don't let logging failures break the app
                pass

    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log info level message."""
        self._write_log(self._format_log("INFO", message, extra_data))

    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log warning level message."""
        self._write_log(self._format_log("WARNING", message, extra_data))

    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log error level message."""
        self._write_log(self._format_log("ERROR", message, extra_data))

    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log debug level message."""
        self._write_log(self._format_log("DEBUG", message, extra_data))

    def frame_progress(self, frame_num: int, total_frames: int, render_time_ms: Optional[int] = None) -> None:
        """Log frame rendering progress."""
        extra_data = {
            "frame_num": frame_num,
            "total_frames": total_frames,
            "progress_percent": (frame_num / total_frames) * 100 if total_frames > 0 else 0
        }
        if render_time_ms is not None:
            extra_data["render_time_ms"] = render_time_ms

        self.info(f"Rendered frame {frame_num}/{total_frames}", extra_data)

    def phase_complete(self, phase: str, duration_seconds: float, success: bool = True) -> None:
        """Log phase completion."""
        extra_data = {
            "phase": phase,
            "duration_seconds": duration_seconds,
            "success": success
        }

        level = "INFO" if success else "ERROR"
        status = "completed" if success else "failed"
        message = f"Phase '{phase}' {status} in {duration_seconds:.1f}s"

        self._write_log(self._format_log(level, message, extra_data))

    def job_complete(self, total_duration: float, success: bool, frames_rendered: int = 0) -> None:
        """Log final job completion."""
        extra_data = {
            "total_duration_seconds": total_duration,
            "success": success,
            "frames_rendered": frames_rendered,
            "average_fps": frames_rendered / total_duration if total_duration > 0 else 0
        }

        level = "INFO" if success else "ERROR"
        status = "succeeded" if success else "failed"
        message = f"Job {status} in {total_duration:.1f}s (rendered {frames_rendered} frames)"

        self._write_log(self._format_log(level, message, extra_data))

    def error_recovery(self, operation: str, attempt: int, max_attempts: int, error: str) -> None:
        """Log error recovery attempts."""
        extra_data = {
            "operation": operation,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "error": error
        }

        self.warning(f"Error recovery: {operation} attempt {attempt}/{max_attempts}: {error}", extra_data)

    def resource_usage(self, operation: str, bytes_used: int, duration_seconds: float) -> None:
        """Log resource usage statistics."""
        extra_data = {
            "operation": operation,
            "bytes_used": bytes_used,
            "duration_seconds": duration_seconds,
            "bytes_per_second": bytes_used / duration_seconds if duration_seconds > 0 else 0
        }

        self.info(f"Resource usage: {operation}", extra_data)
