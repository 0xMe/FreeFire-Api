#!/bin/bash
mkdir -p compiled

cd "$(dirname "$0")"

# Compile all .proto files into ./compiled/
protoc -I=. --python_out=./compiled *.proto

# Fix imports to use package-style paths
sed -i 's/^import \(.*_pb2\)/from Proto.compiled import \1/' compiled/*.py