#!/bin/bash

blogs_dir="/home/neel/notneelpatel.github.io/blog/markdown"

for file in "$blogs_dir"/*.md; do
	if [ -f "$file" ]; then
		python3 blog-engine.py "$file"
	fi
done
