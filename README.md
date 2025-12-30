# Huffman Coding

A lossless data compression tool implementing the Huffman coding algorithm in C with a Python GUI frontend.

## Features

- **Command-line interface** for compression and decompression
- **Python GUI** for easy access
- **Efficient implementation** using priority queues and binary trees
- **Canonical Huffman encoding** for compact file headers

## Project Structure

```
huffman-coding/
├── include/          # Header files
├── src/              # C source files
│   ├── main.c        # CLI entry point
│   ├── huffman.c     # Core compression/decompression logic
│   └── minheap.c     # Min-heap (priority queue) implementation
├── releases/         # Compiled binaries
├── gui.py            # Python GUI frontend
├── Makefile          # Build configuration
```

## Building

### Prerequisites

- **GCC** (MinGW on Windows) or any C11-compatible compiler
- **Make** (or `mingw32-make` on Windows)
- **Python 3.8+** (optional, for GUI)

### Compile

```bash
# Linux/macOS
make

# Windows (with MinGW)
mingw32-make
```

The executable `huffman` (or `huffman.exe` on Windows) will be created in the project root.

## Usage

### Command Line

```bash
# Compress a file
./huffman compress input.txt output.bin

# Decompress a file
./huffman decompress output.bin restored.txt
```

## How It Works

1. **Frequency Analysis**: Count occurrences of each byte in the input
2. **Tree Construction**: Build a Huffman tree using a min-heap (greedy algorithm)
3. **Code Generation**: Assign variable-length binary codes (shorter for frequent symbols)
4. **Encoding**: Replace symbols with their Huffman codes and write to output
5. **Decoding**: Reconstruct data by traversing the Huffman tree bit-by-bit

## File Format

Compressed files contain:
- Header with tree structure or canonical code lengths
- Encoded bitstream
- Padding information for the last byte

## Performance

- **Time Complexity**: O(n log n) for tree building, O(n) for encoding/decoding
- **Space**: Overhead depends on alphabet size (typically small for 256-byte alphabet)
- **Best Results**: Text files, structured data with skewed symbol distributions
- **Poor Results**: Already compressed files (ZIP, JPEG), encrypted data, random data

## Acknowledgments

Based on the Huffman coding algorithm developed by David A. Huffman in 1952.