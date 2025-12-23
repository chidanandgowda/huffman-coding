#ifndef MINHEAP_H
#define MINHEAP_H

struct MinHeapNode {
    char data;
    unsigned freq;
    struct MinHeapNode *left, *right;
};

struct MinHeap {
    unsigned size;
    unsigned capacity;
    struct MinHeapNode **array;
};

struct MinHeapNode* newNode(char data, unsigned freq);
struct MinHeap* createMinHeap(unsigned capacity);
void insertMinHeap(struct MinHeap* minHeap, struct MinHeapNode* node);
struct MinHeapNode* extractMin(struct MinHeap* minHeap);
void buildMinHeap(struct MinHeap* minHeap);
struct MinHeapNode* buildHuffmanTree(char data[], int freq[], int size);
int isLeaf(struct MinHeapNode* root);

#endif

