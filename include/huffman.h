#ifndef HUFFMAN_H
#define HUFFMAN_H

#define MAX_TREE_HT 256

void compressFile(const char* inputFile, const char* outputFile);
void decompressFile(const char* inputFile, const char* outputFile);

#endif

