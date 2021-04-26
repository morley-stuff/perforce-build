echo off
echo "Building file 1..."
type src\file1.txt > bin\output.txt || exit 1
echo "Building file 2..."
type src\file2.txt >> bin\output.txt || exit 1
echo "Stamping date..."
echo %date%-%time% >> bin\output.txt || exit 1
echo "Build completed."