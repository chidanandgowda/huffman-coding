#include <stdio.h>
#include <stdlib.h>
#include "minheap.h"

static void swap(struct MinHeapNode** a, struct MinHeapNode** b) {
    struct MinHeapNode* t = *a;
    *a = *b;
    *b = t;
}

struct MinHeapNode* newNode(char data, unsigned freq) {
    struct MinHeapNode* node = malloc(sizeof(struct MinHeapNode));
    node->data = data;
    node->freq = freq;
    node->left = node->right = NULL;
    return node;
}

struct MinHeap* createMinHeap(unsigned capacity) {
    struct MinHeap* heap = malloc(sizeof(struct MinHeap));
    heap->size = 0;
    heap->capacity = capacity;
    heap->array = malloc(capacity * sizeof(struct MinHeapNode*));
    return heap;
}

static void minHeapify(struct MinHeap* heap, int idx) {
    int smallest = idx;
    int l = 2 * idx + 1;
    int r = 2 * idx + 2;

    if (l < (int)heap->size && heap->array[l]->freq < heap->array[smallest]->freq)
        smallest = l;
    if (r < (int)heap->size && heap->array[r]->freq < heap->array[smallest]->freq)
        smallest = r;

    if (smallest != idx) {
        swap(&heap->array[smallest], &heap->array[idx]);
        minHeapify(heap, smallest);
    }
}

void buildMinHeap(struct MinHeap* heap) {
    for (int i = (heap->size - 1) / 2; i >= 0; i--)
        minHeapify(heap, i);
}

void insertMinHeap(struct MinHeap* heap, struct MinHeapNode* node) {
    int i = heap->size++;
    while (i && node->freq < heap->array[(i - 1) / 2]->freq) {
        heap->array[i] = heap->array[(i - 1) / 2];
        i = (i - 1) / 2;
    }
    heap->array[i] = node;
}

struct MinHeapNode* extractMin(struct MinHeap* heap) {
    struct MinHeapNode* temp = heap->array[0];
    heap->array[0] = heap->array[--heap->size];
    minHeapify(heap, 0);
    return temp;
}

int isLeaf(struct MinHeapNode* root) {
    return !(root->left) && !(root->right);
}

struct MinHeapNode* buildHuffmanTree(char data[], int freq[], int size) {
    struct MinHeap* heap = createMinHeap(size);

    for (int i = 0; i < size; i++)
        heap->array[i] = newNode(data[i], freq[i]);

    heap->size = size;
    buildMinHeap(heap);

    while (heap->size > 1) {
        struct MinHeapNode* left = extractMin(heap);
        struct MinHeapNode* right = extractMin(heap);

        struct MinHeapNode* top = newNode('$', left->freq + right->freq);
        top->left = left;
        top->right = right;

        insertMinHeap(heap, top);
    }
    return extractMin(heap);
}

