#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "huffman.h"
#include "minheap.h"

static void storeCodes(struct MinHeapNode* root, int arr[], int top, char* codes[]) {
    if (root->left) {
        arr[top] = 0;
        storeCodes(root->left, arr, top + 1, codes);
    }
    if (root->right) {
        arr[top] = 1;
        storeCodes(root->right, arr, top + 1, codes);
    }
    if (isLeaf(root)) {
        // Handle edge case: single node tree (top == 0)
        // Assign a default code of "0" when there's only one unique character
        if (top == 0) {
            codes[(unsigned char)root->data] = malloc(2);
            codes[(unsigned char)root->data][0] = '0';
            codes[(unsigned char)root->data][1] = '\0';
        } else {
            codes[(unsigned char)root->data] = malloc(top + 1);
            for (int i = 0; i < top; i++)
                codes[(unsigned char)root->data][i] = arr[i] + '0';
            codes[(unsigned char)root->data][top] = '\0';
        }
    }
}

static void writeHeader(FILE* out, int freq[], long originalSize) {
    // Write original file size first (for proper decompression)
    fwrite(&originalSize, sizeof(long), 1, out);
    fwrite(freq, sizeof(int), 256, out);
}

static long readHeader(FILE* in, int freq[]) {
    long originalSize;
    fread(&originalSize, sizeof(long), 1, in);
    fread(freq, sizeof(int), 256, in);
    return originalSize;
}

void compressFile(const char* inputFile, const char* outputFile) {
    FILE* in = fopen(inputFile, "rb");
    if (!in) {
        fprintf(stderr, "Error: Cannot open input file '%s'\n", inputFile);
        return;
    }
    
    FILE* out = fopen(outputFile, "wb");
    if (!out) {
        fprintf(stderr, "Error: Cannot create output file '%s'\n", outputFile);
        fclose(in);
        return;
    }

    // Calculate original file size
    fseek(in, 0, SEEK_END);
    long originalSize = ftell(in);
    rewind(in);

    // Handle empty file case
    if (originalSize == 0) {
        int freq[256] = {0};
        writeHeader(out, freq, 0);
        fclose(in);
        fclose(out);
        return;
    }

    int freq[256] = {0};
    int c;
    while ((c = fgetc(in)) != EOF)
        freq[c]++;

    char data[256];
    int freqArr[256], size = 0;
    for (int i = 0; i < 256; i++)
        if (freq[i]) {
            data[size] = (char)i;
            freqArr[size++] = freq[i];
        }

    struct MinHeapNode* root = buildHuffmanTree(data, freqArr, size);

    char* codes[256] = {0};
    int arr[MAX_TREE_HT];
    storeCodes(root, arr, 0, codes);

    writeHeader(out, freq, originalSize);

    rewind(in);
    unsigned char buffer = 0;
    int bits = 0;

    while ((c = fgetc(in)) != EOF) {
        for (char* p = codes[c]; *p; p++) {
            buffer = (buffer << 1) | (*p - '0');
            if (++bits == 8) {
                fwrite(&buffer, 1, 1, out);
                buffer = bits = 0;
            }
        }
    }
    if (bits) {
        buffer <<= (8 - bits);
        fwrite(&buffer, 1, 1, out);
    }

    // Free allocated codes
    for (int i = 0; i < 256; i++) {
        if (codes[i]) free(codes[i]);
    }

    fclose(in);
    fclose(out);
}

void decompressFile(const char* inputFile, const char* outputFile) {
    FILE* in = fopen(inputFile, "rb");
    if (!in) {
        fprintf(stderr, "Error: Cannot open input file '%s'\n", inputFile);
        return;
    }
    
    FILE* out = fopen(outputFile, "wb");
    if (!out) {
        fprintf(stderr, "Error: Cannot create output file '%s'\n", outputFile);
        fclose(in);
        return;
    }

    int freq[256];
    long originalSize = readHeader(in, freq);

    // Handle empty file case
    if (originalSize == 0) {
        fclose(in);
        fclose(out);
        return;
    }

    char data[256];
    int freqArr[256], size = 0;
    for (int i = 0; i < 256; i++)
        if (freq[i]) {
            data[size] = (char)i;
            freqArr[size++] = freq[i];
        }

    struct MinHeapNode* root = buildHuffmanTree(data, freqArr, size);
    
    // Handle single unique character case
    if (isLeaf(root)) {
        for (long i = 0; i < originalSize; i++) {
            fputc(root->data, out);
        }
        fclose(in);
        fclose(out);
        return;
    }
    
    struct MinHeapNode* cur = root;
    long bytesWritten = 0;

    int byte;
    while ((byte = fgetc(in)) != EOF && bytesWritten < originalSize) {
        for (int i = 7; i >= 0 && bytesWritten < originalSize; i--) {
            cur = ((byte >> i) & 1) ? cur->right : cur->left;
            if (isLeaf(cur)) {
                fputc(cur->data, out);
                bytesWritten++;
                cur = root;
            }
        }
    }
    fclose(in);
    fclose(out);
}
