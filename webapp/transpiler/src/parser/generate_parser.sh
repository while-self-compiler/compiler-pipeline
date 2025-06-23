#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ANTLR_JAR="$SCRIPT_DIR/antlr-4.13.2-complete.jar"
GRAMMAR_FILE="$SCRIPT_DIR/ewhile.g4"
OUTPUT_DIR="$SCRIPT_DIR/generated_ewhile_parser"

pip install --quiet antlr4-python3-runtime
java -Xmx500M -cp "$ANTLR_JAR" org.antlr.v4.Tool -Dlanguage=Python3 \
  -o "$OUTPUT_DIR" \
  -package generated_while_parser \
  "$GRAMMAR_FILE" \
  -visitor

if [ $? -eq 0 ]; then
    echo "Parser generation successful!"
else
    echo "Parser generation failed!"
fi