"""
Parallel Word Count Application
Beginner-friendly demonstration of sequential and parallel processing.

Usage:
    python main.py data/sample.txt
    python main.py data/sample.txt --workers 4
    python main.py data/sample.txt --workers 4 --generate-mb 10

Notes:
- The program counts whitespace-separated tokens (words).
- Input is split by complete lines, so words are not split across chunks.
- For fair timing, file reading and task setup are included in each approach.
- Parallel execution may be slower for small files due to process overhead.
"""

from __future__ import annotations

import argparse
import multiprocessing
import os
import re
import time
from pathlib import Path
from typing import Iterable


WORD_PATTERN = re.compile(r"\b[\w]+(?:['’-][\w]+)*\b", re.UNICODE)


def count_words(text: str) -> int:
    """Count word-like tokens in text."""
    return len(WORD_PATTERN.findall(text))


def count_lines(lines: list[str]) -> int:
    """Count words in a list of complete lines; suitable for worker processes."""
    return sum(count_words(line) for line in lines)


def read_lines(file_path: Path) -> list[str]:
    """Read a UTF-8 text file, replacing undecodable bytes if necessary."""
    with file_path.open("r", encoding="utf-8", errors="replace") as file:
        return file.readlines()


def split_into_chunks(items: list[str], chunk_count: int) -> list[list[str]]:
    """Split a list into at most chunk_count balanced, non-empty chunks."""
    if not items:
        return []
    chunk_count = max(1, min(chunk_count, len(items)))
    base_size, remainder = divmod(len(items), chunk_count)
    chunks = []
    start = 0
    for i in range(chunk_count):
        size = base_size + (1 if i < remainder else 0)
        chunks.append(items[start:start + size])
        start += size
    return chunks


def sequential_count(file_path: Path) -> tuple[int, float]:
    """Count all words in one process and return (count, seconds)."""
    start = time.perf_counter()
    lines = read_lines(file_path)
    total = count_lines(lines)
    elapsed = time.perf_counter() - start
    return total, elapsed


def parallel_count(file_path: Path, workers: int) -> tuple[int, float, int]:
    """Count words using multiple worker processes and return (count, seconds)."""
    start = time.perf_counter()
    lines = read_lines(file_path)
    if not lines:
        return 0, time.perf_counter() - start, 0

    worker_count = max(1, min(workers, os.cpu_count() or workers, len(lines)))
    chunks = split_into_chunks(lines, worker_count)

    # The context manager ensures worker processes are cleaned up.
    with multiprocessing.Pool(processes=worker_count) as pool:
        partial_counts = pool.map(count_lines, chunks)

    total = sum(partial_counts)
    elapsed = time.perf_counter() - start
    return total, elapsed, worker_count


def generate_sample_file(path: Path, size_mb: float) -> None:
    """Generate a repeatable text file of approximately the requested size."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = (
        "Parallel computing divides work among workers. "
        "This sample sentence is used to benchmark word counting. "
        "Python multiprocessing can run tasks in separate processes.\n"
    )
    target_bytes = max(1, int(size_mb * 1024 * 1024))
    with path.open("w", encoding="utf-8") as file:
        written = 0
        while written < target_bytes:
            file.write(line)
            written += len(line.encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare sequential and parallel word counting."
    )
    parser.add_argument("file", type=Path, help="Path to a UTF-8 text file")
    parser.add_argument(
        "--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)),
        help="Maximum number of worker processes (default: up to 4)"
    )
    parser.add_argument(
        "--generate-mb", type=float, default=0,
        help="Generate a sample input file of approximately this size before running"
    )
    args = parser.parse_args()

    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if args.generate_mb < 0:
        parser.error("--generate-mb cannot be negative")

    if args.generate_mb > 0:
        generate_sample_file(args.file, args.generate_mb)
        print(f"Generated sample file: {args.file} (~{args.generate_mb:g} MB)")

    if not args.file.exists() or not args.file.is_file():
        parser.error(f"Input file does not exist or is not a file: {args.file}")

    print("=" * 48)
    print("       PARALLEL WORD COUNT APPLICATION")
    print("=" * 48)
    print(f"Input file: {args.file}")
    print(f"File size: {args.file.stat().st_size / (1024 * 1024):.2f} MB")
    print()

    sequential_total, sequential_seconds = sequential_count(args.file)
    parallel_total, parallel_seconds, actual_workers = parallel_count(args.file, args.workers)

    print("Sequential Processing")
    print("-" * 24)
    print(f"Total words: {sequential_total:,}")
    print(f"Execution time: {sequential_seconds:.6f} seconds")
    print()

    print("Parallel Processing")
    print("-" * 24)
    print(f"Requested workers: {args.workers}")
    print(f"Total words: {parallel_total:,}")
    print(f"Execution time: {parallel_seconds:.6f} seconds")
    print()

    print("Performance Analysis")
    print("-" * 24)
    print(f"Results match: {'Yes' if sequential_total == parallel_total else 'NO'}")

    if parallel_seconds > 0:
        speedup = sequential_seconds / parallel_seconds
        efficiency = (speedup / max(1, args.workers) * 100
        if actual_workers > 0 else 0)

        print(f"Speedup: {speedup:.3f}x")
        print(f"Actual workers used: {actual_workers}")
        print(f"Parallel efficiency (requested workers): {efficiency:.2f}%")
    else:
        print("Speedup: unavailable (measured parallel time was zero)")

    if sequential_total != parallel_total:
        raise SystemExit("ERROR: sequential and parallel word counts do not match.")

    print()
    print("Note: small files may run slower in parallel because of process overhead.")


if __name__ == "__main__":
    # Required for safe multiprocessing startup on Windows.
    multiprocessing.freeze_support()
    main()
