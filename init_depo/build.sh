#!/bin/bash
set -e
mkdir -p bin
echo "Building file 1..."
cat src/file1.txt > bin/output.txt
echo "Building file 2..."
cat src/file2.txt >> bin/output.txt 
echo "Stamping date..."
date >> bin/output.txt
echo "Build completed."