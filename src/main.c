#include <stdio.h>
#include <string.h>
#include "huffman.h"

int main(int argc, char* argv[]) {
    if (argc != 4) {
        printf("Usage:\n");
        printf("  %s compress <input> <output>\n", argv[0]);
        printf("  %s decompress <input> <output>\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "compress") == 0)
        compressFile(argv[2], argv[3]);
    else if (strcmp(argv[1], "decompress") == 0)
        decompressFile(argv[2], argv[3]);
    else
        printf("Invalid option\n");

    return 0;
}

