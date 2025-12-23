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
        codes[(unsigned char)root->data] = malloc(top + 1);
        for (int i = 0; i < top; i++)
            codes[(unsigned char)root->data][i] = arr[i] + '0';
        codes[(unsigned char)root->data][top] = '\0';
    }
}

static void writeHeader(FILE* out, int freq[]) {
    fwrite(freq, sizeof(int), 256, out);
}

static void readHeader(FILE* in, int freq[]) {
    fread(freq, sizeof(int), 256, in);
}

void compressFile(const char* inputFile, const char* outputFile) {
    FILE* in = fopen(inputFile, "rb");
    FILE* out = fopen(outputFile, "wb");

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

    writeHeader(out, freq);

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

    fclose(in);
    fclose(out);
}

void decompressFile(const char* inputFile, const char* outputFile) {
    FILE* in = fopen(inputFile, "rb");
    FILE* out = fopen(outputFile, "wb");

    int freq[256];
    readHeader(in, freq);

    char data[256];
    int freqArr[256], size = 0;
    for (int i = 0; i < 256; i++)
        if (freq[i]) {
            data[size] = (char)i;
            freqArr[size++] = freq[i];
        }

    struct MinHeapNode* root = buildHuffmanTree(data, freqArr, size);
    struct MinHeapNode* cur = root;

    int byte;
    while ((byte = fgetc(in)) != EOF) {
        for (int i = 7; i >= 0; i--) {
            cur = ((byte >> i) & 1) ? cur->right : cur->left;
            if (isLeaf(cur)) {
                fputc(cur->data, out);
                cur = root;
            }
        }
    }
    fclose(in);
    fclose(out);
}

