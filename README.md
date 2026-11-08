# Parallel Word Count Application (Python)

## Project overview

This project compares sequential word counting with parallel word counting using Python's `multiprocessing` module.

## Requirements
- Python 3.9 or later recommended
- No third-party packages required

## Run the program
From this folder:

```bash
python main.py data/sample.txt
python main.py data/sample.txt --workers 4
python main.py data/benchmark_10mb.txt --workers 4 --generate-mb 10
python main.py data/benchmark_50mb.txt --workers 4 --generate-mb 50
```

## Run tests
```bash
python -m unittest discover -s tests -v
```

## How it works
1. Read the text file into lines.
2. Sequential mode counts words in one process.
3. Parallel mode splits complete lines into balanced chunks.
4. A process pool counts each chunk concurrently.
5. Partial counts are added together.
6. The program compares counts and calculates performance metrics.

## Metrics
- Execution time: elapsed wall-clock time measured with `time.perf_counter()`.
- Speedup: sequential execution time / parallel execution time.
- Approximate parallel efficiency:** speedup / requested worker count × 100%.

Efficiency is approximate because the program may cap actual workers based on CPU count and available lines. For a final report, record the actual machine, Python version, input file size, and requested worker count. Repeat each experiment several times and compare median times if possible.

## Important limitation
The program reads all lines into memory, and process startup/data transfer have overhead. Results depend on file size, CPU, operating system, and worker count. A parallel run is not guaranteed to be faster.

## Suggested repository structure
- `main.py` — application
- `tests/test_main.py` — unit tests
- `data/sample.txt` — small test input
