#!/usr/bin/env python3
"""
Debounced async file writer to prevent thousands of concurrent write tasks.
Batches writes and schedules them with a delay to reduce I/O overhead.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any
import aiofiles
import time


class DebouncedWriter:
    """
    Batches JSON writes with debouncing to prevent overwhelming the event loop.

    Instead of creating thousands of individual asyncio tasks for progress updates,
    this batches writes and schedules them with a delay.
    """

    def __init__(self, debounce_ms: int = 250):
        self.debounce_ms = debounce_ms
        self.pending_writes: Dict[Path, Dict[str, Any]] = {}
        self.last_write_times: Dict[Path, float] = {}
        self.write_tasks: Dict[Path, asyncio.Task] = {}
        self.lock = asyncio.Lock()

    async def write_delayed(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Schedule a delayed write (debounced)."""
        file_path = Path(file_path)

        async with self.lock:
            # Update pending data
            self.pending_writes[file_path] = data.copy()
            current_time = time.time()

            # Cancel existing delayed write if one is pending and not already complete
            if file_path in self.write_tasks and not self.write_tasks[file_path].done():
                self.write_tasks[file_path].cancel()

            # Check if we should write immediately (debounce time elapsed)
            last_write = self.last_write_times.get(file_path, 0)
            time_since_last = current_time - last_write

            if time_since_last >= (self.debounce_ms / 1000.0):
                # Write immediately
                await self._write_now(file_path, data)
            else:
                # Schedule delayed write
                delay = max(0.001, (self.debounce_ms / 1000.0) - time_since_last)
                self.write_tasks[file_path] = asyncio.create_task(
                    self._write_after_delay(file_path, delay)
                )

    async def flush_all(self) -> None:
        """Flush all pending writes immediately."""
        async with self.lock:
            # Cancel all pending tasks
            for task in self.write_tasks.values():
                if not task.done():
                    task.cancel()

            # Write all pending data immediately
            for file_path, data in self.pending_writes.items():
                try:
                    await self._write_now(file_path, data)
                except Exception:
                    pass  # Continue with other files

            # Clear state
            self.pending_writes.clear()
            self.write_tasks.clear()

    async def _write_after_delay(self, file_path: Path, delay: float) -> None:
        """Write after delay (for debouncing)."""
        try:
            await asyncio.sleep(delay)

            async with self.lock:
                if file_path in self.pending_writes:
                    data = self.pending_writes[file_path]
                    await self._write_now(file_path, data)
                    self.pending_writes.pop(file_path, None)

        except asyncio.CancelledError:
            # Task was cancelled due to new write - this is expected behavior
            pass
        except Exception as e:
            print(f"Warning: Debounced write failed for {file_path}: {e}")

    async def _write_now(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Write data immediately."""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write atomically
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))

            self.last_write_times[file_path] = time.time()

        except Exception as e:
            print(f"Warning: Failed to write {file_path}: {e}")
            # Don't re-raise - this should not break the main processing


# Global debounced writer instance
debounced_writer = DebouncedWriter(debounce_ms=500)  # 500ms debounce
