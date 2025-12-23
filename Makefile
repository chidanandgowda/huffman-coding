# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -Iinclude
LDFLAGS =

# Directories
SRC_DIR = src
OBJ_DIR = obj
BIN = huffman

# Source and object files
SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJS = $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

# Default target
all: $(BIN)

# Create executable
$(BIN): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

# Compile source files into object files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c | $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Create obj directory if not present
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

# Clean build files
clean:
	rm -rf $(OBJ_DIR) $(BIN)

# Rebuild everything
rebuild: clean all

.PHONY: all clean rebuild

